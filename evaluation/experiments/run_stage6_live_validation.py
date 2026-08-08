from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from statistics import mean
from time import perf_counter
from typing import Self, cast

import httpx
from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.app.agents.classifier.scoring import L3ProviderRequest
from backend.app.core.settings import RuntimeSettings
from backend.app.infrastructure.config import (
    LoadedClassifierConfiguration,
    RepositoryConfigurationLoader,
)
from backend.app.infrastructure.llm import (
    LLMAdapter,
    LLMProviderResult,
    LLMProviderStatus,
    LLMScoringRequest,
    OpenAICompatibleLLMAdapter,
)
from evaluation.datasets import ReviewedStage4Example, load_stage6_validation
from evaluation.experiments.run_stage6_validation import (
    EmbeddingRuntime,
    L3ExecutionMetadata,
    run as run_candidate_validation,
)
from evaluation.experiments.stage6_config import load_stage6_candidate_set
from evaluation.experiments.stage6_live_config import (
    LIVE_CONFIG_PATH,
    Stage6LiveConfiguration,
    load_stage6_live_configuration,
)

LIVE_REPORT_PATH = Path("evaluation/reports/stage6_live_llm_validation_v1.json")
LIVE_CACHE_PATH = Path("evaluation/reports/generated/stage6_live_llm_cache_v4.json")
SPLIT_MANIFEST_PATH = Path("data/splits/stage6_split_manifest_v1.json")


class LiveValidationError(RuntimeError):
    pass


class LiveProviderUnavailable(LiveValidationError):
    pass


class LiveCacheModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class LiveCachedAttempt(LiveCacheModel):
    attempt_number: int = Field(ge=1, le=10)
    duration_milliseconds: int = Field(ge=0)
    result: LLMProviderResult


class LiveCachedFailure(LiveCacheModel):
    intended_attempt_number: int = Field(ge=1, le=10)
    duration_milliseconds: int = Field(ge=0)
    status: LLMProviderStatus
    reason: str = Field(min_length=1, max_length=1000)


class LiveValidationCache(LiveCacheModel):
    cache_schema_version: str
    experiment_id: str
    experiment_version: str
    configuration_sha256: str
    provider_identifier: str
    model_identifier: str
    prompt_version: str
    split_manifest_sha256: str
    records: dict[str, tuple[LiveCachedAttempt, ...]]
    failures: dict[str, tuple[LiveCachedFailure, ...]] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_attempt_sequences(self) -> Self:
        for attempts in self.records.values():
            numbers = tuple(item.attempt_number for item in attempts)
            if numbers != tuple(range(1, len(numbers) + 1)):
                raise ValueError("live validation cache attempts must be sequential")
        return self


class CachedPrimaryL3Provider:
    def __init__(self, cache: LiveValidationCache) -> None:
        self._cache = cache

    async def evaluate(self, request: L3ProviderRequest) -> object:
        attempts = self._cache.records.get(request.cv_profile.cv_profile_id, ())
        if not attempts:
            raise RuntimeError("cached live L3 output is unavailable")
        result = attempts[0].result
        if result.status is LLMProviderStatus.UNAVAILABLE:
            raise RuntimeError("cached live L3 provider was unavailable")
        if result.status is LLMProviderStatus.INVALID or result.output is None:
            return {"provider_status": "invalid"}
        return result.output.model_dump(mode="python")


def _timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError("generated_at must be an ISO 8601 timestamp") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("generated_at must include a timezone")
    return parsed


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def _empty_cache(
    repository_root: Path,
    configuration: Stage6LiveConfiguration,
) -> LiveValidationCache:
    return LiveValidationCache(
        cache_schema_version="1.0.0",
        experiment_id=configuration.experiment_id,
        experiment_version=configuration.experiment_version,
        configuration_sha256=_sha256(repository_root / LIVE_CONFIG_PATH),
        provider_identifier=configuration.provider_identifier,
        model_identifier=configuration.model_identifier,
        prompt_version=configuration.prompt_version,
        split_manifest_sha256=_sha256(repository_root / SPLIT_MANIFEST_PATH),
        records={},
        failures={},
    )


