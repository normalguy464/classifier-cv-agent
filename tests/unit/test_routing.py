from decimal import Decimal

import pytest

from backend.app.agents.classifier.routing import (
    CONFLICTING_CRITICAL_EVIDENCE,
    CRITICAL_UNSATISFIED_AT_OR_ABOVE_WAITLIST_THRESHOLD,
    INVALID_PROVIDER_OUTPUT,
    LARGE_LEVEL_DISAGREEMENT,
    LOW_SCORE_WITHOUT_EXPLICIT_CRITICAL_UNSATISFIED,
    MISSING_CRITICAL_EVIDENCE,
    MISSING_FINAL_SCORE,
    route_classification,
)
from backend.app.contracts import ClassificationDecision, EvidenceStatus, LevelScoreStatus
from backend.app.domain import (
    AggregationResult,
    BoundaryRule,
    LevelAssessment,
    RequirementAssessment,
    RoutingPolicy,
    ScoringInputError,
    ScoringLevel,
)


def available(level: ScoringLevel, score: str) -> LevelAssessment:
    return LevelAssessment(
        level=level,
        status=LevelScoreStatus.AVAILABLE,
        score=Decimal(score),
    )


def aggregation(
    final_score: str | None,
    level_scores: tuple[str, str, str] = ("70", "70", "70"),
) -> AggregationResult:
    return AggregationResult(
        level_assessments=(
            available(ScoringLevel.L1, level_scores[0]),
            available(ScoringLevel.L2, level_scores[1]),
            available(ScoringLevel.L3, level_scores[2]),
        ),
        final_score=None if final_score is None else Decimal(final_score),
    )


def requirement(
    status: EvidenceStatus,
    requirement_id: str = "req-python",
) -> RequirementAssessment:
    if status is EvidenceStatus.MISSING:
        evidence_ids: tuple[str, ...] = ()
    elif status is EvidenceStatus.CONFLICTING:
        evidence_ids = ("ev-first", "ev-second")
    else:
        evidence_ids = ("ev-first",)
    return RequirementAssessment(
        requirement_id=requirement_id,
        evidence_status=status,
        evidence_ids=evidence_ids,
        rationale="Requirement assessment.",
    )


def policy() -> RoutingPolicy:
    return RoutingPolicy(
        pass_minimum=Decimal("75"),
        waitlist_minimum=Decimal("60"),
        missing_critical_evidence=True,
        conflicting_critical_evidence=True,
        invalid_provider_output=True,
        disagreement_points=Decimal("25"),
        boundary_rules=(
            BoundaryRule(
                rule_id="lower-threshold-boundary",
                minimum=Decimal("58"),
                maximum=Decimal("62"),
            ),
            BoundaryRule(
                rule_id="upper-threshold-boundary",
                minimum=Decimal("73"),
                maximum=Decimal("77"),
            ),
        ),
        low_score_without_explicit_critical_unsatisfied=True,
        critical_unsatisfied_at_or_above_waitlist_threshold=True,
        reject_requires_explicit_unsatisfied_critical=True,
    )


@pytest.mark.parametrize(
    ("status", "reason"),
    [
        (EvidenceStatus.MISSING, MISSING_CRITICAL_EVIDENCE),
        (EvidenceStatus.CONFLICTING, CONFLICTING_CRITICAL_EVIDENCE),
    ],
)
def test_missing_and_conflicting_critical_evidence_take_review_precedence(
    status: EvidenceStatus,
    reason: str,
) -> None:
    result = route_classification(aggregation("90"), (requirement(status),), policy())

    assert result.decision is ClassificationDecision.NEEDS_REVIEW
    assert reason in result.reasons


def test_low_score_without_explicit_critical_failure_needs_review() -> None:
    result = route_classification(
        aggregation("57.99"),
        (requirement(EvidenceStatus.SATISFIED),),
        policy(),
    )

    assert result.decision is ClassificationDecision.NEEDS_REVIEW
    assert result.reasons == (LOW_SCORE_WITHOUT_EXPLICIT_CRITICAL_UNSATISFIED,)


@pytest.mark.parametrize("score", ["60", "63", "78", "100"])
def test_explicit_critical_failure_at_or_above_waitlist_needs_review(score: str) -> None:
    result = route_classification(
        aggregation(score),
        (requirement(EvidenceStatus.UNSATISFIED),),
        policy(),
    )

    assert result.decision is ClassificationDecision.NEEDS_REVIEW
    assert CRITICAL_UNSATISFIED_AT_OR_ABOVE_WAITLIST_THRESHOLD in result.reasons


@pytest.mark.parametrize(
    ("score", "expected_reason"),
    [
        ("58", "lower-threshold-boundary"),
        ("62", "lower-threshold-boundary"),
        ("73", "upper-threshold-boundary"),
        ("77", "upper-threshold-boundary"),
    ],
)
def test_boundary_bands_are_inclusive(score: str, expected_reason: str) -> None:
    result = route_classification(
        aggregation(score),
        (requirement(EvidenceStatus.SATISFIED),),
        policy(),
    )

    assert result.decision is ClassificationDecision.NEEDS_REVIEW
    assert expected_reason in result.reasons


