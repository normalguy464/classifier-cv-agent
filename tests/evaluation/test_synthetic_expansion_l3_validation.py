from __future__ import annotations

import hashlib
import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import cast

import httpx
import pytest

from backend.app.contracts import ClassificationDecision, EvidenceStatus
from backend.app.core.settings import RuntimeSettings
from backend.app.infrastructure.embeddings import HashingEmbeddingAdapter
from backend.app.infrastructure.llm import (
    LLMProviderResult,
    LLMProviderStatus,
    LLMProviderUsage,
    LLMRequirementAssessment,
    LLMScoringOutput,
    LLMScoringRequest,
    LLMWeightedCriterionAssessment,
)
from evaluation.datasets.synthetic_expansion import (
    ApprovedDatasetReview,
    DatasetRole,
    JobVariant,
    SyntheticPairAnnotation,
)
from evaluation.experiments.run_synthetic_expansion_v2_diagnostic import (
    ExpansionEmbeddingRuntime,
)
from evaluation.experiments.run_synthetic_expansion_v2_l3_validation import (
    ExpansionL3CachedFailure,
    ExpansionL3ProviderUnavailable,
    ExpansionL3RequestCapReached,
    ExpansionL3ValidationError,
    _configured_adapter,
    _empty_cache,
    _is_unsafe_requirement_status_mismatch,
    _primary_quality_failure_reason,
    _primary_quality_is_unrecoverable,
    _selected_annotations,
    _write_cache,
    collect_live_outputs,
    migrate_evaluation_policy_cache,
    run_live_validation,
)
from evaluation.experiments.synthetic_expansion_l3_config import (
    CONFIG_PATH,
    ExpansionL3Configuration,
    GEMMA_3_CONFIG_PATH,
    GEMMA_3_NATIVE_CONFIG_PATH,
    GOOGLE_AI_STUDIO_CALIBRATED_CONFIG_PATH,
    GOOGLE_AI_STUDIO_CONFIG_PATH,
    GOOGLE_AI_STUDIO_EXACT_NEGATIVE_CONFIG_PATH,
    GOOGLE_AI_STUDIO_HARD_SCOPED_CONFIG_PATH,
    GOOGLE_AI_STUDIO_QA_REMEDIATED_CONFIG_PATH,
    GOOGLE_AI_STUDIO_SCOPED_CONFIG_PATH,
    GOOGLE_AI_STUDIO_STRICT_SCOPED_CONFIG_PATH,
    GPT_OSS_120B_CONFIG_PATH,
    GPT_OSS_120B_HEALED_CONFIG_PATH,
    GPT_OSS_CONFIG_PATH,
    GPT_OSS_HEALED_CONFIG_PATH,
    NEMOTRON_CONFIG_PATH,
    NEMOTRON_NANO_CONFIG_PATH,
    NEMOTRON_NANO_HEALED_CONFIG_PATH,
    NEMOTRON_ULTRA_CONFIG_PATH,
    NEMOTRON_ULTRA_NATIVE_CONFIG_PATH,
    OPENAI_GPT_5_4_MINI_CONFIG_PATH,
    OPENAI_GPT_5_4_MINI_DYNAMIC_SCHEMA_CONFIG_PATH,
    OPENAI_GPT_5_4_MINI_HYBRID_TUNED_CONFIG_PATH,
    OPENAI_GPT_5_4_MINI_NORMALIZED_CONFIG_PATH,
    OPENAI_GPT_5_4_MINI_REQUIREMENT_GUARDED_CONFIG_PATH,
    OPENAI_GPT_5_4_MINI_ROLE_CALIBRATED_CONFIG_PATH,
    OPENAI_GPT_5_4_MINI_SAFETY_GATED_CONFIG_PATH,
    OPENAI_GPT_5_4_MINI_VALIDATED_CONFIG_PATH,
    QWEN3_NEXT_CONFIG_PATH,
    QWEN3_NEXT_NATIVE_CONFIG_PATH,
    QWEN3_NEXT_SNAPSHOT_CONFIG_PATH,
    load_expansion_l3_configuration,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
GENERATED_AT = datetime.fromisoformat("2026-07-31T23:30:00+07:00")


class ReviewedOutputAdapter:
    def __init__(
        self,
        annotations: tuple[SyntheticPairAnnotation, ...],
        invalid_call_numbers: frozenset[int] = frozenset(),
        unavailable_call_numbers: frozenset[int] = frozenset(),
        model_identifier: str = "google/gemma-4-26b-a4b-it:free",
        provider_identifier: str = "openrouter",
    ) -> None:
        self.call_count = 0
        self._invalid_call_numbers = invalid_call_numbers
        self._unavailable_call_numbers = unavailable_call_numbers
        self._model_identifier = model_identifier
        self._provider_identifier = provider_identifier
        self._annotations_by_digest = {
            hashlib.sha256(item.pair_id.encode("utf-8")).hexdigest()[:16]: item
            for item in annotations
        }

    async def score(self, request: LLMScoringRequest) -> LLMProviderResult:
        self.call_count += 1
        if self.call_count in self._unavailable_call_numbers:
            return LLMProviderResult(
                status=LLMProviderStatus.UNAVAILABLE,
                provider_identifier=self._provider_identifier,
                model_identifier=self._model_identifier,
                prompt_version=request.prompt_version,
                reason="Synthetic provider outage.",
            )
        if self.call_count in self._invalid_call_numbers:
            return LLMProviderResult(
                status=LLMProviderStatus.INVALID,
                provider_identifier=self._provider_identifier,
                model_identifier=self._model_identifier,
                prompt_version=request.prompt_version,
                reason="Synthetic invalid structured output.",
            )
        digest = request.request_id.rsplit("-", 2)[-2]
        annotation = self._annotations_by_digest[digest]
        criteria = tuple(
            LLMWeightedCriterionAssessment(
                criterion_id=item.criterion_id,
                score=item.awarded_points,
                evidence_status=(
                    EvidenceStatus.SATISFIED if item.evidence_ids else EvidenceStatus.MISSING
                ),
                evidence_ids=item.evidence_ids,
                rationale="Synthetic reviewed criterion output.",
            )
            for item in annotation.criterion_assessments
        )
        output = LLMScoringOutput(
            overall_score=annotation.total_score,
            requirement_assessments=tuple(
                LLMRequirementAssessment(
                    requirement_id=item.requirement_id,
                    evidence_status=item.evidence_status,
                    evidence_ids=(
                        () if item.evidence_status is EvidenceStatus.MISSING else item.evidence_ids
                    ),
                    rationale="Synthetic reviewed requirement output.",
                )
                for item in annotation.critical_requirement_assessments
            ),
            criterion_assessments=criteria,
            strengths=("Synthetic schema-valid strength.",),
            risks=("Synthetic adapter is not a live model.",),
            confidence=Decimal("0.90"),
        )
        return LLMProviderResult(
            status=LLMProviderStatus.AVAILABLE,
            provider_identifier=self._provider_identifier,
            model_identifier=self._model_identifier,
            prompt_version=request.prompt_version,
            output=output,
            usage=LLMProviderUsage(
                input_tokens=200,
                output_tokens=100,
                total_tokens=300,
            ),
        )


class EndpointOutputAdapter(ReviewedOutputAdapter):
    async def score(self, request: LLMScoringRequest) -> LLMProviderResult:
        result = await super().score(request)
        output = cast(LLMScoringOutput, result.output)
        criteria = tuple(
            item.model_copy(update={"score": Decimal("0")}) for item in output.criterion_assessments
        )
        return result.model_copy(
            update={
                "output": output.model_copy(
                    update={
                        "overall_score": Decimal("0"),
                        "criterion_assessments": criteria,
                    }
                )
            }
        )


def _annotations(
    configuration_path: Path = CONFIG_PATH,
) -> tuple[SyntheticPairAnnotation, ...]:
    configuration = load_expansion_l3_configuration(REPOSITORY_ROOT, configuration_path)
    annotations, _, _, _, _ = _selected_annotations(REPOSITORY_ROOT, configuration)
    return annotations


def _embedding_runtime() -> ExpansionEmbeddingRuntime:
    return ExpansionEmbeddingRuntime(
        adapter=HashingEmbeddingAdapter(
            dimension=768,
            model_identifier="deterministic-hashing-embedding",
            model_version="test-v1",
        ),
        model_identifier="deterministic-hashing-embedding",
        model_version="test-v1",
        resolved_revision="deterministic-test-revision",
        configured_model_executed=False,
    )


async def _no_sleep(seconds: float) -> None:
    assert seconds >= 4


def test_openrouter_l3_configuration_preselects_balanced_development_sample() -> None:
    configuration = load_expansion_l3_configuration(REPOSITORY_ROOT)
    annotations, _, _, _, split = _selected_annotations(REPOSITORY_ROOT, configuration)

    assert configuration.experiment_version == "1.0.0"
    assert configuration.model_identifier == "google/gemma-4-26b-a4b-it:free"
    assert configuration.l2_candidate_id == "coverage-70-95-v1"
    assert configuration.required_valid_attempt_count == 30
    assert configuration.request_policy.hard_request_cap == 40
    assert len(annotations) == 25
    assert all(item.job_variant is JobVariant.STANDARD for item in annotations)
    assert {role: sum(item.role is role for item in annotations) for role in DatasetRole} == {
        role: 5 for role in DatasetRole
    }
    assert {cast(ApprovedDatasetReview, item.review).final_label for item in annotations} == set(
        ClassificationDecision
    )
    assert set(configuration.primary_pair_ids).isdisjoint(split.held_out.pair_ids)


def test_openrouter_l3_configuration_rejects_duplicate_and_unlinked_samples() -> None:
    configuration = load_expansion_l3_configuration(REPOSITORY_ROOT)
    duplicate_payload = configuration.model_dump(mode="python")
    duplicate_payload["primary_pair_ids"] = (
        configuration.primary_pair_ids[0],
        *configuration.primary_pair_ids[1:-1],
        configuration.primary_pair_ids[0],
    )
    with pytest.raises(ValueError, match="unique"):
        ExpansionL3Configuration.model_validate(duplicate_payload)

    unlinked_payload = configuration.model_dump(mode="python")
    stability = cast(dict[str, object], unlinked_payload["stability"])
    stability["pair_ids"] = (
        *configuration.stability.pair_ids[:-1],
        "pair-not-in-primary",
    )
    with pytest.raises(ValueError, match="primary"):
        ExpansionL3Configuration.model_validate(unlinked_payload)


def test_openrouter_nemotron_configuration_is_versioned_and_interleaved() -> None:
    configuration = load_expansion_l3_configuration(REPOSITORY_ROOT, NEMOTRON_CONFIG_PATH)
    annotations, _, _, _, split = _selected_annotations(REPOSITORY_ROOT, configuration)

    assert configuration.experiment_version == "2.0.0"
    assert configuration.model_identifier == "nvidia/nemotron-3-super-120b-a12b:free"
    assert configuration.request_policy.require_supported_parameters is True
    assert configuration.quality_policy.maximum_endpoint_score_rate == Decimal("0.4")
    assert configuration.quality_policy.maximum_criterion_mean_absolute_error == Decimal("3.5")
    assert configuration.quality_policy.maximum_total_score_mean_absolute_error == Decimal("12")
    assert tuple(item.role for item in annotations[:5]) == tuple(DatasetRole)
    assert set(configuration.primary_pair_ids).isdisjoint(split.held_out.pair_ids)


def test_openrouter_nemotron_configuration_rejects_model_version_mismatch() -> None:
    configuration = load_expansion_l3_configuration(REPOSITORY_ROOT, NEMOTRON_CONFIG_PATH)
    payload = configuration.model_dump(mode="python")
    payload["model_identifier"] = "google/gemma-4-26b-a4b-it:free"

    with pytest.raises(ValueError, match="do not match"):
        ExpansionL3Configuration.model_validate(payload)


def test_openrouter_gpt_oss_configuration_preserves_sample_and_safety_policy() -> None:
    configuration = load_expansion_l3_configuration(REPOSITORY_ROOT, GPT_OSS_CONFIG_PATH)
    annotations, _, _, _, split = _selected_annotations(REPOSITORY_ROOT, configuration)

    assert configuration.experiment_version == "3.0.0"
    assert configuration.model_identifier == "openai/gpt-oss-20b:free"
    assert configuration.request_policy.require_supported_parameters is True
    assert (
        configuration.primary_pair_ids
        == load_expansion_l3_configuration(REPOSITORY_ROOT, NEMOTRON_CONFIG_PATH).primary_pair_ids
    )
    assert len(annotations) == 25
    assert set(configuration.primary_pair_ids).isdisjoint(split.held_out.pair_ids)


def test_openrouter_gpt_oss_healed_configuration_is_versioned_and_opted_in() -> None:
    configuration = load_expansion_l3_configuration(REPOSITORY_ROOT, GPT_OSS_HEALED_CONFIG_PATH)
    previous = load_expansion_l3_configuration(REPOSITORY_ROOT, GPT_OSS_CONFIG_PATH)

    assert configuration.experiment_version == "4.0.0"
    assert configuration.model_identifier == "openai/gpt-oss-20b:free"
    assert configuration.request_policy.require_supported_parameters is True
    assert configuration.request_policy.response_healing_enabled is True
    assert configuration.primary_pair_ids == previous.primary_pair_ids


def test_openrouter_gpt_oss_120b_configuration_is_fixed_and_preserves_sample() -> None:
    configuration = load_expansion_l3_configuration(REPOSITORY_ROOT, GPT_OSS_120B_CONFIG_PATH)
    previous = load_expansion_l3_configuration(REPOSITORY_ROOT, GPT_OSS_HEALED_CONFIG_PATH)

    assert configuration.experiment_version == "5.0.0"
    assert configuration.model_identifier == "openai/gpt-oss-120b:free"
    assert configuration.request_policy.require_supported_parameters is True
    assert configuration.request_policy.response_healing_enabled is True
    assert configuration.primary_pair_ids == previous.primary_pair_ids


def test_openrouter_nemotron_nano_configuration_is_fixed_and_preserves_sample() -> None:
    configuration = load_expansion_l3_configuration(REPOSITORY_ROOT, NEMOTRON_NANO_CONFIG_PATH)
    previous = load_expansion_l3_configuration(REPOSITORY_ROOT, GPT_OSS_120B_CONFIG_PATH)

    assert configuration.experiment_version == "6.0.0"
    assert configuration.model_identifier == "nvidia/nemotron-3-nano-30b-a3b:free"
    assert configuration.request_policy.require_supported_parameters is True
    assert configuration.request_policy.response_healing_enabled is True
    assert configuration.primary_pair_ids == previous.primary_pair_ids


def test_openrouter_nemotron_nano_healed_configuration_keeps_local_validation() -> None:
    configuration = load_expansion_l3_configuration(
        REPOSITORY_ROOT, NEMOTRON_NANO_HEALED_CONFIG_PATH
    )
    previous = load_expansion_l3_configuration(REPOSITORY_ROOT, NEMOTRON_NANO_CONFIG_PATH)

    assert configuration.experiment_version == "7.0.0"
    assert configuration.model_identifier == "nvidia/nemotron-3-nano-30b-a3b:free"
    assert configuration.request_policy.require_supported_parameters is False
    assert configuration.request_policy.response_healing_enabled is True
    assert configuration.primary_pair_ids == previous.primary_pair_ids


def test_openrouter_gpt_oss_120b_healed_configuration_keeps_local_validation() -> None:
    configuration = load_expansion_l3_configuration(
        REPOSITORY_ROOT, GPT_OSS_120B_HEALED_CONFIG_PATH
    )
    previous = load_expansion_l3_configuration(REPOSITORY_ROOT, NEMOTRON_NANO_HEALED_CONFIG_PATH)

    assert configuration.experiment_version == "8.0.0"
    assert configuration.model_identifier == "openai/gpt-oss-120b:free"
    assert configuration.request_policy.require_supported_parameters is False
    assert configuration.request_policy.response_healing_enabled is True
    assert configuration.primary_pair_ids == previous.primary_pair_ids


def test_openrouter_nemotron_ultra_configuration_is_fixed_and_preserves_sample() -> None:
    configuration = load_expansion_l3_configuration(REPOSITORY_ROOT, NEMOTRON_ULTRA_CONFIG_PATH)
    previous = load_expansion_l3_configuration(REPOSITORY_ROOT, GPT_OSS_120B_HEALED_CONFIG_PATH)

    assert configuration.experiment_version == "9.0.0"
    assert configuration.model_identifier == "nvidia/nemotron-3-ultra-550b-a55b:free"
    assert configuration.request_policy.require_supported_parameters is False
    assert configuration.request_policy.response_healing_enabled is True
    assert configuration.primary_pair_ids == previous.primary_pair_ids


def test_openrouter_nemotron_ultra_native_configuration_disables_healing() -> None:
    configuration = load_expansion_l3_configuration(
        REPOSITORY_ROOT, NEMOTRON_ULTRA_NATIVE_CONFIG_PATH
    )
    previous = load_expansion_l3_configuration(REPOSITORY_ROOT, NEMOTRON_ULTRA_CONFIG_PATH)

    assert configuration.experiment_version == "10.0.0"
    assert configuration.model_identifier == "nvidia/nemotron-3-ultra-550b-a55b:free"
    assert configuration.request_policy.require_supported_parameters is False
    assert configuration.request_policy.response_healing_enabled is False
    assert configuration.primary_pair_ids == previous.primary_pair_ids


def test_openrouter_gemma_3_configuration_is_multilingual_fixed_candidate() -> None:
    configuration = load_expansion_l3_configuration(REPOSITORY_ROOT, GEMMA_3_CONFIG_PATH)
    previous = load_expansion_l3_configuration(REPOSITORY_ROOT, NEMOTRON_ULTRA_NATIVE_CONFIG_PATH)

    assert configuration.experiment_version == "11.0.0"
    assert configuration.model_identifier == "google/gemma-3-27b-it:free"
    assert configuration.request_policy.require_supported_parameters is True
    assert configuration.request_policy.response_healing_enabled is False
    assert configuration.primary_pair_ids == previous.primary_pair_ids


def test_openrouter_gemma_3_native_configuration_keeps_contract_validation() -> None:
    configuration = load_expansion_l3_configuration(REPOSITORY_ROOT, GEMMA_3_NATIVE_CONFIG_PATH)
    previous = load_expansion_l3_configuration(REPOSITORY_ROOT, GEMMA_3_CONFIG_PATH)

    assert configuration.experiment_version == "12.0.0"
    assert configuration.model_identifier == "google/gemma-3-27b-it:free"
    assert configuration.request_policy.require_supported_parameters is False
    assert configuration.request_policy.response_healing_enabled is False
    assert configuration.primary_pair_ids == previous.primary_pair_ids


def test_openrouter_qwen3_next_configuration_requires_response_format_support() -> None:
    configuration = load_expansion_l3_configuration(REPOSITORY_ROOT, QWEN3_NEXT_CONFIG_PATH)
    previous = load_expansion_l3_configuration(REPOSITORY_ROOT, GEMMA_3_NATIVE_CONFIG_PATH)

    assert configuration.experiment_version == "13.0.0"
    assert configuration.model_identifier == "qwen/qwen3-next-80b-a3b-instruct:free"
    assert configuration.request_policy.require_supported_parameters is True
    assert configuration.request_policy.response_healing_enabled is False
    assert configuration.primary_pair_ids == previous.primary_pair_ids


def test_openrouter_qwen3_next_native_configuration_keeps_contract_validation() -> None:
    configuration = load_expansion_l3_configuration(REPOSITORY_ROOT, QWEN3_NEXT_NATIVE_CONFIG_PATH)
    previous = load_expansion_l3_configuration(REPOSITORY_ROOT, QWEN3_NEXT_CONFIG_PATH)

    assert configuration.experiment_version == "14.0.0"
    assert configuration.model_identifier == "qwen/qwen3-next-80b-a3b-instruct:free"
    assert configuration.request_policy.require_supported_parameters is False
    assert configuration.request_policy.response_healing_enabled is False
    assert configuration.primary_pair_ids == previous.primary_pair_ids


def test_openrouter_qwen3_next_snapshot_configuration_is_traceable() -> None:
    configuration = load_expansion_l3_configuration(
        REPOSITORY_ROOT, QWEN3_NEXT_SNAPSHOT_CONFIG_PATH
    )
    previous = load_expansion_l3_configuration(REPOSITORY_ROOT, QWEN3_NEXT_NATIVE_CONFIG_PATH)

    assert configuration.experiment_version == "15.0.0"
    assert configuration.model_identifier == "qwen/qwen3-next-80b-a3b-instruct-2509:free"
    assert configuration.request_policy.require_supported_parameters is True
    assert configuration.request_policy.response_healing_enabled is False
    assert configuration.primary_pair_ids == previous.primary_pair_ids


def test_google_ai_studio_configuration_is_versioned_bounded_and_provider_native() -> None:
    configuration = load_expansion_l3_configuration(REPOSITORY_ROOT, GOOGLE_AI_STUDIO_CONFIG_PATH)
    previous = load_expansion_l3_configuration(REPOSITORY_ROOT, QWEN3_NEXT_SNAPSHOT_CONFIG_PATH)
    annotations, _, _, _, split = _selected_annotations(REPOSITORY_ROOT, configuration)

    assert configuration.experiment_version == "16.0.0"
    assert configuration.provider_identifier == "google_ai_studio"
    assert configuration.model_identifier == "gemini-3.5-flash-lite"
    assert configuration.billing_tier_assumption == "free_tier_user_reported"
    assert configuration.request_policy.hard_request_cap == 35
    assert configuration.request_policy.minimum_request_interval_seconds == 6
    assert configuration.request_policy.request_timeout_seconds == 60
    assert configuration.request_policy.maximum_total_retries_per_attempt == 1
    assert configuration.request_policy.include_temperature_parameter is False
    assert configuration.request_policy.require_supported_parameters is False
    assert configuration.request_policy.response_healing_enabled is False
    assert configuration.primary_pair_ids == previous.primary_pair_ids
    assert len(annotations) == 25
    assert set(configuration.primary_pair_ids).isdisjoint(split.held_out.pair_ids)


def test_google_ai_studio_configuration_rejects_deprecated_temperature_parameter() -> None:
    configuration = load_expansion_l3_configuration(REPOSITORY_ROOT, GOOGLE_AI_STUDIO_CONFIG_PATH)
    payload = configuration.model_dump(mode="python")
    request_policy = cast(dict[str, object], payload["request_policy"])
    request_policy["include_temperature_parameter"] = True

    with pytest.raises(ValueError, match="do not match"):
        ExpansionL3Configuration.model_validate(payload)


def test_google_ai_studio_calibrated_configuration_reorders_only_development_cases() -> None:
    configuration = load_expansion_l3_configuration(
        REPOSITORY_ROOT, GOOGLE_AI_STUDIO_CALIBRATED_CONFIG_PATH
    )
    previous = load_expansion_l3_configuration(REPOSITORY_ROOT, GOOGLE_AI_STUDIO_CONFIG_PATH)
    annotations, _, _, _, split = _selected_annotations(REPOSITORY_ROOT, configuration)

    assert configuration.experiment_version == "17.0.0"
    assert configuration.prompt_version == "l3-evidence-rubric-v5"
    assert configuration.provider_identifier == "google_ai_studio"
    assert configuration.model_identifier == previous.model_identifier
    assert configuration.request_policy == previous.request_policy
    assert configuration.primary_pair_ids[0] == "pair-de-lowbd-std"
    assert set(configuration.primary_pair_ids) == set(previous.primary_pair_ids)
    assert len(annotations) == 25
    assert configuration.required_valid_attempt_count == 30
    assert set(configuration.primary_pair_ids).isdisjoint(split.held_out.pair_ids)


def test_google_ai_studio_calibrated_configuration_rejects_prompt_downgrade() -> None:
    configuration = load_expansion_l3_configuration(
        REPOSITORY_ROOT, GOOGLE_AI_STUDIO_CALIBRATED_CONFIG_PATH
    )
    payload = configuration.model_dump(mode="python")
    payload["prompt_version"] = "l3-evidence-rubric-v3"

    with pytest.raises(ValueError, match="prompt version"):
        ExpansionL3Configuration.model_validate(payload)


def test_google_ai_studio_scoped_configuration_uses_remediated_development_only() -> None:
    configuration = load_expansion_l3_configuration(
        REPOSITORY_ROOT, GOOGLE_AI_STUDIO_SCOPED_CONFIG_PATH
    )
    previous = load_expansion_l3_configuration(
        REPOSITORY_ROOT, GOOGLE_AI_STUDIO_CALIBRATED_CONFIG_PATH
    )
    annotations, _, _, _, split = _selected_annotations(REPOSITORY_ROOT, configuration)

    assert configuration.experiment_version == "18.0.0"
    assert configuration.dataset_version == "2.2.0"
    assert configuration.prompt_version == "l3-evidence-rubric-v6"
    assert configuration.model_identifier == previous.model_identifier
    assert configuration.request_policy == previous.request_policy
    assert set(configuration.primary_pair_ids) == set(previous.primary_pair_ids)
    assert configuration.primary_pair_ids[:3] == (
        "pair-qa-failed-std",
        "pair-da-missing-std",
        "pair-de-missing-std",
    )
    assert len(annotations) == 25
    assert configuration.required_valid_attempt_count == 30
    assert set(configuration.primary_pair_ids).isdisjoint(split.held_out.pair_ids)


def test_google_ai_studio_scoped_configuration_rejects_old_dataset_lineage() -> None:
    configuration = load_expansion_l3_configuration(
        REPOSITORY_ROOT, GOOGLE_AI_STUDIO_SCOPED_CONFIG_PATH
    )
    payload = configuration.model_dump(mode="python")
    payload["dataset_version"] = "2.1.0"

    with pytest.raises(ValueError, match="remediated dataset lineage"):
        ExpansionL3Configuration.model_validate(payload)


def test_google_ai_studio_qa_remediated_configuration_is_development_only() -> None:
    configuration = load_expansion_l3_configuration(
        REPOSITORY_ROOT, GOOGLE_AI_STUDIO_QA_REMEDIATED_CONFIG_PATH
    )
    previous = load_expansion_l3_configuration(REPOSITORY_ROOT, GOOGLE_AI_STUDIO_SCOPED_CONFIG_PATH)
    annotations, _, _, _, split = _selected_annotations(REPOSITORY_ROOT, configuration)

    assert configuration.experiment_version == "19.0.0"
    assert configuration.dataset_version == "2.3.0"
    assert configuration.prompt_version == "l3-evidence-rubric-v6"
    assert configuration.model_identifier == previous.model_identifier
    assert configuration.request_policy == previous.request_policy
    assert configuration.primary_pair_ids == previous.primary_pair_ids
    assert configuration.l2_candidate_set_version == "1.3.0"
    assert len(annotations) == 25
    assert configuration.required_valid_attempt_count == 30
    assert set(configuration.primary_pair_ids).isdisjoint(split.held_out.pair_ids)


def test_google_ai_studio_qa_remediated_configuration_rejects_v2_2_lineage() -> None:
    configuration = load_expansion_l3_configuration(
        REPOSITORY_ROOT, GOOGLE_AI_STUDIO_QA_REMEDIATED_CONFIG_PATH
    )
    payload = configuration.model_dump(mode="python")
    payload["dataset_version"] = "2.2.0"

    with pytest.raises(ValueError, match="remediated dataset lineage"):
        ExpansionL3Configuration.model_validate(payload)


def test_google_ai_studio_strict_scoped_configuration_keeps_v2_3_lineage() -> None:
    configuration = load_expansion_l3_configuration(
        REPOSITORY_ROOT, GOOGLE_AI_STUDIO_STRICT_SCOPED_CONFIG_PATH
    )
    previous = load_expansion_l3_configuration(
        REPOSITORY_ROOT, GOOGLE_AI_STUDIO_QA_REMEDIATED_CONFIG_PATH
    )
    annotations, _, _, _, split = _selected_annotations(REPOSITORY_ROOT, configuration)

    assert configuration.experiment_version == "20.0.0"
    assert configuration.dataset_version == "2.3.0"
    assert configuration.prompt_version == "l3-evidence-rubric-v7"
    assert configuration.model_identifier == previous.model_identifier
    assert configuration.request_policy == previous.request_policy
    assert configuration.primary_pair_ids == previous.primary_pair_ids
    assert configuration.l2_configuration_path == previous.l2_configuration_path
    assert len(annotations) == 25
    assert configuration.required_valid_attempt_count == 30
    assert set(configuration.primary_pair_ids).isdisjoint(split.held_out.pair_ids)


def test_google_ai_studio_hard_scoped_configuration_changes_only_prompt() -> None:
    configuration = load_expansion_l3_configuration(
        REPOSITORY_ROOT, GOOGLE_AI_STUDIO_HARD_SCOPED_CONFIG_PATH
    )
    previous = load_expansion_l3_configuration(
        REPOSITORY_ROOT, GOOGLE_AI_STUDIO_STRICT_SCOPED_CONFIG_PATH
    )
    annotations, _, _, _, split = _selected_annotations(REPOSITORY_ROOT, configuration)

    assert configuration.experiment_version == "21.0.0"
    assert configuration.dataset_version == "2.3.0"
    assert configuration.prompt_version == "l3-evidence-rubric-v8"
    assert configuration.model_identifier == previous.model_identifier
    assert configuration.request_policy == previous.request_policy
    assert configuration.primary_pair_ids == previous.primary_pair_ids
    assert configuration.l2_configuration_path == previous.l2_configuration_path
    assert len(annotations) == 25
    assert configuration.required_valid_attempt_count == 30
    assert set(configuration.primary_pair_ids).isdisjoint(split.held_out.pair_ids)


def test_google_ai_studio_exact_negative_configuration_uses_v2_3_1() -> None:
    configuration = load_expansion_l3_configuration(
        REPOSITORY_ROOT, GOOGLE_AI_STUDIO_EXACT_NEGATIVE_CONFIG_PATH
    )
    previous = load_expansion_l3_configuration(
        REPOSITORY_ROOT, GOOGLE_AI_STUDIO_HARD_SCOPED_CONFIG_PATH
    )
    annotations, _, _, _, split = _selected_annotations(REPOSITORY_ROOT, configuration)

    assert configuration.experiment_version == "22.0.0"
    assert configuration.dataset_version == "2.3.1"
    assert configuration.prompt_version == "l3-evidence-rubric-v8"
    assert configuration.model_identifier == previous.model_identifier
    assert configuration.request_policy == previous.request_policy
    assert configuration.primary_pair_ids == previous.primary_pair_ids
    assert configuration.l2_candidate_set_version == "1.3.1"
    assert len(annotations) == 25
    assert configuration.required_valid_attempt_count == 30
    assert set(configuration.primary_pair_ids).isdisjoint(split.held_out.pair_ids)


@pytest.mark.asyncio
async def test_google_ai_studio_runtime_adapter_accepts_only_the_expected_base_url() -> None:
    configuration = load_expansion_l3_configuration(REPOSITORY_ROOT, GOOGLE_AI_STUDIO_CONFIG_PATH)
    settings = RuntimeSettings(
        _env_file=None,
        classifier_llm_adapter="environment_configured",
        classifier_llm_provider="google_ai_studio",
        classifier_llm_model="gemini-3.5-flash-lite",
        classifier_llm_api_key="private-test-value",
        classifier_llm_base_url="https://generativelanguage.googleapis.com/v1beta/openai",
    )
    async with httpx.AsyncClient() as client:
        adapter = _configured_adapter(settings, configuration, client)
        assert adapter is not None

        invalid_settings = settings.model_copy(
            update={"classifier_llm_base_url": "https://openrouter.ai/api/v1"}
        )
        with pytest.raises(ExpansionL3ValidationError, match="does not match provider"):
            _configured_adapter(invalid_settings, configuration, client)


def test_openai_gpt_5_4_mini_configuration_is_bounded_and_development_only() -> None:
    configuration = load_expansion_l3_configuration(
        REPOSITORY_ROOT, OPENAI_GPT_5_4_MINI_CONFIG_PATH
    )
    previous = load_expansion_l3_configuration(
        REPOSITORY_ROOT, GOOGLE_AI_STUDIO_EXACT_NEGATIVE_CONFIG_PATH
    )
    annotations, _, _, _, split = _selected_annotations(REPOSITORY_ROOT, configuration)
    cost_policy = configuration.cost_policy

    assert configuration.experiment_version == "23.0.0"
    assert configuration.provider_identifier == "openai"
    assert configuration.model_identifier == "gpt-5.4-mini-2026-03-17"
    assert configuration.prompt_version == "l3-evidence-rubric-v9"
    assert configuration.request_policy.hard_request_cap == 35
    assert configuration.request_policy.minimum_request_interval_seconds == 1
    assert configuration.request_policy.max_completion_tokens == 4096
    assert configuration.request_policy.reasoning_effort == "none"
    assert configuration.request_policy.include_temperature_parameter is False
    assert cost_policy is not None
    assert cost_policy.maximum_estimated_experiment_cost_usd == Decimal("1.00")
    assert set(configuration.primary_pair_ids) == set(previous.primary_pair_ids)
    assert [item.role for item in annotations[:5]] == [
        DatasetRole.QA_ENGINEER,
        DatasetRole.DATA_ANALYST,
        DatasetRole.DATA_ENGINEER,
        DatasetRole.PYTHON_BACKEND,
        DatasetRole.FRONTEND,
    ]
    assert set(configuration.primary_pair_ids).isdisjoint(split.held_out.pair_ids)


def test_openai_gpt_5_4_mini_configuration_rejects_cost_above_budget() -> None:
    configuration = load_expansion_l3_configuration(
        REPOSITORY_ROOT, OPENAI_GPT_5_4_MINI_CONFIG_PATH
    )
    payload = configuration.model_dump(mode="python")
    request_policy = cast(dict[str, object], payload["request_policy"])
    request_policy["hard_request_cap"] = 40

    with pytest.raises(ValueError, match="exceeds the budget"):
        ExpansionL3Configuration.model_validate(payload)


def test_openai_gpt_5_4_mini_normalized_configuration_preserves_sample_and_policy() -> None:
    configuration = load_expansion_l3_configuration(
        REPOSITORY_ROOT, OPENAI_GPT_5_4_MINI_NORMALIZED_CONFIG_PATH
    )
    previous = load_expansion_l3_configuration(REPOSITORY_ROOT, OPENAI_GPT_5_4_MINI_CONFIG_PATH)

    assert configuration.experiment_version == "24.0.0"
    assert configuration.model_identifier == previous.model_identifier
    assert configuration.prompt_version == previous.prompt_version
    assert configuration.request_policy == previous.request_policy
    assert configuration.cost_policy == previous.cost_policy
    assert configuration.primary_pair_ids == previous.primary_pair_ids
    assert configuration.stability == previous.stability


def test_openai_gpt_5_4_mini_validated_configuration_changes_only_prompt_lineage() -> None:
    configuration = load_expansion_l3_configuration(
        REPOSITORY_ROOT, OPENAI_GPT_5_4_MINI_VALIDATED_CONFIG_PATH
    )
    previous = load_expansion_l3_configuration(
        REPOSITORY_ROOT, OPENAI_GPT_5_4_MINI_NORMALIZED_CONFIG_PATH
    )

    assert configuration.experiment_version == "25.0.0"
    assert configuration.prompt_version == "l3-evidence-rubric-v10"
    assert configuration.model_identifier == previous.model_identifier
    assert configuration.request_policy == previous.request_policy
    assert configuration.cost_policy == previous.cost_policy
    assert configuration.primary_pair_ids == previous.primary_pair_ids
    assert configuration.stability == previous.stability


def test_openai_gpt_5_4_mini_dynamic_schema_configuration_caps_the_full_series() -> None:
    configuration = load_expansion_l3_configuration(
        REPOSITORY_ROOT, OPENAI_GPT_5_4_MINI_DYNAMIC_SCHEMA_CONFIG_PATH
    )
    previous = load_expansion_l3_configuration(
        REPOSITORY_ROOT, OPENAI_GPT_5_4_MINI_VALIDATED_CONFIG_PATH
    )

    assert configuration.experiment_version == "26.0.0"
    assert configuration.prompt_version == previous.prompt_version
    assert configuration.model_identifier == previous.model_identifier
    assert configuration.primary_pair_ids == previous.primary_pair_ids
    assert configuration.stability == previous.stability
    assert configuration.request_policy.hard_request_cap == 32
    assert configuration.request_policy.prior_series_request_count == 13
    assert configuration.request_policy.series_hard_request_cap == 45
    assert configuration.request_policy.development_panel_pair_count == 5
    assert configuration.request_policy.require_development_panel_pass_before_batch is True


def test_openai_gpt_5_4_mini_dynamic_schema_configuration_rejects_series_overrun() -> None:
    configuration = load_expansion_l3_configuration(
        REPOSITORY_ROOT, OPENAI_GPT_5_4_MINI_DYNAMIC_SCHEMA_CONFIG_PATH
    )
    payload = configuration.model_dump(mode="python")
    request_policy = cast(dict[str, object], payload["request_policy"])
    request_policy["hard_request_cap"] = 33

    with pytest.raises(ValueError, match="series request cap"):
        ExpansionL3Configuration.model_validate(payload)


def test_openai_gpt_5_4_mini_dynamic_schema_configuration_requires_panel_gate() -> None:
    configuration = load_expansion_l3_configuration(
        REPOSITORY_ROOT, OPENAI_GPT_5_4_MINI_DYNAMIC_SCHEMA_CONFIG_PATH
    )
    payload = configuration.model_dump(mode="python")
    request_policy = cast(dict[str, object], payload["request_policy"])
    request_policy["require_development_panel_pass_before_batch"] = False
    request_policy["development_panel_pair_count"] = 0

    with pytest.raises(ValueError, match="dynamic-schema panel"):
        ExpansionL3Configuration.model_validate(payload)


def test_openai_role_calibrated_configuration_freezes_mapping_and_request_series() -> None:
    configuration = load_expansion_l3_configuration(
        REPOSITORY_ROOT, OPENAI_GPT_5_4_MINI_ROLE_CALIBRATED_CONFIG_PATH
    )
    previous = load_expansion_l3_configuration(
        REPOSITORY_ROOT, OPENAI_GPT_5_4_MINI_DYNAMIC_SCHEMA_CONFIG_PATH
    )

    assert configuration.experiment_version == "27.0.0"
    assert configuration.prompt_version == "l3-evidence-rubric-v11"
    assert configuration.l3_score_mapping_version == "l3-deterministic-level-mapping-v1"
    assert configuration.model_identifier == previous.model_identifier
    assert configuration.primary_pair_ids == previous.primary_pair_ids
    assert configuration.stability == previous.stability
    assert configuration.request_policy.hard_request_cap == 32
    assert configuration.request_policy.prior_series_request_count == 18
    assert configuration.request_policy.series_hard_request_cap == 50
    assert configuration.request_policy.development_panel_pair_count == 5
    assert configuration.request_policy.require_development_panel_pass_before_batch is True


def test_openai_role_calibrated_configuration_rejects_legacy_score_mapping() -> None:
    configuration = load_expansion_l3_configuration(
        REPOSITORY_ROOT, OPENAI_GPT_5_4_MINI_ROLE_CALIBRATED_CONFIG_PATH
    )
    payload = configuration.model_dump(mode="python")
    payload["l3_score_mapping_version"] = "provider-weighted-points-v1"

    with pytest.raises(ValueError, match="score mapping version"):
        ExpansionL3Configuration.model_validate(payload)


def test_openai_requirement_guarded_configuration_preserves_quality_gates() -> None:
    configuration = load_expansion_l3_configuration(
        REPOSITORY_ROOT, OPENAI_GPT_5_4_MINI_REQUIREMENT_GUARDED_CONFIG_PATH
    )
    previous = load_expansion_l3_configuration(
        REPOSITORY_ROOT, OPENAI_GPT_5_4_MINI_ROLE_CALIBRATED_CONFIG_PATH
    )

    assert configuration.experiment_version == "28.0.0"
    assert configuration.prompt_version == "l3-evidence-rubric-v12"
    assert configuration.l3_score_mapping_version == previous.l3_score_mapping_version
    assert configuration.quality_policy == previous.quality_policy
    assert configuration.primary_pair_ids == previous.primary_pair_ids
    assert configuration.stability == previous.stability
    assert configuration.request_policy.hard_request_cap == 32
    assert configuration.request_policy.prior_series_request_count == 23
    assert configuration.request_policy.series_hard_request_cap == 55
    assert configuration.request_policy.development_panel_pair_count == 5
    assert configuration.request_policy.require_development_panel_pass_before_batch is True


def test_openai_safety_gated_configuration_allows_only_conservative_status_error() -> None:
    configuration = load_expansion_l3_configuration(
        REPOSITORY_ROOT, OPENAI_GPT_5_4_MINI_SAFETY_GATED_CONFIG_PATH
    )
    previous = load_expansion_l3_configuration(
        REPOSITORY_ROOT, OPENAI_GPT_5_4_MINI_REQUIREMENT_GUARDED_CONFIG_PATH
    )

    assert configuration.experiment_version == "29.0.0"
    assert configuration.prompt_version == previous.prompt_version
    assert configuration.l3_score_mapping_version == previous.l3_score_mapping_version
    assert configuration.request_policy == previous.request_policy
    assert configuration.quality_policy.required_requirement_status_match_rate == Decimal("0.95")
    assert configuration.quality_policy.maximum_unsafe_requirement_status_mismatch_count == 0
    assert configuration.quality_policy.maximum_total_score_mean_absolute_error == Decimal("12")


@pytest.mark.parametrize(
    ("human_status", "model_status", "expected"),
    [
        (EvidenceStatus.SATISFIED, EvidenceStatus.CONFLICTING, False),
        (EvidenceStatus.UNSATISFIED, EvidenceStatus.MISSING, False),
        (EvidenceStatus.MISSING, EvidenceStatus.SATISFIED, True),
        (EvidenceStatus.CONFLICTING, EvidenceStatus.UNSATISFIED, True),
        (EvidenceStatus.SATISFIED, EvidenceStatus.SATISFIED, False),
    ],
)
def test_requirement_status_safety_classification(
    human_status: EvidenceStatus,
    model_status: EvidenceStatus,
    expected: bool,
) -> None:
    assert _is_unsafe_requirement_status_mismatch(human_status, model_status) is expected


def test_evaluation_policy_cache_migration_rejects_request_or_prompt_changes(
    tmp_path: Path,
) -> None:
    source_configuration = load_expansion_l3_configuration(
        REPOSITORY_ROOT, OPENAI_GPT_5_4_MINI_REQUIREMENT_GUARDED_CONFIG_PATH
    )
    source_cache_path = tmp_path / "source.json"
    target_cache_path = tmp_path / "target.json"
    _write_cache(
        REPOSITORY_ROOT,
        source_cache_path,
        _empty_cache(
            REPOSITORY_ROOT,
            source_configuration,
            OPENAI_GPT_5_4_MINI_REQUIREMENT_GUARDED_CONFIG_PATH,
        ),
    )

    migrated = migrate_evaluation_policy_cache(
        REPOSITORY_ROOT,
        OPENAI_GPT_5_4_MINI_REQUIREMENT_GUARDED_CONFIG_PATH,
        OPENAI_GPT_5_4_MINI_SAFETY_GATED_CONFIG_PATH,
        source_cache_path,
        target_cache_path,
    )

    assert migrated.experiment_id.endswith("v7")
    assert migrated.total_request_count == 0
    assert target_cache_path.exists()

    hybrid_cache_path = tmp_path / "hybrid.json"
    hybrid_migrated = migrate_evaluation_policy_cache(
        REPOSITORY_ROOT,
        OPENAI_GPT_5_4_MINI_SAFETY_GATED_CONFIG_PATH,
        OPENAI_GPT_5_4_MINI_HYBRID_TUNED_CONFIG_PATH,
        target_cache_path,
        hybrid_cache_path,
    )
    assert hybrid_migrated.experiment_id.endswith("v8")
    assert hybrid_migrated.total_request_count == 0

    with pytest.raises(ExpansionL3ValidationError, match="permits only"):
        migrate_evaluation_policy_cache(
            REPOSITORY_ROOT,
            OPENAI_GPT_5_4_MINI_ROLE_CALIBRATED_CONFIG_PATH,
            OPENAI_GPT_5_4_MINI_SAFETY_GATED_CONFIG_PATH,
            source_cache_path,
            target_cache_path,
        )


def test_openai_hybrid_tuned_configuration_is_candidate_protective() -> None:
    configuration = load_expansion_l3_configuration(
        REPOSITORY_ROOT, OPENAI_GPT_5_4_MINI_HYBRID_TUNED_CONFIG_PATH
    )
    previous = load_expansion_l3_configuration(
        REPOSITORY_ROOT, OPENAI_GPT_5_4_MINI_SAFETY_GATED_CONFIG_PATH
    )
    hybrid = configuration.hybrid_policy

    assert hybrid is not None
    assert configuration.experiment_version == "30.0.0"
    assert configuration.prompt_version == previous.prompt_version
    assert configuration.request_policy == previous.request_policy
    assert configuration.quality_policy.required_stability_requirement_agreement_rate == Decimal(
        "0.8"
    )
    assert (
        configuration.quality_policy.required_stability_requirement_route_agreement_rate
        == Decimal("1")
    )
    assert hybrid.candidate_id == "openai-role-calibrated-hybrid-v1"
    assert hybrid.l2_candidate_id == configuration.l2_candidate_id
    assert hybrid.aggregation.l1_deterministic_rules == Decimal("0.40")
    assert hybrid.aggregation.l2_section_semantic_matching == Decimal("0.20")
    assert hybrid.aggregation.l3_evidence_grounded_reasoning == Decimal("0.40")
    assert hybrid.thresholds.waitlist_minimum == Decimal("70")
    assert hybrid.thresholds.pass_minimum == Decimal("85")
    assert hybrid.disagreement_points == Decimal("35")


@pytest.mark.asyncio
async def test_openai_dynamic_schema_panel_failure_blocks_the_remaining_batch(
    tmp_path: Path,
) -> None:
    annotations = _annotations(OPENAI_GPT_5_4_MINI_DYNAMIC_SCHEMA_CONFIG_PATH)
    cache_path = tmp_path / "panel-failed.json"
    panel_adapter = EndpointOutputAdapter(
        annotations,
        model_identifier="gpt-5.4-mini-2026-03-17",
        provider_identifier="openai",
    )
    progress = await collect_live_outputs(
        REPOSITORY_ROOT,
        panel_adapter,
        cache_path=cache_path,
        configuration_path=OPENAI_GPT_5_4_MINI_DYNAMIC_SCHEMA_CONFIG_PATH,
        maximum_new_requests=25,
        request_interval_seconds=4,
        sleep=_no_sleep,
    )
    blocked_adapter = EndpointOutputAdapter(
        annotations,
        model_identifier="gpt-5.4-mini-2026-03-17",
        provider_identifier="openai",
    )
    blocked_progress = await collect_live_outputs(
        REPOSITORY_ROOT,
        blocked_adapter,
        cache_path=cache_path,
        configuration_path=OPENAI_GPT_5_4_MINI_DYNAMIC_SCHEMA_CONFIG_PATH,
        maximum_new_requests=1,
        request_interval_seconds=4,
        sleep=_no_sleep,
    )

    panel = cast(dict[str, object], progress["development_panel"])
    assert panel_adapter.call_count == 5
    assert blocked_adapter.call_count == 0
    assert panel["complete"] is True
    assert panel["passed"] is False
    assert progress["quality_failure_terminal"] is True
    assert blocked_progress["total_http_request_count"] == 5


@pytest.mark.asyncio
async def test_openai_runtime_adapter_accepts_only_the_official_base_url() -> None:
    configuration = load_expansion_l3_configuration(
        REPOSITORY_ROOT, OPENAI_GPT_5_4_MINI_VALIDATED_CONFIG_PATH
    )
    settings = RuntimeSettings(
        _env_file=None,
        classifier_llm_adapter="environment_configured",
        classifier_llm_provider="openai",
        classifier_llm_model="gpt-5.4-mini-2026-03-17",
        classifier_llm_api_key="private-test-value",
        classifier_llm_base_url="https://api.openai.com/v1",
    )
    async with httpx.AsyncClient() as client:
        adapter = _configured_adapter(settings, configuration, client)
        assert adapter is not None

        invalid_settings = settings.model_copy(
            update={"classifier_llm_base_url": "https://openrouter.ai/api/v1"}
        )
        with pytest.raises(ExpansionL3ValidationError, match="does not match provider"):
            _configured_adapter(invalid_settings, configuration, client)


@pytest.mark.asyncio
async def test_openai_report_estimates_observed_usage_charge_and_excludes_held_out(
    tmp_path: Path,
) -> None:
    annotations = _annotations(OPENAI_GPT_5_4_MINI_DYNAMIC_SCHEMA_CONFIG_PATH)
    adapter = ReviewedOutputAdapter(
        annotations,
        model_identifier="gpt-5.4-mini-2026-03-17",
        provider_identifier="openai",
    )
    report = await run_live_validation(
        REPOSITORY_ROOT,
        GENERATED_AT,
        adapter,
        cache_path=tmp_path / "openai-complete.json",
        configuration_path=OPENAI_GPT_5_4_MINI_DYNAMIC_SCHEMA_CONFIG_PATH,
        request_interval_seconds=4,
        sleep=_no_sleep,
        embedding_runtime=_embedding_runtime(),
    )
    serialized = json.dumps(report)
    configuration = load_expansion_l3_configuration(
        REPOSITORY_ROOT, OPENAI_GPT_5_4_MINI_DYNAMIC_SCHEMA_CONFIG_PATH
    )
    _, _, _, _, split = _selected_annotations(REPOSITORY_ROOT, configuration)
    request_accounting = cast(dict[str, object], report["request_accounting"])
    cost_control = cast(dict[str, object], request_accounting["cost_control"])

    assert adapter.call_count == 30
    assert report["report_scope"] == "silver-development-openai-live-l3"
    assert request_accounting["estimated_provider_charge_usd"] == pytest.approx(0.018)
    assert request_accounting["hard_request_cap"] == 32
    assert request_accounting["prior_series_request_count"] == 13
    assert request_accounting["series_hard_request_cap"] == 45
    assert request_accounting["cumulative_series_request_count"] == 43
    assert cost_control["worst_case_estimated_experiment_cost_usd"] == pytest.approx(0.877824)
    assert cost_control["requests_without_priced_usage"] == 0
    assert all(pair_id not in serialized for pair_id in split.held_out.pair_ids)


@pytest.mark.asyncio
async def test_google_ai_studio_report_is_provider_specific_and_excludes_held_out(
    tmp_path: Path,
) -> None:
    annotations = _annotations(GOOGLE_AI_STUDIO_CONFIG_PATH)
    adapter = ReviewedOutputAdapter(
        annotations,
        model_identifier="gemini-3.5-flash-lite",
        provider_identifier="google_ai_studio",
    )
    report = await run_live_validation(
        REPOSITORY_ROOT,
        GENERATED_AT,
        adapter,
        cache_path=tmp_path / "google-complete.json",
        configuration_path=GOOGLE_AI_STUDIO_CONFIG_PATH,
        request_interval_seconds=6,
        sleep=_no_sleep,
        embedding_runtime=_embedding_runtime(),
    )
    serialized = json.dumps(report)
    configuration = load_expansion_l3_configuration(REPOSITORY_ROOT, GOOGLE_AI_STUDIO_CONFIG_PATH)
    _, _, _, _, split = _selected_annotations(REPOSITORY_ROOT, configuration)
    request_accounting = cast(dict[str, object], report["request_accounting"])

    assert adapter.call_count == 30
    assert report["report_scope"] == "silver-development-google_ai_studio-live-l3"
    assert report["quality_gate_passed"] is True
    assert request_accounting["hard_request_cap"] == 35
    assert request_accounting["minimum_request_interval_seconds"] == 6
    assert request_accounting["request_timeout_seconds"] == 60
    assert request_accounting["include_temperature_parameter"] is False
    assert all(pair_id not in serialized for pair_id in split.held_out.pair_ids)


@pytest.mark.asyncio
async def test_openrouter_l3_collector_resumes_without_repeating_valid_requests(
    tmp_path: Path,
) -> None:
    cache_path = tmp_path / "resume.json"
    first = ReviewedOutputAdapter(_annotations())
    first_progress = await collect_live_outputs(
        REPOSITORY_ROOT,
        first,
        cache_path,
        maximum_new_requests=1,
        request_interval_seconds=4,
        sleep=_no_sleep,
    )
    second = ReviewedOutputAdapter(_annotations())
    second_progress = await collect_live_outputs(
        REPOSITORY_ROOT,
        second,
        cache_path,
        maximum_new_requests=4,
        request_interval_seconds=4,
        sleep=_no_sleep,
    )

    assert first.call_count == 1
    assert second.call_count == 4
    assert first_progress["cached_valid_attempt_count"] == 1
    assert second_progress["cached_valid_attempt_count"] == 5
    assert second_progress["total_http_request_count"] == 5
    assert second_progress["remaining_request_budget"] == 35


@pytest.mark.asyncio
async def test_openrouter_l3_invalid_output_is_audited_then_retried_once(
    tmp_path: Path,
) -> None:
    cache_path = tmp_path / "invalid.json"
    invalid = ReviewedOutputAdapter(_annotations(), invalid_call_numbers=frozenset({1}))
    invalid_progress = await collect_live_outputs(
        REPOSITORY_ROOT,
        invalid,
        cache_path,
        maximum_new_requests=1,
        request_interval_seconds=4,
        sleep=_no_sleep,
    )
    valid = ReviewedOutputAdapter(_annotations())
    valid_progress = await collect_live_outputs(
        REPOSITORY_ROOT,
        valid,
        cache_path,
        maximum_new_requests=1,
        request_interval_seconds=4,
        sleep=_no_sleep,
    )

    assert invalid_progress["cached_valid_attempt_count"] == 0
    assert invalid_progress["failed_request_count"] == 1
    assert valid_progress["cached_valid_attempt_count"] == 1
    assert valid_progress["failed_request_count"] == 1
    assert valid_progress["total_http_request_count"] == 2


@pytest.mark.asyncio
async def test_openrouter_l3_collector_stops_after_unrecoverable_primary_failure(
    tmp_path: Path,
) -> None:
    cache_path = tmp_path / "invalid-exhausted.json"
    adapter = ReviewedOutputAdapter(
        _annotations(),
        invalid_call_numbers=frozenset({1, 2}),
    )

    for _ in range(3):
        progress = await collect_live_outputs(
            REPOSITORY_ROOT,
            adapter,
            cache_path,
            maximum_new_requests=1,
            request_interval_seconds=4,
            sleep=_no_sleep,
        )

    assert adapter.call_count == 2
    assert progress["cached_valid_attempt_count"] == 0
    assert progress["failed_request_count"] == 2
    assert progress["total_http_request_count"] == 2
    assert progress["quality_failure_terminal"] is True


def test_l3_request_budget_shortfall_is_a_terminal_quality_failure() -> None:
    configuration = load_expansion_l3_configuration(
        REPOSITORY_ROOT, GOOGLE_AI_STUDIO_EXACT_NEGATIVE_CONFIG_PATH
    )
    annotations = _annotations(GOOGLE_AI_STUDIO_EXACT_NEGATIVE_CONFIG_PATH)
    cache = _empty_cache(
        REPOSITORY_ROOT,
        configuration,
        GOOGLE_AI_STUDIO_EXACT_NEGATIVE_CONFIG_PATH,
    )
    first_pair_id = annotations[0].pair_id
    cache = cache.model_copy(
        update={
            "failures": {
                first_pair_id: (
                    ExpansionL3CachedFailure(
                        intended_attempt_number=1,
                        duration_milliseconds=1,
                        status=LLMProviderStatus.INVALID,
                        reason="LLM provider output failed schema validation (root:value_error).",
                    ),
                )
            }
        }
    )
    constrained_configuration = configuration.model_copy(
        update={
            "request_policy": configuration.request_policy.model_copy(
                update={"hard_request_cap": 30}
            )
        }
    )

    assert _primary_quality_is_unrecoverable(cache, constrained_configuration, annotations) is True
    assert "hard request budget" in cast(
        str,
        _primary_quality_failure_reason(cache, constrained_configuration, annotations),
    )


@pytest.mark.asyncio
async def test_l3_invalid_stability_repeat_is_terminal_after_retry_exhaustion(
    tmp_path: Path,
) -> None:
    cache_path = tmp_path / "invalid-stability-repeat.json"
    annotations = _annotations(GOOGLE_AI_STUDIO_EXACT_NEGATIVE_CONFIG_PATH)
    first = ReviewedOutputAdapter(
        annotations,
        invalid_call_numbers=frozenset({26}),
        model_identifier="gemini-3.5-flash-lite",
        provider_identifier="google_ai_studio",
    )
    first_progress = await collect_live_outputs(
        REPOSITORY_ROOT,
        first,
        cache_path,
        configuration_path=GOOGLE_AI_STUDIO_EXACT_NEGATIVE_CONFIG_PATH,
        maximum_new_requests=26,
        request_interval_seconds=6,
        sleep=_no_sleep,
    )
    retry = ReviewedOutputAdapter(
        annotations,
        invalid_call_numbers=frozenset({1}),
        model_identifier="gemini-3.5-flash-lite",
        provider_identifier="google_ai_studio",
    )
    terminal_progress = await collect_live_outputs(
        REPOSITORY_ROOT,
        retry,
        cache_path,
        configuration_path=GOOGLE_AI_STUDIO_EXACT_NEGATIVE_CONFIG_PATH,
        maximum_new_requests=1,
        request_interval_seconds=6,
        sleep=_no_sleep,
    )
    no_more_requests = ReviewedOutputAdapter(
        annotations,
        model_identifier="gemini-3.5-flash-lite",
        provider_identifier="google_ai_studio",
    )
    repeated_progress = await collect_live_outputs(
        REPOSITORY_ROOT,
        no_more_requests,
        cache_path,
        configuration_path=GOOGLE_AI_STUDIO_EXACT_NEGATIVE_CONFIG_PATH,
        maximum_new_requests=1,
        request_interval_seconds=6,
        sleep=_no_sleep,
    )

    assert first.call_count == 26
    assert first_progress["cached_valid_attempt_count"] == 25
    assert retry.call_count == 1
    assert terminal_progress["quality_failure_terminal"] is True
    assert terminal_progress["failed_request_count"] == 2
    assert no_more_requests.call_count == 0
    assert repeated_progress["total_http_request_count"] == 27


@pytest.mark.asyncio
async def test_openrouter_l3_terminal_quality_failure_produces_partial_report(
    tmp_path: Path,
) -> None:
    cache_path = tmp_path / "terminal-failure.json"
    adapter = ReviewedOutputAdapter(
        _annotations(),
        invalid_call_numbers=frozenset({1, 2}),
    )
    for _ in range(2):
        await collect_live_outputs(
            REPOSITORY_ROOT,
            adapter,
            cache_path,
            maximum_new_requests=1,
            request_interval_seconds=4,
            sleep=_no_sleep,
        )

    report = await run_live_validation(
        REPOSITORY_ROOT,
        GENERATED_AT,
        adapter,
        cache_path=cache_path,
        request_interval_seconds=4,
        sleep=_no_sleep,
    )
    provider_quality = cast(dict[str, object], report["provider_quality"])
    hybrid = cast(dict[str, object], report["hybrid_diagnostic"])

    assert adapter.call_count == 2
    assert report["experiment_status"] == "stopped_quality_failure"
    assert report["quality_gate_passed"] is False
    assert provider_quality["valid_output_rate"] == 0
    assert provider_quality["attempted_pair_count"] == 1
    assert provider_quality["valid_output_rate_among_attempted_pairs"] == 0
    assert hybrid["executed"] is False


@pytest.mark.asyncio
async def test_openrouter_l3_provider_failure_is_cached_and_stops_batch(
    tmp_path: Path,
) -> None:
    cache_path = tmp_path / "unavailable.json"
    adapter = ReviewedOutputAdapter(_annotations(), unavailable_call_numbers=frozenset({1}))

    with pytest.raises(ExpansionL3ProviderUnavailable, match="outage"):
        await collect_live_outputs(
            REPOSITORY_ROOT,
            adapter,
            cache_path,
            maximum_new_requests=1,
            request_interval_seconds=4,
            sleep=_no_sleep,
        )

    cache = json.loads(cache_path.read_text(encoding="utf-8"))
    assert sum(len(items) for items in cache["failures"].values()) == 1
    assert not cache["records"]


@pytest.mark.asyncio
async def test_openrouter_l3_provider_unavailable_retry_limit_is_terminal(
    tmp_path: Path,
) -> None:
    cache_path = tmp_path / "unavailable-terminal.json"
    adapter = ReviewedOutputAdapter(_annotations(), unavailable_call_numbers=frozenset({1, 2, 3}))

    with pytest.raises(ExpansionL3ProviderUnavailable, match="outage"):
        await collect_live_outputs(
            REPOSITORY_ROOT,
            adapter,
            cache_path,
            maximum_new_requests=1,
            request_interval_seconds=4,
            sleep=_no_sleep,
        )
    progress = await collect_live_outputs(
        REPOSITORY_ROOT,
        adapter,
        cache_path,
        maximum_new_requests=1,
        request_interval_seconds=4,
        sleep=_no_sleep,
    )
    repeated_progress = await collect_live_outputs(
        REPOSITORY_ROOT,
        adapter,
        cache_path,
        maximum_new_requests=1,
        request_interval_seconds=4,
        sleep=_no_sleep,
    )
    report = await run_live_validation(
        REPOSITORY_ROOT,
        GENERATED_AT,
        adapter,
        cache_path=cache_path,
        request_interval_seconds=4,
        sleep=_no_sleep,
    )

    assert adapter.call_count == 2
    assert progress["provider_failure_terminal"] is True
    assert repeated_progress["total_http_request_count"] == 2
    assert report["experiment_status"] == "stopped_provider_unavailable"
    assert report["quality_gate_passed"] is False


@pytest.mark.asyncio
async def test_openrouter_l3_hard_cap_blocks_every_additional_request(
    tmp_path: Path,
) -> None:
    configuration = load_expansion_l3_configuration(REPOSITORY_ROOT)
    cache_path = tmp_path / "cap.json"
    pair_id = configuration.primary_pair_ids[0]
    failure = ExpansionL3CachedFailure(
        intended_attempt_number=1,
        duration_milliseconds=1,
        status=LLMProviderStatus.UNAVAILABLE,
        reason="Synthetic capacity failure.",
    )
    cache = _empty_cache(REPOSITORY_ROOT, configuration).model_copy(
        update={"failures": {pair_id: (failure,) * 40}}
    )
    _write_cache(REPOSITORY_ROOT, cache_path, cache)
    adapter = ReviewedOutputAdapter(_annotations())

    with pytest.raises(ExpansionL3RequestCapReached, match="cap"):
        await collect_live_outputs(
            REPOSITORY_ROOT,
            adapter,
            cache_path,
            maximum_new_requests=1,
            request_interval_seconds=4,
            sleep=_no_sleep,
        )

    assert adapter.call_count == 0


@pytest.mark.asyncio
async def test_openrouter_l3_report_is_traceable_and_excludes_held_out_and_secrets(
    tmp_path: Path,
) -> None:
    annotations = _annotations()
    adapter = ReviewedOutputAdapter(annotations)
    report = await run_live_validation(
        REPOSITORY_ROOT,
        GENERATED_AT,
        adapter,
        cache_path=tmp_path / "complete.json",
        request_interval_seconds=4,
        sleep=_no_sleep,
        embedding_runtime=_embedding_runtime(),
    )
    configuration = load_expansion_l3_configuration(REPOSITORY_ROOT)
    _, _, _, _, split = _selected_annotations(REPOSITORY_ROOT, configuration)
    serialized = json.dumps(report)
    provider_quality = cast(dict[str, object], report["provider_quality"])
    stability = cast(dict[str, object], report["stability"])
    hybrid = cast(dict[str, object], report["hybrid_diagnostic"])
    hybrid_cases = cast(list[dict[str, object]], hybrid["cases"])

    assert adapter.call_count == 30
    assert report["is_final_performance"] is False
    assert report["quality_gate_passed"] is True
    assert report["configuration_freeze_eligible"] is False
    assert provider_quality["sample_count"] == 25
    assert provider_quality["attempted_pair_count"] == 25
    assert provider_quality["requirement_status_match_rate"] == 1
    assert stability["case_count"] == 5
    assert stability["passes_stability_policy"] is True
    assert len(hybrid_cases) == 25
    assert not {case["pair_id"] for case in hybrid_cases}.intersection(split.held_out.pair_ids)
    assert all(pair_id not in serialized for pair_id in split.held_out.pair_ids)
    assert "sk-or-v1" not in serialized
