from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
from typing import Any, cast

import httpx
import pytest

from backend.app.agents.classifier.prompts import (
    AUTHORITATIVE_REQUIREMENTS_PROMPT_VERSION,
    CONFLICT_AUDITED_PROMPT_VERSION,
    CRITERION_STATUS_PROMPT_VERSION,
    ANCHORED_PROMPT_VERSION,
    CALIBRATED_PROMPT_VERSION,
    HARD_SCOPED_PROMPT_VERSION,
    GPT_5_4_MINI_PROMPT_VERSION,
    LIVE_PROMPT_VERSION,
    PROMPT_VERSION,
    REQUIREMENT_GUARDED_PROMPT_VERSION,
    ROLE_CALIBRATED_PROMPT_VERSION,
    SCOPED_PROMPT_VERSION,
    STRICT_SCOPED_PROMPT_VERSION,
    VALIDATED_PROMPT_VERSION,
    build_l3_messages,
)
from backend.app.contracts import (
    CVProfile,
    Evidence,
    EvidenceLocation,
    EvidenceSection,
    EvidenceSourceType,
    EvidenceStatus,
    LevelScoreStatus,
)
from backend.app.agents.classifier.scoring.l3 import L3ProviderRequest, score_l3
from backend.app.agents.classifier.scoring.l3_calibration import L3CalibrationLevel
from backend.app.domain import RequirementAssessment
from backend.app.infrastructure.config import RepositoryConfigurationLoader
from backend.app.infrastructure.llm import (
    CoreL3ProviderBridge,
    DeterministicCoreL3Provider,
    DeterministicFakeLLMAdapter,
    InvalidLLMAdapter,
    InvalidCoreL3Provider,
    LLMConfigurationError,
    LLMProviderStatus,
    LLMQualitativeAssessmentOutput,
    LLMQualitativeCriterionAssessment,
    LLMRequirementAssessment,
    LLMRequirementReference,
    LLMScoringOutput,
    LLMScoringRequest,
    LLMWeightedCriterionAssessment,
    OpenAICompatibleLLMAdapter,
    UnavailableCoreL3Provider,
    UnavailableLLMAdapter,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def valid_request() -> LLMScoringRequest:
    loaded = RepositoryConfigurationLoader(REPOSITORY_ROOT).load_for_job("junior-data-analyst-v1")
    return LLMScoringRequest(
        request_id="request-l3-test",
        job_profile=loaded.job_profile,
        rubric=loaded.rubric,
        evidence=(
            Evidence(
                evidence_id="ev-l3-test",
                source_type=EvidenceSourceType.PARSER,
                section=EvidenceSection.PROJECTS,
                text="Dự án dùng SQL và Python để phân tích dữ liệu.",
                location=EvidenceLocation(source_record_id="record-l3-test"),
            ),
        ),
        prompt_version=PROMPT_VERSION,
    )


def valid_output() -> LLMScoringOutput:
    scores = {
        "mandatory-requirements": Decimal("30"),
        "technical-analysis": Decimal("20"),
        "analytical-reasoning": Decimal("15"),
        "projects-and-impact": Decimal("10"),
        "communication-and-evidence-quality": Decimal("5"),
    }
    return LLMScoringOutput(
        overall_score=Decimal("80"),
        requirement_assessments=tuple(
            LLMRequirementAssessment(
                requirement_id=requirement_id,
                evidence_status=EvidenceStatus.SATISFIED,
                evidence_ids=("ev-l3-test",),
                rationale="Thông tin được cung cấp hỗ trợ yêu cầu bắt buộc.",
            )
            for requirement_id in (
                "da-sql",
                "da-analysis-language",
                "da-analytical-project",
            )
        ),
        criterion_assessments=tuple(
            LLMWeightedCriterionAssessment(
                criterion_id=criterion_id,
                score=score,
                evidence_status=EvidenceStatus.SATISFIED,
                evidence_ids=("ev-l3-test",),
                rationale="Thông tin được cung cấp hỗ trợ điểm tiêu chí.",
            )
            for criterion_id, score in scores.items()
        ),
        strengths=("Có dự án liên quan.",),
        risks=("Chiều sâu chưa được xác minh độc lập.",),
        warnings=(),
        confidence=Decimal("0.80"),
    )


def qualitative_output(request: LLMScoringRequest) -> LLMQualitativeAssessmentOutput:
    return LLMQualitativeAssessmentOutput(
        requirement_assessments=tuple(
            LLMRequirementAssessment(
                requirement_id=requirement_id,
                evidence_status=EvidenceStatus.SATISFIED,
                evidence_ids=("ev-l3-test",),
                rationale="Thông tin trực tiếp hỗ trợ yêu cầu.",
            )
            for requirement_id in request.rubric.critical_requirement_ids
        ),
        criterion_assessments=tuple(
            LLMQualitativeCriterionAssessment(
                criterion_id=item.criterion_id,
                calibration_level=L3CalibrationLevel.DEVELOPING,
                evidence_status=EvidenceStatus.SATISFIED,
                evidence_ids=("ev-l3-test",),
                rationale="Thông tin thể hiện mức đang phát triển.",
            )
            for item in request.rubric.criteria
        ),
        strengths=("Có thông tin thực hành liên quan.",),
        risks=("Một số chiều sâu chưa được kiểm chứng.",),
        confidence=Decimal("0.80"),
    )


def test_live_prompt_serializes_exact_dynamic_output_constraints_without_labels() -> None:
    request = valid_request()
    messages = build_l3_messages(
        request.job_profile,
        request.rubric,
        request.evidence,
        LIVE_PROMPT_VERSION,
    )
    payload = json.loads(messages[1]["content"])
    constraints = cast(dict[str, object], payload["output_constraints"])
    criteria = cast(list[dict[str, object]], constraints["criteria_exactly"])

    assert constraints["requirement_ids_exactly"] == list(request.rubric.critical_requirement_ids)
    assert [item["criterion_id"] for item in criteria] == [
        item.criterion_id for item in request.rubric.criteria
    ]
    assert constraints["allowed_evidence_ids"] == ["ev-l3-test"]
    status_rules = cast(dict[str, str], constraints["evidence_status_rules"])
    assert "must be empty" in status_rules["missing"]
    assert "at least two distinct" in status_rules["conflicting"]
    anchored_messages = build_l3_messages(
        request.job_profile,
        request.rubric,
        request.evidence,
        ANCHORED_PROMPT_VERSION,
    )
    anchored_payload = json.loads(anchored_messages[1]["content"])
    anchored_constraints = cast(dict[str, object], anchored_payload["output_constraints"])
    scoring_anchors = cast(dict[str, str], anchored_constraints["scoring_anchors"])
    assert set(scoring_anchors) == {"0.00", "0.25", "0.50", "0.70", "0.85", "1.00"}
    assert "verifiability" in scoring_anchors["1.00"]
    serialized = json.dumps(anchored_payload, ensure_ascii=False)
    assert "draft_label" not in serialized
    assert "final_label" not in serialized

    calibrated_messages = build_l3_messages(
        request.job_profile,
        request.rubric,
        request.evidence,
        CALIBRATED_PROMPT_VERSION,
    )
    calibrated_payload = json.loads(calibrated_messages[1]["content"])
    calibrated_constraints = cast(dict[str, object], calibrated_payload["output_constraints"])
    requirement_rules = cast(dict[str, str], calibrated_constraints["requirement_decision_rules"])
    calibration_protocol = cast(dict[str, object], calibrated_constraints["calibration_protocol"])
    criterion_caps = cast(
        dict[str, dict[str, str]], calibration_protocol["criterion_specific_caps"]
    )
    score_bands = cast(dict[str, str], calibration_protocol["overall_score_bands"])

    assert "coursework" in requirement_rules["satisfied"]
    assert "does not override" in requirement_rules["unsatisfied"]
    assert "0.35" in criterion_caps["mandatory_requirements"]["any_unsatisfied"]
    assert (
        "0.67"
        in criterion_caps["mandatory_requirements"][
            "any_missing_without_unsatisfied_or_conflicting"
        ]
    )
    assert "0.55" in criterion_caps["projects_and_impact"]["project_without_clear_outcome"]
    assert set(score_bands) == {"90-100", "75-89", "60-74", "40-59", "0-39"}
    calibrated_serialized = json.dumps(calibrated_payload, ensure_ascii=False)
    assert "draft_label" not in calibrated_serialized
    assert "final_label" not in calibrated_serialized

    role_messages = build_l3_messages(
        request.job_profile,
        request.rubric,
        request.evidence,
        ROLE_CALIBRATED_PROMPT_VERSION,
    )
    role_payload = json.loads(role_messages[1]["content"])
    role_constraints = cast(dict[str, object], role_payload["output_constraints"])
    qualitative = cast(dict[str, object], role_constraints["qualitative_calibration"])
    role_profile = cast(dict[str, str], qualitative["role_calibration_profile"])

    assert qualitative["mapping_version"] == "l3-deterministic-level-mapping-v1"
    assert "SQL" in role_profile["technical_specialization"]
    assert "calibration_protocol" not in role_constraints
    assert "Do not produce numeric criterion scores" in role_messages[0]["content"]
    assert "draft_label" not in json.dumps(role_payload, ensure_ascii=False)

    guarded_messages = build_l3_messages(
        request.job_profile,
        request.rubric,
        request.evidence,
        REQUIREMENT_GUARDED_PROMPT_VERSION,
    )
    guarded_payload = json.loads(guarded_messages[1]["content"])
    guarded_constraints = cast(dict[str, object], guarded_payload["output_constraints"])
    capability_guards = cast(dict[str, str], guarded_constraints["requirement_capability_guards"])

    assert "Python or R" in capability_guards["language_boundary"]
    assert "exact capability boundaries" in guarded_messages[0]["content"]
    assert "requirement_status_algorithm" in guarded_constraints
    assert "hard_requirement_invariants" in guarded_constraints

    audited_messages = build_l3_messages(
        request.job_profile,
        request.rubric,
        request.evidence,
        CONFLICT_AUDITED_PROMPT_VERSION,
    )
    audited_payload = json.loads(audited_messages[1]["content"])
    audited_constraints = cast(dict[str, object], audited_payload["output_constraints"])
    conflict_audit = cast(dict[str, str], audited_constraints["requirement_conflict_audit"])

    assert "every evidence item" in conflict_audit["scan_scope"]
    assert "never cancels" in conflict_audit["positive_does_not_override_negative"]
    assert "other section" in conflict_audit["other_section_rule"]
    assert "stronger" in audited_messages[0]["content"]
    assert "draft_label" not in json.dumps(audited_payload, ensure_ascii=False)

    authoritative = tuple(
        RequirementAssessment(
            requirement_id=requirement_id,
            evidence_status=EvidenceStatus.MISSING,
            evidence_ids=(),
            rationale="No deterministic positive or negative signal was found.",
        )
        for requirement_id in request.rubric.critical_requirement_ids
    )
    authoritative_messages = build_l3_messages(
        request.job_profile,
        request.rubric,
        request.evidence,
        AUTHORITATIVE_REQUIREMENTS_PROMPT_VERSION,
        authoritative,
    )
    authoritative_payload = json.loads(authoritative_messages[1]["content"])
    authoritative_constraints = cast(dict[str, object], authoritative_payload["output_constraints"])
    references = cast(
        list[dict[str, object]],
        authoritative_constraints["authoritative_requirement_assessments"],
    )

    assert {item["requirement_id"] for item in references} == set(
        request.rubric.critical_requirement_ids
    )
    assert {item["evidence_status"] for item in references} == {"missing"}
    assert "Copy those assessments exactly" in authoritative_messages[0]["content"]

    criterion_status_messages = build_l3_messages(
        request.job_profile,
        request.rubric,
        request.evidence,
        CRITERION_STATUS_PROMPT_VERSION,
        authoritative,
    )
    criterion_status_payload = json.loads(criterion_status_messages[1]["content"])
    criterion_status_constraints = cast(
        dict[str, object], criterion_status_payload["output_constraints"]
    )
    criterion_status_rule = cast(
        dict[str, str], criterion_status_constraints["criterion_evidence_status_rule"]
    )

    assert "no supplied evidence" in criterion_status_rule["missing"]
    assert "limitation" in criterion_status_rule["unsatisfied"]
    assert "still relevant criterion evidence" in criterion_status_messages[0]["content"]


@pytest.mark.asyncio
async def test_openai_authoritative_prompt_replaces_provider_requirement_statuses() -> None:
    base_request = valid_request()
    references = tuple(
        LLMRequirementReference(
            requirement_id=requirement_id,
            evidence_status=EvidenceStatus.MISSING,
            evidence_ids=(),
            rationale="The deterministic requirement engine found no direct signal.",
        )
        for requirement_id in base_request.rubric.critical_requirement_ids
    )
    request = base_request.model_copy(
        update={
            "prompt_version": AUTHORITATIVE_REQUIREMENTS_PROMPT_VERSION,
            "authoritative_requirement_assessments": references,
        }
    )

    def handler(http_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                qualitative_output(request).model_dump(mode="python"),
                                default=float,
                            )
                        }
                    }
                ]
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        adapter = OpenAICompatibleLLMAdapter(
            provider_identifier="openai",
            model_identifier="gpt-5.4-mini-2026-03-17",
            api_key="secret-test",
            base_url="https://api.openai.com/v1",
            prompt_version=AUTHORITATIVE_REQUIREMENTS_PROMPT_VERSION,
            client=client,
            include_temperature_parameter=False,
            max_completion_tokens=4096,
            reasoning_effort="none",
        )
        result = await adapter.score(request)

    assert result.status is LLMProviderStatus.AVAILABLE
    assert result.output is not None
    assert {item.evidence_status for item in result.output.requirement_assessments} == {
        EvidenceStatus.MISSING
    }
    assert all(not item.evidence_ids for item in result.output.requirement_assessments)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "prompt_version",
    [
        ROLE_CALIBRATED_PROMPT_VERSION,
        REQUIREMENT_GUARDED_PROMPT_VERSION,
        CONFLICT_AUDITED_PROMPT_VERSION,
    ],
)
async def test_openai_role_calibrated_adapter_derives_scores_from_qualitative_levels(
    prompt_version: str,
) -> None:
    request = valid_request().model_copy(update={"prompt_version": prompt_version})
    captured_payload: dict[str, object] = {}

    def handler(http_request: httpx.Request) -> httpx.Response:
        captured_payload.update(cast(dict[str, object], json.loads(http_request.content)))
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                qualitative_output(request).model_dump(mode="python"),
                                default=float,
                            )
                        }
                    }
                ]
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        adapter = OpenAICompatibleLLMAdapter(
            provider_identifier="openai",
            model_identifier="gpt-5.4-mini-2026-03-17",
            api_key="secret-test",
            base_url="https://api.openai.com/v1",
            prompt_version=prompt_version,
            client=client,
            include_temperature_parameter=False,
            max_completion_tokens=4096,
            reasoning_effort="none",
        )
        result = await adapter.score(request)

    assert result.status is LLMProviderStatus.AVAILABLE
    assert result.output is not None
    assert result.output.overall_score == Decimal("70.0")
    assert result.calibration_levels == {
        item.criterion_id: L3CalibrationLevel.DEVELOPING for item in request.rubric.criteria
    }
    assert [item.score for item in result.output.criterion_assessments] == [
        Decimal("28.0"),
        Decimal("15.0"),
        Decimal("12.0"),
        Decimal("9.0"),
        Decimal("6.0"),
    ]
    response_format = cast(dict[str, object], captured_payload["response_format"])
    json_schema = cast(dict[str, object], response_format["json_schema"])
    schema = cast(dict[str, object], json_schema["schema"])
    properties = cast(dict[str, object], schema["properties"])
    definitions = cast(dict[str, dict[str, object]], schema["$defs"])
    criterion = definitions["LLMQualitativeCriterionAssessment"]
    variants = cast(list[dict[str, object]], criterion["anyOf"])
    criterion_properties = cast(dict[str, object], variants[0]["properties"])

    assert "overall_score" not in properties
    assert "score" not in criterion_properties
    assert "calibration_level" in criterion_properties
    assert json_schema["name"] == "classifier_l3_role_calibration"


