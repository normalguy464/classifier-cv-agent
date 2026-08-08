from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import Final, Self

from backend.app.contracts import (
    ClassificationDecision,
    EvidenceSection,
    EvidenceStatus,
    LevelScoreStatus,
)
from backend.app.domain.errors import ScoringInputError

MINIMUM_SCORE: Final[Decimal] = Decimal("0")
MAXIMUM_SCORE: Final[Decimal] = Decimal("100")
MINIMUM_CONFIDENCE: Final[Decimal] = Decimal("0")
MAXIMUM_CONFIDENCE: Final[Decimal] = Decimal("1")


class ScoringLevel(StrEnum):
    L1 = "l1"
    L2 = "l2"
    L3 = "l3"


class L2ScoringMode(StrEnum):
    TOP_K_MEAN = "top_k_mean"
    QUERY_COVERAGE = "query_coverage"


class MatchMode(StrEnum):
    ANY = "any"
    ALL = "all"


def _validate_non_empty(value: str, field_name: str) -> None:
    if not value.strip():
        raise ScoringInputError(f"{field_name} must not be empty")


def _validate_unique_non_empty(values: tuple[str, ...], field_name: str) -> None:
    normalized = tuple(value.strip().casefold() for value in values)
    if any(not value for value in normalized):
        raise ScoringInputError(f"{field_name} must not contain empty values")
    if len(normalized) != len(set(normalized)):
        raise ScoringInputError(f"{field_name} must contain unique values")


def _validate_decimal_range(
    value: Decimal,
    minimum: Decimal,
    maximum: Decimal,
    field_name: str,
) -> None:
    if not value.is_finite() or value < minimum or value > maximum:
        raise ScoringInputError(f"{field_name} must be between {minimum} and {maximum}")


@dataclass(frozen=True, slots=True)
class RequirementRule:
    requirement_id: str
    evidence_sections: tuple[EvidenceSection, ...]
    positive_terms: tuple[str, ...]
    explicit_negative_terms: tuple[str, ...]
    match_mode: MatchMode = MatchMode.ANY
    positive_evidence_sections: tuple[EvidenceSection, ...] = ()
    positive_term_groups: tuple[tuple[str, ...], ...] = ()

    def __post_init__(self) -> None:
        _validate_non_empty(self.requirement_id, "requirement_id")
        if not self.evidence_sections:
            raise ScoringInputError("evidence_sections must not be empty")
        if len(self.evidence_sections) != len(set(self.evidence_sections)):
            raise ScoringInputError("evidence_sections must contain unique values")
        if not self.positive_terms:
            raise ScoringInputError("positive_terms must not be empty")
        _validate_unique_non_empty(self.positive_terms, "positive_terms")
        _validate_unique_non_empty(self.explicit_negative_terms, "explicit_negative_terms")
        if len(self.positive_evidence_sections) != len(set(self.positive_evidence_sections)):
            raise ScoringInputError("positive_evidence_sections must contain unique values")
        if any(
            section not in self.evidence_sections for section in self.positive_evidence_sections
        ):
            raise ScoringInputError(
                "positive_evidence_sections must reference configured evidence sections"
            )
        normalized_positive = {term.strip().casefold() for term in self.positive_terms}
        normalized_groups: set[tuple[str, ...]] = set()
        for group in self.positive_term_groups:
            if not group:
                raise ScoringInputError("positive_term_groups must not contain empty groups")
            _validate_unique_non_empty(group, "positive_term_group")
            normalized_group = tuple(term.strip().casefold() for term in group)
            if not set(normalized_group).issubset(normalized_positive):
                raise ScoringInputError("positive_term_groups must reference positive_terms")
            normalized_groups.add(normalized_group)
        if len(normalized_groups) != len(self.positive_term_groups):
            raise ScoringInputError("positive_term_groups must contain unique groups")

    @property
    def effective_positive_evidence_sections(self) -> tuple[EvidenceSection, ...]:
        return self.positive_evidence_sections or self.evidence_sections


