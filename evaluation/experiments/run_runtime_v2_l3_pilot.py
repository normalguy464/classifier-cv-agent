from __future__ import annotations

import argparse
import asyncio
import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from statistics import mean
from typing import Annotated, Literal, Protocol, Self, cast

import httpx
import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.app.contracts import CVProfile, EvidenceStatus, JobProfile, ScoringRubric
from backend.app.core.settings import RuntimeSettings
from backend.app.agents.classifier.scoring.l1 import score_l1
from backend.app.agents.classifier.scoring.l3_calibration import (
    L3CalibrationLevel,
    calibrated_l3_criterion_scores,
)
from backend.app.infrastructure.config import build_l1_policy, load_yaml_artifact
from backend.app.infrastructure.config.artifacts import L1RulesConfigurationArtifact
from backend.app.infrastructure.llm import (
    LLMProviderResult,
    LLMProviderStatus,
    LLMProviderUsage,
    LLMRequirementReference,
    LLMScoringOutput,
    LLMScoringRequest,
    OpenAICompatibleLLMAdapter,
)
from evaluation.datasets.runtime_v2 import RuntimeV2SplitManifest, file_sha256
from evaluation.datasets.synthetic_expansion import SyntheticPairAnnotation

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = Path("evaluation/configs/runtime_v2_l3_pilot_v1.yaml")
CACHE_PATH = Path("evaluation/reports/generated/runtime_v2_l3_pilot_cache_v1.json")
REPORT_PATH = Path("evaluation/reports/runtime_v2_l3_pilot_v1.json")


class FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class PilotDataPolicy(FrozenModel):
    partition: Literal["development", "validation"] = "development"
    development_only: bool
    validation_allowed: bool
    stage7_v1_test_allowed: Literal[False]
    raw_provider_response_persisted: Literal[False]

    @model_validator(mode="after")
    def validate_partition_flags(self) -> Self:
        expected = {
            "development": (True, False),
            "validation": (False, True),
        }[self.partition]
        if (self.development_only, self.validation_allowed) != expected:
            raise ValueError("L3 data partition flags are inconsistent")
        return self


class PilotRequestPolicy(FrozenModel):
    hard_request_cap: int = Field(ge=5, le=60)
    maximum_retries_per_pair: int = Field(ge=0, le=1)
    minimum_request_interval_seconds: Decimal = Field(ge=0, le=60)
    request_timeout_seconds: Decimal = Field(gt=0, le=180)
    max_completion_tokens: int = Field(ge=256, le=8192)
    reasoning_effort: Literal["none", "low"]
    include_temperature_parameter: Literal[False]


class PilotCostPolicy(FrozenModel):
    input_usd_per_million_tokens: Decimal = Field(ge=0)
    cached_input_usd_per_million_tokens: Decimal = Field(ge=0)
    output_usd_per_million_tokens: Decimal = Field(ge=0)
    maximum_estimated_cost_usd: Decimal = Field(gt=0, le=1)


class PilotQualityPolicy(FrozenModel):
    required_valid_output_rate: Decimal = Field(ge=Decimal("1"), le=Decimal("1"))
    required_requirement_status_match_rate: Decimal = Field(ge=Decimal("0.95"), le=1)
    maximum_unsafe_requirement_status_mismatch_count: Literal[0]
    maximum_criterion_mae: Decimal = Field(ge=0, le=10)
    maximum_total_score_mae: Decimal = Field(ge=0, le=30)
    maximum_endpoint_score_rate: Decimal = Field(ge=0, le=1)