def test_scoped_prompt_limits_negative_evidence_to_the_exact_requirement() -> None:
    request = valid_request()
    messages = build_l3_messages(
        request.job_profile,
        request.rubric,
        request.evidence,
        SCOPED_PROMPT_VERSION,
    )
    payload = json.loads(messages[1]["content"])
    constraints = cast(dict[str, object], payload["output_constraints"])
    scoping_rules = cast(dict[str, str], constraints["requirement_scoping_rules"])
    serialized = json.dumps(payload, ensure_ascii=False)

    assert "independently" in scoping_rules["independent_assessment"]
    assert "exact capability" in scoping_rules["exact_negative_scope"]
    assert "criterion scores" in scoping_rules["general_limit_scope"]
    assert "calibration_protocol" in constraints
    assert "draft_label" not in serialized
    assert "final_label" not in serialized


def test_strict_scoped_prompt_uses_direct_evidence_status_algorithm() -> None:
    request = valid_request()
    messages = build_l3_messages(
        request.job_profile,
        request.rubric,
        request.evidence,
        STRICT_SCOPED_PROMPT_VERSION,
    )
    payload = json.loads(messages[1]["content"])
    constraints = cast(dict[str, object], payload["output_constraints"])
    algorithm = cast(dict[str, str], constraints["requirement_status_algorithm"])

    assert "coursework" in algorithm["context_only"]
    assert "exact named capability" in algorithm["exact_negative"]
    assert "both direct_positive and exact_negative" in algorithm["conflicting"]
    assert "never change" in algorithm["criterion_only_limits"]
    assert "requirement_scoping_rules" in constraints
    assert "calibration_protocol" in constraints


