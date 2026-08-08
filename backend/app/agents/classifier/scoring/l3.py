from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Annotated, Final, Protocol, Self, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

from backend.app.contracts import (
    CVProfile,
    EvidenceStatus,
    JobProfile,
    LevelScoreStatus,
    ScoringRubric,
)
from backend.app.domain import (
    CriterionAssessment,
    LevelAssessment,
    RequirementAssessment,
    ScoringInputError,
    ScoringLevel,
)

SCORE_QUANTUM: Final[Decimal] = Decimal("0.01")
ProviderScore: TypeAlias = Annotated[
    Decimal,
    Field(ge=Decimal("0"), le=Decimal("100"), max_digits=5, decimal_places=2),
]
ProviderConfidence: TypeAlias = Annotated[
    Decimal,
    Field(ge=Decimal("0"), le=Decimal("1"), max_digits=3, decimal_places=2),
]
ProviderText: TypeAlias = Annotated[str, Field(min_length=1, max_length=4000)]


@dataclass(frozen=True, slots=True)
class L3ProviderRequest:
    cv_profile: CVProfile
    job_profile: JobProfile
    rubric: ScoringRubric
    prompt_version: str

    def __post_init__(self) -> None:
        if not self.prompt_version.strip():
            raise ScoringInputError("prompt_version must not be empty")
        if self.rubric.job_profile_id != self.job_profile.job_profile_id:
            raise ScoringInputError("rubric job_profile_id must match the job profile")
        requirement_ids = {item.requirement_id for item in self.job_profile.requirements}
        unknown_ids = set(self.rubric.critical_requirement_ids).difference(requirement_ids)
        if unknown_ids:
            raise ScoringInputError(
                f"rubric contains unknown critical requirement IDs: {sorted(unknown_ids)}"
            )


class L3Provider(Protocol):
    async def evaluate(self, request: L3ProviderRequest) -> object: ...


class _StructuredOutputModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class _RequirementOutput(_StructuredOutputModel):
    requirement_id: ProviderText
    evidence_status: EvidenceStatus
    evidence_ids: tuple[ProviderText, ...] = ()
    rationale: ProviderText


class _CriterionOutput(_StructuredOutputModel):
    criterion_id: ProviderText
    score: ProviderScore
    evidence_status: EvidenceStatus
    evidence_ids: tuple[ProviderText, ...] = ()
    rationale: ProviderText

    @field_validator("score", mode="before")
    @classmethod
    def reject_non_numeric_score(cls, value: object) -> object:
        if isinstance(value, (bool, str)) or not isinstance(value, (Decimal, float, int)):
            raise ValueError("score must be a JSON number")
        return value


class _L3StructuredOutput(_StructuredOutputModel):
    requirement_assessments: Annotated[tuple[_RequirementOutput, ...], Field(min_length=1)]
    criterion_assessments: Annotated[tuple[_CriterionOutput, ...], Field(min_length=1)]
    overall_score: ProviderScore
    strengths: tuple[ProviderText, ...] = ()
    risks: tuple[ProviderText, ...] = ()
    warnings: tuple[ProviderText, ...] = ()
    confidence: ProviderConfidence | None = None

    @field_validator("overall_score", "confidence", mode="before")
    @classmethod
    def reject_non_numeric_values(cls, value: object) -> object:
        if value is None:
            return value
        if isinstance(value, (bool, str)) or not isinstance(value, (Decimal, float, int)):
            raise ValueError("numeric output fields must be JSON numbers")
        return value

    @model_validator(mode="after")
    def validate_unique_identifiers(self) -> Self:
        requirement_ids = tuple(item.requirement_id for item in self.requirement_assessments)
        criterion_ids = tuple(item.criterion_id for item in self.criterion_assessments)
        if len(requirement_ids) != len(set(requirement_ids)):
            raise ValueError("requirement assessments must have unique identifiers")
        if len(criterion_ids) != len(set(criterion_ids)):
            raise ValueError("criterion assessments must have unique identifiers")
        return self


def _validate_and_convert_output(
    raw_output: object,
    request: L3ProviderRequest,
) -> LevelAssessment:
    output = _L3StructuredOutput.model_validate(raw_output)
    evidence_ids = {item.evidence_id for item in request.cv_profile.evidence}
    expected_requirement_ids = set(request.rubric.critical_requirement_ids)
    actual_requirement_ids = {item.requirement_id for item in output.requirement_assessments}
    if actual_requirement_ids != expected_requirement_ids:
        raise ScoringInputError(
            "L3 requirement assessments must exactly match critical rubric requirements"
        )
    criteria_by_id = {item.criterion_id: item for item in request.rubric.criteria}
    actual_criterion_ids = {item.criterion_id for item in output.criterion_assessments}
    if actual_criterion_ids != set(criteria_by_id):
        raise ScoringInputError("L3 criterion assessments must exactly match rubric criteria")

    requirement_assessments = tuple(
        RequirementAssessment(
            requirement_id=item.requirement_id,
            evidence_status=item.evidence_status,
            evidence_ids=item.evidence_ids,
            rationale=item.rationale,
        )
        for item in output.requirement_assessments
    )
    criterion_assessments = tuple(
        CriterionAssessment(
            criterion_id=item.criterion_id,
            weighted_score=item.score,
            evidence_status=item.evidence_status,
            evidence_ids=item.evidence_ids,
            rationale=item.rationale,
        )
        for item in output.criterion_assessments
    )
    referenced_evidence_ids = {
        evidence_id
        for assessment in requirement_assessments
        for evidence_id in assessment.evidence_ids
    }
    referenced_evidence_ids.update(
        evidence_id
        for assessment in criterion_assessments
        for evidence_id in assessment.evidence_ids
    )
    unknown_evidence_ids = referenced_evidence_ids.difference(evidence_ids)
    if unknown_evidence_ids:
        raise ScoringInputError(
            f"L3 output references unknown evidence IDs: {sorted(unknown_evidence_ids)}"
        )
    for assessment in criterion_assessments:
        maximum = criteria_by_id[assessment.criterion_id].weight
        if assessment.weighted_score > maximum:
            raise ScoringInputError(
                f"L3 criterion score exceeds rubric weight: {assessment.criterion_id}"
            )
    calculated_score = sum(
        (assessment.weighted_score for assessment in criterion_assessments),
        Decimal("0"),
    ).quantize(SCORE_QUANTUM, rounding=ROUND_HALF_UP)
    if calculated_score != output.overall_score:
        raise ScoringInputError("L3 overall_score must equal the criterion score sum")
    return LevelAssessment(
        level=ScoringLevel.L3,
        status=LevelScoreStatus.AVAILABLE,
        score=calculated_score,
        criterion_assessments=criterion_assessments,
        requirement_assessments=requirement_assessments,
        confidence=output.confidence,
        strengths=output.strengths,
        risks=output.risks,
        warnings=output.warnings,
    )


async def score_l3(
    request: L3ProviderRequest,
    provider: L3Provider,
) -> LevelAssessment:
    try:
        raw_output = await provider.evaluate(request)
    except Exception:
        return LevelAssessment.unavailable(
            ScoringLevel.L3,
            "L3 reasoning provider is unavailable.",
        )
    try:
        return _validate_and_convert_output(raw_output, request)
    except (ValidationError, ScoringInputError):
        return LevelAssessment.invalid(
            ScoringLevel.L3,
            "L3 reasoning provider returned invalid structured output.",
        )