class RuntimeV2L3PilotConfiguration(FrozenModel):
    schema_version: Literal["1.0.0"]
    experiment_id: Literal[
        "runtime-v2-l3-pilot-v1",
        "runtime-v2-l3-pilot-v2",
        "runtime-v2-l3-pilot-v3",
        "runtime-v2-l3-development-panel-v1",
        "runtime-v2-l3-calibration-probe-v4",
        "runtime-v2-l3-development-panel-v2",
        "runtime-v2-l3-validation-v1",
        "runtime-v2-l3-fresh-confirmation-v1",
        "runtime-v2-l3-fresh-confirmation-v2",
        "runtime-v2-l3-fresh-confirmation-v2-rescore-v3",
        "runtime-v2-l3-development-panel-v2-rescore-v3",
        "runtime-v2-l3-fresh-confirmation-v1-rescore-v3",
    ]
    experiment_version: Literal["1.0.0", "2.0.0", "3.0.0"]
    status: Literal["approved_after_offline_checkpoint"]
    reviewed_dataset_directory: Path
    split_manifest_path: Path
    offline_checkpoint_path: Path
    runtime_configuration_directory: Path = Path("configs/runtime/five_role_v2_candidate")
    provider_identifier: Literal["openai"]
    model_identifier: Literal["gpt-5.4-mini-2026-03-17"]
    prompt_version: Literal[
        "l3-evidence-rubric-v12",
        "l3-evidence-rubric-v13",
        "l3-evidence-rubric-v14",
        "l3-evidence-rubric-v15",
    ]
    score_mapping_version: Literal[
        "l3-deterministic-level-mapping-v1",
        "l3-deterministic-level-mapping-v2",
        "l3-deterministic-level-mapping-v3",
    ]
    data_policy: PilotDataPolicy
    request_policy: PilotRequestPolicy
    cost_policy: PilotCostPolicy
    pilot_pair_ids: Annotated[tuple[str, ...], Field(min_length=5, max_length=50)]
    quality_policy: PilotQualityPolicy

    @model_validator(mode="after")
    def validate_configuration(self) -> Self:
        paths = (
            self.reviewed_dataset_directory,
            self.split_manifest_path,
            self.offline_checkpoint_path,
            self.runtime_configuration_directory,
        )
        if any(path.is_absolute() or ".." in path.parts for path in paths):
            raise ValueError("pilot paths must be repository-relative")
        if len(self.pilot_pair_ids) != len(set(self.pilot_pair_ids)):
            raise ValueError("pilot pair identifiers must be unique")
        if self.request_policy.hard_request_cap < len(self.pilot_pair_ids):
            raise ValueError("pilot hard request cap must cover primary pairs")
        expected = {
            "runtime-v2-l3-pilot-v1": ("1.0.0", "l3-evidence-rubric-v12"),
            "runtime-v2-l3-pilot-v2": ("2.0.0", "l3-evidence-rubric-v13"),
            "runtime-v2-l3-pilot-v3": ("3.0.0", "l3-evidence-rubric-v14"),
            "runtime-v2-l3-development-panel-v1": (
                "1.0.0",
                "l3-evidence-rubric-v14",
            ),
            "runtime-v2-l3-calibration-probe-v4": (
                "1.0.0",
                "l3-evidence-rubric-v15",
            ),
            "runtime-v2-l3-development-panel-v2": (
                "2.0.0",
                "l3-evidence-rubric-v15",
            ),
            "runtime-v2-l3-validation-v1": (
                "1.0.0",
                "l3-evidence-rubric-v15",
            ),
            "runtime-v2-l3-fresh-confirmation-v1": (
                "1.0.0",
                "l3-evidence-rubric-v15",
            ),
            "runtime-v2-l3-fresh-confirmation-v2": (
                "2.0.0",
                "l3-evidence-rubric-v15",
            ),
            "runtime-v2-l3-fresh-confirmation-v2-rescore-v3": (
                "3.0.0",
                "l3-evidence-rubric-v15",
            ),
            "runtime-v2-l3-development-panel-v2-rescore-v3": (
                "3.0.0",
                "l3-evidence-rubric-v15",
            ),
            "runtime-v2-l3-fresh-confirmation-v1-rescore-v3": (
                "2.0.0",
                "l3-evidence-rubric-v15",
            ),
        }
        if (self.experiment_version, self.prompt_version) != expected[self.experiment_id]:
            raise ValueError("pilot experiment, version, and prompt version must be aligned")
        expected_mapping = {
            "runtime-v2-l3-calibration-probe-v4": "l3-deterministic-level-mapping-v1",
            "runtime-v2-l3-fresh-confirmation-v2-rescore-v3": "l3-deterministic-level-mapping-v3",
            "runtime-v2-l3-development-panel-v2-rescore-v3": "l3-deterministic-level-mapping-v3",
            "runtime-v2-l3-fresh-confirmation-v1-rescore-v3": "l3-deterministic-level-mapping-v3",
        }.get(
            self.experiment_id,
            (
                "l3-deterministic-level-mapping-v2"
                if self.prompt_version == "l3-evidence-rubric-v15"
                else "l3-deterministic-level-mapping-v1"
            ),
        )
        if self.score_mapping_version != expected_mapping:
            raise ValueError("pilot prompt and score mapping version must be aligned")
        return self