def test_hard_scoped_prompt_marks_education_as_context_only() -> None:
    request = valid_request()
    education = Evidence(
        evidence_id="ev-l3-education",
        source_type=EvidenceSourceType.PARSER,
        section=EvidenceSection.EDUCATION,
        text="Hoàn thành học phần nhập môn phân tích dữ liệu.",
        location=EvidenceLocation(source_record_id="record-l3-test"),
    )
    messages = build_l3_messages(
        request.job_profile,
        request.rubric,
        (*request.evidence, education),
        HARD_SCOPED_PROMPT_VERSION,
    )
    payload = json.loads(messages[1]["content"])
    constraints = cast(dict[str, object], payload["output_constraints"])
    invariants = cast(dict[str, str], constraints["hard_requirement_invariants"])

    assert constraints["context_only_evidence_ids"] == ["ev-l3-education"]
    assert "never use" in invariants["education"]
    assert "does not name" in invariants["unnamed_negative"]
    assert "never context_only" in invariants["evidence_ids"]


def test_gpt_5_4_mini_prompt_preserves_hard_status_rules_without_labels() -> None:
    request = valid_request()
    messages = build_l3_messages(
        request.job_profile,
        request.rubric,
        request.evidence,
        GPT_5_4_MINI_PROMPT_VERSION,
    )
    payload = json.loads(messages[1]["content"])
    constraints = cast(dict[str, object], payload["output_constraints"])
    system_prompt = messages[0]["content"]
    serialized = json.dumps(payload, ensure_ascii=False)

    assert "assess every requirement_id independently" in system_prompt
    assert "context_only" in system_prompt
    assert "Preserve missing as distinct from unsatisfied" in system_prompt
    assert "hard_requirement_invariants" in constraints
    assert "requirement_status_algorithm" in constraints
    assert "draft_label" not in serialized
    assert "final_label" not in serialized


