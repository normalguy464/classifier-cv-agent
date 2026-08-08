from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import random
from collections import Counter
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import asdict, dataclass
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from statistics import mean
from time import perf_counter
from typing import cast

import httpx
import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.app.agents.classifier.routing import route_classification
from backend.app.agents.classifier.scoring import (
    L3ProviderRequest,
    score_l1,
    score_l2,
    score_l3,
)
from backend.app.contracts import (
    CVProfile,
    ClassificationDecision,
    EvidenceStatus,
    JobProfile,
    LevelScoreStatus,
    ScoringRubric,
)
from backend.app.core.settings import RuntimeSettings
from backend.app.domain import AggregationResult, LevelAssessment, ScoringLevel
from backend.app.infrastructure.config import (
    LoadedClassifierConfiguration,
    RepositoryConfigurationLoader,
    build_l2_policy,
    build_routing_policy,
)
from backend.app.infrastructure.calibration import SklearnExtraTreesL2Calibrator
from backend.app.infrastructure.embeddings import (
    CoreEmbeddingAdapterBridge,
    EmbeddingAdapter,
    EmbeddingInputType,
    EmbeddingResult,
    SentenceTransformerEmbeddingAdapter,
)
from backend.app.infrastructure.llm import (
    LLMAdapter,
    LLMProviderResult,
    LLMProviderStatus,
    LLMRequirementReference,
    LLMScoringOutput,
    LLMScoringRequest,
    OpenAICompatibleLLMAdapter,
)
from evaluation.baselines import EmbeddingOnlyBaseline, KeywordRuleBaseline, TfidfCosineBaseline
from evaluation.datasets.stage7 import (
    Stage7EvaluationProtocol,
    Stage7FrozenManifest,
    stage7_manifest_sha256,
    validate_stage7_frozen_test_set,
)
from evaluation.datasets.synthetic_expansion import (
    ApprovedDatasetReview,
    DatasetRole,
    SyntheticPairAnnotation,
)
from evaluation.metrics import ClassificationMetrics, calculate_metrics

PROTOCOL_PATH = Path("evaluation/configs/stage7_frozen_evaluation_v1.yaml")
DATASET_DIRECTORY = Path("data/frozen_test/stage7_v1")
CACHE_PATH = Path("evaluation/reports/generated/stage7_frozen_l3_cache_v1.json")
REPORT_PATH = Path("evaluation/reports/stage7_frozen_evaluation_v1.json")
RUNTIME_DIRECTORY = Path("configs/runtime/five_role_v1")
SCORE_QUANTUM = Decimal("0.01")


@dataclass(frozen=True)
class Stage7ExecutionTarget:
    protocol_path: Path
    dataset_directory: Path
    runtime_directory: Path
    report_id: str
    report_scope: str


V1_EXECUTION_TARGET = Stage7ExecutionTarget(
    protocol_path=PROTOCOL_PATH,
    dataset_directory=DATASET_DIRECTORY,
    runtime_directory=RUNTIME_DIRECTORY,
    report_id="stage7-five-role-frozen-evaluation-v1",
    report_scope="gold-frozen-five-role-final-test",
)


class Stage7EvaluationError(RuntimeError):
    pass


class Stage7ProviderUnavailable(Stage7EvaluationError):
    pass


class Stage7RequestCapReached(Stage7EvaluationError):
    pass


class Stage7CacheModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class Stage7CachedAttempt(Stage7CacheModel):
    attempt_number: int = Field(ge=1, le=2)
    duration_milliseconds: int = Field(ge=0)
    result: LLMProviderResult


class Stage7CachedFailure(Stage7CacheModel):
    intended_attempt_number: int = Field(ge=1, le=2)
    duration_milliseconds: int = Field(ge=0)
    status: LLMProviderStatus
    reason: str = Field(min_length=1, max_length=1000)


class Stage7EvaluationCache(Stage7CacheModel):
    cache_schema_version: str
    protocol_sha256: str
    dataset_manifest_sha256: str
    runtime_manifest_sha256: str
    provider_identifier: str
    model_identifier: str
    prompt_version: str
    records: dict[str, tuple[Stage7CachedAttempt, ...]] = Field(default_factory=dict)
    failures: dict[str, tuple[Stage7CachedFailure, ...]] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_attempts(self) -> Stage7EvaluationCache:
        for attempts in self.records.values():
            numbers = tuple(item.attempt_number for item in attempts)
            if numbers != tuple(range(1, len(numbers) + 1)):
                raise ValueError("Stage 7 cached attempts must be sequential")
            if any(
                item.result.provider_identifier != self.provider_identifier
                or item.result.model_identifier != self.model_identifier
                or item.result.prompt_version != self.prompt_version
                for item in attempts
            ):
                raise ValueError("Stage 7 cached provider metadata does not match")
        return self

    @property
    def total_http_request_count(self) -> int:
        return sum(len(items) for items in self.records.values()) + sum(
            len(items) for items in self.failures.values()
        )


