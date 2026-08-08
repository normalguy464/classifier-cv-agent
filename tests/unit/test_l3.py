import asyncio
from copy import deepcopy
from decimal import Decimal

import pytest

from backend.app.agents.classifier.scoring.l3 import L3ProviderRequest, score_l3
from backend.app.contracts import (
    CVProfile,
    Evidence,
    EvidenceLocation,
    EvidenceSection,
    EvidenceSourceType,
    EvidenceStatus,
    ExperienceRange,
    JobProfile,
    JobRequirement,
    LevelScoreStatus,
    RequirementPriority,
    RubricCriterion,
    ScoringRubric,
    SeniorityLevel,
)
from backend.app.domain import ScoringInputError, ScoringLevel


def make_cv() -> CVProfile:
    return CVProfile(
        cv_profile_id="cv-l3-test",
        candidate_reference="candidate-l3-test",
        evidence=(
            Evidence(
                evidence_id="ev-python",
                source_type=EvidenceSourceType.MANUAL,
                section=EvidenceSection.SKILLS,
                text="Python backend project.",
                location=EvidenceLocation(source_record_id="record-python"),
            ),
            Evidence(
                evidence_id="ev-project",
                source_type=EvidenceSourceType.MANUAL,
                section=EvidenceSection.PROJECTS,
                text="Delivered a documented API.",
                location=EvidenceLocation(source_record_id="record-project"),
            ),
        ),
    )


def make_job() -> JobProfile:
    return JobProfile(
        job_profile_id="job-l3-test",
        title="Junior Backend Developer",
        seniority=SeniorityLevel.JUNIOR,
        experience_range=ExperienceRange(minimum_years=0, maximum_years=2),
        responsibilities=("Build backend services.",),
        requirements=(
            JobRequirement(
                requirement_id="req-python",
                title="Python",
                description="Use Python.",
                priority=RequirementPriority.REQUIRED,
                is_critical=True,
                accepted_evidence=("Project evidence.",),
                missing_evidence_policy="Review missing information.",
                explicit_failure_policy="Require explicit contrary information.",
            ),
        ),
    )


def make_rubric(job_profile_id: str = "job-l3-test") -> ScoringRubric:
    return ScoringRubric(
        rubric_id="rubric-l3-test",
        rubric_version="1.0.0",
        job_profile_id=job_profile_id,
        criteria=(
            RubricCriterion(
                criterion_id="technical-skill",
                title="Technical skill",
                description="Technical evidence.",
                weight=Decimal("60"),
            ),
            RubricCriterion(
                criterion_id="project-impact",
                title="Project impact",
                description="Project evidence.",
                weight=Decimal("40"),
            ),
        ),
        critical_requirement_ids=("req-python",),
    )


def make_request() -> L3ProviderRequest:
    return L3ProviderRequest(
        cv_profile=make_cv(),
        job_profile=make_job(),
        rubric=make_rubric(),
        prompt_version="l3-prompt-v1",
    )


def valid_output() -> dict[str, object]:
    return {
        "requirement_assessments": [
            {
                "requirement_id": "req-python",
                "evidence_status": "satisfied",
                "evidence_ids": ["ev-python"],
                "rationale": "Python is used in a backend project.",
            }
        ],
        "criterion_assessments": [
            {
                "criterion_id": "technical-skill",
                "score": 48,
                "evidence_status": "satisfied",
                "evidence_ids": ["ev-python"],
                "rationale": "The technical evidence is relevant.",
            },
            {
                "criterion_id": "project-impact",
                "score": 20,
                "evidence_status": "satisfied",
                "evidence_ids": ["ev-project"],
                "rationale": "The project has a documented output.",
            },
        ],
        "overall_score": 68,
        "strengths": ["Relevant Python project."],
        "risks": ["Limited delivery detail."],
        "warnings": [],
        "confidence": 0.8,
    }


class StaticProvider:
    def __init__(self, output: object) -> None:
        self.output = output
        self.requests: list[L3ProviderRequest] = []

    async def evaluate(self, request: L3ProviderRequest) -> object:
        self.requests.append(request)
        return self.output