def test_validated_prompt_requires_evidence_cardinality_and_exact_total() -> None:
    request = valid_request()
    messages = build_l3_messages(
        request.job_profile,
        request.rubric,
        request.evidence,
        VALIDATED_PROMPT_VERSION,
    )
    payload = json.loads(messages[1]["content"])
    system_prompt = messages[0]["content"]

    assert "criterion_assessments must each use every requested ID exactly once" in system_prompt
    assert "missing requires an empty evidence_ids array" in system_prompt
    assert "overall_score to that exact sum" in system_prompt
    assert "hard_requirement_invariants" in payload["output_constraints"]


@pytest.mark.asyncio
async def test_deterministic_fake_returns_repeatable_valid_output() -> None:
    request = valid_request()
    adapter = DeterministicFakeLLMAdapter(valid_output())

    first = await adapter.score(request)
    second = await adapter.score(request)

    assert first == second
    assert first.status is LLMProviderStatus.AVAILABLE
    assert first.output == valid_output()


@pytest.mark.asyncio
async def test_deterministic_fake_rejects_unknown_evidence_reference() -> None:
    output = valid_output()
    assessments = list(output.criterion_assessments)
    assessments[0] = assessments[0].model_copy(update={"evidence_ids": ("ev-unknown",)})
    invalid_output = output.model_copy(update={"criterion_assessments": tuple(assessments)})

    result = await DeterministicFakeLLMAdapter(invalid_output).score(valid_request())

    assert result.status is LLMProviderStatus.INVALID
    assert result.output is None


@pytest.mark.asyncio
async def test_openai_compatible_adapter_reports_malformed_response_envelope() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"choices": []})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        adapter = OpenAICompatibleLLMAdapter(
            "provider-test",
            "model-test",
            "secret-test",
            "https://provider.invalid/v1",
            PROMPT_VERSION,
            client,
        )
        result = await adapter.score(valid_request())

    assert result.status is LLMProviderStatus.INVALID
    assert result.reason == "LLM provider response choices were missing or empty."


@pytest.mark.asyncio
async def test_openai_compatible_adapter_reports_reasoning_only_without_leaking_text() -> None:
    sensitive_reasoning = "must-not-appear-in-envelope-diagnostics"

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {"content": None, "reasoning": sensitive_reasoning},
                        "finish_reason": "length",
                    }
                ]
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        adapter = OpenAICompatibleLLMAdapter(
            "provider-test",
            "model-test",
            "secret-test",
            "https://provider.invalid/v1",
            PROMPT_VERSION,
            client,
        )
        result = await adapter.score(valid_request())

    assert result.status is LLMProviderStatus.INVALID
    assert result.reason is not None
    assert "reasoning, finish_reason" in result.reason
    assert sensitive_reasoning not in result.reason


@pytest.mark.asyncio
async def test_openai_compatible_adapter_reports_error_envelope_without_leaking_text() -> None:
    sensitive_error = "must-not-appear-in-error-diagnostics"

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"error": {"message": sensitive_error}})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        adapter = OpenAICompatibleLLMAdapter(
            "provider-test",
            "model-test",
            "secret-test",
            "https://provider.invalid/v1",
            PROMPT_VERSION,
            client,
        )
        result = await adapter.score(valid_request())

    assert result.status is LLMProviderStatus.UNAVAILABLE
    assert result.reason == "LLM provider response contained an error object."
    assert sensitive_error not in cast(str, result.reason)


