from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Annotated, Literal, Self

from pydantic import Field, field_validator, model_validator

from backend.app.contracts.common import (
    Confidence,
    ContractModel,
    EvidenceStatus,
    Identifier,
    NonEmptyText,
    Score,
)
from backend.app.contracts.cv_profile import CVProfile, EvidenceId
from backend.app.contracts.job_profile import JobProfile


class RubricCriterion(ContractModel):
    criterion_id: Identifier
    title: NonEmptyText
    description: NonEmptyText
    weight: Score


class ScoringRubric(ContractModel):
    schema_version: Literal["1.0.0"] = "1.0.0"
    rubric_id: Identifier
    rubric_version: NonEmptyText
    job_profile_id: Identifier
    criteria: Annotated[tuple[RubricCriterion, ...], Field(min_length=1)]
    critical_requirement_ids: Annotated[tuple[Identifier, ...], Field(min_length=1)]

    @model_validator(mode="after")
    def validate_criteria(self) -> Self:
        criterion_ids = tuple(item.criterion_id for item in self.criteria)
        if len(criterion_ids) != len(set(criterion_ids)):
            raise ValueError("criterion identifiers must be unique")
        if sum(item.weight for item in self.criteria) != Decimal("100"):
            raise ValueError("rubric criteria weights must total 100")
        if len(self.critical_requirement_ids) != len(set(self.critical_requirement_ids)):
            raise ValueError("critical requirement identifiers must be unique")
        return self


class AggregationWeights(ContractModel):
    l1_deterministic_rules: Annotated[Decimal, Field(ge=Decimal("0"), le=Decimal("1"))]
    l2_section_semantic_matching: Annotated[Decimal, Field(ge=Decimal("0"), le=Decimal("1"))]
    l3_evidence_grounded_reasoning: Annotated[Decimal, Field(ge=Decimal("0"), le=Decimal("1"))]

    @model_validator(mode="after")
    def validate_total(self) -> Self:
        total = (
            self.l1_deterministic_rules
            + self.l2_section_semantic_matching
            + self.l3_evidence_grounded_reasoning
        )
        if total != Decimal("1"):
            raise ValueError("aggregation weights must total 1")
        return self


class DecisionThresholds(ContractModel):
    pass_minimum: Score
    waitlist_minimum: Score

    @model_validator(mode="after")
    def validate_thresholds(self) -> Self:
        if self.waitlist_minimum >= self.pass_minimum:
            raise ValueError("waitlist_minimum must be lower than pass_minimum")
        return self


class ReviewBand(ContractModel):
    minimum: Score
    maximum: Score

    @model_validator(mode="after")
    def validate_band(self) -> Self:
        if self.maximum < self.minimum:
            raise ValueError("review band maximum must be greater than or equal to minimum")
        return self


class NeedsReviewPolicy(ContractModel):
    missing_critical_evidence: bool
    conflicting_critical_evidence: bool
    invalid_provider_output: bool
    disagreement_points: Score
    boundary_score_bands: Annotated[tuple[ReviewBand, ...], Field(min_length=1)]


class ModelMetadata(ContractModel):
    embedding_model_identifier: NonEmptyText
    embedding_model_version: NonEmptyText
    llm_provider_identifier: NonEmptyText
    llm_model_identifier: NonEmptyText
    prompt_version: NonEmptyText


class ClassificationConfig(ContractModel):
    schema_version: Literal["1.1.0"] = "1.1.0"
    configuration_id: Identifier
    configuration_version: NonEmptyText
    job_profile_artifact_version: NonEmptyText
    l1_rules_configuration_version: NonEmptyText
    models_configuration_version: NonEmptyText
    aggregation: AggregationWeights
    thresholds: DecisionThresholds
    needs_review_policy: NeedsReviewPolicy
    models: ModelMetadata


class ClassificationRequest(ContractModel):
    schema_version: Literal["1.1.0"] = "1.1.0"
    request_id: Identifier
    cv_profile: CVProfile
    job_profile: JobProfile
    rubric: ScoringRubric
    configuration: ClassificationConfig

    @model_validator(mode="after")
    def validate_artifact_references(self) -> Self:
        if self.rubric.job_profile_id != self.job_profile.job_profile_id:
            raise ValueError("rubric job_profile_id must match the supplied job profile")
        requirement_ids = {item.requirement_id for item in self.job_profile.requirements}
        unknown_critical_ids = set(self.rubric.critical_requirement_ids).difference(requirement_ids)
        if unknown_critical_ids:
            raise ValueError(
                f"unknown critical requirement identifiers: {sorted(unknown_critical_ids)}"
            )
        return self


class ClassificationDecision(StrEnum):
    PASS = "pass"
    WAITLIST = "waitlist"
    REJECT = "reject"
    NEEDS_REVIEW = "needs_review"


class FinalDecision(StrEnum):
    PASS = "pass"
    WAITLIST = "waitlist"
    REJECT = "reject"


