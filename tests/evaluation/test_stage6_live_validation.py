from __future__ import annotations

import json
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import cast

import pytest

from backend.app.contracts import EvidenceStatus
from backend.app.infrastructure.embeddings import HashingEmbeddingAdapter
from backend.app.infrastructure.llm import (
    LLMAdapter,
    LLMProviderResult,
    LLMProviderStatus,
    LLMProviderUsage,
    LLMRequirementAssessment,
    LLMScoringOutput,
    LLMScoringRequest,
    LLMWeightedCriterionAssessment,
)
from evaluation.datasets import load_stage6_validation
from evaluation.experiments.run_stage6_live_validation import (
    LiveProviderUnavailable,
    LiveValidationError,
    collect_live_outputs,
    run_live_validation,
)
from evaluation.experiments.run_stage6_validation import EmbeddingRuntime
from evaluation.experiments.stage6_live_config import (
    Stage6LiveConfiguration,
    load_stage6_live_configuration,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
GENERATED_AT = datetime.fromisoformat("2026-07-26T23:00:00+07:00")


class StructuredTestLLMAdapter:
    def __init__(self, invalid_call_number: int | None = None) -> None:
        self.call_count = 0
        self._invalid_call_number = invalid_call_number

    async def score(self, request: LLMScoringRequest) -> LLMProviderResult:
        self.call_count += 1
        if self.call_count == self._invalid_call_number:
            return LLMProviderResult(
                status=LLMProviderStatus.INVALID,
                provider_identifier="google_ai_studio",
                model_identifier="gemini-3.5-flash-lite",
                prompt_version=request.prompt_version,
                reason="Synthetic invalid structured output.",
            )
        evidence_id = request.evidence[0].evidence_id
        criteria = tuple(
            LLMWeightedCriterionAssessment(
                criterion_id=criterion.criterion_id,
                score=(criterion.weight * Decimal("0.70")).quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP,
                ),
                evidence_status=EvidenceStatus.SATISFIED,
                evidence_ids=(evidence_id,),
                rationale="Synthetic structured assessment for deterministic tests.",
            )
            for criterion in request.rubric.criteria
        )
        output = LLMScoringOutput(
            overall_score=sum((item.score for item in criteria), Decimal("0")),
            requirement_assessments=tuple(
                LLMRequirementAssessment(
                    requirement_id=requirement_id,
                    evidence_status=EvidenceStatus.SATISFIED,
                    evidence_ids=(evidence_id,),
                    rationale="Synthetic requirement assessment for deterministic tests.",
                )
                for requirement_id in request.rubric.critical_requirement_ids
            ),
            criterion_assessments=criteria,
            strengths=("Synthetic output is schema-valid.",),
            risks=("Synthetic output is not a real provider result.",),
            confidence=Decimal("0.70"),
        )
        return LLMProviderResult(
            status=LLMProviderStatus.AVAILABLE,
            provider_identifier="google_ai_studio",
            model_identifier="gemini-3.5-flash-lite",
            prompt_version=request.prompt_version,
            output=output,
            usage=LLMProviderUsage(
                input_tokens=100,
                output_tokens=50,
                total_tokens=150,
            ),
        )


class UnavailableTestLLMAdapter:
    async def score(self, request: LLMScoringRequest) -> LLMProviderResult:
        return LLMProviderResult(
            status=LLMProviderStatus.UNAVAILABLE,
            provider_identifier="google_ai_studio",
            model_identifier="gemini-3.5-flash-lite",
            prompt_version=request.prompt_version,
            reason="Synthetic provider outage.",
        )


def _embedding_runtime() -> EmbeddingRuntime:
    return EmbeddingRuntime(
        adapter=HashingEmbeddingAdapter(
            dimension=768,
            model_identifier="stage6-live-test-embedding",
            model_version="1.0.0",
        ),
        model_identifier="stage6-live-test-embedding",
        configured_model_version="1.0.0",
        resolved_model_revision="0" * 40,
        configured_model_executed=False,
    )


def test_live_configuration_is_versioned_and_uses_validation_cases_only() -> None:
    configuration = load_stage6_live_configuration(REPOSITORY_ROOT)
    examples = load_stage6_validation(REPOSITORY_ROOT)
    examples_by_id = {item.cv_profile.cv_profile_id: item for item in examples}
    validation_ids = set(examples_by_id)
    manifest = json.loads(
        (REPOSITORY_ROOT / "data" / "splits" / "stage6_split_manifest_v1.json").read_text(
            encoding="utf-8"
        )
    )
    frozen_ids = set(cast(list[str], manifest["frozen_test"]["cv_profile_ids"]))

    assert configuration.experiment_version == "1.3.0"
    assert configuration.provider_identifier == "google_ai_studio"
    assert configuration.model_identifier == "gemini-3.5-flash-lite"
    assert configuration.prompt_version == "l3-evidence-rubric-v3"
    assert configuration.provider_request_policy.maximum_invalid_retries_per_attempt == 2
    assert configuration.data_policy.validation_only is True
    assert configuration.data_policy.frozen_test_allowed is False
    assert set(configuration.stability.case_ids).issubset(validation_ids)
    assert set(configuration.stability.case_ids).isdisjoint(frozen_ids)
    assert {
        examples_by_id[cv_profile_id].final_label.value
        for cv_profile_id in configuration.stability.case_ids
    } == {"pass", "waitlist", "reject", "needs_review"}
    assert {
        examples_by_id[cv_profile_id].job_profile_id
        for cv_profile_id in configuration.stability.case_ids
    } == {
        "junior-data-analyst-v1",
        "junior-python-backend-developer-v1",
    }