@pytest.mark.asyncio
async def test_openai_compatible_adapter_categorizes_error_without_raw_message() -> None:
    raw_message = "No endpoints found matching your data policy for private-user-value"

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"error": {"code": 404, "message": raw_message}},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        adapter = OpenAICompatibleLLMAdapter(
            "provider-test",
            "model-test",
            "secret-test",
            "https://provider.invalid/v1",
            PROMPT_VERSION,
            client,
        )
        result = await adapter.score(valid_request())

    assert result.status is LLMProviderStatus.UNAVAILABLE
    assert result.reason == (
        "LLM provider response contained an error object (no_matching_endpoint, code 404)."
    )
    assert raw_message not in cast(str, result.reason)


@pytest.mark.asyncio
async def test_openai_compatible_adapter_reports_schema_paths_without_input_values() -> None:
    sensitive_value = "must-not-appear-in-diagnostics"
    malformed = valid_output().model_dump(mode="python")
    malformed["confidence"] = sensitive_value

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": json.dumps(malformed, default=float)}}]},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        adapter = OpenAICompatibleLLMAdapter(
            "provider-test",
            "model-test",
            "secret-test",
            "https://provider.invalid/v1",
            PROMPT_VERSION,
            client,
        )
        result = await adapter.score(valid_request())

    assert result.status is LLMProviderStatus.INVALID
    assert result.reason is not None
    assert "confidence:value_error" in result.reason
    assert sensitive_value not in result.reason


@pytest.mark.asyncio
async def test_openai_compatible_adapter_reports_request_consistency_failure() -> None:
    inconsistent = valid_output().model_dump(mode="python")
    inconsistent["criterion_assessments"][0]["criterion_id"] = "unknown-criterion"

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": json.dumps(inconsistent, default=float)}}]},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        adapter = OpenAICompatibleLLMAdapter(
            "provider-test",
            "model-test",
            "secret-test",
            "https://provider.invalid/v1",
            PROMPT_VERSION,
            client,
        )
        result = await adapter.score(valid_request())

    assert result.status is LLMProviderStatus.INVALID
    assert result.reason is not None
    assert "criterion identifiers do not match the rubric" in result.reason


@pytest.mark.asyncio
async def test_deterministic_fake_rejects_prompt_version_mismatch() -> None:
    request = valid_request().model_copy(update={"prompt_version": "different-prompt-v1"})

    result = await DeterministicFakeLLMAdapter(valid_output()).score(request)

    assert result.status is LLMProviderStatus.INVALID
    assert result.output is None


@pytest.mark.asyncio
async def test_core_l3_bridge_maps_available_output_to_core_provider_shape() -> None:
    request = valid_request()
    core_request = L3ProviderRequest(
        cv_profile=CVProfile(
            cv_profile_id="cv-core-bridge",
            candidate_reference="candidate-core-bridge",
            evidence=request.evidence,
        ),
        job_profile=request.job_profile,
        rubric=request.rubric,
        prompt_version=request.prompt_version,
    )
    assessment = await score_l3(
        core_request,
        CoreL3ProviderBridge(DeterministicFakeLLMAdapter(valid_output())),
    )

    assert assessment.status is LevelScoreStatus.AVAILABLE
    assert assessment.score == Decimal("80")
    assert len(assessment.requirement_assessments) == 3


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("adapter", "status"),
    [
        (InvalidLLMAdapter(), LLMProviderStatus.INVALID),
        (UnavailableLLMAdapter(), LLMProviderStatus.UNAVAILABLE),
    ],
)
async def test_failure_fakes_return_typed_provider_status(
    adapter: InvalidLLMAdapter | UnavailableLLMAdapter,
    status: LLMProviderStatus,
) -> None:
    result = await adapter.score(valid_request())

    assert result.status is status
    assert result.output is None
    assert result.reason


@pytest.mark.asyncio
async def test_openai_compatible_adapter_sends_structured_request_and_validates_output() -> None:
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["authorization"] = request.headers["Authorization"]
        captured["payload"] = json.loads(request.content)
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                valid_output().model_dump(mode="python"),
                                default=float,
                            ),
                        }
                    }
                ],
                "usage": {
                    "prompt_tokens": 120,
                    "completion_tokens": 80,
                    "total_tokens": 200,
                    "prompt_tokens_details": {"cached_tokens": 20},
                    "completion_tokens_details": {"reasoning_tokens": 30},
                },
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        adapter = OpenAICompatibleLLMAdapter(
            provider_identifier="provider-test",
            model_identifier="model-test",
            api_key="secret-test",
            base_url="https://provider.invalid/v1",
            prompt_version=PROMPT_VERSION,
            client=client,
        )
        result = await adapter.score(valid_request())

    payload = cast(dict[str, Any], captured["payload"])
    assert result.status is LLMProviderStatus.AVAILABLE
    assert result.output == valid_output()
    assert result.usage is not None
    assert result.usage.input_tokens == 120
    assert result.usage.output_tokens == 80
    assert result.usage.total_tokens == 200
    assert result.usage.cached_input_tokens == 20
    assert result.usage.reasoning_tokens == 30
    assert captured["authorization"] == "Bearer secret-test"
    assert payload["model"] == "model-test"
    assert payload["temperature"] == 0.0
    assert cast(dict[str, object], payload["response_format"])["type"] == "json_schema"
    serialized_messages = json.dumps(payload["messages"], ensure_ascii=False)
    assert "ev-l3-test" in serialized_messages
    assert "draft_label" not in serialized_messages
    assert "pilot_annotations" not in serialized_messages


@pytest.mark.asyncio
async def test_openai_compatible_adapter_can_omit_deprecated_temperature_parameter() -> None:
    captured_payload: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured_payload.update(cast(dict[str, object], json.loads(request.content)))
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                valid_output().model_dump(mode="python"),
                                default=float,
                            )
                        }
                    }
                ]
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        adapter = OpenAICompatibleLLMAdapter(
            provider_identifier="google_ai_studio",
            model_identifier="gemini-3.5-flash-lite",
            api_key="secret-test",
            base_url="https://provider.invalid/v1",
            prompt_version=PROMPT_VERSION,
            client=client,
            include_temperature_parameter=False,
        )
        result = await adapter.score(valid_request())

    assert result.status is LLMProviderStatus.AVAILABLE
    assert "temperature" not in captured_payload
    assert cast(dict[str, object], captured_payload["response_format"])["type"] == "json_schema"