class LevelScoreStatus(StrEnum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    INVALID = "invalid"


class LevelScore(ContractModel):
    value: Score | None
    status: LevelScoreStatus
    reason: NonEmptyText | None = None

    @model_validator(mode="after")
    def validate_score_availability(self) -> Self:
        if self.status is LevelScoreStatus.AVAILABLE and self.value is None:
            raise ValueError("available score must have a value")
        if self.status is not LevelScoreStatus.AVAILABLE and self.value is not None:
            raise ValueError("unavailable or invalid score must not have a value")
        if self.status is not LevelScoreStatus.AVAILABLE and self.reason is None:
            raise ValueError("unavailable or invalid score must include a reason")
        return self


class ScoreBreakdown(ContractModel):
    l1: LevelScore
    l2: LevelScore
    l3: LevelScore
    final_score: Score | None


class CriterionAssessment(ContractModel):
    criterion_id: Identifier
    score: Score
    evidence_status: EvidenceStatus
    evidence_ids: tuple[EvidenceId, ...] = ()
    rationale: NonEmptyText

    @model_validator(mode="after")
    def validate_assessment_evidence(self) -> Self:
        if (
            self.evidence_status in {EvidenceStatus.SATISFIED, EvidenceStatus.UNSATISFIED}
            and not self.evidence_ids
        ):
            raise ValueError("satisfied and unsatisfied assessments require evidence identifiers")
        return self


class QualityGate(ContractModel):
    requires_review: bool
    reasons: tuple[NonEmptyText, ...] = ()

    @model_validator(mode="after")
    def validate_reasons(self) -> Self:
        if self.requires_review and not self.reasons:
            raise ValueError("a review gate requires at least one reason")
        if not self.requires_review and self.reasons:
            raise ValueError("a non-review gate must not include review reasons")
        return self


class RunVersions(ContractModel):
    job_profile_artifact_version: NonEmptyText
    rubric_version: NonEmptyText
    configuration_version: NonEmptyText
    l1_rules_configuration_version: NonEmptyText
    models_configuration_version: NonEmptyText
    embedding_model_identifier: NonEmptyText
    embedding_model_version: NonEmptyText
    llm_provider_identifier: NonEmptyText
    llm_model_identifier: NonEmptyText
    prompt_version: NonEmptyText


class ClassificationResult(ContractModel):
    schema_version: Literal["1.1.0"] = "1.1.0"
    classification_result_id: Identifier
    request_id: Identifier
    cv_profile_id: Identifier
    job_profile_id: Identifier
    proposed_decision: ClassificationDecision
    scores: ScoreBreakdown
    criterion_assessments: tuple[CriterionAssessment, ...]
    strengths: tuple[NonEmptyText, ...] = ()
    risks: tuple[NonEmptyText, ...] = ()
    warnings: tuple[NonEmptyText, ...] = ()
    confidence: Confidence | None
    quality_gate: QualityGate
    versions: RunVersions
    created_at: datetime

    @field_validator("created_at")
    @classmethod
    def validate_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("created_at must include a timezone")
        return value

    @model_validator(mode="after")
    def validate_decision_and_quality_gate(self) -> Self:
        if self.proposed_decision is ClassificationDecision.NEEDS_REVIEW:
            if not self.quality_gate.requires_review:
                raise ValueError("needs_review decisions require a review quality gate")
        else:
            if self.quality_gate.requires_review:
                raise ValueError("a review quality gate requires a needs_review decision")
            if self.scores.final_score is None:
                raise ValueError("non-review decisions require a final score")
        return self


class ApprovalStatus(StrEnum):
    APPROVED = "approved"
    OVERRIDDEN = "overridden"


class ApprovedDecision(ContractModel):
    schema_version: Literal["1.0.0"] = "1.0.0"
    approved_decision_id: Identifier
    classification_result_id: Identifier
    approval_status: ApprovalStatus
    proposed_decision: ClassificationDecision
    final_decision: FinalDecision
    reviewer_reference: Identifier
    decision_reason: NonEmptyText
    override_reason: NonEmptyText | None = None
    decided_at: datetime

    @field_validator("decided_at")
    @classmethod
    def validate_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("decided_at must include a timezone")
        return value

    @model_validator(mode="after")
    def validate_approval_state(self) -> Self:
        if self.approval_status is ApprovalStatus.APPROVED:
            if self.final_decision.value != self.proposed_decision.value:
                raise ValueError("approved decisions must preserve the proposed decision")
            if self.override_reason is not None:
                raise ValueError("approved decisions must not include an override reason")
        if self.approval_status is ApprovalStatus.OVERRIDDEN:
            if self.final_decision.value == self.proposed_decision.value:
                raise ValueError("overridden decisions must change the proposed decision")
            if self.override_reason is None:
                raise ValueError("overridden decisions require an override reason")
        return self