class PilotAttempt(FrozenModel):
    pair_id: str
    attempt_number: int = Field(ge=1, le=2)
    status: LLMProviderStatus
    output: LLMScoringOutput | None = None
    usage: LLMProviderUsage | None = None
    reason: str | None = None
    calibration_levels: dict[str, str] | None = None

    @model_validator(mode="after")
    def validate_result(self) -> Self:
        if self.status is LLMProviderStatus.AVAILABLE:
            if self.output is None or self.reason is not None:
                raise ValueError("available pilot attempt requires output")
        elif (
            self.output is not None
            or self.usage is not None
            or self.reason is None
            or self.calibration_levels is not None
        ):
            raise ValueError("failed pilot attempt requires only a reason")
        return self


class PilotCache(FrozenModel):
    schema_version: Literal["1.0.0"]
    experiment_id: Literal[
        "runtime-v2-l3-pilot-v1",
        "runtime-v2-l3-pilot-v2",
        "runtime-v2-l3-pilot-v3",
        "runtime-v2-l3-development-panel-v1",
        "runtime-v2-l3-calibration-probe-v4",
        "runtime-v2-l3-development-panel-v2",
        "runtime-v2-l3-validation-v1",
        "runtime-v2-l3-fresh-confirmation-v1",
        "runtime-v2-l3-fresh-confirmation-v2",
        "runtime-v2-l3-fresh-confirmation-v2-rescore-v3",
        "runtime-v2-l3-development-panel-v2-rescore-v3",
        "runtime-v2-l3-fresh-confirmation-v1-rescore-v3",
    ]
    configuration_sha256: str
    reviewed_manifest_sha256: str
    split_manifest_sha256: str
    provider_identifier: str
    model_identifier: str
    prompt_version: str
    attempts: tuple[PilotAttempt, ...] = ()


class PilotAdapter(Protocol):
    async def score(self, request: LLMScoringRequest) -> LLMProviderResult: ...