@pytest.mark.asyncio
async def test_openai_compatible_adapter_sends_bounded_completion_and_reasoning_effort() -> None:
    captured_payload: dict[str, object] = {}
    request = valid_request()
    request = request.model_copy(
        update={
            "evidence": (
                *request.evidence,
                request.evidence[0].model_copy(update={"evidence_id": "ev-l3-second"}),
            )
        }
    )

    def handler(request: httpx.Request) -> httpx.Response:
        captured_payload.update(cast(dict[str, object], json.loads(request.content)))
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                valid_output().model_dump(mode="python"),
                                default=float,
                            )
                        }
                    }
                ]
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        adapter = OpenAICompatibleLLMAdapter(
            provider_identifier="openai",
            model_identifier="gpt-5.4-mini-2026-03-17",
            api_key="secret-test",
            base_url="https://api.openai.com/v1",
            prompt_version=PROMPT_VERSION,
            client=client,
            include_temperature_parameter=False,
            max_completion_tokens=4096,
            reasoning_effort="none",
        )
        result = await adapter.score(request)

    assert result.status is LLMProviderStatus.AVAILABLE
    assert captured_payload["max_completion_tokens"] == 4096
    assert captured_payload["reasoning_effort"] == "none"
    assert "temperature" not in captured_payload
    response_format = cast(dict[str, object], captured_payload["response_format"])
    json_schema = cast(dict[str, object], response_format["json_schema"])
    schema = cast(dict[str, object], json_schema["schema"])
    properties = cast(dict[str, object], schema["properties"])
    definitions = cast(dict[str, dict[str, object]], schema["$defs"])
    criterion = definitions["LLMWeightedCriterionAssessment"]
    criterion_variants = cast(list[dict[str, object]], criterion["anyOf"])
    requirement = definitions["LLMRequirementAssessment"]
    requirement_variants = cast(list[dict[str, object]], requirement["anyOf"])
    satisfied_criterion_properties = cast(dict[str, object], criterion_variants[0]["properties"])
    missing_criterion_properties = cast(dict[str, object], criterion_variants[2]["properties"])
    conflicting_criterion_properties = cast(dict[str, object], criterion_variants[3]["properties"])
    satisfied_evidence_ids = cast(dict[str, object], satisfied_criterion_properties["evidence_ids"])
    missing_evidence_ids = cast(dict[str, object], missing_criterion_properties["evidence_ids"])
    conflicting_evidence_ids = cast(
        dict[str, object], conflicting_criterion_properties["evidence_ids"]
    )
    criterion_assessments = cast(dict[str, object], properties["criterion_assessments"])
    requirement_assessments = cast(dict[str, object], properties["requirement_assessments"])

    assert schema["required"] == list(properties)
    assert all(
        variant["required"] == list(cast(dict[str, object], variant["properties"]))
        for variant in (*criterion_variants, *requirement_variants)
    )
    assert cast(dict[str, object], properties["overall_score"])["type"] == "number"
    assert cast(dict[str, object], satisfied_criterion_properties["score"])["type"] == "number"
    assert criterion_assessments["minItems"] == len(request.rubric.criteria)
    assert criterion_assessments["maxItems"] == len(request.rubric.criteria)
    assert requirement_assessments["minItems"] == len(request.rubric.critical_requirement_ids)
    assert requirement_assessments["maxItems"] == len(request.rubric.critical_requirement_ids)
    assert len(criterion_variants) == 4
    assert len(requirement_variants) == 4
    assert cast(dict[str, object], satisfied_criterion_properties["criterion_id"])["enum"] == [
        item.criterion_id for item in request.rubric.criteria
    ]
    assert cast(
        dict[str, object],
        cast(dict[str, object], requirement_variants[0]["properties"])["requirement_id"],
    )["enum"] == list(request.rubric.critical_requirement_ids)
    assert cast(dict[str, object], satisfied_criterion_properties["evidence_status"])["enum"] == [
        "satisfied"
    ]
    assert (satisfied_evidence_ids["minItems"], satisfied_evidence_ids["maxItems"]) == (1, 2)
    assert (missing_evidence_ids["minItems"], missing_evidence_ids["maxItems"]) == (0, 0)
    assert (
        conflicting_evidence_ids["minItems"],
        conflicting_evidence_ids["maxItems"],
    ) == (2, 2)
    assert cast(dict[str, object], satisfied_evidence_ids["items"])["enum"] == [
        "ev-l3-test",
        "ev-l3-second",
    ]
    assert "default" not in json.dumps(schema)


@pytest.mark.asyncio
async def test_openai_adapter_derives_redundant_total_from_criterion_scores() -> None:
    output_payload = valid_output().model_dump(mode="python")
    output_payload["overall_score"] = 79.5

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(output_payload, default=float),
                        }
                    }
                ]
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        adapter = OpenAICompatibleLLMAdapter(
            "openai",
            "gpt-5.4-mini-2026-03-17",
            "secret-test",
            "https://api.openai.com/v1",
            PROMPT_VERSION,
            client,
        )
        result = await adapter.score(valid_request())

    assert result.status is LLMProviderStatus.AVAILABLE
    assert result.output is not None
    assert result.output.overall_score == Decimal("80")


@pytest.mark.asyncio
async def test_openai_adapter_ignores_material_redundant_total_mismatch() -> None:
    output_payload = valid_output().model_dump(mode="python")
    output_payload["overall_score"] = 70

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(output_payload, default=float),
                        }
                    }
                ]
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        adapter = OpenAICompatibleLLMAdapter(
            "openai",
            "gpt-5.4-mini-2026-03-17",
            "secret-test",
            "https://api.openai.com/v1",
            PROMPT_VERSION,
            client,
        )
        result = await adapter.score(valid_request())

    assert result.status is LLMProviderStatus.AVAILABLE
    assert result.output is not None
    assert result.output.overall_score == Decimal("80")