def test_live_configuration_rejects_duplicate_stability_case_ids() -> None:
    configuration = load_stage6_live_configuration(REPOSITORY_ROOT)
    payload = configuration.model_dump(mode="python")
    stability = cast(dict[str, object], payload["stability"])
    stability["case_ids"] = (
        configuration.stability.case_ids[0],
        configuration.stability.case_ids[0],
    )

    with pytest.raises(ValueError, match="unique"):
        Stage6LiveConfiguration.model_validate(payload)


@pytest.mark.asyncio
async def test_live_runner_reports_provider_quality_and_never_exposes_frozen_ids(
    tmp_path: Path,
) -> None:
    adapter = StructuredTestLLMAdapter()
    cache_path = tmp_path / "live-cache.json"

    report = await run_live_validation(
        REPOSITORY_ROOT,
        GENERATED_AT,
        adapter,
        _embedding_runtime(),
        cache_path,
    )
    manifest = json.loads(
        (REPOSITORY_ROOT / "data" / "splits" / "stage6_split_manifest_v1.json").read_text(
            encoding="utf-8"
        )
    )
    frozen_ids = cast(list[str], manifest["frozen_test"]["cv_profile_ids"])
    serialized_report = json.dumps(report)
    provider_validation = cast(dict[str, object], report["provider_validation"])
    primary = cast(dict[str, object], provider_validation["primary_quality"])
    stability = cast(dict[str, object], provider_validation["stability"])
    split = cast(dict[str, object], report["split_traceability"])

    assert adapter.call_count == 24
    assert primary["sample_count"] == 20
    assert primary["available_output_count"] == 20
    assert primary["valid_output_rate"] == 1
    assert stability["case_count"] == 4
    assert stability["attempts_per_case"] == 2
    assert stability["passes_policy"] is True
    assert provider_validation["provider_quality_gate_passed"] is True
    assert split["frozen_test_evaluated"] is False
    assert all(cv_profile_id not in serialized_report for cv_profile_id in frozen_ids)
    assert "secret-test" not in serialized_report


@pytest.mark.asyncio
async def test_live_runner_resumes_generated_cache_without_repeating_calls(
    tmp_path: Path,
) -> None:
    cache_path = tmp_path / "resume-cache.json"
    first_adapter = StructuredTestLLMAdapter()

    with pytest.raises(LiveValidationError, match="incomplete"):
        await run_live_validation(
            REPOSITORY_ROOT,
            GENERATED_AT,
            first_adapter,
            _embedding_runtime(),
            cache_path,
            maximum_new_requests=5,
        )

    second_adapter = StructuredTestLLMAdapter()
    report = await run_live_validation(
        REPOSITORY_ROOT,
        GENERATED_AT,
        second_adapter,
        _embedding_runtime(),
        cache_path,
    )

    assert first_adapter.call_count == 5
    assert second_adapter.call_count == 19
    assert report["report_id"] == "stage6-live-llm-validation-v1"


@pytest.mark.asyncio
async def test_live_collector_reports_partial_progress_without_requiring_a_report(
    tmp_path: Path,
) -> None:
    adapter = StructuredTestLLMAdapter()

    progress = await collect_live_outputs(
        REPOSITORY_ROOT,
        adapter,
        tmp_path / "progress-cache.json",
        maximum_new_requests=4,
    )

    assert progress["cached_attempt_count"] == 4
    assert progress["required_attempt_count"] == 24
    assert progress["remaining_attempt_count"] == 20
    assert progress["complete"] is False


@pytest.mark.asyncio
async def test_live_runner_audits_invalid_output_then_retries_without_using_it(
    tmp_path: Path,
) -> None:
    cache_path = tmp_path / "invalid-cache.json"
    invalid_adapter = StructuredTestLLMAdapter(invalid_call_number=1)

    progress = await collect_live_outputs(
        REPOSITORY_ROOT,
        invalid_adapter,
        cache_path,
        maximum_new_requests=1,
    )
    valid_adapter = StructuredTestLLMAdapter()
    report = await run_live_validation(
        REPOSITORY_ROOT,
        GENERATED_AT,
        valid_adapter,
        _embedding_runtime(),
        cache_path,
    )
    provider_validation = cast(dict[str, object], report["provider_validation"])
    primary = cast(dict[str, object], provider_validation["primary_quality"])

    assert progress["cached_attempt_count"] == 0
    assert progress["remaining_attempt_count"] == 24
    assert primary["invalid_output_count"] == 0
    assert provider_validation["invalid_structured_output_retry_count"] == 1
    assert provider_validation["provider_quality_gate_passed"] is True


@pytest.mark.asyncio
async def test_live_runner_stops_on_provider_unavailability_without_caching_failure(
    tmp_path: Path,
) -> None:
    cache_path = tmp_path / "unavailable-cache.json"
    adapter: LLMAdapter = UnavailableTestLLMAdapter()

    with pytest.raises(LiveProviderUnavailable, match="outage"):
        await run_live_validation(
            REPOSITORY_ROOT,
            GENERATED_AT,
            adapter,
            _embedding_runtime(),
            cache_path,
        )

    assert not cache_path.exists()