class FailingProvider:
    async def evaluate(self, request: L3ProviderRequest) -> object:
        raise RuntimeError(f"secret-provider-detail-{request.prompt_version}")


def test_l3_validates_structured_output_and_weighted_criterion_sum() -> None:
    request = make_request()
    provider = StaticProvider(valid_output())

    result = asyncio.run(score_l3(request, provider))

    assert result.level is ScoringLevel.L3
    assert result.status is LevelScoreStatus.AVAILABLE
    assert result.score == Decimal("68.00")
    assert tuple(item.weighted_score for item in result.criterion_assessments) == (
        Decimal("48"),
        Decimal("20"),
    )
    assert result.requirement_assessments[0].evidence_status is EvidenceStatus.SATISFIED
    assert result.confidence == Decimal("0.8")
    assert provider.requests == [request]


def test_l3_provider_failure_is_unavailable_and_does_not_expose_provider_error() -> None:
    result = asyncio.run(score_l3(make_request(), FailingProvider()))

    assert result.status is LevelScoreStatus.UNAVAILABLE
    assert result.score is None
    assert result.reason == "L3 reasoning provider is unavailable."
    assert "secret-provider-detail" not in result.reason


def invalid_outputs() -> list[dict[str, object]]:
    extra_field = valid_output()
    extra_field["provider_object"] = {"raw": True}

    missing_criterion = valid_output()
    missing_criterion["criterion_assessments"] = [
        deepcopy(missing_criterion["criterion_assessments"][0])
    ]
    missing_criterion["overall_score"] = 48

    unknown_evidence = valid_output()
    unknown_evidence["criterion_assessments"][0]["evidence_ids"] = ["ev-unknown"]

    above_weight = valid_output()
    above_weight["criterion_assessments"][0]["score"] = 61
    above_weight["overall_score"] = 81

    wrong_total = valid_output()
    wrong_total["overall_score"] = 67

    string_score = valid_output()
    string_score["criterion_assessments"][0]["score"] = "48"

    missing_with_evidence = valid_output()
    missing_with_evidence["requirement_assessments"][0]["evidence_status"] = "missing"

    duplicate_criterion = valid_output()
    duplicate_criterion["criterion_assessments"][1]["criterion_id"] = "technical-skill"

    unknown_requirement = valid_output()
    unknown_requirement["requirement_assessments"][0]["requirement_id"] = "req-unknown"

    out_of_range = valid_output()
    out_of_range["criterion_assessments"][0]["score"] = 101
    out_of_range["overall_score"] = 121

    return [
        extra_field,
        missing_criterion,
        unknown_evidence,
        above_weight,
        wrong_total,
        string_score,
        missing_with_evidence,
        duplicate_criterion,
        unknown_requirement,
        out_of_range,
    ]


@pytest.mark.parametrize("output", invalid_outputs())
def test_l3_invalid_structured_outputs_are_reported_as_invalid(
    output: dict[str, object],
) -> None:
    result = asyncio.run(score_l3(make_request(), StaticProvider(output)))

    assert result.status is LevelScoreStatus.INVALID
    assert result.score is None
    assert result.reason == "L3 reasoning provider returned invalid structured output."


def test_l3_provider_request_rejects_mismatched_job_and_unknown_requirements() -> None:
    with pytest.raises(ScoringInputError, match="job_profile_id"):
        L3ProviderRequest(
            cv_profile=make_cv(),
            job_profile=make_job(),
            rubric=make_rubric("other-job"),
            prompt_version="l3-prompt-v1",
        )

    rubric = make_rubric().model_copy(update={"critical_requirement_ids": ("req-unknown",)})
    with pytest.raises(ScoringInputError, match="unknown critical"):
        L3ProviderRequest(
            cv_profile=make_cv(),
            job_profile=make_job(),
            rubric=rubric,
            prompt_version="l3-prompt-v1",
        )


def test_l3_provider_request_rejects_blank_prompt_version() -> None:
    with pytest.raises(ScoringInputError, match="prompt_version"):
        L3ProviderRequest(
            cv_profile=make_cv(),
            job_profile=make_job(),
            rubric=make_rubric(),
            prompt_version=" ",
        )