@pytest.mark.parametrize("max_completion_tokens", [0, 128001, True])
@pytest.mark.asyncio
async def test_openai_compatible_adapter_rejects_invalid_completion_limit(
    max_completion_tokens: int,
) -> None:
    async with httpx.AsyncClient() as client:
        with pytest.raises(LLMConfigurationError, match="maximum completion tokens"):
            OpenAICompatibleLLMAdapter(
                provider_identifier="openai",
                model_identifier="gpt-5.4-mini-2026-03-17",
                api_key="secret-test",
                base_url="https://api.openai.com/v1",
                prompt_version=PROMPT_VERSION,
                client=client,
                max_completion_tokens=max_completion_tokens,
            )


@pytest.mark.asyncio
async def test_openai_compatible_adapter_ignores_abnormal_usage_without_losing_valid_score() -> (
    None
):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                valid_output().model_dump(mode="python"),
                                default=float,
                            ),
                        }
                    }
                ],
                "usage": {
                    "prompt_tokens": 120,
                    "completion_tokens": 80,
                    "total_tokens": 10,
                },
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        adapter = OpenAICompatibleLLMAdapter(
            provider_identifier="provider-test",
            model_identifier="model-test",
            api_key="secret-test",
            base_url="https://provider.invalid/v1",
            prompt_version=PROMPT_VERSION,
            client=client,
        )
        result = await adapter.score(valid_request())

    assert result.status is LLMProviderStatus.AVAILABLE
    assert result.output == valid_output()
    assert result.usage is None


@pytest.mark.asyncio
async def test_openai_compatible_adapter_routes_malformed_json_to_invalid() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "not-json"}}]},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        adapter = OpenAICompatibleLLMAdapter(
            "provider-test",
            "model-test",
            "secret-test",
            "https://provider.invalid/v1",
            PROMPT_VERSION,
            client,
        )
        result = await adapter.score(valid_request())

    assert result.status is LLMProviderStatus.INVALID
    assert result.output is None
    assert result.reason == "LLM provider output failed schema validation: root:json_invalid."


@pytest.mark.asyncio
async def test_openai_compatible_adapter_routes_http_failure_to_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, json={"error": "unavailable"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        adapter = OpenAICompatibleLLMAdapter(
            "provider-test",
            "model-test",
            "secret-test",
            "https://provider.invalid/v1",
            PROMPT_VERSION,
            client,
        )
        result = await adapter.score(valid_request())

    assert result.status is LLMProviderStatus.UNAVAILABLE
    assert result.output is None
    assert "503" in cast(str, result.reason)


@pytest.mark.asyncio
async def test_openai_compatible_adapter_sanitizes_http_error_diagnostics() -> None:
    sensitive_message = "private request content must not be retained"

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            400,
            json={
                "error": {
                    "message": sensitive_message,
                    "type": "invalid_request_error",
                    "code": "invalid_json_schema",
                    "param": "response_format",
                }
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        adapter = OpenAICompatibleLLMAdapter(
            "openai",
            "gpt-5.4-mini-2026-03-17",
            "secret-test",
            "https://api.openai.com/v1",
            PROMPT_VERSION,
            client,
        )
        result = await adapter.score(valid_request())

    assert result.status is LLMProviderStatus.UNAVAILABLE
    assert result.reason == (
        "LLM provider returned HTTP status 400 "
        "(type=invalid_request_error, code=invalid_json_schema, param=response_format)."
    )
    assert sensitive_message not in cast(str, result.reason)


@pytest.mark.asyncio
async def test_openai_compatible_adapter_reports_numeric_retry_after_without_other_headers() -> (
    None
):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            429,
            headers={"Retry-After": "60", "X-Sensitive-Diagnostic": "must-not-appear"},
            json={"error": "rate limited"},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        adapter = OpenAICompatibleLLMAdapter(
            "provider-test",
            "model-test",
            "secret-test",
            "https://provider.invalid/v1",
            PROMPT_VERSION,
            client,
        )
        result = await adapter.score(valid_request())

    assert result.status is LLMProviderStatus.UNAVAILABLE
    assert result.reason == "LLM provider returned HTTP status 429; retry after 60 seconds."
    assert "must-not-appear" not in cast(str, result.reason)


@pytest.mark.asyncio
async def test_openai_compatible_adapter_can_require_supported_provider_parameters() -> None:
    captured_payload: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured_payload.update(cast(dict[str, object], json.loads(request.content)))
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                valid_output().model_dump(mode="python"),
                                default=float,
                            )
                        }
                    }
                ]
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        adapter = OpenAICompatibleLLMAdapter(
            "openrouter",
            "model-test",
            "secret-test",
            "https://provider.invalid/v1",
            PROMPT_VERSION,
            client,
            require_supported_parameters=True,
        )
        result = await adapter.score(valid_request())

    assert result.status is LLMProviderStatus.AVAILABLE
    assert captured_payload["provider"] == {"require_parameters": True}


@pytest.mark.asyncio
async def test_openai_compatible_adapter_can_enable_response_healing() -> None:
    captured_payload: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured_payload.update(cast(dict[str, object], json.loads(request.content)))
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                valid_output().model_dump(mode="python"),
                                default=float,
                            )
                        }
                    }
                ]
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        adapter = OpenAICompatibleLLMAdapter(
            "openrouter",
            "model-test",
            "secret-test",
            "https://provider.invalid/v1",
            PROMPT_VERSION,
            client,
            enable_response_healing=True,
        )
        result = await adapter.score(valid_request())

    assert result.status is LLMProviderStatus.AVAILABLE
    assert captured_payload["plugins"] == [{"id": "response-healing"}]