@dataclass(frozen=True, slots=True)
class L1Policy:
    job_profile_id: str
    rules: tuple[RequirementRule, ...]

    def __post_init__(self) -> None:
        _validate_non_empty(self.job_profile_id, "job_profile_id")
        if not self.rules:
            raise ScoringInputError("L1 policy must contain at least one rule")
        requirement_ids = tuple(rule.requirement_id for rule in self.rules)
        if len(requirement_ids) != len(set(requirement_ids)):
            raise ScoringInputError("L1 requirement rules must have unique identifiers")


@dataclass(frozen=True, slots=True)
class L2CriterionPolicy:
    criterion_id: str
    query_text: str
    evidence_sections: tuple[EvidenceSection, ...]
    similarity_floor: Decimal
    similarity_ceiling: Decimal
    top_k: int = 1
    scoring_mode: L2ScoringMode = L2ScoringMode.TOP_K_MEAN
    additional_query_texts: tuple[str, ...] = ()
    minimum_query_score: Decimal = Decimal("0")
    section_weights: tuple[tuple[EvidenceSection, Decimal], ...] = ()

    def __post_init__(self) -> None:
        _validate_non_empty(self.criterion_id, "criterion_id")
        _validate_non_empty(self.query_text, "query_text")
        if not self.evidence_sections:
            raise ScoringInputError("evidence_sections must not be empty")
        if len(self.evidence_sections) != len(set(self.evidence_sections)):
            raise ScoringInputError("evidence_sections must contain unique values")
        if (
            not self.similarity_floor.is_finite()
            or not self.similarity_ceiling.is_finite()
            or self.similarity_floor < Decimal("-1")
            or self.similarity_ceiling > Decimal("1")
            or self.similarity_floor >= self.similarity_ceiling
        ):
            raise ScoringInputError(
                "similarity_floor and similarity_ceiling must define an increasing range within -1 and 1"
            )
        if self.top_k < 1:
            raise ScoringInputError("top_k must be at least 1")
        _validate_unique_non_empty(self.additional_query_texts, "additional_query_texts")
        query_texts = (self.query_text, *self.additional_query_texts)
        if len(query_texts) != len(set(query_texts)):
            raise ScoringInputError("L2 query texts must be unique")
        if (
            not self.minimum_query_score.is_finite()
            or self.minimum_query_score < MINIMUM_SCORE
            or self.minimum_query_score > MAXIMUM_SCORE
        ):
            raise ScoringInputError("minimum_query_score must be between 0 and 100")
        sections = tuple(item[0] for item in self.section_weights)
        if len(sections) != len(set(sections)):
            raise ScoringInputError("section weights must have unique sections")
        if any(section not in self.evidence_sections for section in sections):
            raise ScoringInputError("section weights must reference configured evidence sections")
        for _, weight in self.section_weights:
            if not weight.is_finite() or weight <= Decimal("0") or weight > Decimal("1"):
                raise ScoringInputError("section weights must be above 0 and at most 1")
        if self.scoring_mode is L2ScoringMode.TOP_K_MEAN and self.additional_query_texts:
            raise ScoringInputError("top_k_mean does not allow additional query texts")

    @property
    def query_texts(self) -> tuple[str, ...]:
        return (self.query_text, *self.additional_query_texts)

    def section_weight(self, section: EvidenceSection) -> Decimal:
        return dict(self.section_weights).get(section, Decimal("1"))


@dataclass(frozen=True, slots=True)
class L2Policy:
    job_profile_id: str
    criteria: tuple[L2CriterionPolicy, ...]

    def __post_init__(self) -> None:
        _validate_non_empty(self.job_profile_id, "job_profile_id")
        if not self.criteria:
            raise ScoringInputError("L2 policy must contain at least one criterion")
        criterion_ids = tuple(criterion.criterion_id for criterion in self.criteria)
        if len(criterion_ids) != len(set(criterion_ids)):
            raise ScoringInputError("L2 criteria must have unique identifiers")

    @property
    def query_count(self) -> int:
        return sum(len(criterion.query_texts) for criterion in self.criteria)