class CachingEmbeddingAdapter:
    def __init__(self, adapter: EmbeddingAdapter) -> None:
        self._adapter = adapter
        self._vectors: dict[tuple[EmbeddingInputType, str], tuple[float, ...]] = {}

    @property
    def model_identifier(self) -> str:
        return self._adapter.model_identifier

    @property
    def model_version(self) -> str:
        return self._adapter.model_version

    def embed(
        self,
        texts: Sequence[str],
        input_type: EmbeddingInputType,
    ) -> EmbeddingResult:
        keys = tuple((input_type, text) for text in texts)
        missing = tuple(dict.fromkeys(text for key, text in keys if key not in self._vectors))
        if missing:
            result = self._adapter.embed(missing, input_type)
            self._vectors.update(
                ((input_type, text), vector)
                for text, vector in zip(missing, result.vectors, strict=True)
            )
        vectors = tuple(self._vectors[key] for key in keys)
        return EmbeddingResult(
            model_identifier=self.model_identifier,
            model_version=self.model_version,
            dimension=len(vectors[0]),
            vectors=vectors,
        )


class CachedStage7L3Provider:
    def __init__(self, outputs: dict[str, LLMScoringOutput]) -> None:
        self._outputs = outputs

    async def evaluate(self, request: L3ProviderRequest) -> object:
        output = self._outputs.get(request.cv_profile.cv_profile_id)
        if output is None:
            raise RuntimeError("cached Stage 7 L3 output is unavailable")
        return output.model_dump(mode="python")


def _timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("generated_at must include a timezone")
    return parsed


def _load_protocol(
    repository_root: Path,
    target: Stage7ExecutionTarget = V1_EXECUTION_TARGET,
) -> Stage7EvaluationProtocol:
    payload = yaml.safe_load((repository_root / target.protocol_path).read_text(encoding="utf-8"))
    return Stage7EvaluationProtocol.model_validate(payload)