@pytest.mark.asyncio
async def test_openai_compatible_adapter_requires_complete_environment_without_leaking_secret() -> (
    None
):
    models = RepositoryConfigurationLoader(REPOSITORY_ROOT).load_models_artifact()
    async with httpx.AsyncClient() as client:
        with pytest.raises(LLMConfigurationError) as error:
            OpenAICompatibleLLMAdapter.from_environment(
                models,
                client=client,
                environment={
                    "CLASSIFIER_LLM_PROVIDER": "provider-test",
                    "CLASSIFIER_LLM_MODEL": "model-test",
                    "CLASSIFIER_LLM_API_KEY": "private-value",
                },
            )
        assert "private-value" not in str(error.value)


def test_llm_output_rejects_abnormal_score_total() -> None:
    payload = valid_output().model_dump()
    payload["overall_score"] = Decimal("81")

    with pytest.raises(ValueError, match="criterion score sum"):
        LLMScoringOutput.model_validate(payload)


def test_llm_output_rejects_numeric_strings() -> None:
    payload = valid_output().model_dump()
    payload["overall_score"] = "80"

    with pytest.raises(ValueError, match="JSON numbers"):
        LLMScoringOutput.model_validate(payload)


@pytest.mark.asyncio
async def test_deterministic_core_l3_provider_is_bounded_traceable_and_input_sensitive() -> None:
    loader = RepositoryConfigurationLoader(REPOSITORY_ROOT)
    loaded = loader.load_for_job("junior-data-analyst-v1")
    evidence = valid_request().evidence
    base_profile = CVProfile(
        cv_profile_id="cv-offline-l3",
        candidate_reference="candidate-offline-l3",
        evidence=evidence,
    )
    request = L3ProviderRequest(
        cv_profile=base_profile,
        job_profile=loaded.job_profile,
        rubric=loaded.rubric,
        prompt_version=PROMPT_VERSION,
    )
    provider = DeterministicCoreL3Provider(loader.load_l1_policy("junior-data-analyst-v1"))

    first = await provider.evaluate(request)
    repeated = await provider.evaluate(request)
    assessment = await score_l3(request, provider)

    assert first == repeated
    assert assessment.status is LevelScoreStatus.AVAILABLE
    assert assessment.score is not None
    assert Decimal("0") <= assessment.score <= Decimal("100")
    known_evidence_ids = {item.evidence_id for item in base_profile.evidence}
    assert {
        evidence_id
        for item in (
            *assessment.requirement_assessments,
            *assessment.criterion_assessments,
        )
        for evidence_id in item.evidence_ids
    }.issubset(known_evidence_ids)
    criterion_rationales = [item.rationale for item in assessment.criterion_assessments]
    assert all("Chế độ L3 offline mô phỏng tiêu chí" in item for item in criterion_rationales)
    assert len(set(criterion_rationales)) == len(criterion_rationales)
    assert all("Deterministic offline score" not in item for item in criterion_rationales)
    assert assessment.warnings == ("Đang dùng L3 mô phỏng; không có request nào được gửi tới LLM.",)
    extra_evidence = Evidence(
        evidence_id="ev-l3-extra",
        source_type=EvidenceSourceType.PARSER,
        section=EvidenceSection.SKILLS,
        text="SQL và Python được sử dụng trong dự án.",
        location=EvidenceLocation(source_record_id="record-l3-extra"),
    )
    changed_request = L3ProviderRequest(
        cv_profile=CVProfile(
            cv_profile_id="cv-offline-l3-more",
            candidate_reference="candidate-offline-more",
            evidence=(*evidence, extra_evidence),
        ),
        job_profile=loaded.job_profile,
        rubric=loaded.rubric,
        prompt_version=PROMPT_VERSION,
    )
    changed = await provider.evaluate(changed_request)

    assert (
        cast(dict[str, object], first)["overall_score"]
        != cast(dict[str, object], changed)["overall_score"]
    )


@pytest.mark.asyncio
async def test_deterministic_core_l3_provider_accepts_only_its_configured_prompt() -> None:
    loader = RepositoryConfigurationLoader(
        REPOSITORY_ROOT,
        REPOSITORY_ROOT / "configs" / "runtime" / "five_role_v1",
    )
    loaded = loader.load_for_job("junior-frontend-std-v2")
    profile = CVProfile(
        cv_profile_id="cv-offline-l3-v12",
        candidate_reference="candidate-offline-l3-v12",
        evidence=valid_request().evidence,
    )
    request = L3ProviderRequest(
        cv_profile=profile,
        job_profile=loaded.job_profile,
        rubric=loaded.rubric,
        prompt_version=REQUIREMENT_GUARDED_PROMPT_VERSION,
    )
    provider = DeterministicCoreL3Provider(
        loader.load_l1_policy("junior-frontend-std-v2"),
        prompt_version=REQUIREMENT_GUARDED_PROMPT_VERSION,
    )

    available = await score_l3(request, provider)
    invalid = await score_l3(
        request.__class__(
            cv_profile=request.cv_profile,
            job_profile=request.job_profile,
            rubric=request.rubric,
            prompt_version=ROLE_CALIBRATED_PROMPT_VERSION,
        ),
        provider,
    )

    assert available.status is LevelScoreStatus.AVAILABLE
    assert invalid.status is LevelScoreStatus.INVALID


@pytest.mark.asyncio
async def test_core_failure_providers_map_to_invalid_and_unavailable() -> None:
    loaded = RepositoryConfigurationLoader(REPOSITORY_ROOT).load_for_job("junior-data-analyst-v1")
    request = L3ProviderRequest(
        cv_profile=CVProfile(
            cv_profile_id="cv-core-failure",
            candidate_reference="candidate-core-failure",
            evidence=valid_request().evidence,
        ),
        job_profile=loaded.job_profile,
        rubric=loaded.rubric,
        prompt_version=PROMPT_VERSION,
    )

    invalid = await score_l3(request, InvalidCoreL3Provider())
    unavailable = await score_l3(request, UnavailableCoreL3Provider())

    assert invalid.status is LevelScoreStatus.INVALID
    assert unavailable.status is LevelScoreStatus.UNAVAILABLE
