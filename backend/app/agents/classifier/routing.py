from __future__ import annotations

from decimal import Decimal
from typing import Final

from backend.app.contracts import ClassificationDecision, EvidenceStatus, LevelScoreStatus
from backend.app.domain import (
    AggregationResult,
    RequirementAssessment,
    RoutingPolicy,
    RoutingResult,
    ScoringInputError,
    ScoringLevel,
)

MISSING_CRITICAL_EVIDENCE: Final[str] = "missing-critical-evidence"
CONFLICTING_CRITICAL_EVIDENCE: Final[str] = "conflicting-critical-evidence"
LOW_SCORE_WITHOUT_EXPLICIT_CRITICAL_UNSATISFIED: Final[str] = (
    "low-score-without-explicit-critical-unsatisfied"
)
CRITICAL_UNSATISFIED_AT_OR_ABOVE_WAITLIST_THRESHOLD: Final[str] = (
    "critical-unsatisfied-at-or-above-waitlist-threshold"
)
INVALID_PROVIDER_OUTPUT: Final[str] = "invalid-provider-output"
LARGE_LEVEL_DISAGREEMENT: Final[str] = "large-level-disagreement"
MISSING_FINAL_SCORE: Final[str] = "missing-final-score"


def _append_once(reasons: list[str], reason: str) -> None:
    if reason not in reasons:
        reasons.append(reason)


def _validate_requirement_assessments(
    assessments: tuple[RequirementAssessment, ...],
) -> None:
    if not assessments:
        raise ScoringInputError("routing requires critical requirement assessments")
    requirement_ids = tuple(item.requirement_id for item in assessments)
    if len(requirement_ids) != len(set(requirement_ids)):
        raise ScoringInputError("routing requirement assessments must have unique identifiers")


def _available_level_scores(aggregation: AggregationResult) -> tuple[Decimal, ...]:
    return tuple(
        item.score
        for item in aggregation.level_assessments
        if item.status is LevelScoreStatus.AVAILABLE and item.score is not None
    )


def route_classification(
    aggregation: AggregationResult,
    critical_requirement_assessments: tuple[RequirementAssessment, ...],
    policy: RoutingPolicy,
) -> RoutingResult:
    _validate_requirement_assessments(critical_requirement_assessments)
    statuses = {item.evidence_status for item in critical_requirement_assessments}
    final_score = aggregation.final_score
    reasons: list[str] = []

    if policy.missing_critical_evidence and EvidenceStatus.MISSING in statuses:
        _append_once(reasons, MISSING_CRITICAL_EVIDENCE)
    if policy.conflicting_critical_evidence and EvidenceStatus.CONFLICTING in statuses:
        _append_once(reasons, CONFLICTING_CRITICAL_EVIDENCE)
    if (
        policy.low_score_without_explicit_critical_unsatisfied
        and final_score is not None
        and final_score < policy.waitlist_minimum
        and EvidenceStatus.UNSATISFIED not in statuses
    ):
        _append_once(reasons, LOW_SCORE_WITHOUT_EXPLICIT_CRITICAL_UNSATISFIED)
    if (
        policy.critical_unsatisfied_at_or_above_waitlist_threshold
        and final_score is not None
        and final_score >= policy.waitlist_minimum
        and EvidenceStatus.UNSATISFIED in statuses
    ):
        _append_once(reasons, CRITICAL_UNSATISFIED_AT_OR_ABOVE_WAITLIST_THRESHOLD)

    provider_levels = {ScoringLevel.L2, ScoringLevel.L3}
    if policy.invalid_provider_output and any(
        item.level in provider_levels and item.status is not LevelScoreStatus.AVAILABLE
        for item in aggregation.level_assessments
    ):
        _append_once(reasons, INVALID_PROVIDER_OUTPUT)

    available_scores = _available_level_scores(aggregation)
    if (
        len(available_scores) >= 2
        and max(available_scores) - min(available_scores) >= policy.disagreement_points
    ):
        _append_once(reasons, LARGE_LEVEL_DISAGREEMENT)

    if final_score is not None:
        for boundary_rule in policy.boundary_rules:
            if boundary_rule.minimum <= final_score <= boundary_rule.maximum:
                _append_once(reasons, boundary_rule.rule_id)

    if final_score is None and not reasons:
        _append_once(reasons, MISSING_FINAL_SCORE)

    if reasons:
        return RoutingResult(
            decision=ClassificationDecision.NEEDS_REVIEW,
            final_score=final_score,
            reasons=tuple(reasons),
        )
    if final_score is None:
        raise ScoringInputError("routing cannot decide without a final score")
    if final_score >= policy.pass_minimum:
        return RoutingResult(
            decision=ClassificationDecision.PASS,
            final_score=final_score,
            reasons=(),
        )
    if final_score >= policy.waitlist_minimum:
        return RoutingResult(
            decision=ClassificationDecision.WAITLIST,
            final_score=final_score,
            reasons=(),
        )
    has_explicit_unsatisfied = EvidenceStatus.UNSATISFIED in statuses
    if policy.reject_requires_explicit_unsatisfied_critical and not has_explicit_unsatisfied:
        return RoutingResult(
            decision=ClassificationDecision.NEEDS_REVIEW,
            final_score=final_score,
            reasons=(LOW_SCORE_WITHOUT_EXPLICIT_CRITICAL_UNSATISFIED,),
        )
    return RoutingResult(
        decision=ClassificationDecision.REJECT,
        final_score=final_score,
        reasons=(),
    )