def _load_cache(
    repository_root: Path,
    configuration: Stage6LiveConfiguration,
    cache_path: Path,
) -> LiveValidationCache:
    absolute_path = repository_root / cache_path
    if not absolute_path.exists():
        return _empty_cache(repository_root, configuration)
    cache = LiveValidationCache.model_validate_json(absolute_path.read_text(encoding="utf-8"))
    expected = _empty_cache(repository_root, configuration)
    if (
        cache.experiment_id != expected.experiment_id
        or cache.experiment_version != expected.experiment_version
        or cache.configuration_sha256 != expected.configuration_sha256
        or cache.provider_identifier != expected.provider_identifier
        or cache.model_identifier != expected.model_identifier
        or cache.prompt_version != expected.prompt_version
        or cache.split_manifest_sha256 != expected.split_manifest_sha256
    ):
        raise LiveValidationError("live validation cache metadata does not match the experiment")
    normalized_records: dict[str, tuple[LiveCachedAttempt, ...]] = {}
    normalized_failures = dict(cache.failures)
    for cv_profile_id, attempts in cache.records.items():
        available_attempts: list[LiveCachedAttempt] = []
        failures = list(normalized_failures.get(cv_profile_id, ()))
        for attempt in attempts:
            if attempt.result.status is LLMProviderStatus.AVAILABLE:
                available_attempts.append(
                    attempt.model_copy(update={"attempt_number": len(available_attempts) + 1})
                )
            else:
                failures.append(
                    LiveCachedFailure(
                        intended_attempt_number=len(available_attempts) + 1,
                        duration_milliseconds=attempt.duration_milliseconds,
                        status=attempt.result.status,
                        reason=cast(str, attempt.result.reason),
                    )
                )
        if available_attempts:
            normalized_records[cv_profile_id] = tuple(available_attempts)
        if failures:
            normalized_failures[cv_profile_id] = tuple(failures)
    return cache.model_copy(
        update={
            "records": normalized_records,
            "failures": normalized_failures,
        }
    )


def _write_cache(
    repository_root: Path,
    cache_path: Path,
    cache: LiveValidationCache,
) -> None:
    absolute_path = repository_root / cache_path
    absolute_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_path.write_text(
        json.dumps(
            cache.model_dump(mode="python"),
            ensure_ascii=False,
            indent=2,
            default=float,
        )
        + "\n",
        encoding="utf-8",
    )


def _required_attempts(
    example: ReviewedStage4Example,
    configuration: Stage6LiveConfiguration,
) -> int:
    if example.cv_profile.cv_profile_id in set(configuration.stability.case_ids):
        return configuration.stability.total_attempts_per_case
    return 1


def _validate_experiment_links(
    repository_root: Path,
    configuration: Stage6LiveConfiguration,
    examples: tuple[ReviewedStage4Example, ...],
) -> None:
    candidate_set = load_stage6_candidate_set(repository_root)
    if (
        configuration.candidate_set_id != candidate_set.candidate_set_id
        or configuration.candidate_set_version != candidate_set.candidate_set_version
    ):
        raise LiveValidationError("live LLM experiment does not match the Stage 6 candidate set")
    validation_ids = {item.cv_profile.cv_profile_id for item in examples}
    stability_ids = set(configuration.stability.case_ids)
    if not stability_ids.issubset(validation_ids):
        raise LiveValidationError("live LLM stability cases must come only from validation")


def _provider_request(
    loaded: LoadedClassifierConfiguration,
    example: ReviewedStage4Example,
    attempt_number: int,
    prompt_version: str,
) -> LLMScoringRequest:
    digest = hashlib.sha256(example.cv_profile.cv_profile_id.encode("utf-8")).hexdigest()[:16]
    return LLMScoringRequest(
        request_id=f"stage6-live-{digest}-{attempt_number}",
        job_profile=loaded.job_profile,
        rubric=loaded.rubric,
        evidence=example.cv_profile.evidence,
        prompt_version=prompt_version,
    )