@dataclass(frozen=True, slots=True)
class RequirementAssessment:
    requirement_id: str
    evidence_status: EvidenceStatus
    evidence_ids: tuple[str, ...]
    rationale: str

    def __post_init__(self) -> None:
        _validate_non_empty(self.requirement_id, "requirement_id")
        _validate_non_empty(self.rationale, "rationale")
        _validate_unique_non_empty(self.evidence_ids, "evidence_ids")
        if self.evidence_status in {EvidenceStatus.SATISFIED, EvidenceStatus.UNSATISFIED}:
            if not self.evidence_ids:
                raise ScoringInputError(
                    "satisfied and unsatisfied requirement assessments require evidence"
                )
        if self.evidence_status is EvidenceStatus.MISSING and self.evidence_ids:
            raise ScoringInputError("missing requirement assessments must not reference evidence")
        if self.evidence_status is EvidenceStatus.CONFLICTING and len(self.evidence_ids) < 2:
            raise ScoringInputError(
                "conflicting requirement assessments require at least two evidence references"
            )


@dataclass(frozen=True, slots=True)
class CriterionAssessment:
    criterion_id: str
    weighted_score: Decimal
    evidence_status: EvidenceStatus
    evidence_ids: tuple[str, ...]
    rationale: str

    def __post_init__(self) -> None:
        _validate_non_empty(self.criterion_id, "criterion_id")
        _validate_non_empty(self.rationale, "rationale")
        _validate_decimal_range(
            self.weighted_score,
            MINIMUM_SCORE,
            MAXIMUM_SCORE,
            "weighted_score",
        )
        _validate_unique_non_empty(self.evidence_ids, "evidence_ids")
        if self.evidence_status in {EvidenceStatus.SATISFIED, EvidenceStatus.UNSATISFIED}:
            if not self.evidence_ids:
                raise ScoringInputError(
                    "satisfied and unsatisfied criterion assessments require evidence"
                )
        if self.evidence_status is EvidenceStatus.MISSING and self.evidence_ids:
            raise ScoringInputError("missing criterion assessments must not reference evidence")
        if self.evidence_status is EvidenceStatus.CONFLICTING and len(self.evidence_ids) < 2:
            raise ScoringInputError(
                "conflicting criterion assessments require at least two evidence references"
            )


@dataclass(frozen=True, slots=True)
class LevelAssessment:
    level: ScoringLevel
    status: LevelScoreStatus
    score: Decimal | None
    criterion_assessments: tuple[CriterionAssessment, ...] = ()
    requirement_assessments: tuple[RequirementAssessment, ...] = ()
    confidence: Decimal | None = None
    strengths: tuple[str, ...] = ()
    risks: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    reason: str | None = None

    def __post_init__(self) -> None:
        criterion_ids = tuple(item.criterion_id for item in self.criterion_assessments)
        requirement_ids = tuple(item.requirement_id for item in self.requirement_assessments)
        if len(criterion_ids) != len(set(criterion_ids)):
            raise ScoringInputError("criterion assessments must have unique identifiers")
        if len(requirement_ids) != len(set(requirement_ids)):
            raise ScoringInputError("requirement assessments must have unique identifiers")
        _validate_unique_non_empty(self.strengths, "strengths")
        _validate_unique_non_empty(self.risks, "risks")
        _validate_unique_non_empty(self.warnings, "warnings")
        if self.status is LevelScoreStatus.AVAILABLE:
            if self.score is None:
                raise ScoringInputError("available level assessments require a score")
            _validate_decimal_range(self.score, MINIMUM_SCORE, MAXIMUM_SCORE, "score")
            if self.reason is not None:
                raise ScoringInputError("available level assessments must not include a reason")
        else:
            if self.score is not None:
                raise ScoringInputError(
                    "unavailable or invalid level assessments must not include a score"
                )
            if self.criterion_assessments or self.requirement_assessments:
                raise ScoringInputError(
                    "unavailable or invalid level assessments must not include assessments"
                )
            if self.confidence is not None:
                raise ScoringInputError(
                    "unavailable or invalid level assessments must not include confidence"
                )
            if self.reason is None or not self.reason.strip():
                raise ScoringInputError("unavailable or invalid level assessments require a reason")
        if self.confidence is not None:
            _validate_decimal_range(
                self.confidence,
                MINIMUM_CONFIDENCE,
                MAXIMUM_CONFIDENCE,
                "confidence",
            )

    @classmethod
    def unavailable(cls, level: ScoringLevel, reason: str) -> Self:
        return cls(level=level, status=LevelScoreStatus.UNAVAILABLE, score=None, reason=reason)

    @classmethod
    def invalid(cls, level: ScoringLevel, reason: str) -> Self:
        return cls(level=level, status=LevelScoreStatus.INVALID, score=None, reason=reason)


