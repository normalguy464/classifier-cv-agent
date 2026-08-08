from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
from collections.abc import Awaitable, Callable
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from statistics import mean
from time import perf_counter
from typing import cast

import httpx
from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.app.agents.classifier.routing import route_classification
from backend.app.agents.classifier.scoring import (
    L3ProviderRequest,
    aggregate_level_scores,
    score_l1,
    score_l2,
    score_l3,
)
from backend.app.agents.classifier.scoring.l2_policy import build_query_coverage_l2_policy
from backend.app.contracts import (
    CVProfile,
    ClassificationDecision,
    EvidenceStatus,
    JobProfile,
    LevelScoreStatus,
    ScoringRubric,
)
from backend.app.core.settings import RuntimeSettings
from backend.app.infrastructure.llm import (
    LLMAdapter,
    LLMProviderResult,
    LLMProviderStatus,
    LLMScoringOutput,
    LLMScoringRequest,
    OpenAICompatibleLLMAdapter,
)
from evaluation.datasets.synthetic_expansion import (
    ApprovedDatasetReview,
    DatasetRole,
    JobVariant,
    SyntheticExpansionSilverSplitManifest,
    SyntheticPairAnnotation,
)
from evaluation.experiments.run_synthetic_expansion_v2_diagnostic import (
    ExpansionEmbeddingRuntime,
    build_diagnostic_routing_policy,
    build_expansion_l1_policy,
    default_embedding_runtime,
    load_development,
)
from evaluation.experiments.run_synthetic_expansion_v2_l2_tuning import (
    precompute_l2_adapters,
)
from evaluation.experiments.stage6_config import load_stage6_candidate_set
from evaluation.experiments.synthetic_expansion_l2_config import (
    load_expansion_l2_candidate_set,
)
from evaluation.experiments.synthetic_expansion_l3_config import (
    CONFIG_PATH,
    ExpansionL3Configuration,
    load_expansion_l3_configuration,
)
from evaluation.metrics import calculate_metrics

CACHE_PATH = Path("evaluation/reports/generated/synthetic_expansion_v2_openrouter_l3_cache_v1.json")
REPORT_PATH = Path("evaluation/reports/synthetic_expansion_v2_openrouter_l3_validation_v1.json")


class ExpansionL3ValidationError(RuntimeError):
    pass


class ExpansionL3ProviderUnavailable(ExpansionL3ValidationError):
    pass


class ExpansionL3RequestCapReached(ExpansionL3ValidationError):
    pass


class ExpansionL3CacheModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class ExpansionL3CachedAttempt(ExpansionL3CacheModel):
    attempt_number: int = Field(ge=1, le=2)
    duration_milliseconds: int = Field(ge=0)
    result: LLMProviderResult


class ExpansionL3CachedFailure(ExpansionL3CacheModel):
    intended_attempt_number: int = Field(ge=1, le=2)
    duration_milliseconds: int = Field(ge=0)
    status: LLMProviderStatus
    reason: str = Field(min_length=1, max_length=1000)


class ExpansionL3ValidationCache(ExpansionL3CacheModel):
    cache_schema_version: str
    experiment_id: str
    experiment_version: str
    configuration_sha256: str
    dataset_manifest_sha256: str
    split_manifest_sha256: str
    provider_identifier: str
    model_identifier: str
    prompt_version: str
    records: dict[str, tuple[ExpansionL3CachedAttempt, ...]]
    failures: dict[str, tuple[ExpansionL3CachedFailure, ...]] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_attempt_sequences(self) -> ExpansionL3ValidationCache:
        for attempts in self.records.values():
            numbers = tuple(item.attempt_number for item in attempts)
            if numbers != tuple(range(1, len(numbers) + 1)):
                raise ValueError("expansion L3 cache attempts must be sequential")
            if any(
                item.result.provider_identifier != self.provider_identifier
                or item.result.model_identifier != self.model_identifier
                or item.result.prompt_version != self.prompt_version
                for item in attempts
            ):
                raise ValueError("expansion L3 cached result metadata must match the cache")
        return self

    @property
    def total_request_count(self) -> int:
        return sum(len(items) for items in self.records.values()) + sum(
            len(items) for items in self.failures.values()
        )


class CachedExpansionL3Provider:
    def __init__(
        self,
        outputs_by_cv_profile_id: dict[str, LLMScoringOutput],
    ) -> None:
        self._outputs_by_cv_profile_id = outputs_by_cv_profile_id

    async def evaluate(self, request: L3ProviderRequest) -> object:
        output = self._outputs_by_cv_profile_id.get(request.cv_profile.cv_profile_id)
        if output is None:
            raise RuntimeError("cached expansion L3 output is unavailable")
        return output.model_dump(mode="python")


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
    configuration: ExpansionL3Configuration,
    configuration_path: Path = CONFIG_PATH,
) -> ExpansionL3ValidationCache:
    return ExpansionL3ValidationCache(
        cache_schema_version="1.0.0",
        experiment_id=configuration.experiment_id,
        experiment_version=configuration.experiment_version,
        configuration_sha256=_sha256(repository_root / configuration_path),
        dataset_manifest_sha256=_sha256(
            repository_root / configuration.reviewed_dataset_directory / "manifest.json"
        ),
        split_manifest_sha256=_sha256(repository_root / configuration.split_manifest_path),
        provider_identifier=configuration.provider_identifier,
        model_identifier=configuration.model_identifier,
        prompt_version=configuration.prompt_version,
        records={},
        failures={},
    )


def _load_cache(
    repository_root: Path,
    configuration: ExpansionL3Configuration,
    cache_path: Path,
    configuration_path: Path = CONFIG_PATH,
) -> ExpansionL3ValidationCache:
    absolute_path = repository_root / cache_path
    if not absolute_path.exists():
        return _empty_cache(repository_root, configuration, configuration_path)
    cache = ExpansionL3ValidationCache.model_validate_json(
        absolute_path.read_text(encoding="utf-8")
    )
    expected = _empty_cache(repository_root, configuration, configuration_path)
    if (
        cache.experiment_id != expected.experiment_id
        or cache.experiment_version != expected.experiment_version
        or cache.configuration_sha256 != expected.configuration_sha256
        or cache.dataset_manifest_sha256 != expected.dataset_manifest_sha256
        or cache.split_manifest_sha256 != expected.split_manifest_sha256
        or cache.provider_identifier != expected.provider_identifier
        or cache.model_identifier != expected.model_identifier
        or cache.prompt_version != expected.prompt_version
    ):
        raise ExpansionL3ValidationError(
            "expansion L3 cache metadata does not match the experiment"
        )
    return cache