@pytest.mark.parametrize(
    ("score", "status", "decision"),
    [
        ("57.99", EvidenceStatus.UNSATISFIED, ClassificationDecision.REJECT),
        ("62.01", EvidenceStatus.SATISFIED, ClassificationDecision.WAITLIST),
        ("72.99", EvidenceStatus.SATISFIED, ClassificationDecision.WAITLIST),
        ("77.01", EvidenceStatus.SATISFIED, ClassificationDecision.PASS),
        ("100", EvidenceStatus.SATISFIED, ClassificationDecision.PASS),
    ],
)
def test_scores_immediately_outside_review_bands_route_normally(
    score: str,
    status: EvidenceStatus,
    decision: ClassificationDecision,
) -> None:
    result = route_classification(aggregation(score), (requirement(status),), policy())

    assert result.decision is decision
    assert result.reasons == ()


def test_invalid_or_unavailable_l2_or_l3_needs_review() -> None:
    levels = (
        available(ScoringLevel.L1, "80"),
        LevelAssessment.invalid(ScoringLevel.L2, "Invalid vectors."),
        LevelAssessment.unavailable(ScoringLevel.L3, "Provider unavailable."),
    )
    result = route_classification(
        AggregationResult(level_assessments=levels, final_score=None),
        (requirement(EvidenceStatus.SATISFIED),),
        policy(),
    )

    assert result.decision is ClassificationDecision.NEEDS_REVIEW
    assert result.reasons == (INVALID_PROVIDER_OUTPUT,)


def test_level_disagreement_at_exact_threshold_needs_review() -> None:
    result = route_classification(
        aggregation("75", ("50", "75", "60")),
        (requirement(EvidenceStatus.SATISFIED),),
        policy(),
    )

    assert result.decision is ClassificationDecision.NEEDS_REVIEW
    assert LARGE_LEVEL_DISAGREEMENT in result.reasons


def test_disagreement_just_below_threshold_does_not_trigger_review() -> None:
    result = route_classification(
        aggregation("70", ("50.01", "75", "60")),
        (requirement(EvidenceStatus.SATISFIED),),
        policy(),
    )

    assert result.decision is ClassificationDecision.WAITLIST
    assert LARGE_LEVEL_DISAGREEMENT not in result.reasons


def test_missing_final_score_is_safe_even_when_provider_rule_is_disabled() -> None:
    disabled_provider_policy = RoutingPolicy(
        pass_minimum=Decimal("75"),
        waitlist_minimum=Decimal("60"),
        missing_critical_evidence=True,
        conflicting_critical_evidence=True,
        invalid_provider_output=False,
        disagreement_points=Decimal("25"),
        boundary_rules=policy().boundary_rules,
        low_score_without_explicit_critical_unsatisfied=True,
        critical_unsatisfied_at_or_above_waitlist_threshold=True,
        reject_requires_explicit_unsatisfied_critical=True,
    )
    levels = (
        available(ScoringLevel.L1, "80"),
        LevelAssessment.unavailable(ScoringLevel.L2, "Unavailable."),
        available(ScoringLevel.L3, "80"),
    )

    result = route_classification(
        AggregationResult(level_assessments=levels, final_score=None),
        (requirement(EvidenceStatus.SATISFIED),),
        disabled_provider_policy,
    )

    assert result.decision is ClassificationDecision.NEEDS_REVIEW
    assert result.reasons == (MISSING_FINAL_SCORE,)


def test_routing_collects_review_reasons_in_policy_precedence_order() -> None:
    assessments = (
        requirement(EvidenceStatus.MISSING, "req-python"),
        requirement(EvidenceStatus.CONFLICTING, "req-sql"),
    )

    result = route_classification(
        aggregation("60", ("40", "70", "70")),
        assessments,
        policy(),
    )

    assert result.reasons == (
        MISSING_CRITICAL_EVIDENCE,
        CONFLICTING_CRITICAL_EVIDENCE,
        LARGE_LEVEL_DISAGREEMENT,
        "lower-threshold-boundary",
    )


def test_routing_rejects_empty_or_duplicate_requirement_assessments() -> None:
    assessment = requirement(EvidenceStatus.SATISFIED)

    with pytest.raises(ScoringInputError, match="requires"):
        route_classification(aggregation("80"), (), policy())
    with pytest.raises(ScoringInputError, match="unique"):
        route_classification(aggregation("80"), (assessment, assessment), policy())


def test_routing_policy_rejects_invalid_thresholds_and_boundary_ranges() -> None:
    with pytest.raises(ScoringInputError, match="lower"):
        RoutingPolicy(
            pass_minimum=Decimal("60"),
            waitlist_minimum=Decimal("60"),
            missing_critical_evidence=True,
            conflicting_critical_evidence=True,
            invalid_provider_output=True,
            disagreement_points=Decimal("25"),
            boundary_rules=policy().boundary_rules,
            low_score_without_explicit_critical_unsatisfied=True,
            critical_unsatisfied_at_or_above_waitlist_threshold=True,
            reject_requires_explicit_unsatisfied_critical=True,
        )
    with pytest.raises(ScoringInputError, match="maximum"):
        BoundaryRule(
            rule_id="invalid-band",
            minimum=Decimal("62"),
            maximum=Decimal("58"),
        )