@dataclass(frozen=True, slots=True)
class AggregationResult:
    level_assessments: tuple[LevelAssessment, ...]
    final_score: Decimal | None

    def __post_init__(self) -> None:
        levels = tuple(item.level for item in self.level_assessments)
        if len(levels) != len(set(levels)):
            raise ScoringInputError("aggregation levels must be unique")
        if self.final_score is not None:
            _validate_decimal_range(
                self.final_score,
                MINIMUM_SCORE,
                MAXIMUM_SCORE,
                "final_score",
            )


@dataclass(frozen=True, slots=True)
class BoundaryRule:
    rule_id: str
    minimum: Decimal
    maximum: Decimal

    def __post_init__(self) -> None:
        _validate_non_empty(self.rule_id, "rule_id")
        _validate_decimal_range(self.minimum, MINIMUM_SCORE, MAXIMUM_SCORE, "minimum")
        _validate_decimal_range(self.maximum, MINIMUM_SCORE, MAXIMUM_SCORE, "maximum")
        if self.maximum < self.minimum:
            raise ScoringInputError("boundary maximum must be greater than or equal to minimum")


@dataclass(frozen=True, slots=True)
class RoutingPolicy:
    pass_minimum: Decimal
    waitlist_minimum: Decimal
    missing_critical_evidence: bool
    conflicting_critical_evidence: bool
    invalid_provider_output: bool
    disagreement_points: Decimal
    boundary_rules: tuple[BoundaryRule, ...]
    low_score_without_explicit_critical_unsatisfied: bool
    critical_unsatisfied_at_or_above_waitlist_threshold: bool
    reject_requires_explicit_unsatisfied_critical: bool

    def __post_init__(self) -> None:
        _validate_decimal_range(
            self.pass_minimum,
            MINIMUM_SCORE,
            MAXIMUM_SCORE,
            "pass_minimum",
        )
        _validate_decimal_range(
            self.waitlist_minimum,
            MINIMUM_SCORE,
            MAXIMUM_SCORE,
            "waitlist_minimum",
        )
        _validate_decimal_range(
            self.disagreement_points,
            MINIMUM_SCORE,
            MAXIMUM_SCORE,
            "disagreement_points",
        )
        if self.waitlist_minimum >= self.pass_minimum:
            raise ScoringInputError("waitlist_minimum must be lower than pass_minimum")
        if not self.boundary_rules:
            raise ScoringInputError("routing policy must contain at least one boundary rule")
        rule_ids = tuple(rule.rule_id for rule in self.boundary_rules)
        if len(rule_ids) != len(set(rule_ids)):
            raise ScoringInputError("boundary rules must have unique identifiers")


@dataclass(frozen=True, slots=True)
class RoutingResult:
    decision: ClassificationDecision
    final_score: Decimal | None
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        _validate_unique_non_empty(self.reasons, "reasons")
        if self.decision is ClassificationDecision.NEEDS_REVIEW:
            if not self.reasons:
                raise ScoringInputError("needs_review routing results require at least one reason")
        else:
            if self.reasons:
                raise ScoringInputError("non-review routing results must not include reasons")
            if self.final_score is None:
                raise ScoringInputError("non-review routing results require a final score")
        if self.final_score is not None:
            _validate_decimal_range(
                self.final_score,
                MINIMUM_SCORE,
                MAXIMUM_SCORE,
                "final_score",
            )