async def _collect_outputs(
    repository_root: Path,
    configuration: Stage6LiveConfiguration,
    examples: tuple[ReviewedStage4Example, ...],
    adapter: LLMAdapter,
    cache_path: Path,
    request_interval_seconds: float,
    maximum_new_requests: int | None,
) -> LiveValidationCache:
    if request_interval_seconds < 0:
        raise ValueError("request interval must not be negative")
    if maximum_new_requests is not None and maximum_new_requests < 1:
        raise ValueError("maximum new requests must be positive")
    cache = _load_cache(repository_root, configuration, cache_path)
    loader = RepositoryConfigurationLoader(repository_root)
    new_request_count = 0
    maximum_attempts = max(_required_attempts(item, configuration) for item in examples)
    for attempt_number in range(1, maximum_attempts + 1):
        for example in examples:
            if attempt_number > _required_attempts(example, configuration):
                continue
            cv_profile_id = example.cv_profile.cv_profile_id
            existing = cache.records.get(cv_profile_id, ())
            if len(existing) >= attempt_number:
                continue
            if maximum_new_requests is not None and new_request_count >= maximum_new_requests:
                return cache
            failure_count = sum(
                item.intended_attempt_number == attempt_number
                for item in cache.failures.get(cv_profile_id, ())
            )
            if (
                failure_count
                > configuration.provider_request_policy.maximum_invalid_retries_per_attempt
            ):
                raise LiveValidationError(
                    "live provider exceeded the configured invalid-output retry limit"
                )
            if new_request_count and request_interval_seconds:
                await asyncio.sleep(request_interval_seconds)
            loaded = loader.load_for_job(example.job_profile_id)
            started = perf_counter()
            result = await adapter.score(
                _provider_request(
                    loaded,
                    example,
                    attempt_number,
                    configuration.prompt_version,
                )
            )
            duration_milliseconds = max(0, round((perf_counter() - started) * 1000))
            if result.status is LLMProviderStatus.UNAVAILABLE:
                raise LiveProviderUnavailable(cast(str, result.reason))
            if result.status is LLMProviderStatus.INVALID:
                updated_failures = dict(cache.failures)
                updated_failures[cv_profile_id] = (
                    *updated_failures.get(cv_profile_id, ()),
                    LiveCachedFailure(
                        intended_attempt_number=attempt_number,
                        duration_milliseconds=duration_milliseconds,
                        status=result.status,
                        reason=cast(str, result.reason),
                    ),
                )
                cache = cache.model_copy(update={"failures": updated_failures})
                _write_cache(repository_root, cache_path, cache)
                new_request_count += 1
                continue
            updated_records = dict(cache.records)
            updated_records[cv_profile_id] = (
                *existing,
                LiveCachedAttempt(
                    attempt_number=attempt_number,
                    duration_milliseconds=duration_milliseconds,
                    result=result,
                ),
            )
            cache = cache.model_copy(update={"records": updated_records})
            _write_cache(repository_root, cache_path, cache)
            new_request_count += 1
    return cache


def _cache_complete(
    cache: LiveValidationCache,
    configuration: Stage6LiveConfiguration,
    examples: tuple[ReviewedStage4Example, ...],
) -> bool:
    return all(
        len(cache.records.get(item.cv_profile.cv_profile_id, ()))
        == _required_attempts(item, configuration)
        for item in examples
    )


async def collect_live_outputs(
    repository_root: Path,
    adapter: LLMAdapter,
    cache_path: Path = LIVE_CACHE_PATH,
    request_interval_seconds: float = 0,
    maximum_new_requests: int | None = None,
) -> dict[str, object]:
    configuration = load_stage6_live_configuration(repository_root)
    examples = load_stage6_validation(repository_root)
    _validate_experiment_links(repository_root, configuration, examples)
    cache = await _collect_outputs(
        repository_root,
        configuration,
        examples,
        adapter,
        cache_path,
        request_interval_seconds,
        maximum_new_requests,
    )
    required_attempt_count = sum(_required_attempts(item, configuration) for item in examples)
    cached_attempt_count = sum(len(items) for items in cache.records.values())
    return {
        "experiment_id": configuration.experiment_id,
        "cached_attempt_count": cached_attempt_count,
        "required_attempt_count": required_attempt_count,
        "remaining_attempt_count": required_attempt_count - cached_attempt_count,
        "complete": _cache_complete(cache, configuration, examples),
    }