def load_pilot_configuration(
    repository_root: Path,
    configuration_path: Path = CONFIG_PATH,
) -> RuntimeV2L3PilotConfiguration:
    payload = yaml.safe_load((repository_root / configuration_path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Runtime v2 L3 pilot configuration must be a mapping")
    return RuntimeV2L3PilotConfiguration.model_validate(cast(dict[str, object], payload))


def _timestamp(value: str) -> datetime:
    try:
        timestamp = datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError("generated_at must be an ISO 8601 timestamp") from error
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("generated_at must include a timezone")
    return timestamp


def _load_data(
    repository_root: Path,
    configuration: RuntimeV2L3PilotConfiguration,
) -> tuple[
    dict[str, SyntheticPairAnnotation],
    dict[str, CVProfile],
    dict[str, JobProfile],
    dict[str, ScoringRubric],
    RuntimeV2SplitManifest,
]:
    reviewed = repository_root / configuration.reviewed_dataset_directory
    pairs = {
        item.pair_id: item
        for item in (
            SyntheticPairAnnotation.model_validate_json(line)
            for line in (reviewed / "pairs.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    }
    profiles = {
        item.cv_profile_id: item
        for item in (
            CVProfile.model_validate_json(line)
            for line in (reviewed / "cv_profiles.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    }
    jobs = {
        item.job_profile_id: item
        for item in (
            JobProfile.model_validate_json(line)
            for line in (reviewed / "job_profiles.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    }
    rubrics = {
        item.rubric_id: item
        for item in (
            ScoringRubric.model_validate_json(line)
            for line in (reviewed / "rubrics.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    }
    split = RuntimeV2SplitManifest.model_validate_json(
        (repository_root / configuration.split_manifest_path).read_text(encoding="utf-8")
    )
    allowed_pair_ids = (
        split.development.pair_ids
        if configuration.data_policy.partition == "development"
        else split.validation.pair_ids
    )
    if not set(configuration.pilot_pair_ids).issubset(allowed_pair_ids):
        raise ValueError("L3 cases must belong only to the configured partition")
    pilot_roles = {pairs[pair_id].role.value for pair_id in configuration.pilot_pair_ids}
    if len(pilot_roles) != 5:
        raise ValueError("L3 pilot must cover exactly five roles")
    checkpoint = cast(
        dict[str, object],
        json.loads(
            (repository_root / configuration.offline_checkpoint_path).read_text(encoding="utf-8")
        ),
    )
    gate = cast(dict[str, object], checkpoint["quality_gate"])
    if gate.get("passed") is not True:
        raise ValueError("offline L1/L2 checkpoint must pass before L3 pilot")
    if checkpoint.get("llm_provider_calls_made") is not False:
        raise ValueError("offline checkpoint must not contain provider calls")
    return pairs, profiles, jobs, rubrics, split


def _empty_cache(
    repository_root: Path,
    configuration: RuntimeV2L3PilotConfiguration,
    configuration_path: Path,
) -> PilotCache:
    reviewed = repository_root / configuration.reviewed_dataset_directory
    return PilotCache(
        schema_version="1.0.0",
        experiment_id=configuration.experiment_id,
        configuration_sha256=file_sha256(repository_root / configuration_path),
        reviewed_manifest_sha256=file_sha256(reviewed / "manifest.json"),
        split_manifest_sha256=file_sha256(repository_root / configuration.split_manifest_path),
        provider_identifier=configuration.provider_identifier,
        model_identifier=configuration.model_identifier,
        prompt_version=configuration.prompt_version,
    )


def _load_cache(
    repository_root: Path,
    cache_path: Path,
    expected: PilotCache,
) -> PilotCache:
    path = repository_root / cache_path
    if not path.exists():
        return expected
    payload = cast(dict[str, object], json.loads(path.read_text(encoding="utf-8")))
    attempts = payload.get("attempts")
    if isinstance(attempts, list):
        for attempt_value in cast(list[object], attempts):
            if not isinstance(attempt_value, dict):
                continue
            attempt = cast(dict[str, object], attempt_value)
            output_value = attempt.get("output")
            if not isinstance(output_value, dict):
                continue
            output = cast(dict[str, object], output_value)
            for field_name in ("overall_score", "confidence"):
                value = output.get(field_name)
                if isinstance(value, str):
                    output[field_name] = Decimal(value)
            criteria = output.get("criterion_assessments")
            if isinstance(criteria, list):
                for criterion_value in cast(list[object], criteria):
                    if not isinstance(criterion_value, dict):
                        continue
                    criterion = cast(dict[str, object], criterion_value)
                    score = criterion.get("score")
                    if isinstance(score, str):
                        criterion["score"] = Decimal(score)
    cache = PilotCache.model_validate(payload)
    if cache.model_copy(update={"attempts": ()}) != expected:
        raise ValueError("L3 pilot cache does not match configuration or data hashes")
    return cache


def _write_cache(repository_root: Path, cache_path: Path, cache: PilotCache) -> None:
    path = repository_root / cache_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            cache.model_dump(mode="python"),
            ensure_ascii=False,
            indent=2,
            default=_json_default,
        )
        + "\n",
        encoding="utf-8",
    )


def _json_default(value: object) -> float:
    if isinstance(value, Decimal):
        return float(value)
    raise TypeError(f"unsupported cache JSON value: {type(value).__name__}")


def _request(
    pair: SyntheticPairAnnotation,
    profiles: dict[str, CVProfile],
    jobs: dict[str, JobProfile],
    rubrics: dict[str, ScoringRubric],
    prompt_version: str,
    attempt_number: int,
    authoritative_requirements: tuple[LLMRequirementReference, ...] = (),
) -> LLMScoringRequest:
    profile = profiles[pair.cv_profile_id]
    return LLMScoringRequest(
        request_id=f"{pair.pair_id}-pilot-{attempt_number}",
        job_profile=jobs[pair.job_profile_id],
        rubric=rubrics[pair.rubric_id],
        evidence=profile.evidence,
        prompt_version=prompt_version,
        authoritative_requirement_assessments=authoritative_requirements,
    )


async def collect_pilot(
    repository_root: Path,
    adapter: PilotAdapter,
    configuration_path: Path = CONFIG_PATH,
    cache_path: Path = CACHE_PATH,
    maximum_new_requests: int | None = None,
) -> PilotCache:
    configuration = load_pilot_configuration(repository_root, configuration_path)
    pairs, profiles, jobs, rubrics, _ = _load_data(repository_root, configuration)
    l1_policies = {}
    if configuration.prompt_version in {
        "l3-evidence-rubric-v14",
        "l3-evidence-rubric-v15",
    }:
        l1_artifact = load_yaml_artifact(
            repository_root / configuration.runtime_configuration_directory / "l1_rules.yaml",
            L1RulesConfigurationArtifact,
        )
        l1_policies = {item.job_profile_id: build_l1_policy(item) for item in l1_artifact.policies}
    cache = _load_cache(
        repository_root,
        cache_path,
        _empty_cache(repository_root, configuration, configuration_path),
    )
    attempts = list(cache.attempts)
    new_requests = 0
    for pair_id in configuration.pilot_pair_ids:
        existing = [item for item in attempts if item.pair_id == pair_id]
        if any(item.status is LLMProviderStatus.AVAILABLE for item in existing):
            continue
        while len(existing) <= configuration.request_policy.maximum_retries_per_pair:
            if len(attempts) >= configuration.request_policy.hard_request_cap:
                return cache.model_copy(update={"attempts": tuple(attempts)})
            if maximum_new_requests is not None and new_requests >= maximum_new_requests:
                return cache.model_copy(update={"attempts": tuple(attempts)})
            if new_requests > 0:
                await asyncio.sleep(
                    float(configuration.request_policy.minimum_request_interval_seconds)
                )
            result = await adapter.score(
                _request(
                    pairs[pair_id],
                    profiles,
                    jobs,
                    rubrics,
                    configuration.prompt_version,
                    len(existing) + 1,
                    (
                        tuple(
                            LLMRequirementReference(
                                requirement_id=item.requirement_id,
                                evidence_status=item.evidence_status,
                                evidence_ids=item.evidence_ids,
                                rationale=item.rationale,
                            )
                            for item in score_l1(
                                profiles[pairs[pair_id].cv_profile_id],
                                rubrics[pairs[pair_id].rubric_id],
                                l1_policies[pairs[pair_id].job_profile_id],
                            ).requirement_assessments
                        )
                        if configuration.prompt_version
                        in {"l3-evidence-rubric-v14", "l3-evidence-rubric-v15"}
                        else ()
                    ),
                )
            )
            attempt = PilotAttempt(
                pair_id=pair_id,
                attempt_number=len(existing) + 1,
                status=result.status,
                output=result.output,
                usage=result.usage,
                reason=result.reason,
                calibration_levels=(
                    None
                    if result.calibration_levels is None
                    else {key: value.value for key, value in result.calibration_levels.items()}
                ),
            )
            attempts.append(attempt)
            existing.append(attempt)
            new_requests += 1
            cache = cache.model_copy(update={"attempts": tuple(attempts)})
            _write_cache(repository_root, cache_path, cache)
            if result.status is LLMProviderStatus.AVAILABLE:
                break
    return cache.model_copy(update={"attempts": tuple(attempts)})


def _unsafe_mismatch(human: EvidenceStatus, predicted: EvidenceStatus) -> bool:
    return human is not predicted and predicted in {
        EvidenceStatus.SATISFIED,
        EvidenceStatus.UNSATISFIED,
    }


def _estimated_cost(
    attempts: tuple[PilotAttempt, ...],
    configuration: RuntimeV2L3PilotConfiguration,
) -> Decimal:
    total = Decimal("0")
    for attempt in attempts:
        if attempt.usage is None:
            continue
        usage = attempt.usage
        uncached = max(0, usage.input_tokens - usage.cached_input_tokens)
        total += (
            Decimal(uncached) * configuration.cost_policy.input_usd_per_million_tokens
            + Decimal(usage.cached_input_tokens)
            * configuration.cost_policy.cached_input_usd_per_million_tokens
            + Decimal(usage.output_tokens) * configuration.cost_policy.output_usd_per_million_tokens
        ) / Decimal("1000000")
    return total


def _effective_output(
    attempt: PilotAttempt,
    rubric: ScoringRubric,
    configuration: RuntimeV2L3PilotConfiguration,
) -> LLMScoringOutput:
    if attempt.output is None:
        raise ValueError("available pilot attempt has no output")
    if configuration.score_mapping_version == "l3-deterministic-level-mapping-v1":
        return attempt.output
    if attempt.calibration_levels is None:
        raise ValueError("mapping v2 requires persisted qualitative calibration levels")
    levels = {
        criterion_id: L3CalibrationLevel(level)
        for criterion_id, level in attempt.calibration_levels.items()
    }
    scores = calibrated_l3_criterion_scores(
        rubric,
        {
            item.requirement_id: item.evidence_status
            for item in attempt.output.requirement_assessments
        },
        levels,
        {item.criterion_id: item.evidence_status for item in attempt.output.criterion_assessments},
        configuration.score_mapping_version,
    )
    criteria = tuple(
        item.model_copy(update={"score": scores[item.criterion_id]})
        for item in attempt.output.criterion_assessments
    )
    return attempt.output.model_copy(
        update={
            "criterion_assessments": criteria,
            "overall_score": sum((item.score for item in criteria), Decimal("0")),
        }
    )


def build_pilot_report(
    repository_root: Path,
    generated_at: datetime,
    cache: PilotCache,
    configuration_path: Path = CONFIG_PATH,
) -> dict[str, object]:
    configuration = load_pilot_configuration(repository_root, configuration_path)
    pairs, _, _, rubrics, _ = _load_data(repository_root, configuration)
    available = {
        item.pair_id: item
        for item in cache.attempts
        if item.status is LLMProviderStatus.AVAILABLE and item.output is not None
    }
    requirement_total = 0
    requirement_matches = 0
    unsafe = 0
    criterion_errors: list[float] = []
    total_errors: list[float] = []
    endpoint_scores = 0
    criterion_count = 0
    cases: list[dict[str, object]] = []
    for pair_id in configuration.pilot_pair_ids:
        attempt = available.get(pair_id)
        if attempt is None or attempt.output is None:
            continue
        pair = pairs[pair_id]
        output = _effective_output(attempt, rubrics[pair.rubric_id], configuration)
        human_requirements = {
            item.requirement_id: item.evidence_status
            for item in pair.critical_requirement_assessments
        }
        predicted_requirements = {
            item.requirement_id: item.evidence_status for item in output.requirement_assessments
        }
        for requirement_id, human in human_requirements.items():
            predicted = predicted_requirements[requirement_id]
            requirement_total += 1
            requirement_matches += predicted is human
            unsafe += _unsafe_mismatch(human, predicted)
        human_criteria = {
            item.criterion_id: float(item.awarded_points) for item in pair.criterion_assessments
        }
        maximums = {
            item.criterion_id: float(item.weight) for item in rubrics[pair.rubric_id].criteria
        }
        for item in output.criterion_assessments:
            score = float(item.score)
            criterion_errors.append(abs(score - human_criteria[item.criterion_id]))
            endpoint_scores += score in {0.0, maximums[item.criterion_id]}
            criterion_count += 1
        total_errors.append(abs(float(output.overall_score) - float(pair.total_score)))
        cases.append(
            {
                "pair_id": pair_id,
                "role": pair.role.value,
                "human_total_score": float(pair.total_score),
                "l3_total_score": float(output.overall_score),
                "requirement_matches": sum(
                    predicted_requirements[item] is human_requirements[item]
                    for item in human_requirements
                ),
                "requirement_count": len(human_requirements),
            }
        )
    valid_rate = len(available) / len(configuration.pilot_pair_ids)
    requirement_rate = requirement_matches / requirement_total if requirement_total else 0.0
    criterion_mae = mean(criterion_errors) if criterion_errors else 100.0
    total_mae = mean(total_errors) if total_errors else 100.0
    endpoint_rate = endpoint_scores / criterion_count if criterion_count else 1.0
    cost = _estimated_cost(cache.attempts, configuration)
    checks = {
        "valid_output_rate": valid_rate
        >= float(configuration.quality_policy.required_valid_output_rate),
        "requirement_status_match_rate": requirement_rate
        >= float(configuration.quality_policy.required_requirement_status_match_rate),
        "unsafe_requirement_status_mismatch_count": unsafe
        <= configuration.quality_policy.maximum_unsafe_requirement_status_mismatch_count,
        "criterion_mae": criterion_mae <= float(configuration.quality_policy.maximum_criterion_mae),
        "total_score_mae": total_mae <= float(configuration.quality_policy.maximum_total_score_mae),
        "endpoint_score_rate": endpoint_rate
        <= float(configuration.quality_policy.maximum_endpoint_score_rate),
        "estimated_cost": cost <= configuration.cost_policy.maximum_estimated_cost_usd,
    }
    return {
        "schema_version": "1.0.0",
        "report_id": configuration.experiment_id,
        "generated_at": generated_at.isoformat(),
        "provider_identifier": configuration.provider_identifier,
        "model_identifier": configuration.model_identifier,
        "prompt_version": configuration.prompt_version,
        "score_mapping_version": configuration.score_mapping_version,
        "request_count": len(cache.attempts),
        "valid_output_count": len(available),
        "valid_output_rate": valid_rate,
        "requirement_status_match_rate": requirement_rate,
        "unsafe_requirement_status_mismatch_count": unsafe,
        "criterion_mae": criterion_mae,
        "total_score_mae": total_mae,
        "endpoint_score_rate": endpoint_rate,
        "estimated_cost_usd": str(cost.quantize(Decimal("0.0000001"))),
        "quality_gate": {"passed": all(checks.values()), "checks": checks},
        "cases": cases,
        "data_policy": configuration.data_policy.model_dump(mode="json"),
        "traceability": {
            "configuration_sha256": file_sha256(repository_root / configuration_path),
            "reviewed_manifest_sha256": cache.reviewed_manifest_sha256,
            "split_manifest_sha256": cache.split_manifest_sha256,
            "offline_checkpoint_sha256": file_sha256(
                repository_root / configuration.offline_checkpoint_path
            ),
            "raw_provider_response_persisted": False,
        },
    }


def _configured_adapter(
    settings: RuntimeSettings,
    configuration: RuntimeV2L3PilotConfiguration,
    client: httpx.AsyncClient,
) -> OpenAICompatibleLLMAdapter:
    provider = settings.classifier_llm_provider
    model = settings.classifier_llm_model
    api_key = settings.classifier_llm_api_key
    base_url = settings.classifier_llm_base_url
    if (
        settings.classifier_llm_adapter != "environment_configured"
        or provider is None
        or model is None
        or api_key is None
        or base_url is None
    ):
        raise ValueError("live L3 settings are incomplete")
    if provider != configuration.provider_identifier or model != configuration.model_identifier:
        raise ValueError("live L3 provider or model does not match the pilot configuration")
    if base_url.rstrip("/") != "https://api.openai.com/v1":
        raise ValueError("live L3 base URL does not match OpenAI")
    secret = api_key.get_secret_value()
    if secret.startswith("<") or "replace" in secret.casefold():
        raise ValueError("live L3 API key is still a placeholder")
    return OpenAICompatibleLLMAdapter(
        provider_identifier=provider,
        model_identifier=model,
        api_key=secret,
        base_url=base_url,
        prompt_version=configuration.prompt_version,
        client=client,
        include_temperature_parameter=configuration.request_policy.include_temperature_parameter,
        max_completion_tokens=configuration.request_policy.max_completion_tokens,
        reasoning_effort=configuration.request_policy.reasoning_effort,
        score_mapping_version=configuration.score_mapping_version,
    )


async def _main_async(arguments: argparse.Namespace) -> Path | None:
    configuration_path = Path(cast(str, arguments.configuration_path))
    cache_path = Path(cast(str, arguments.cache_path))
    report_path = Path(cast(str, arguments.report_path))
    configuration = load_pilot_configuration(REPOSITORY_ROOT, configuration_path)
    _load_data(REPOSITORY_ROOT, configuration)
    settings = RuntimeSettings()
    timeout = httpx.Timeout(float(configuration.request_policy.request_timeout_seconds))
    async with httpx.AsyncClient(timeout=timeout) as client:
        adapter = _configured_adapter(settings, configuration, client)
        if cast(bool, arguments.preflight):
            print(
                json.dumps(
                    {
                        "preflight_passed": True,
                        "provider_identifier": configuration.provider_identifier,
                        "model_identifier": configuration.model_identifier,
                        "pilot_pair_count": len(configuration.pilot_pair_ids),
                        "hard_request_cap": configuration.request_policy.hard_request_cap,
                        "maximum_estimated_cost_usd": str(
                            configuration.cost_policy.maximum_estimated_cost_usd
                        ),
                    },
                    ensure_ascii=False,
                )
            )
            return None
        cache = await collect_pilot(
            REPOSITORY_ROOT,
            adapter,
            configuration_path=configuration_path,
            cache_path=cache_path,
            maximum_new_requests=cast(int | None, arguments.maximum_new_requests),
        )
    report = build_pilot_report(
        REPOSITORY_ROOT,
        _timestamp(cast(str, arguments.generated_at)),
        cache,
        configuration_path=configuration_path,
    )
    output_path = REPOSITORY_ROOT / report_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--maximum-new-requests", type=int)
    parser.add_argument("--generated-at", default="2026-08-08T10:00:00+07:00")
    parser.add_argument("--configuration-path", default=str(CONFIG_PATH))
    parser.add_argument("--cache-path", default=str(CACHE_PATH))
    parser.add_argument("--report-path", default=str(REPORT_PATH))
    arguments = parser.parse_args()
    output = asyncio.run(_main_async(arguments))
    if output is not None:
        print(output)


if __name__ == "__main__":
    main()