def _load_json_lines(path: Path, model_type: type[BaseModel]) -> tuple[BaseModel, ...]:
    return tuple(
        model_type.model_validate_json(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )


def _load_frozen_data(
    repository_root: Path,
    target: Stage7ExecutionTarget = V1_EXECUTION_TARGET,
) -> tuple[
    Stage7FrozenManifest,
    tuple[SyntheticPairAnnotation, ...],
    dict[str, CVProfile],
    dict[str, JobProfile],
    dict[str, ScoringRubric],
]:
    directory = repository_root / target.dataset_directory
    quality = validate_stage7_frozen_test_set(repository_root, directory)
    if not quality.passed or quality.warnings:
        raise Stage7EvaluationError("frozen Stage 7 dataset did not pass preflight QC")
    manifest = Stage7FrozenManifest.model_validate_json(
        (directory / "manifest.json").read_text(encoding="utf-8")
    )
    annotations = cast(
        tuple[SyntheticPairAnnotation, ...],
        _load_json_lines(directory / "pairs.jsonl", SyntheticPairAnnotation),
    )
    profiles = cast(
        tuple[CVProfile, ...], _load_json_lines(directory / "cv_profiles.jsonl", CVProfile)
    )
    jobs = cast(
        tuple[JobProfile, ...], _load_json_lines(directory / "job_profiles.jsonl", JobProfile)
    )
    rubrics = cast(
        tuple[ScoringRubric, ...],
        _load_json_lines(directory / "rubrics.jsonl", ScoringRubric),
    )
    return (
        manifest,
        annotations,
        {item.cv_profile_id: item for item in profiles},
        {item.job_profile_id: item for item in jobs},
        {item.rubric_id: item for item in rubrics},
    )


def _new_cache(
    repository_root: Path,
    manifest: Stage7FrozenManifest,
    provider_identifier: str,
    model_identifier: str,
    prompt_version: str,
    target: Stage7ExecutionTarget = V1_EXECUTION_TARGET,
) -> Stage7EvaluationCache:
    return Stage7EvaluationCache(
        cache_schema_version="1.0.0",
        protocol_sha256=stage7_manifest_sha256(repository_root / target.protocol_path),
        dataset_manifest_sha256=stage7_manifest_sha256(
            repository_root / target.dataset_directory / "manifest.json"
        ),
        runtime_manifest_sha256=manifest.runtime_manifest_sha256,
        provider_identifier=provider_identifier,
        model_identifier=model_identifier,
        prompt_version=prompt_version,
    )


def _load_cache(
    repository_root: Path,
    cache_path: Path,
    expected: Stage7EvaluationCache,
) -> Stage7EvaluationCache:
    path = repository_root / cache_path
    if not path.is_file():
        return expected
    cache = Stage7EvaluationCache.model_validate_json(path.read_text(encoding="utf-8"))
    immutable_fields = (
        "cache_schema_version",
        "protocol_sha256",
        "dataset_manifest_sha256",
        "runtime_manifest_sha256",
        "provider_identifier",
        "model_identifier",
        "prompt_version",
    )
    if any(getattr(cache, field) != getattr(expected, field) for field in immutable_fields):
        raise Stage7EvaluationError("Stage 7 cache does not match the frozen evaluation")
    return cache


def _write_cache(repository_root: Path, cache_path: Path, cache: Stage7EvaluationCache) -> None:
    path = repository_root / cache_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(_json_value(cache.model_dump(mode="python")), ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )


def _json_value(value: object) -> object:
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral_value() else float(value)
    if isinstance(value, dict):
        mapping = cast(dict[object, object], value)
        return {str(key): _json_value(item) for key, item in mapping.items()}
    if isinstance(value, tuple):
        values = cast(tuple[object, ...], value)
        return [_json_value(item) for item in values]
    if isinstance(value, list):
        values = cast(list[object], value)
        return [_json_value(item) for item in values]
    return value


def _required_attempts(pair_id: str, protocol: Stage7EvaluationProtocol) -> int:
    return 2 if pair_id in set(protocol.stability_pair_ids) else 1


def _provider_request(
    annotation: SyntheticPairAnnotation,
    profile: CVProfile,
    job: JobProfile,
    rubric: ScoringRubric,
    attempt_number: int,
    prompt_version: str,
    authoritative_requirements: tuple[LLMRequirementReference, ...] = (),
) -> LLMScoringRequest:
    digest = hashlib.sha256(f"{annotation.pair_id}:{attempt_number}".encode()).hexdigest()[:16]
    return LLMScoringRequest(
        request_id=f"stage7-l3-{digest}",
        job_profile=job,
        rubric=rubric,
        evidence=profile.evidence,
        prompt_version=prompt_version,
        authoritative_requirement_assessments=authoritative_requirements,
    )


async def collect_stage7_outputs(
    repository_root: Path,
    adapter: LLMAdapter,
    cache_path: Path = CACHE_PATH,
    maximum_new_requests: int | None = None,
    request_interval_seconds: float | None = None,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    target: Stage7ExecutionTarget = V1_EXECUTION_TARGET,
) -> Stage7EvaluationCache:
    protocol = _load_protocol(repository_root, target)
    manifest, annotations, profiles, jobs, rubrics = _load_frozen_data(repository_root, target)
    loader = RepositoryConfigurationLoader(
        repository_root,
        repository_root / target.runtime_directory,
    )
    runtime_manifest = loader.runtime_manifest
    if runtime_manifest is None:
        raise Stage7EvaluationError("Stage 7 runtime manifest is unavailable")
    strategy = runtime_manifest.strategy
    expected = _new_cache(
        repository_root,
        manifest,
        strategy.provider_identifier,
        strategy.model_identifier,
        strategy.prompt_version,
        target,
    )
    cache = _load_cache(repository_root, cache_path, expected)
    interval = (
        float(protocol.request_policy.minimum_request_interval_seconds)
        if request_interval_seconds is None
        else request_interval_seconds
    )
    if interval < float(protocol.request_policy.minimum_request_interval_seconds):
        raise ValueError("request interval is below the frozen Stage 7 minimum")
    if maximum_new_requests is not None and maximum_new_requests < 1:
        raise ValueError("maximum_new_requests must be positive")
    authoritative_by_pair: dict[str, tuple[LLMRequirementReference, ...]] = {}
    if strategy.prompt_version in {"l3-evidence-rubric-v14", "l3-evidence-rubric-v15"}:
        for annotation in annotations:
            l1 = score_l1(
                profiles[annotation.cv_profile_id],
                rubrics[annotation.rubric_id],
                loader.load_l1_policy(annotation.job_profile_id),
            )
            authoritative_by_pair[annotation.pair_id] = tuple(
                LLMRequirementReference(
                    requirement_id=item.requirement_id,
                    evidence_status=item.evidence_status,
                    evidence_ids=item.evidence_ids,
                    rationale=item.rationale,
                )
                for item in l1.requirement_assessments
            )
    new_requests = 0
    for attempt_number in (1, 2):
        for annotation in annotations:
            if attempt_number > _required_attempts(annotation.pair_id, protocol):
                continue
            if len(cache.records.get(annotation.pair_id, ())) >= attempt_number:
                continue
            failures = tuple(
                item
                for item in cache.failures.get(annotation.pair_id, ())
                if item.intended_attempt_number == attempt_number
            )
            while len(failures) <= protocol.request_policy.retry_count_per_attempt:
                if maximum_new_requests is not None and new_requests >= maximum_new_requests:
                    return cache
                if (
                    cache.total_http_request_count
                    >= protocol.request_policy.maximum_http_request_count
                ):
                    raise Stage7RequestCapReached("Stage 7 HTTP request cap reached")
                if new_requests:
                    await sleep(interval)
                started = perf_counter()
                result = await adapter.score(
                    _provider_request(
                        annotation,
                        profiles[annotation.cv_profile_id],
                        jobs[annotation.job_profile_id],
                        rubrics[annotation.rubric_id],
                        attempt_number,
                        strategy.prompt_version,
                        authoritative_by_pair.get(annotation.pair_id, ()),
                    )
                )
                duration = max(0, round((perf_counter() - started) * 1000))
                new_requests += 1
                if result.status is LLMProviderStatus.AVAILABLE:
                    records = dict(cache.records)
                    records[annotation.pair_id] = (
                        *records.get(annotation.pair_id, ()),
                        Stage7CachedAttempt(
                            attempt_number=attempt_number,
                            duration_milliseconds=duration,
                            result=result,
                        ),
                    )
                    cache = cache.model_copy(update={"records": records})
                    _write_cache(repository_root, cache_path, cache)
                    break
                failure_map = dict(cache.failures)
                failure = Stage7CachedFailure(
                    intended_attempt_number=attempt_number,
                    duration_milliseconds=duration,
                    status=result.status,
                    reason=cast(str, result.reason),
                )
                failure_map[annotation.pair_id] = (
                    *failure_map.get(annotation.pair_id, ()),
                    failure,
                )
                cache = cache.model_copy(update={"failures": failure_map})
                _write_cache(repository_root, cache_path, cache)
                if (
                    result.status is LLMProviderStatus.UNAVAILABLE
                    and protocol.request_policy.stop_on_provider_unavailability
                ):
                    raise Stage7ProviderUnavailable(cast(str, result.reason))
                failures = (*failures, failure)
    return cache


def _metrics_payload(metrics: ClassificationMetrics) -> dict[str, object]:
    return asdict(metrics)


def _decision_safety(
    expected: tuple[ClassificationDecision, ...],
    predicted: tuple[ClassificationDecision, ...],
) -> dict[str, object]:
    false_rejects = tuple(
        index
        for index, (actual, prediction) in enumerate(zip(expected, predicted, strict=True))
        if actual is not ClassificationDecision.REJECT
        and prediction is ClassificationDecision.REJECT
    )
    unsafe_passes = tuple(
        index
        for index, (actual, prediction) in enumerate(zip(expected, predicted, strict=True))
        if prediction is ClassificationDecision.PASS
        and actual in {ClassificationDecision.REJECT, ClassificationDecision.NEEDS_REVIEW}
    )
    review_support = sum(item is ClassificationDecision.NEEDS_REVIEW for item in expected)
    review_hits = sum(
        actual is ClassificationDecision.NEEDS_REVIEW
        and prediction is ClassificationDecision.NEEDS_REVIEW
        for actual, prediction in zip(expected, predicted, strict=True)
    )
    return {
        "needs_review_recall": review_hits / review_support if review_support else 0.0,
        "review_rate": sum(item is ClassificationDecision.NEEDS_REVIEW for item in predicted)
        / len(predicted),
        "false_reject_indexes": list(false_rejects),
        "unsafe_pass_indexes": list(unsafe_passes),
    }


def _variant_result(
    levels: tuple[LevelAssessment, ...],
    selected: tuple[ScoringLevel, ...],
    loaded: LoadedClassifierConfiguration,
) -> tuple[ClassificationDecision, Decimal | None, tuple[str, ...]]:
    selected_assessments = tuple(item for item in levels if item.level in selected)
    if any(item.status is not LevelScoreStatus.AVAILABLE for item in selected_assessments):
        aggregation = AggregationResult(selected_assessments, None)
    else:
        public_config = loaded.classification_config
        weights = {
            ScoringLevel.L1: public_config.aggregation.l1_deterministic_rules,
            ScoringLevel.L2: public_config.aggregation.l2_section_semantic_matching,
            ScoringLevel.L3: public_config.aggregation.l3_evidence_grounded_reasoning,
        }
        denominator = sum((weights[level] for level in selected), Decimal("0"))
        score = (
            sum(
                (
                    cast(Decimal, assessment.score) * weights[assessment.level]
                    for assessment in selected_assessments
                ),
                Decimal("0"),
            )
            / denominator
        )
        aggregation = AggregationResult(
            selected_assessments,
            score.quantize(SCORE_QUANTUM, rounding=ROUND_HALF_UP),
        )
    l1 = next(item for item in levels if item.level is ScoringLevel.L1)
    routing = route_classification(
        aggregation,
        l1.requirement_assessments,
        build_routing_policy(loaded),
    )
    return routing.decision, routing.final_score, routing.reasons


def _bootstrap_interval(
    expected: tuple[ClassificationDecision, ...],
    predicted: tuple[ClassificationDecision, ...],
    seed: int,
    resamples: int,
) -> dict[str, list[float]]:
    generator = random.Random(seed)
    accuracy_values: list[float] = []
    macro_f1_values: list[float] = []
    for _ in range(resamples):
        indexes = tuple(generator.randrange(len(expected)) for _ in expected)
        metrics = calculate_metrics(
            tuple(expected[index] for index in indexes),
            tuple(predicted[index] for index in indexes),
        )
        accuracy_values.append(metrics.accuracy)
        macro_f1_values.append(metrics.macro_f1)

    def interval(values: list[float]) -> list[float]:
        ordered = sorted(values)
        return [ordered[int(0.025 * (len(ordered) - 1))], ordered[int(0.975 * (len(ordered) - 1))]]

    return {
        "accuracy_95_percent": interval(accuracy_values),
        "macro_f1_95_percent": interval(macro_f1_values),
    }


def _provider_quality(
    annotations: tuple[SyntheticPairAnnotation, ...],
    cache: Stage7EvaluationCache,
) -> dict[str, object]:
    requirement_matches = 0
    requirement_count = 0
    unsafe_mismatches = 0
    criterion_errors: list[Decimal] = []
    total_errors: list[Decimal] = []
    cases: list[dict[str, object]] = []
    for annotation in annotations:
        attempts = cache.records.get(annotation.pair_id, ())
        if not attempts:
            cases.append({"pair_id": annotation.pair_id, "outcome": "invalid_or_unavailable"})
            continue
        output = cast(LLMScoringOutput, attempts[0].result.output)
        human_requirements = {
            item.requirement_id: item.evidence_status
            for item in annotation.critical_requirement_assessments
        }
        model_requirements = {
            item.requirement_id: item.evidence_status for item in output.requirement_assessments
        }
        mismatches: list[dict[str, object]] = []
        for requirement_id, human_status in human_requirements.items():
            model_status = model_requirements[requirement_id]
            requirement_count += 1
            requirement_matches += model_status is human_status
            unsafe = model_status is not human_status and model_status in {
                EvidenceStatus.SATISFIED,
                EvidenceStatus.UNSATISFIED,
            }
            unsafe_mismatches += unsafe
            if model_status is not human_status:
                mismatches.append(
                    {
                        "requirement_id": requirement_id,
                        "human_status": human_status.value,
                        "model_status": model_status.value,
                        "unsafe": unsafe,
                    }
                )
        human_criteria = {
            item.criterion_id: item.awarded_points for item in annotation.criterion_assessments
        }
        model_criteria = {item.criterion_id: item.score for item in output.criterion_assessments}
        case_errors = {
            criterion_id: abs(model_criteria[criterion_id] - human_score)
            for criterion_id, human_score in human_criteria.items()
        }
        criterion_errors.extend(case_errors.values())
        total_error = abs(output.overall_score - annotation.total_score)
        total_errors.append(total_error)
        cases.append(
            {
                "pair_id": annotation.pair_id,
                "outcome": "available",
                "human_total_score": float(annotation.total_score),
                "l3_score": float(output.overall_score),
                "requirement_mismatches": mismatches,
                "criterion_absolute_errors": {
                    key: float(value) for key, value in case_errors.items()
                },
                "total_score_absolute_error": float(total_error),
            }
        )
    primary_available = sum(bool(cache.records.get(item.pair_id)) for item in annotations)
    return {
        "primary_case_count": len(annotations),
        "available_output_count": primary_available,
        "valid_output_rate": primary_available / len(annotations),
        "requirement_status_accuracy": requirement_matches / requirement_count,
        "unsafe_requirement_mismatch_count": unsafe_mismatches,
        "criterion_mae": float(mean(criterion_errors)) if criterion_errors else None,
        "total_score_mae": float(mean(total_errors)) if total_errors else None,
        "cases": cases,
    }


def _requirement_route(output: LLMScoringOutput) -> str:
    statuses = {item.evidence_status for item in output.requirement_assessments}
    if statuses.intersection({EvidenceStatus.MISSING, EvidenceStatus.CONFLICTING}):
        return "needs_review"
    if EvidenceStatus.UNSATISFIED in statuses:
        return "explicit_unsatisfied"
    return "all_satisfied"


def _stability(
    protocol: Stage7EvaluationProtocol,
    cache: Stage7EvaluationCache,
) -> dict[str, object]:
    cases: list[dict[str, object]] = []
    exact_matches = 0
    route_matches = 0
    score_ranges: list[Decimal] = []
    for pair_id in protocol.stability_pair_ids:
        outputs = tuple(
            cast(LLMScoringOutput, item.result.output) for item in cache.records.get(pair_id, ())
        )
        if len(outputs) != 2:
            cases.append({"pair_id": pair_id, "evaluable": False})
            continue
        signatures = tuple(
            tuple(
                sorted(
                    (item.requirement_id, item.evidence_status.value)
                    for item in output.requirement_assessments
                )
            )
            for output in outputs
        )
        routes = tuple(_requirement_route(output) for output in outputs)
        score_range = abs(outputs[0].overall_score - outputs[1].overall_score)
        exact_matches += signatures[0] == signatures[1]
        route_matches += routes[0] == routes[1]
        score_ranges.append(score_range)
        cases.append(
            {
                "pair_id": pair_id,
                "evaluable": True,
                "scores": [float(output.overall_score) for output in outputs],
                "score_range": float(score_range),
                "requirement_statuses_agree": signatures[0] == signatures[1],
                "requirement_routes_agree": routes[0] == routes[1],
            }
        )
    count = len(score_ranges)
    return {
        "evaluable_case_count": count,
        "requirement_status_agreement_rate": exact_matches / count if count else None,
        "requirement_route_agreement_rate": route_matches / count if count else None,
        "maximum_score_range": float(max(score_ranges)) if score_ranges else None,
        "cases": cases,
    }


def _usage_and_cost(
    protocol: Stage7EvaluationProtocol,
    cache: Stage7EvaluationCache,
) -> dict[str, object]:
    attempts = tuple(item for values in cache.records.values() for item in values)
    failures = tuple(item for values in cache.failures.values() for item in values)
    usage = tuple(item.result.usage for item in attempts if item.result.usage is not None)
    input_tokens = sum(item.input_tokens for item in usage)
    cached_tokens = sum(item.cached_input_tokens for item in usage)
    output_tokens = sum(item.output_tokens for item in usage)
    policy = protocol.request_policy
    estimated_cost = (
        Decimal(input_tokens - cached_tokens) * policy.input_usd_per_million_tokens
        + Decimal(cached_tokens) * policy.cached_input_usd_per_million_tokens
        + Decimal(output_tokens) * policy.output_usd_per_million_tokens
    ) / Decimal("1000000")
    durations = tuple(item.duration_milliseconds for item in attempts) + tuple(
        item.duration_milliseconds for item in failures
    )
    return {
        "total_http_request_count": cache.total_http_request_count,
        "valid_attempt_count": len(attempts),
        "failed_request_count": len(failures),
        "requests_with_usage": len(usage),
        "input_tokens": input_tokens,
        "cached_input_tokens": cached_tokens,
        "output_tokens": output_tokens,
        "estimated_provider_charge_usd": float(estimated_cost),
        "charge_verified": False,
        "average_request_duration_milliseconds": mean(durations) if durations else None,
        "maximum_request_duration_milliseconds": max(durations) if durations else None,
        "raw_provider_response_persisted": False,
    }


async def build_stage7_report(
    repository_root: Path,
    generated_at: datetime,
    cache: Stage7EvaluationCache,
    embedding_adapter: EmbeddingAdapter | None = None,
    target: Stage7ExecutionTarget = V1_EXECUTION_TARGET,
) -> dict[str, object]:
    started = perf_counter()
    protocol = _load_protocol(repository_root, target)
    manifest, annotations, profiles, jobs, rubrics = _load_frozen_data(repository_root, target)
    loader = RepositoryConfigurationLoader(
        repository_root,
        repository_root / target.runtime_directory,
    )
    models = loader.load_models_artifact()
    cached_embedding = CachingEmbeddingAdapter(
        embedding_adapter
        or SentenceTransformerEmbeddingAdapter.from_configuration(models.embedding)
    )
    l2_score_calibrator = (
        None
        if models.embedding.calibration is None
        else SklearnExtraTreesL2Calibrator(repository_root, models.embedding.calibration)
    )
    outputs_by_profile = {
        annotation.cv_profile_id: cast(
            LLMScoringOutput,
            cache.records[annotation.pair_id][0].result.output,
        )
        for annotation in annotations
        if cache.records.get(annotation.pair_id)
    }
    cached_l3 = CachedStage7L3Provider(outputs_by_profile)
    expected = tuple(
        cast(ApprovedDatasetReview, annotation.review).final_label for annotation in annotations
    )
    variants: dict[str, tuple[ScoringLevel, ...]] = {
        "l1_only": (ScoringLevel.L1,),
        "l2_only": (ScoringLevel.L2,),
        "l3_only": (ScoringLevel.L3,),
        "l1_l2": (ScoringLevel.L1, ScoringLevel.L2),
        "l1_l3": (ScoringLevel.L1, ScoringLevel.L3),
        "l2_l3": (ScoringLevel.L2, ScoringLevel.L3),
        "l1_l2_l3": (ScoringLevel.L1, ScoringLevel.L2, ScoringLevel.L3),
    }
    variant_predictions: dict[str, list[ClassificationDecision]] = {name: [] for name in variants}
    keyword_predictions: list[ClassificationDecision] = []
    tfidf_predictions: list[ClassificationDecision] = []
    embedding_predictions: list[ClassificationDecision] = []
    full_cases: list[dict[str, object]] = []
    l1_requirement_match_count = 0
    l1_requirement_count = 0
    l1_requirement_mismatches: list[dict[str, object]] = []
    for annotation in annotations:
        profile = profiles[annotation.cv_profile_id]
        job = jobs[annotation.job_profile_id]
        rubric = rubrics[annotation.rubric_id]
        loaded = loader.load_for_job(job.job_profile_id)
        l1_policy = loader.load_l1_policy(job.job_profile_id)
        l1 = score_l1(profile, rubric, l1_policy)
        human_requirement_statuses = {
            item.requirement_id: item.evidence_status
            for item in annotation.critical_requirement_assessments
        }
        for assessment in l1.requirement_assessments:
            human_status = human_requirement_statuses[assessment.requirement_id]
            l1_requirement_count += 1
            l1_requirement_match_count += assessment.evidence_status is human_status
            if assessment.evidence_status is not human_status:
                l1_requirement_mismatches.append(
                    {
                        "pair_id": annotation.pair_id,
                        "requirement_id": assessment.requirement_id,
                        "human_status": human_status.value,
                        "l1_status": assessment.evidence_status.value,
                    }
                )
        l2_policy = build_l2_policy(loaded)
        l2 = score_l2(
            profile,
            rubric,
            l2_policy,
            CoreEmbeddingAdapterBridge(cached_embedding, l2_policy.query_count),
            l2_score_calibrator,
        )
        if annotation.cv_profile_id in outputs_by_profile:
            l3 = await score_l3(
                L3ProviderRequest(
                    cv_profile=profile,
                    job_profile=job,
                    rubric=rubric,
                    prompt_version=models.llm.prompt_version,
                ),
                cached_l3,
            )
        else:
            l3 = LevelAssessment.invalid(
                ScoringLevel.L3,
                "Stage 7 L3 output was invalid or unavailable.",
            )
        levels = (l1, l2, l3)
        case_variants: dict[str, object] = {}
        for name, selected in variants.items():
            decision, final_score, reasons = _variant_result(levels, selected, loaded)
            variant_predictions[name].append(decision)
            case_variants[name] = {
                "decision": decision.value,
                "final_score": None if final_score is None else float(final_score),
                "review_reasons": list(reasons),
            }
        keyword_predictions.append(
            KeywordRuleBaseline(l1_policy)
            .predict(profile, rubric, loaded.classification_config.thresholds)
            .decision
        )
        tfidf_predictions.append(
            TfidfCosineBaseline()
            .predict(profile, job, loaded.classification_config.thresholds)
            .decision
        )
        matching = models.embedding.matching
        embedding_predictions.append(
            EmbeddingOnlyBaseline(
                cached_embedding,
                matching.similarity_floor,
                matching.similarity_ceiling,
                matching.top_k,
            )
            .predict(profile, job, loaded.classification_config.thresholds)
            .decision
        )
        full_cases.append(
            {
                "pair_id": annotation.pair_id,
                "role": annotation.role.value,
                "scenario": annotation.scenario.value,
                "expected_label": cast(ApprovedDatasetReview, annotation.review).final_label.value,
                "l1_score": float(cast(Decimal, l1.score)),
                "l2_score": float(cast(Decimal, l2.score)),
                "l3_score": None if l3.score is None else float(l3.score),
                "variants": case_variants,
            }
        )
    baseline_predictions = {
        "keyword": tuple(keyword_predictions),
        "tfidf": tuple(tfidf_predictions),
        "embedding": tuple(embedding_predictions),
    }
    baseline_report = {
        name: _metrics_payload(calculate_metrics(expected, predictions))
        for name, predictions in baseline_predictions.items()
    }
    ablations: dict[str, object] = {}
    for name, predictions_list in variant_predictions.items():
        predictions = tuple(predictions_list)
        metrics = calculate_metrics(expected, predictions)
        safety = _decision_safety(expected, predictions)
        ablations[name] = {
            "metrics": _metrics_payload(metrics),
            **safety,
        }
    final_predictions = tuple(variant_predictions["l1_l2_l3"])
    final_metrics = calculate_metrics(expected, final_predictions)
    final_safety = _decision_safety(expected, final_predictions)
    provider_quality = _provider_quality(annotations, cache)
    stability = _stability(protocol, cache)
    metrics_policy = protocol.metrics
    quality_checks = {
        "minimum_accuracy": final_metrics.accuracy >= float(metrics_policy.minimum_accuracy),
        "minimum_macro_f1": final_metrics.macro_f1 >= float(metrics_policy.minimum_macro_f1),
        "minimum_needs_review_recall": cast(float, final_safety["needs_review_recall"])
        >= float(metrics_policy.minimum_needs_review_recall),
        "maximum_false_reject_count": len(cast(list[int], final_safety["false_reject_indexes"]))
        <= metrics_policy.maximum_false_reject_count,
        "maximum_unsafe_pass_count": len(cast(list[int], final_safety["unsafe_pass_indexes"]))
        <= metrics_policy.maximum_unsafe_pass_count,
        "minimum_requirement_status_accuracy": cast(
            float, provider_quality["requirement_status_accuracy"]
        )
        >= float(metrics_policy.minimum_requirement_status_accuracy),
        "maximum_unsafe_requirement_mismatch_count": cast(
            int, provider_quality["unsafe_requirement_mismatch_count"]
        )
        <= metrics_policy.maximum_unsafe_requirement_mismatch_count,
        "maximum_criterion_mae": cast(float, provider_quality["criterion_mae"])
        <= float(metrics_policy.maximum_criterion_mae),
        "maximum_total_score_mae": cast(float, provider_quality["total_score_mae"])
        <= float(metrics_policy.maximum_total_score_mae),
        "maximum_review_rate": cast(float, final_safety["review_rate"])
        <= float(metrics_policy.maximum_review_rate),
        "minimum_valid_output_rate": cast(float, provider_quality["valid_output_rate"])
        >= float(metrics_policy.minimum_valid_output_rate),
        "minimum_stability_exact_requirement_agreement": cast(
            float, stability["requirement_status_agreement_rate"]
        )
        >= float(metrics_policy.minimum_stability_exact_requirement_agreement),
        "minimum_stability_route_agreement": cast(
            float, stability["requirement_route_agreement_rate"]
        )
        >= float(metrics_policy.minimum_stability_route_agreement),
        "maximum_stability_score_range": cast(float, stability["maximum_score_range"])
        <= float(metrics_policy.maximum_stability_score_range),
    }
    per_role: dict[str, object] = {}
    for role in DatasetRole:
        indexes = tuple(index for index, item in enumerate(annotations) if item.role is role)
        per_role[role.value] = _metrics_payload(
            calculate_metrics(
                tuple(expected[index] for index in indexes),
                tuple(final_predictions[index] for index in indexes),
            )
        )
    mismatch_cases = [
        case
        for index, case in enumerate(full_cases)
        if final_predictions[index] is not expected[index]
    ]
    final_review_reasons = Counter(
        reason
        for case in full_cases
        for reason in cast(
            list[str],
            cast(dict[str, object], cast(dict[str, object], case["variants"])["l1_l2_l3"])[
                "review_reasons"
            ],
        )
    )
    level_score_summary = {
        level: {
            "minimum": min(cast(float, case[f"{level}_score"]) for case in full_cases),
            "maximum": max(cast(float, case[f"{level}_score"]) for case in full_cases),
            "mean": mean(cast(float, case[f"{level}_score"]) for case in full_cases),
        }
        for level in ("l1", "l2", "l3")
    }
    return {
        "report_schema_version": "1.0.0",
        "report_id": target.report_id,
        "report_scope": target.report_scope,
        "is_final_performance": True,
        "generated_at": generated_at.isoformat(),
        "tuning_allowed": False,
        "traceability": {
            "protocol_path": target.protocol_path.as_posix(),
            "protocol_sha256": stage7_manifest_sha256(repository_root / target.protocol_path),
            "dataset_manifest_path": (target.dataset_directory / "manifest.json").as_posix(),
            "dataset_manifest_sha256": cache.dataset_manifest_sha256,
            "runtime_manifest_sha256": manifest.runtime_manifest_sha256,
            "provider_identifier": cache.provider_identifier,
            "model_identifier": cache.model_identifier,
            "prompt_version": cache.prompt_version,
            "raw_provider_response_persisted": False,
        },
        "sample_count": len(annotations),
        "ground_truth_label_distribution": dict(Counter(item.value for item in expected)),
        "baselines": baseline_report,
        "ablations": ablations,
        "final_hybrid": {
            "metrics": _metrics_payload(final_metrics),
            **final_safety,
            "bootstrap_confidence_intervals": _bootstrap_interval(
                expected,
                final_predictions,
                protocol.bootstrap_seed,
                protocol.bootstrap_resamples,
            ),
            "per_role_metrics": per_role,
        },
        "l3_provider_quality": provider_quality,
        "stability": stability,
        "usage_latency_and_cost": _usage_and_cost(protocol, cache),
        "error_analysis": {
            "label_mismatch_count": len(mismatch_cases),
            "label_mismatch_cases": mismatch_cases,
            "predicted_label_distribution": dict(Counter(item.value for item in final_predictions)),
            "final_review_reason_distribution": dict(final_review_reasons),
            "l1_requirement_status_accuracy": (l1_requirement_match_count / l1_requirement_count),
            "l1_requirement_mismatch_count": len(l1_requirement_mismatches),
            "l1_requirement_mismatches": l1_requirement_mismatches,
            "level_score_summary": level_score_summary,
        },
        "quality_gate": {
            "passed": all(quality_checks.values()),
            "checks": quality_checks,
        },
        "performance": {
            "offline_scoring_and_report_milliseconds": round((perf_counter() - started) * 1000),
            "embedding_model_identifier": cached_embedding.model_identifier,
            "embedding_model_version": cached_embedding.model_version,
        },
        "limitations": [
            "The frozen test set is synthetic and covers five junior technology roles only.",
            "Ground truth was finalized by a two-person consensus panel rather than independent scoring.",
            "Provider charges are local estimates and must be verified against the provider invoice.",
            "Test outcomes must not be used to tune the frozen runtime.",
        ],
        "cases": full_cases,
    }


def _configured_adapter(
    settings: RuntimeSettings,
    protocol: Stage7EvaluationProtocol,
    client: httpx.AsyncClient,
    loader: RepositoryConfigurationLoader,
) -> OpenAICompatibleLLMAdapter:
    runtime_manifest = loader.runtime_manifest
    if runtime_manifest is None:
        raise Stage7EvaluationError("runtime manifest is unavailable")
    strategy = runtime_manifest.strategy
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
        raise Stage7EvaluationError("live Stage 7 LLM settings are incomplete")
    secret = api_key.get_secret_value()
    if secret.startswith("<") or "replace" in secret.casefold():
        raise Stage7EvaluationError("Stage 7 LLM key contains a placeholder")
    if provider != strategy.provider_identifier or model != strategy.model_identifier:
        raise Stage7EvaluationError("live Stage 7 provider or model differs from frozen runtime")
    if base_url.rstrip("/") != "https://api.openai.com/v1":
        raise Stage7EvaluationError("live Stage 7 base URL differs from frozen provider")
    return OpenAICompatibleLLMAdapter(
        provider_identifier=provider,
        model_identifier=model,
        api_key=secret,
        base_url=base_url,
        prompt_version=strategy.prompt_version,
        client=client,
        include_temperature_parameter=protocol.request_policy.include_temperature_parameter,
        max_completion_tokens=protocol.request_policy.max_completion_tokens,
        reasoning_effort=protocol.request_policy.reasoning_effort,
    )


async def run_live_stage7(
    repository_root: Path,
    generated_at: datetime,
    maximum_new_requests: int | None = None,
    cache_path: Path = CACHE_PATH,
    report_path: Path = REPORT_PATH,
    target: Stage7ExecutionTarget = V1_EXECUTION_TARGET,
) -> Path | None:
    protocol = _load_protocol(repository_root, target)
    loader = RepositoryConfigurationLoader(
        repository_root,
        repository_root / target.runtime_directory,
    )
    timeout = httpx.Timeout(float(protocol.request_policy.request_timeout_seconds))
    async with httpx.AsyncClient(timeout=timeout) as client:
        adapter = _configured_adapter(RuntimeSettings(), protocol, client, loader)
        cache = await collect_stage7_outputs(
            repository_root,
            adapter,
            cache_path=cache_path,
            maximum_new_requests=maximum_new_requests,
            target=target,
        )
    required = protocol.request_policy.intended_request_count
    valid = sum(len(items) for items in cache.records.values())
    if valid < required:
        return None
    report = await build_stage7_report(repository_root, generated_at, cache, target=target)
    path = repository_root / report_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


async def _main_async(arguments: argparse.Namespace) -> None:
    repository_root = Path(__file__).resolve().parents[2]
    path = await run_live_stage7(
        repository_root,
        _timestamp(cast(str, arguments.generated_at)),
        maximum_new_requests=cast(int | None, arguments.maximum_new_requests),
        cache_path=Path(cast(str, arguments.cache)),
        report_path=Path(cast(str, arguments.report)),
    )
    if path is None:
        print(json.dumps({"status": "incomplete", "cache": cast(str, arguments.cache)}))
        return
    print(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated-at", required=True)
    parser.add_argument("--maximum-new-requests", type=int)
    parser.add_argument("--cache", default=CACHE_PATH.as_posix())
    parser.add_argument("--report", default=REPORT_PATH.as_posix())
    arguments = parser.parse_args()
    asyncio.run(_main_async(arguments))


if __name__ == "__main__":
    main()