def _usage_payload(attempts: tuple[LiveCachedAttempt, ...]) -> dict[str, object]:
    available_usage = tuple(item.result.usage for item in attempts if item.result.usage is not None)
    durations = tuple(item.duration_milliseconds for item in attempts)
    return {
        "request_count": len(attempts),
        "requests_with_usage": len(available_usage),
        "input_tokens": sum(item.input_tokens for item in available_usage),
        "output_tokens": sum(item.output_tokens for item in available_usage),
        "total_tokens": sum(item.total_tokens for item in available_usage),
        "cached_input_tokens": sum(item.cached_input_tokens for item in available_usage),
        "reasoning_tokens": sum(item.reasoning_tokens for item in available_usage),
        "total_duration_milliseconds": sum(durations),
        "average_duration_milliseconds": mean(durations) if durations else None,
        "maximum_duration_milliseconds": max(durations) if durations else None,
    }


def _primary_quality_payload(
    examples: tuple[ReviewedStage4Example, ...],
    cache: LiveValidationCache,
) -> dict[str, object]:
    cases: list[dict[str, object]] = []
    requirement_count = 0
    requirement_matches = 0
    criterion_absolute_errors: list[Decimal] = []
    total_score_absolute_errors: list[Decimal] = []
    primary_attempts: list[LiveCachedAttempt] = []
    for example in examples:
        attempt = cache.records[example.cv_profile.cv_profile_id][0]
        primary_attempts.append(attempt)
        output = attempt.result.output
        case: dict[str, object] = {
            "cv_profile_id": example.cv_profile.cv_profile_id,
            "job_profile_id": example.job_profile_id,
            "provider_status": attempt.result.status.value,
            "expected_total_score": float(example.total_score),
            "l3_score": float(output.overall_score) if output is not None else None,
        }
        if output is not None:
            human_requirements = {
                item.requirement_id: item.evidence_status
                for item in example.requirement_assessments
            }
            output_requirements = {
                item.requirement_id: item.evidence_status for item in output.requirement_assessments
            }
            matched_requirements = sum(
                output_requirements.get(requirement_id) is status
                for requirement_id, status in human_requirements.items()
            )
            requirement_count += len(human_requirements)
            requirement_matches += matched_requirements
            human_criteria = {
                item.criterion_id: item.awarded_points for item in example.criterion_assessments
            }
            output_criteria = {
                item.criterion_id: item.score for item in output.criterion_assessments
            }
            case_errors = {
                criterion_id: abs(output_criteria[criterion_id] - human_score)
                for criterion_id, human_score in human_criteria.items()
            }
            criterion_absolute_errors.extend(case_errors.values())
            score_error = abs(output.overall_score - example.total_score)
            total_score_absolute_errors.append(score_error)
            case["requirement_status_match_count"] = matched_requirements
            case["requirement_status_count"] = len(human_requirements)
            case["criterion_absolute_errors"] = {
                key: float(value) for key, value in case_errors.items()
            }
            case["total_score_absolute_error"] = float(score_error)
        cases.append(case)
    available_count = sum(
        item.result.status is LLMProviderStatus.AVAILABLE for item in primary_attempts
    )
    return {
        "sample_count": len(examples),
        "available_output_count": available_count,
        "invalid_output_count": len(examples) - available_count,
        "valid_output_rate": available_count / len(examples),
        "requirement_status_match_rate": (
            requirement_matches / requirement_count if requirement_count else None
        ),
        "criterion_mean_absolute_error": (
            float(mean(criterion_absolute_errors)) if criterion_absolute_errors else None
        ),
        "total_score_mean_absolute_error": (
            float(mean(total_score_absolute_errors)) if total_score_absolute_errors else None
        ),
        "usage_and_latency": _usage_payload(tuple(primary_attempts)),
        "cases": cases,
    }