def _write_cache(
    repository_root: Path,
    cache_path: Path,
    cache: ExpansionL3ValidationCache,
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


def migrate_evaluation_policy_cache(
    repository_root: Path,
    source_configuration_path: Path,
    target_configuration_path: Path,
    source_cache_path: Path,
    target_cache_path: Path,
) -> ExpansionL3ValidationCache:
    source_configuration = load_expansion_l3_configuration(
        repository_root, source_configuration_path
    )
    target_configuration = load_expansion_l3_configuration(
        repository_root, target_configuration_path
    )
    excluded_fields = {
        "experiment_id",
        "experiment_version",
        "quality_policy",
        "hybrid_policy",
    }
    if source_configuration.model_dump(
        mode="python", exclude=excluded_fields
    ) != target_configuration.model_dump(mode="python", exclude=excluded_fields):
        raise ExpansionL3ValidationError(
            "L3 cache migration permits only experiment identity and evaluation-policy changes"
        )
    source_cache = _load_cache(
        repository_root,
        source_configuration,
        source_cache_path,
        source_configuration_path,
    )
    target_cache = _empty_cache(
        repository_root,
        target_configuration,
        target_configuration_path,
    ).model_copy(
        update={
            "records": source_cache.records,
            "failures": source_cache.failures,
        }
    )
    _write_cache(repository_root, target_cache_path, target_cache)
    return target_cache


def _selected_annotations(
    repository_root: Path,
    configuration: ExpansionL3Configuration,
) -> tuple[
    tuple[SyntheticPairAnnotation, ...],
    dict[str, CVProfile],
    dict[str, JobProfile],
    dict[str, ScoringRubric],
    SyntheticExpansionSilverSplitManifest,
]:
    annotations, profiles, jobs, rubrics, split = load_development(
        repository_root,
        configuration.reviewed_dataset_directory,
        configuration.split_manifest_path,
    )
    annotations_by_id = {item.pair_id: item for item in annotations}
    missing = set(configuration.primary_pair_ids) - set(annotations_by_id)
    if missing:
        raise ExpansionL3ValidationError("configured L3 sample is not development-only")
    selected = tuple(annotations_by_id[pair_id] for pair_id in configuration.primary_pair_ids)
    if split.source_dataset_id != configuration.dataset_id:
        raise ExpansionL3ValidationError("L3 dataset identifier does not match the split")
    if split.source_dataset_version != configuration.dataset_version:
        raise ExpansionL3ValidationError("L3 dataset version does not match the split")
    if split.development.partition_id != configuration.development_partition_id:
        raise ExpansionL3ValidationError("L3 development partition does not match")
    if split.held_out.partition_id != configuration.held_out_partition_id:
        raise ExpansionL3ValidationError("L3 held-out partition does not match")
    role_counts = {role: sum(item.role is role for item in selected) for role in DatasetRole}
    if set(role_counts.values()) != {5}:
        raise ExpansionL3ValidationError("L3 sample must contain five pairs per role")
    if any(item.job_variant is not JobVariant.STANDARD for item in selected):
        raise ExpansionL3ValidationError("L3 sample must use only standard job variants")
    if len({item.candidate_reference for item in selected}) != len(selected):
        raise ExpansionL3ValidationError("L3 sample must use unique candidate profiles")
    labels = {cast(ApprovedDatasetReview, item.review).final_label for item in selected}
    if labels != set(ClassificationDecision):
        raise ExpansionL3ValidationError("L3 sample must cover all classification labels")
    stability = tuple(annotations_by_id[pair_id] for pair_id in configuration.stability.pair_ids)
    if {item.role for item in stability} != set(DatasetRole):
        raise ExpansionL3ValidationError("L3 stability sample must cover every role")
    return selected, profiles, jobs, rubrics, split


def _required_attempts(
    annotation: SyntheticPairAnnotation,
    configuration: ExpansionL3Configuration,
) -> int:
    if annotation.pair_id in set(configuration.stability.pair_ids):
        return configuration.stability.total_attempts_per_pair
    return 1


def _provider_request(
    annotation: SyntheticPairAnnotation,
    profile: CVProfile,
    job: JobProfile,
    rubric: ScoringRubric,
    attempt_number: int,
    prompt_version: str,
) -> LLMScoringRequest:
    digest = hashlib.sha256(annotation.pair_id.encode("utf-8")).hexdigest()[:16]
    return LLMScoringRequest(
        request_id=f"expansion-l3-live-{digest}-{attempt_number}",
        job_profile=job,
        rubric=rubric,
        evidence=profile.evidence,
        prompt_version=prompt_version,
    )


async def _collect_outputs(
    repository_root: Path,
    configuration: ExpansionL3Configuration,
    annotations: tuple[SyntheticPairAnnotation, ...],
    profiles: dict[str, CVProfile],
    jobs: dict[str, JobProfile],
    rubrics: dict[str, ScoringRubric],
    adapter: LLMAdapter,
    cache_path: Path,
    configuration_path: Path,
    maximum_new_requests: int | None,
    request_interval_seconds: float | None,
    sleep: Callable[[float], Awaitable[None]],
) -> ExpansionL3ValidationCache:
    interval = (
        configuration.request_policy.minimum_request_interval_seconds
        if request_interval_seconds is None
        else request_interval_seconds
    )
    if interval < configuration.request_policy.minimum_request_interval_seconds:
        raise ValueError("request interval is below the configured minimum")
    if maximum_new_requests is not None and maximum_new_requests < 1:
        raise ValueError("maximum new requests must be positive")
    cache = _load_cache(repository_root, configuration, cache_path, configuration_path)
    if cache.total_request_count >= configuration.request_policy.hard_request_cap:
        raise ExpansionL3RequestCapReached("expansion L3 hard request cap reached")
    if _primary_quality_is_unrecoverable(cache, configuration, annotations):
        return cache
    if _provider_availability_is_unrecoverable(cache, configuration, annotations):
        return cache
    new_request_count = 0
    maximum_attempts = max(_required_attempts(item, configuration) for item in annotations)
    for attempt_number in range(1, maximum_attempts + 1):
        for annotation in annotations:
            if attempt_number > _required_attempts(annotation, configuration):
                continue
            existing = cache.records.get(annotation.pair_id, ())
            if len(existing) >= attempt_number:
                continue
            if attempt_number > 1 and len(existing) < attempt_number - 1:
                continue
            if maximum_new_requests is not None and new_request_count >= maximum_new_requests:
                return cache
            if _primary_quality_is_unrecoverable(cache, configuration, annotations):
                return cache
            if _provider_availability_is_unrecoverable(cache, configuration, annotations):
                return cache
            if cache.total_request_count >= configuration.request_policy.hard_request_cap:
                raise ExpansionL3RequestCapReached("expansion L3 hard request cap reached")
            panel = _development_panel_annotations(configuration, annotations)
            if (
                configuration.request_policy.require_development_panel_pass_before_batch
                and annotation not in panel
                and not _development_panel_complete(cache, configuration, annotations)
            ):
                return cache
            invalid_failures = sum(
                item.intended_attempt_number == attempt_number
                and item.status is LLMProviderStatus.INVALID
                for item in cache.failures.get(annotation.pair_id, ())
            )
            if invalid_failures > configuration.request_policy.maximum_invalid_retries_per_attempt:
                continue
            total_failures = sum(
                item.intended_attempt_number == attempt_number
                for item in cache.failures.get(annotation.pair_id, ())
            )
            if total_failures > configuration.request_policy.maximum_total_retries_per_attempt:
                continue
            if new_request_count:
                await sleep(interval)
            started = perf_counter()
            result = await adapter.score(
                _provider_request(
                    annotation,
                    profiles[annotation.cv_profile_id],
                    jobs[annotation.job_profile_id],
                    rubrics[annotation.rubric_id],
                    attempt_number,
                    configuration.prompt_version,
                )
            )
            duration_milliseconds = max(0, round((perf_counter() - started) * 1000))
            new_request_count += 1
            if result.status is not LLMProviderStatus.AVAILABLE:
                failures = dict(cache.failures)
                failures[annotation.pair_id] = (
                    *failures.get(annotation.pair_id, ()),
                    ExpansionL3CachedFailure(
                        intended_attempt_number=attempt_number,
                        duration_milliseconds=duration_milliseconds,
                        status=result.status,
                        reason=cast(str, result.reason),
                    ),
                )
                cache = cache.model_copy(update={"failures": failures})
                _write_cache(repository_root, cache_path, cache)
                if result.status is LLMProviderStatus.UNAVAILABLE:
                    if _provider_availability_is_unrecoverable(cache, configuration, annotations):
                        return cache
                    raise ExpansionL3ProviderUnavailable(cast(str, result.reason))
                if _primary_quality_is_unrecoverable(cache, configuration, annotations):
                    return cache
                continue
            records = dict(cache.records)
            records[annotation.pair_id] = (
                *existing,
                ExpansionL3CachedAttempt(
                    attempt_number=attempt_number,
                    duration_milliseconds=duration_milliseconds,
                    result=result,
                ),
            )
            cache = cache.model_copy(update={"records": records})
            _write_cache(repository_root, cache_path, cache)
    return cache


def _cache_complete(
    cache: ExpansionL3ValidationCache,
    configuration: ExpansionL3Configuration,
    annotations: tuple[SyntheticPairAnnotation, ...],
) -> bool:
    return all(
        len(cache.records.get(item.pair_id, ())) == _required_attempts(item, configuration)
        for item in annotations
    )


def _primary_quality_is_unrecoverable(
    cache: ExpansionL3ValidationCache,
    configuration: ExpansionL3Configuration,
    annotations: tuple[SyntheticPairAnnotation, ...],
) -> bool:
    return _primary_quality_failure_reason(cache, configuration, annotations) is not None


def _primary_quality_failure_reason(
    cache: ExpansionL3ValidationCache,
    configuration: ExpansionL3Configuration,
    annotations: tuple[SyntheticPairAnnotation, ...],
) -> str | None:
    panel_failure = _development_panel_failure_reason(cache, configuration, annotations)
    if panel_failure is not None:
        return panel_failure
    cached_attempt_count = sum(len(items) for items in cache.records.values())
    remaining_valid_attempt_count = (
        configuration.required_valid_attempt_count - cached_attempt_count
    )
    remaining_request_budget = (
        configuration.request_policy.hard_request_cap - cache.total_request_count
    )
    if remaining_request_budget < remaining_valid_attempt_count:
        return (
            "The remaining hard request budget cannot cover the required valid attempts, "
            "so complete valid-output coverage became unreachable."
        )
    maximum_failures = configuration.request_policy.maximum_total_retries_per_attempt + 1
    for annotation in annotations:
        attempts = cache.records.get(annotation.pair_id, ())
        for attempt_number in range(1, _required_attempts(annotation, configuration) + 1):
            if len(attempts) >= attempt_number:
                continue
            failures = tuple(
                item
                for item in cache.failures.get(annotation.pair_id, ())
                if item.intended_attempt_number == attempt_number
            )
            if len(failures) >= maximum_failures and any(
                item.status is LLMProviderStatus.INVALID for item in failures
            ):
                return (
                    "At least one required attempt exhausted its invalid-output retry "
                    "allowance, so complete valid-output coverage became unreachable."
                )
    return None


def _development_panel_annotations(
    configuration: ExpansionL3Configuration,
    annotations: tuple[SyntheticPairAnnotation, ...],
) -> tuple[SyntheticPairAnnotation, ...]:
    return annotations[: configuration.request_policy.development_panel_pair_count]


def _development_panel_complete(
    cache: ExpansionL3ValidationCache,
    configuration: ExpansionL3Configuration,
    annotations: tuple[SyntheticPairAnnotation, ...],
) -> bool:
    panel = _development_panel_annotations(configuration, annotations)
    return bool(panel) and all(cache.records.get(item.pair_id) for item in panel)


def _development_panel_failure_reason(
    cache: ExpansionL3ValidationCache,
    configuration: ExpansionL3Configuration,
    annotations: tuple[SyntheticPairAnnotation, ...],
) -> str | None:
    if not configuration.request_policy.require_development_panel_pass_before_batch:
        return None
    if not _development_panel_complete(cache, configuration, annotations):
        return None
    panel = _development_panel_annotations(configuration, annotations)
    quality = _provider_quality(configuration, panel, cache)
    if cast(bool, quality["passes_primary_policy"]):
        return None
    return (
        "The development panel did not satisfy the configured provider quality thresholds, "
        "so batch collection was not opened."
    )


def _development_panel_payload(
    cache: ExpansionL3ValidationCache,
    configuration: ExpansionL3Configuration,
    annotations: tuple[SyntheticPairAnnotation, ...],
) -> dict[str, object]:
    required = configuration.request_policy.require_development_panel_pass_before_batch
    panel = _development_panel_annotations(configuration, annotations)
    if not required:
        return {
            "required_before_batch": False,
            "pair_count": 0,
            "complete": False,
            "passed": None,
        }
    if not _development_panel_complete(cache, configuration, annotations):
        return {
            "required_before_batch": True,
            "pair_count": len(panel),
            "complete": False,
            "passed": None,
        }
    quality = _provider_quality(configuration, panel, cache)
    return {
        "required_before_batch": True,
        "pair_count": len(panel),
        "complete": True,
        "passed": quality["passes_primary_policy"],
        "quality": quality,
    }


def _provider_availability_is_unrecoverable(
    cache: ExpansionL3ValidationCache,
    configuration: ExpansionL3Configuration,
    annotations: tuple[SyntheticPairAnnotation, ...],
) -> bool:
    maximum_failures = configuration.request_policy.maximum_total_retries_per_attempt + 1
    for annotation in annotations:
        attempts = cache.records.get(annotation.pair_id, ())
        for attempt_number in range(1, _required_attempts(annotation, configuration) + 1):
            if len(attempts) >= attempt_number:
                continue
            failures = tuple(
                item
                for item in cache.failures.get(annotation.pair_id, ())
                if item.intended_attempt_number == attempt_number
            )
            if len(failures) >= maximum_failures and all(
                item.status is LLMProviderStatus.UNAVAILABLE for item in failures
            ):
                return True
    return False


async def collect_live_outputs(
    repository_root: Path,
    adapter: LLMAdapter,
    cache_path: Path = CACHE_PATH,
    configuration_path: Path = CONFIG_PATH,
    maximum_new_requests: int | None = None,
    request_interval_seconds: float | None = None,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> dict[str, object]:
    configuration = load_expansion_l3_configuration(repository_root, configuration_path)
    annotations, profiles, jobs, rubrics, _ = _selected_annotations(repository_root, configuration)
    cache = await _collect_outputs(
        repository_root,
        configuration,
        annotations,
        profiles,
        jobs,
        rubrics,
        adapter,
        cache_path,
        configuration_path,
        maximum_new_requests,
        request_interval_seconds,
        sleep,
    )
    cached_attempt_count = sum(len(items) for items in cache.records.values())
    return {
        "experiment_id": configuration.experiment_id,
        "cached_valid_attempt_count": cached_attempt_count,
        "required_valid_attempt_count": configuration.required_valid_attempt_count,
        "remaining_valid_attempt_count": (
            configuration.required_valid_attempt_count - cached_attempt_count
        ),
        "failed_request_count": sum(len(items) for items in cache.failures.values()),
        "total_http_request_count": cache.total_request_count,
        "hard_request_cap": configuration.request_policy.hard_request_cap,
        "prior_series_request_count": configuration.request_policy.prior_series_request_count,
        "series_hard_request_cap": configuration.request_policy.series_hard_request_cap,
        "cumulative_series_request_count": (
            configuration.request_policy.prior_series_request_count + cache.total_request_count
        ),
        "remaining_request_budget": (
            configuration.request_policy.hard_request_cap - cache.total_request_count
        ),
        "complete": _cache_complete(cache, configuration, annotations),
        "development_panel": _development_panel_payload(cache, configuration, annotations),
        "quality_failure_terminal": _primary_quality_is_unrecoverable(
            cache, configuration, annotations
        ),
        "provider_failure_terminal": _provider_availability_is_unrecoverable(
            cache, configuration, annotations
        ),
    }


def _usage_payload(attempts: tuple[ExpansionL3CachedAttempt, ...]) -> dict[str, object]:
    usage = tuple(item.result.usage for item in attempts if item.result.usage is not None)
    durations = tuple(item.duration_milliseconds for item in attempts)
    return {
        "request_count": len(attempts),
        "requests_with_usage": len(usage),
        "input_tokens": sum(item.input_tokens for item in usage),
        "output_tokens": sum(item.output_tokens for item in usage),
        "total_tokens": sum(item.total_tokens for item in usage),
        "cached_input_tokens": sum(item.cached_input_tokens for item in usage),
        "reasoning_tokens": sum(item.reasoning_tokens for item in usage),
        "total_duration_milliseconds": sum(durations),
        "average_duration_milliseconds": mean(durations) if durations else None,
        "maximum_duration_milliseconds": max(durations) if durations else None,
    }


def _cost_payload(
    configuration: ExpansionL3Configuration,
    cache: ExpansionL3ValidationCache,
) -> dict[str, object]:
    attempts = tuple(item for items in cache.records.values() for item in items)
    usage = tuple(item.result.usage for item in attempts if item.result.usage is not None)
    if configuration.cost_policy is None:
        return {
            "estimated_provider_charge_usd": 0.0,
            "maximum_estimated_experiment_cost_usd": 0.0,
            "worst_case_estimated_experiment_cost_usd": 0.0,
            "requests_with_priced_usage": len(usage),
            "requests_without_priced_usage": cache.total_request_count - len(usage),
            "charge_verified": False,
        }
    input_tokens = sum(item.input_tokens for item in usage)
    cached_input_tokens = sum(item.cached_input_tokens for item in usage)
    output_tokens = sum(item.output_tokens for item in usage)
    uncached_input_tokens = input_tokens - cached_input_tokens
    policy = configuration.cost_policy
    estimated_charge = (
        Decimal(uncached_input_tokens) * policy.input_usd_per_million_tokens
        + Decimal(cached_input_tokens) * policy.cached_input_usd_per_million_tokens
        + Decimal(output_tokens) * policy.output_usd_per_million_tokens
    ) / Decimal("1000000")
    maximum_completion_tokens = cast(int, configuration.request_policy.max_completion_tokens)
    worst_case_charge = (
        Decimal(configuration.request_policy.hard_request_cap)
        * (
            Decimal(policy.assumed_max_input_tokens_per_request)
            * policy.input_usd_per_million_tokens
            + Decimal(maximum_completion_tokens) * policy.output_usd_per_million_tokens
        )
        / Decimal("1000000")
    )
    return {
        "estimated_provider_charge_usd": float(estimated_charge),
        "maximum_estimated_experiment_cost_usd": float(
            policy.maximum_estimated_experiment_cost_usd
        ),
        "worst_case_estimated_experiment_cost_usd": float(worst_case_charge),
        "requests_with_priced_usage": len(usage),
        "requests_without_priced_usage": cache.total_request_count - len(usage),
        "charge_verified": False,
    }


def _failure_category(reason: str) -> str:
    if "overall_score:less_than_equal" in reason:
        return "overall_score_above_100"
    if "root:json_invalid" in reason:
        return "malformed_output_json"
    if "HTTP status 429" in reason:
        return "provider_rate_limited"
    if reason == "LLM provider output failed structured validation.":
        return "legacy_unspecified_structured_validation"
    if "request consistency validation" in reason:
        return "request_consistency_validation"
    if "schema validation" in reason:
        return "other_schema_validation"
    return "other_provider_failure"


def _request_quality_payload(cache: ExpansionL3ValidationCache) -> dict[str, object]:
    valid_attempts = tuple(item for items in cache.records.values() for item in items)
    failures = tuple(item for items in cache.failures.values() for item in items)
    request_count = len(valid_attempts) + len(failures)
    durations = tuple(item.duration_milliseconds for item in valid_attempts) + tuple(
        item.duration_milliseconds for item in failures
    )
    category_counts: dict[str, int] = {}
    for failure in failures:
        category = _failure_category(failure.reason)
        category_counts[category] = category_counts.get(category, 0) + 1
    return {
        "valid_output_rate": len(valid_attempts) / request_count if request_count else None,
        "failure_category_counts": category_counts,
        "average_duration_milliseconds": mean(durations) if durations else None,
        "maximum_duration_milliseconds": max(durations) if durations else None,
    }


def _provider_quality(
    configuration: ExpansionL3Configuration,
    annotations: tuple[SyntheticPairAnnotation, ...],
    cache: ExpansionL3ValidationCache,
) -> dict[str, object]:
    cases: list[dict[str, object]] = []
    requirement_matches = 0
    requirement_count = 0
    unsafe_requirement_mismatch_count = 0
    criterion_errors: list[Decimal] = []
    score_errors: list[Decimal] = []
    primary_attempts: list[ExpansionL3CachedAttempt] = []
    attempted_pair_count = 0
    for annotation in annotations:
        attempts = cache.records.get(annotation.pair_id, ())
        pair_failures = tuple(
            item
            for item in cache.failures.get(annotation.pair_id, ())
            if item.intended_attempt_number == 1
        )
        if attempts or pair_failures:
            attempted_pair_count += 1
        if not attempts:
            failures = tuple(
                item for item in pair_failures if item.status is LLMProviderStatus.INVALID
            )
            cases.append(
                {
                    "pair_id": annotation.pair_id,
                    "role": annotation.role.value,
                    "scenario": annotation.scenario.value,
                    "expected_label": cast(
                        ApprovedDatasetReview, annotation.review
                    ).final_label.value,
                    "outcome": (
                        "invalid_exhausted"
                        if len(failures)
                        > configuration.request_policy.maximum_invalid_retries_per_attempt
                        else "not_available"
                    ),
                    "failure_reasons": [item.reason for item in failures],
                }
            )
            continue
        attempt = attempts[0]
        primary_attempts.append(attempt)
        output = cast(LLMScoringOutput, attempt.result.output)
        human_requirements = {
            item.requirement_id: item.evidence_status
            for item in annotation.critical_requirement_assessments
        }
        model_requirements = {
            item.requirement_id: item.evidence_status for item in output.requirement_assessments
        }
        matched = sum(
            model_requirements.get(requirement_id) is status
            for requirement_id, status in human_requirements.items()
        )
        requirement_matches += matched
        requirement_count += len(human_requirements)
        requirement_mismatches = [
            {
                "requirement_id": requirement_id,
                "human_status": human_status.value,
                "model_status": model_requirements[requirement_id].value,
                "unsafe": _is_unsafe_requirement_status_mismatch(
                    human_status,
                    model_requirements[requirement_id],
                ),
            }
            for requirement_id, human_status in human_requirements.items()
            if model_requirements[requirement_id] is not human_status
        ]
        case_unsafe_requirement_mismatch_count = sum(
            cast(bool, item["unsafe"]) for item in requirement_mismatches
        )
        unsafe_requirement_mismatch_count += case_unsafe_requirement_mismatch_count
        human_criteria = {
            item.criterion_id: item.awarded_points for item in annotation.criterion_assessments
        }
        model_criteria = {item.criterion_id: item.score for item in output.criterion_assessments}
        case_criterion_errors = {
            criterion_id: abs(model_criteria[criterion_id] - human_score)
            for criterion_id, human_score in human_criteria.items()
        }
        criterion_errors.extend(case_criterion_errors.values())
        score_error = abs(output.overall_score - annotation.total_score)
        score_errors.append(score_error)
        cases.append(
            {
                "pair_id": annotation.pair_id,
                "role": annotation.role.value,
                "scenario": annotation.scenario.value,
                "expected_label": cast(ApprovedDatasetReview, annotation.review).final_label.value,
                "outcome": "available",
                "human_total_score": float(annotation.total_score),
                "l3_score": float(output.overall_score),
                "requirement_status_match_count": matched,
                "requirement_status_count": len(human_requirements),
                "requirement_status_mismatches": requirement_mismatches,
                "unsafe_requirement_status_mismatch_count": (
                    case_unsafe_requirement_mismatch_count
                ),
                "criterion_absolute_errors": {
                    key: float(value) for key, value in case_criterion_errors.items()
                },
                "total_score_absolute_error": float(score_error),
                "calibration_levels": (
                    None
                    if attempt.result.calibration_levels is None
                    else {
                        key: value.value for key, value in attempt.result.calibration_levels.items()
                    }
                ),
            }
        )
    requirement_rate = requirement_matches / requirement_count if requirement_count else None
    quality = configuration.quality_policy
    criterion_mean_absolute_error = (
        Decimal(str(mean(criterion_errors))) if criterion_errors else None
    )
    total_score_mean_absolute_error = Decimal(str(mean(score_errors))) if score_errors else None
    endpoint_score_count = sum(
        cast(LLMScoringOutput, item.result.output).overall_score in {Decimal("0"), Decimal("100")}
        for item in primary_attempts
    )
    endpoint_score_rate = (
        Decimal(endpoint_score_count) / Decimal(len(primary_attempts)) if primary_attempts else None
    )
    calibration_passes = (
        endpoint_score_rate is not None
        and criterion_mean_absolute_error is not None
        and total_score_mean_absolute_error is not None
        and endpoint_score_rate <= quality.maximum_endpoint_score_rate
        and criterion_mean_absolute_error <= quality.maximum_criterion_mean_absolute_error
        and total_score_mean_absolute_error <= quality.maximum_total_score_mean_absolute_error
    )
    return {
        "sample_count": len(annotations),
        "attempted_pair_count": attempted_pair_count,
        "available_output_count": len(primary_attempts),
        "valid_output_rate": len(primary_attempts) / len(annotations),
        "valid_output_rate_among_attempted_pairs": (
            len(primary_attempts) / attempted_pair_count if attempted_pair_count else None
        ),
        "endpoint_score_count": endpoint_score_count,
        "endpoint_score_rate": (
            None if endpoint_score_rate is None else float(endpoint_score_rate)
        ),
        "requirement_status_match_rate": requirement_rate,
        "unsafe_requirement_status_mismatch_count": unsafe_requirement_mismatch_count,
        "requirement_status_policy": {
            "minimum_match_rate": float(quality.required_requirement_status_match_rate),
            "maximum_unsafe_mismatch_count": (
                quality.maximum_unsafe_requirement_status_mismatch_count
            ),
            "passes": (
                requirement_rate is not None
                and Decimal(str(requirement_rate)) >= quality.required_requirement_status_match_rate
                and unsafe_requirement_mismatch_count
                <= quality.maximum_unsafe_requirement_status_mismatch_count
            ),
        },
        "criterion_mean_absolute_error": (
            None if criterion_mean_absolute_error is None else float(criterion_mean_absolute_error)
        ),
        "total_score_mean_absolute_error": (
            None
            if total_score_mean_absolute_error is None
            else float(total_score_mean_absolute_error)
        ),
        "calibration_policy": {
            "maximum_endpoint_score_rate": float(quality.maximum_endpoint_score_rate),
            "maximum_criterion_mean_absolute_error": float(
                quality.maximum_criterion_mean_absolute_error
            ),
            "maximum_total_score_mean_absolute_error": float(
                quality.maximum_total_score_mean_absolute_error
            ),
            "passes": calibration_passes,
        },
        "usage_and_latency": _usage_payload(tuple(primary_attempts)),
        "passes_primary_policy": (
            len(primary_attempts) == len(annotations)
            and requirement_rate is not None
            and Decimal(str(len(primary_attempts) / len(annotations)))
            >= quality.required_primary_valid_output_rate
            and Decimal(str(requirement_rate)) >= quality.required_requirement_status_match_rate
            and unsafe_requirement_mismatch_count
            <= quality.maximum_unsafe_requirement_status_mismatch_count
            and calibration_passes
        ),
        "cases": cases,
    }


def _is_unsafe_requirement_status_mismatch(
    human_status: EvidenceStatus,
    model_status: EvidenceStatus,
) -> bool:
    return human_status is not model_status and model_status in {
        EvidenceStatus.SATISFIED,
        EvidenceStatus.UNSATISFIED,
    }


def _stability_quality(
    configuration: ExpansionL3Configuration,
    cache: ExpansionL3ValidationCache,
) -> dict[str, object]:
    cases: list[dict[str, object]] = []
    score_ranges: list[Decimal] = []
    agreements = 0
    route_agreements = 0
    attempts_for_usage: list[ExpansionL3CachedAttempt] = []
    evaluable_case_count = 0
    for pair_id in configuration.stability.pair_ids:
        attempts = cache.records.get(pair_id, ())
        attempts_for_usage.extend(attempts)
        outputs = tuple(cast(LLMScoringOutput, item.result.output) for item in attempts)
        scores = tuple(item.overall_score for item in outputs)
        if len(attempts) != configuration.stability.total_attempts_per_pair:
            cases.append(
                {
                    "pair_id": pair_id,
                    "status": "not_evaluable",
                    "scores": [float(item) for item in scores],
                    "score_range": None,
                    "requirement_statuses_agree": None,
                }
            )
            continue
        evaluable_case_count += 1
        score_range = max(scores) - min(scores)
        score_ranges.append(score_range)
        signatures = tuple(
            tuple(
                sorted(
                    (item.requirement_id, item.evidence_status.value)
                    for item in output.requirement_assessments
                )
            )
            for output in outputs
        )
        agrees = len(set(signatures)) == 1
        agreements += agrees
        route_signatures = tuple(_requirement_route_signature(output) for output in outputs)
        route_agrees = len(set(route_signatures)) == 1
        route_agreements += route_agrees
        cases.append(
            {
                "pair_id": pair_id,
                "status": "evaluable",
                "scores": [float(item) for item in scores],
                "score_range": float(score_range),
                "requirement_statuses_agree": agrees,
                "requirement_routes_agree": route_agrees,
                "requirement_route_signatures": list(route_signatures),
            }
        )
    agreement_rate = agreements / evaluable_case_count if evaluable_case_count else None
    route_agreement_rate = route_agreements / evaluable_case_count if evaluable_case_count else None
    maximum_range = max(score_ranges) if score_ranges else None
    quality = configuration.quality_policy
    return {
        "case_count": len(configuration.stability.pair_ids),
        "evaluable_case_count": evaluable_case_count,
        "attempts_per_pair": configuration.stability.total_attempts_per_pair,
        "maximum_score_range": None if maximum_range is None else float(maximum_range),
        "average_score_range": float(mean(score_ranges)) if score_ranges else None,
        "requirement_status_agreement_rate": agreement_rate,
        "requirement_route_agreement_rate": route_agreement_rate,
        "usage_and_latency": _usage_payload(tuple(attempts_for_usage)),
        "passes_stability_policy": (
            evaluable_case_count == len(configuration.stability.pair_ids)
            and maximum_range is not None
            and agreement_rate is not None
            and route_agreement_rate is not None
            and maximum_range <= quality.maximum_stability_score_range
            and Decimal(str(agreement_rate))
            >= quality.required_stability_requirement_agreement_rate
            and Decimal(str(route_agreement_rate))
            >= quality.required_stability_requirement_route_agreement_rate
        ),
        "cases": cases,
    }


def _requirement_route_signature(output: LLMScoringOutput) -> str:
    statuses = {item.evidence_status for item in output.requirement_assessments}
    if statuses.intersection({EvidenceStatus.MISSING, EvidenceStatus.CONFLICTING}):
        return "needs_review"
    if EvidenceStatus.UNSATISFIED in statuses:
        return "explicit_unsatisfied"
    return "all_satisfied"


async def _hybrid_diagnostic(
    repository_root: Path,
    configuration: ExpansionL3Configuration,
    annotations: tuple[SyntheticPairAnnotation, ...],
    profiles: dict[str, CVProfile],
    jobs: dict[str, JobProfile],
    rubrics: dict[str, ScoringRubric],
    cache: ExpansionL3ValidationCache,
    embedding_runtime: ExpansionEmbeddingRuntime | None,
) -> dict[str, object]:
    l2_candidates = load_expansion_l2_candidate_set(
        repository_root,
        configuration.l2_configuration_path,
    )
    if (
        l2_candidates.candidate_set_id != configuration.l2_candidate_set_id
        or l2_candidates.candidate_set_version != configuration.l2_candidate_set_version
    ):
        raise ExpansionL3ValidationError("L3 experiment does not match the L2 candidate set")
    l2_candidate = next(
        item
        for item in l2_candidates.candidates
        if item.candidate_id == configuration.l2_candidate_id
    )
    runtime = embedding_runtime or default_embedding_runtime(repository_root)
    bridges = precompute_l2_adapters(
        annotations,
        profiles,
        jobs,
        rubrics,
        l2_candidates,
        runtime,
    )
    outputs_by_cv_profile_id = {
        annotation.cv_profile_id: cast(
            LLMScoringOutput,
            cache.records[annotation.pair_id][0].result.output,
        )
        for annotation in annotations
    }
    l3_provider = CachedExpansionL3Provider(outputs_by_cv_profile_id)
    stage6_candidates = load_stage6_candidate_set(repository_root)
    aggregation_candidate = next(
        item for item in stage6_candidates.candidates if item.candidate_id == "approved-current-v1"
    )
    if configuration.hybrid_policy is not None:
        if configuration.hybrid_policy.l2_candidate_id != configuration.l2_candidate_id:
            raise ExpansionL3ValidationError("L3 hybrid policy does not match L2 candidate")
        aggregation_candidate = aggregation_candidate.model_copy(
            update={
                "candidate_id": configuration.hybrid_policy.candidate_id,
                "aggregation": configuration.hybrid_policy.aggregation,
                "thresholds": configuration.hybrid_policy.thresholds,
                "disagreement_points": configuration.hybrid_policy.disagreement_points,
                "boundary_offset_points": configuration.hybrid_policy.boundary_offset_points,
            }
        )
    routing_policy = build_diagnostic_routing_policy(repository_root, aggregation_candidate)
    expected: list[ClassificationDecision] = []
    predicted: list[ClassificationDecision] = []
    cases: list[dict[str, object]] = []
    for annotation in annotations:
        profile = profiles[annotation.cv_profile_id]
        job = jobs[annotation.job_profile_id]
        rubric = rubrics[annotation.rubric_id]
        l1_policy = build_expansion_l1_policy(annotation.role, job.job_profile_id)
        l1 = score_l1(profile, rubric, l1_policy)
        l2_policy = build_query_coverage_l2_policy(
            job,
            rubric,
            l2_candidates.coverage_configuration(l2_candidate),
        )
        l2 = score_l2(profile, rubric, l2_policy, bridges[l2_policy.query_count])
        l3 = await score_l3(
            L3ProviderRequest(
                cv_profile=profile,
                job_profile=job,
                rubric=rubric,
                prompt_version=configuration.prompt_version,
            ),
            l3_provider,
        )
        if any(item.status is not LevelScoreStatus.AVAILABLE for item in (l1, l2, l3)):
            raise ExpansionL3ValidationError("hybrid diagnostic level is unavailable")
        aggregation = aggregate_level_scores((l1, l2, l3), aggregation_candidate.aggregation)
        routing = route_classification(aggregation, l1.requirement_assessments, routing_policy)
        expected_label = cast(ApprovedDatasetReview, annotation.review).final_label
        expected.append(expected_label)
        predicted.append(routing.decision)
        cases.append(
            {
                "pair_id": annotation.pair_id,
                "role": annotation.role.value,
                "scenario": annotation.scenario.value,
                "expected_label": expected_label.value,
                "predicted_label": routing.decision.value,
                "l1_score": float(cast(Decimal, l1.score)),
                "l2_score": float(cast(Decimal, l2.score)),
                "l3_score": float(cast(Decimal, l3.score)),
                "final_score": (
                    None if routing.final_score is None else float(routing.final_score)
                ),
                "review_reasons": list(routing.reasons),
            }
        )
    metrics = calculate_metrics(tuple(expected), tuple(predicted))
    false_reject_count = sum(
        actual is not ClassificationDecision.REJECT and prediction is ClassificationDecision.REJECT
        for actual, prediction in zip(expected, predicted, strict=True)
    )
    unsafe_pass_count = sum(
        prediction is ClassificationDecision.PASS
        and actual in {ClassificationDecision.REJECT, ClassificationDecision.NEEDS_REVIEW}
        for actual, prediction in zip(expected, predicted, strict=True)
    )
    review_support = sum(item is ClassificationDecision.NEEDS_REVIEW for item in expected)
    review_hits = sum(
        actual is ClassificationDecision.NEEDS_REVIEW
        and prediction is ClassificationDecision.NEEDS_REVIEW
        for actual, prediction in zip(expected, predicted, strict=True)
    )
    return {
        "hybrid_candidate_id": aggregation_candidate.candidate_id,
        "aggregation_weights": {
            "l1": float(aggregation_candidate.aggregation.l1_deterministic_rules),
            "l2": float(aggregation_candidate.aggregation.l2_section_semantic_matching),
            "l3": float(aggregation_candidate.aggregation.l3_evidence_grounded_reasoning),
        },
        "thresholds": {
            "waitlist_minimum": float(aggregation_candidate.thresholds.waitlist_minimum),
            "pass_minimum": float(aggregation_candidate.thresholds.pass_minimum),
            "disagreement_points": float(aggregation_candidate.disagreement_points),
            "boundary_offset_points": float(aggregation_candidate.boundary_offset_points),
        },
        "l2_candidate_id": configuration.l2_candidate_id,
        "embedding_model_identifier": runtime.model_identifier,
        "embedding_resolved_revision": runtime.resolved_revision,
        "accuracy": metrics.accuracy,
        "macro_f1": metrics.macro_f1,
        "needs_review_recall": review_hits / review_support,
        "review_rate": sum(item is ClassificationDecision.NEEDS_REVIEW for item in predicted)
        / len(predicted),
        "false_reject_count": false_reject_count,
        "unsafe_pass_count": unsafe_pass_count,
        "cases": cases,
    }


async def run_live_validation(
    repository_root: Path,
    generated_at: datetime,
    adapter: LLMAdapter,
    cache_path: Path = CACHE_PATH,
    configuration_path: Path = CONFIG_PATH,
    maximum_new_requests: int | None = None,
    request_interval_seconds: float | None = None,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    embedding_runtime: ExpansionEmbeddingRuntime | None = None,
) -> dict[str, object]:
    if generated_at.tzinfo is None or generated_at.utcoffset() is None:
        raise ValueError("generated_at must include a timezone")
    configuration = load_expansion_l3_configuration(repository_root, configuration_path)
    annotations, profiles, jobs, rubrics, _ = _selected_annotations(repository_root, configuration)
    cache = await _collect_outputs(
        repository_root,
        configuration,
        annotations,
        profiles,
        jobs,
        rubrics,
        adapter,
        cache_path,
        configuration_path,
        maximum_new_requests,
        request_interval_seconds,
        sleep,
    )
    cache_complete = _cache_complete(cache, configuration, annotations)
    terminal_quality_failure_reason = _primary_quality_failure_reason(
        cache, configuration, annotations
    )
    terminal_quality_failure = terminal_quality_failure_reason is not None
    terminal_provider_failure = _provider_availability_is_unrecoverable(
        cache, configuration, annotations
    )
    if not cache_complete and not terminal_quality_failure and not terminal_provider_failure:
        raise ExpansionL3ValidationError("expansion L3 cache is incomplete")
    provider_quality = _provider_quality(configuration, annotations, cache)
    stability = _stability_quality(configuration, cache)
    hybrid: dict[str, object]
    if cache_complete:
        hybrid = await _hybrid_diagnostic(
            repository_root,
            configuration,
            annotations,
            profiles,
            jobs,
            rubrics,
            cache,
            embedding_runtime,
        )
    else:
        hybrid = {
            "executed": False,
            "reason": "Live L3 valid-output coverage is insufficient for a hybrid diagnostic.",
        }
    quality_gate_passed = cast(bool, provider_quality["passes_primary_policy"]) and cast(
        bool, stability["passes_stability_policy"]
    )
    cost = _cost_payload(configuration, cache)
    return {
        "report_schema_version": "1.0.0",
        "report_id": configuration.experiment_id,
        "report_scope": f"silver-development-{configuration.provider_identifier}-live-l3",
        "is_final_performance": False,
        "experiment_status": (
            "completed"
            if cache_complete
            else (
                "stopped_quality_failure"
                if terminal_quality_failure
                else "stopped_provider_unavailable"
            )
        ),
        "generated_at": generated_at.isoformat(),
        "traceability": {
            "configuration_file": configuration_path.as_posix(),
            "configuration_sha256": _sha256(repository_root / configuration_path),
            "dataset_manifest_sha256": _sha256(
                repository_root / configuration.reviewed_dataset_directory / "manifest.json"
            ),
            "split_manifest_sha256": _sha256(repository_root / configuration.split_manifest_path),
            "dataset_id": configuration.dataset_id,
            "dataset_version": configuration.dataset_version,
            "development_partition_id": configuration.development_partition_id,
            "primary_pair_count": len(annotations),
            "held_out_partition_id": configuration.held_out_partition_id,
            "held_out_evaluated": False,
            "original_stage6_frozen_test_evaluated": False,
            "provider_identifier": configuration.provider_identifier,
            "model_identifier": configuration.model_identifier,
            "prompt_version": configuration.prompt_version,
            "l3_score_mapping_version": configuration.l3_score_mapping_version,
            "raw_provider_response_persisted": False,
        },
        "request_accounting": {
            "hard_request_cap": configuration.request_policy.hard_request_cap,
            "prior_series_request_count": (configuration.request_policy.prior_series_request_count),
            "series_hard_request_cap": configuration.request_policy.series_hard_request_cap,
            "cumulative_series_request_count": (
                configuration.request_policy.prior_series_request_count + cache.total_request_count
            ),
            "minimum_request_interval_seconds": (
                configuration.request_policy.minimum_request_interval_seconds
            ),
            "request_timeout_seconds": configuration.request_policy.request_timeout_seconds,
            "maximum_total_retries_per_attempt": (
                configuration.request_policy.maximum_total_retries_per_attempt
            ),
            "include_temperature_parameter": (
                configuration.request_policy.include_temperature_parameter
            ),
            "max_completion_tokens": configuration.request_policy.max_completion_tokens,
            "reasoning_effort": configuration.request_policy.reasoning_effort,
            "total_http_request_count": cache.total_request_count,
            "valid_attempt_count": sum(len(items) for items in cache.records.values()),
            "failed_request_count": sum(len(items) for items in cache.failures.values()),
            "invalid_structured_output_count": sum(
                item.status is LLMProviderStatus.INVALID
                for items in cache.failures.values()
                for item in items
            ),
            "billing_tier_assumption": configuration.billing_tier_assumption,
            "estimated_provider_charge_usd": cost["estimated_provider_charge_usd"],
            "charge_verified": cost["charge_verified"],
            "cost_control": cost,
            "request_quality": _request_quality_payload(cache),
        },
        "early_stopping": {
            "triggered": terminal_quality_failure or terminal_provider_failure,
            "reason": (
                terminal_quality_failure_reason
                if terminal_quality_failure
                else (
                    "At least one primary case exhausted its provider-unavailable retry "
                    "allowance, so the live experiment could not continue safely."
                    if terminal_provider_failure
                    else None
                )
            ),
        },
        "provider_quality": provider_quality,
        "development_panel": _development_panel_payload(cache, configuration, annotations),
        "stability": stability,
        "hybrid_diagnostic": hybrid,
        "quality_gate_passed": quality_gate_passed,
        "configuration_freeze_eligible": False,
        "freeze_blockers": [
            *(
                [
                    "The configured LLM provider did not satisfy the structured-output quality policy."
                ]
                if terminal_quality_failure or terminal_provider_failure
                else []
            ),
            "The five-role labels are Silver and have one human reviewer.",
            "The three new roles do not yet have approved runtime configuration artifacts.",
            "Held-out and frozen-test evaluation is intentionally not executed.",
        ],
    }


def _configured_adapter(
    settings: RuntimeSettings,
    configuration: ExpansionL3Configuration,
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
        raise ExpansionL3ValidationError("live L3 settings are incomplete")
    secret = api_key.get_secret_value()
    if secret.startswith("<") or "replace" in secret.casefold():
        raise ExpansionL3ValidationError("LLM API key still contains a placeholder")
    if provider != configuration.provider_identifier:
        raise ExpansionL3ValidationError("runtime L3 provider does not match experiment")
    if model != configuration.model_identifier:
        raise ExpansionL3ValidationError("runtime L3 model does not match experiment")
    expected_base_urls = {
        "openrouter": "https://openrouter.ai/api/v1",
        "google_ai_studio": "https://generativelanguage.googleapis.com/v1beta/openai",
        "openai": "https://api.openai.com/v1",
    }
    if base_url.rstrip("/") != expected_base_urls[configuration.provider_identifier]:
        raise ExpansionL3ValidationError("runtime L3 base URL does not match provider")
    return OpenAICompatibleLLMAdapter(
        provider_identifier=provider,
        model_identifier=model,
        api_key=secret,
        base_url=base_url,
        prompt_version=configuration.prompt_version,
        client=client,
        include_temperature_parameter=(configuration.request_policy.include_temperature_parameter),
        require_supported_parameters=(configuration.request_policy.require_supported_parameters),
        enable_response_healing=configuration.request_policy.response_healing_enabled,
        max_completion_tokens=configuration.request_policy.max_completion_tokens,
        reasoning_effort=configuration.request_policy.reasoning_effort,
    )


async def _main_async(arguments: argparse.Namespace) -> Path | None:
    repository_root = Path(__file__).resolve().parents[2]
    configuration_path = Path(cast(str, arguments.configuration))
    configuration = load_expansion_l3_configuration(repository_root, configuration_path)
    settings = RuntimeSettings()
    timeout = httpx.Timeout(configuration.request_policy.request_timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout) as client:
        adapter = _configured_adapter(settings, configuration, client)
        if cast(bool, arguments.collect_only):
            progress = await collect_live_outputs(
                repository_root,
                adapter,
                cache_path=Path(cast(str, arguments.cache)),
                configuration_path=configuration_path,
                maximum_new_requests=cast(int | None, arguments.maximum_new_requests),
                request_interval_seconds=cast(float | None, arguments.request_interval_seconds),
            )
            print(json.dumps(progress, ensure_ascii=False))
            return None
        report = await run_live_validation(
            repository_root,
            _timestamp(cast(str, arguments.generated_at)),
            adapter,
            cache_path=Path(cast(str, arguments.cache)),
            configuration_path=configuration_path,
            maximum_new_requests=cast(int | None, arguments.maximum_new_requests),
            request_interval_seconds=cast(float | None, arguments.request_interval_seconds),
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
    parser.add_argument("--collect-only", action="store_true")
    parser.add_argument("--maximum-new-requests", type=int)
    parser.add_argument("--request-interval-seconds", type=float)
    parser.add_argument("--generated-at", default="2026-07-31T23:30:00+07:00")
    parser.add_argument("--configuration", default=CONFIG_PATH.as_posix())
    parser.add_argument("--cache", default=CACHE_PATH.as_posix())
    parser.add_argument("--output", default=REPORT_PATH.as_posix())
    arguments = parser.parse_args()
    output = asyncio.run(_main_async(arguments))
    if output is not None:
        print(output)


if __name__ == "__main__":
    main()