def _stability_payload(
    configuration: Stage6LiveConfiguration,
    cache: LiveValidationCache,
) -> dict[str, object]:
    cases: list[dict[str, object]] = []
    score_ranges: list[Decimal] = []
    requirement_agreements = 0
    all_attempts: list[LiveCachedAttempt] = []
    for cv_profile_id in configuration.stability.case_ids:
        attempts = cache.records[cv_profile_id]
        all_attempts.extend(attempts)
        outputs = tuple(
            item.result.output
            for item in attempts
            if item.result.status is LLMProviderStatus.AVAILABLE and item.result.output is not None
        )
        scores = tuple(item.overall_score for item in outputs)
        score_range = max(scores) - min(scores) if scores else Decimal("100")
        score_ranges.append(score_range)
        requirement_signatures = tuple(
            tuple(
                sorted(
                    (
                        assessment.requirement_id,
                        assessment.evidence_status.value,
                    )
                    for assessment in output.requirement_assessments
                )
            )
            for output in outputs
        )
        requirement_agreement = (
            len(outputs) == len(attempts) and len(set(requirement_signatures)) == 1
        )
        requirement_agreements += requirement_agreement
        cases.append(
            {
                "cv_profile_id": cv_profile_id,
                "attempt_count": len(attempts),
                "available_output_count": len(outputs),
                "scores": [float(item) for item in scores],
                "score_range": float(score_range),
                "requirement_statuses_agree": requirement_agreement,
            }
        )
    requirement_agreement_rate = requirement_agreements / len(cases)
    maximum_score_range = max(score_ranges)
    quality = configuration.quality_policy
    return {
        "case_count": len(cases),
        "attempts_per_case": configuration.stability.total_attempts_per_case,
        "maximum_score_range": float(maximum_score_range),
        "average_score_range": float(mean(score_ranges)),
        "requirement_status_agreement_rate": requirement_agreement_rate,
        "passes_policy": (
            maximum_score_range <= quality.maximum_stability_score_range
            and Decimal(str(requirement_agreement_rate))
            >= quality.required_requirement_status_agreement_rate
        ),
        "usage_and_latency": _usage_payload(tuple(all_attempts)),
        "cases": cases,
    }


async def run_live_validation(
    repository_root: Path,
    generated_at: datetime,
    adapter: LLMAdapter,
    embedding_runtime: EmbeddingRuntime | None = None,
    cache_path: Path = LIVE_CACHE_PATH,
    request_interval_seconds: float = 0,
    maximum_new_requests: int | None = None,
) -> dict[str, object]:
    if generated_at.tzinfo is None or generated_at.utcoffset() is None:
        raise ValueError("generated_at must include a timezone")
    configuration = load_stage6_live_configuration(repository_root)
    examples = load_stage6_validation(repository_root)
    _validate_experiment_links(repository_root, configuration, examples)
    cache = await _collect_outputs(
        repository_root,
        configuration,
        examples,
        adapter,
        cache_path,
        request_interval_seconds,
        maximum_new_requests,
    )
    if not _cache_complete(cache, configuration, examples):
        raise LiveValidationError("live validation cache is incomplete")
    report = await run_candidate_validation(
        repository_root,
        generated_at,
        embedding_runtime,
        CachedPrimaryL3Provider(cache),
        L3ExecutionMetadata(
            strategy_identifier="environment-configured-evidence-grounded-llm",
            provider_identifier=configuration.provider_identifier,
            model_identifier=configuration.model_identifier,
            prompt_version=configuration.prompt_version,
            live_provider_executed=True,
        ),
    )
    primary_quality = _primary_quality_payload(examples, cache)
    stability = _stability_payload(configuration, cache)
    valid_output_rate = cast(float, primary_quality["valid_output_rate"])
    provider_quality_gate_passed = Decimal(
        str(valid_output_rate)
    ) >= configuration.quality_policy.required_primary_valid_output_rate and cast(
        bool, stability["passes_policy"]
    )
    recommendation = cast(dict[str, object], report["recommendation"])
    readiness = cast(dict[str, object], report["freeze_readiness"])
    report["report_id"] = "stage6-live-llm-validation-v1"
    report["report_scope"] = "stage6-validation-only-live-gemini"
    report["live_experiment"] = {
        "configuration_file": LIVE_CONFIG_PATH.as_posix(),
        "configuration_sha256": _sha256(repository_root / LIVE_CONFIG_PATH),
        "experiment_id": configuration.experiment_id,
        "experiment_version": configuration.experiment_version,
        "provider_identifier": configuration.provider_identifier,
        "model_identifier": configuration.model_identifier,
        "prompt_version": configuration.prompt_version,
        "billing": {
            "tier_assumption": configuration.billing_tier_assumption,
            "estimated_provider_charge_usd": 0.0,
            "charge_verified": False,
        },
        "cache_traceability": {
            "cache_file": cache_path.as_posix(),
            "cache_sha256": _sha256(repository_root / cache_path),
            "cache_is_generated_and_git_ignored": True,
            "raw_provider_response_persisted": False,
        },
    }
    report["provider_validation"] = {
        "primary_quality": primary_quality,
        "stability": stability,
        "invalid_structured_output_retry_count": sum(
            len(items) for items in cache.failures.values()
        ),
        "quality_policy": configuration.quality_policy.model_dump(mode="json"),
        "provider_quality_gate_passed": provider_quality_gate_passed,
    }
    readiness["live_llm_model_evaluated"] = True
    readiness["prompt_quality_with_live_llm_evaluated"] = True
    readiness["provider_quality_gate_passed"] = provider_quality_gate_passed
    readiness["configuration_frozen"] = False
    if not provider_quality_gate_passed:
        readiness["blocking_decision"] = (
            "Live LLM structured-output or stability policy did not pass."
        )
    elif recommendation["candidate_id"] is None:
        readiness["blocking_decision"] = (
            "No candidate satisfies every Stage 6 classifier selection constraint."
        )
    else:
        readiness["blocking_decision"] = (
            "Human approval is required before freezing the recommended candidate."
        )
    return report


def write_live_report(
    repository_root: Path,
    generated_at: datetime,
    adapter: LLMAdapter,
    output_path: Path = LIVE_REPORT_PATH,
    cache_path: Path = LIVE_CACHE_PATH,
    request_interval_seconds: float = 0,
    maximum_new_requests: int | None = None,
) -> Path:
    report = asyncio.run(
        run_live_validation(
            repository_root,
            generated_at,
            adapter,
            cache_path=cache_path,
            request_interval_seconds=request_interval_seconds,
            maximum_new_requests=maximum_new_requests,
        )
    )
    absolute_output = repository_root / output_path
    absolute_output.parent.mkdir(parents=True, exist_ok=True)
    absolute_output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return absolute_output


def _configured_adapter(
    settings: RuntimeSettings,
    configuration: Stage6LiveConfiguration,
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
        raise LiveValidationError("environment-configured LLM settings are incomplete")
    secret = api_key.get_secret_value()
    if secret.startswith("<") or "replace" in secret.casefold():
        raise LiveValidationError("CLASSIFIER_LLM_API_KEY still contains a placeholder")
    if provider != configuration.provider_identifier or model != configuration.model_identifier:
        raise LiveValidationError("runtime provider or model does not match live experiment config")
    return OpenAICompatibleLLMAdapter(
        provider_identifier=provider,
        model_identifier=model,
        api_key=secret,
        base_url=base_url,
        prompt_version=configuration.prompt_version,
        client=client,
    )


async def _main_async(arguments: argparse.Namespace) -> Path | None:
    repository_root = Path(__file__).resolve().parents[2]
    configuration = load_stage6_live_configuration(repository_root)
    settings = RuntimeSettings()
    async with httpx.AsyncClient(timeout=settings.classifier_request_timeout_seconds) as client:
        adapter = _configured_adapter(settings, configuration, client)
        if cast(bool, arguments.collect_only):
            progress = await collect_live_outputs(
                repository_root,
                adapter,
                cache_path=Path(cast(str, arguments.cache)),
                request_interval_seconds=cast(
                    float,
                    arguments.request_interval_seconds,
                ),
                maximum_new_requests=cast(
                    int | None,
                    arguments.maximum_new_requests,
                ),
            )
            print(json.dumps(progress, ensure_ascii=False))
            return None
        report = await run_live_validation(
            repository_root,
            _timestamp(cast(str, arguments.generated_at)),
            adapter,
            cache_path=Path(cast(str, arguments.cache)),
            request_interval_seconds=cast(float, arguments.request_interval_seconds),
            maximum_new_requests=cast(int | None, arguments.maximum_new_requests),
        )
    output_path = repository_root / Path(cast(str, arguments.output))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--generated-at",
        default=datetime.now().astimezone().isoformat(timespec="seconds"),
    )
    parser.add_argument("--output", default=LIVE_REPORT_PATH.as_posix())
    parser.add_argument("--cache", default=LIVE_CACHE_PATH.as_posix())
    parser.add_argument("--request-interval-seconds", type=float, default=0.0)
    parser.add_argument("--maximum-new-requests", type=int)
    parser.add_argument("--collect-only", action="store_true")
    arguments = parser.parse_args()
    asyncio.run(_main_async(arguments))


if __name__ == "__main__":
    main()
