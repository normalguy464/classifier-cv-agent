from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from backend.app.agents.classifier.scoring.aggregation import (
    aggregate_level_scores,
    select_result_criterion_assessments,
)
from backend.app.contracts import (
    AggregationWeights,
    EvidenceStatus,
    LevelScoreStatus,
    RubricCriterion,
    ScoringRubric,
)
from backend.app.domain import (
    CriterionAssessment,
    LevelAssessment,
    RequirementAssessment,
    ScoringInputError,
    ScoringLevel,
)


def available(level: ScoringLevel, score: str) -> LevelAssessment:
    return LevelAssessment(
        level=level,
        status=LevelScoreStatus.AVAILABLE,
        score=Decimal(score),
    )


def standard_weights() -> AggregationWeights:
    return AggregationWeights(
        l1_deterministic_rules=Decimal("0.45"),
        l2_section_semantic_matching=Decimal("0.25"),
        l3_evidence_grounded_reasoning=Decimal("0.30"),
    )


def criterion_rubric() -> ScoringRubric:
    return ScoringRubric(
        rubric_id="rubric-aggregation-test",
        rubric_version="1.0.0",
        job_profile_id="job-aggregation-test",
        criteria=(
            RubricCriterion(
                criterion_id="mandatory-requirements",
                title="Mandatory requirements",
                description="Critical requirements.",
                weight=Decimal("30"),
            ),
            RubricCriterion(
                criterion_id="technical-skill",
                title="Technical skill",
                description="Technical evidence.",
                weight=Decimal("70"),
            ),
        ),
        critical_requirement_ids=("req-python",),
    )


def criterion(
    criterion_id: str,
    score: str,
    evidence_id: str,
) -> CriterionAssessment:
    return CriterionAssessment(
        criterion_id=criterion_id,
        weighted_score=Decimal(score),
        evidence_status=EvidenceStatus.SATISFIED,
        evidence_ids=(evidence_id,),
        rationale=f"Provider rationale for {criterion_id}.",
    )


def l1_with_requirements(
    *statuses: EvidenceStatus,
) -> LevelAssessment:
    assessments = tuple(
        RequirementAssessment(
            requirement_id=f"req-{index}",
            evidence_status=status,
            evidence_ids=(
                ()
                if status is EvidenceStatus.MISSING
                else (
                    (f"ev-{index}-first", f"ev-{index}-second")
                    if status is EvidenceStatus.CONFLICTING
                    else (f"ev-{index}",)
                )
            ),
            rationale="L1 requirement rationale.",
        )
        for index, status in enumerate(statuses, start=1)
    )
    return LevelAssessment(
        level=ScoringLevel.L1,
        status=LevelScoreStatus.AVAILABLE,
        score=Decimal("50"),
        requirement_assessments=assessments,
    )


def provider_level(
    level: ScoringLevel,
    mandatory_score: str,
    technical_score: str,
) -> LevelAssessment:
    return LevelAssessment(
        level=level,
        status=LevelScoreStatus.AVAILABLE,
        score=Decimal(mandatory_score) + Decimal(technical_score),
        criterion_assessments=(
            criterion("mandatory-requirements", mandatory_score, f"ev-{level}-mandatory"),
            criterion("technical-skill", technical_score, f"ev-{level}-technical"),
        ),
    )


def test_aggregation_applies_configured_level_weights() -> None:
    result = aggregate_level_scores(
        (
            available(ScoringLevel.L3, "90"),
            available(ScoringLevel.L1, "80"),
            available(ScoringLevel.L2, "60"),
        ),
        standard_weights(),
    )

    assert tuple(item.level for item in result.level_assessments) == tuple(ScoringLevel)
    assert result.final_score == Decimal("78.00")


def test_aggregation_rounds_half_up_to_two_decimal_places() -> None:
    weights = AggregationWeights(
        l1_deterministic_rules=Decimal("0.50"),
        l2_section_semantic_matching=Decimal("0.50"),
        l3_evidence_grounded_reasoning=Decimal("0"),
    )

    result = aggregate_level_scores(
        (
            available(ScoringLevel.L1, "0.01"),
            available(ScoringLevel.L2, "0"),
            available(ScoringLevel.L3, "0"),
        ),
        weights,
    )

    assert result.final_score == Decimal("0.01")


@pytest.mark.parametrize(
    "failed_level",
    [
        LevelAssessment.unavailable(ScoringLevel.L2, "Provider unavailable."),
        LevelAssessment.invalid(ScoringLevel.L3, "Invalid structured output."),
    ],
)
def test_aggregation_does_not_reweight_when_a_level_is_unavailable_or_invalid(
    failed_level: LevelAssessment,
) -> None:
    levels = {
        ScoringLevel.L1: available(ScoringLevel.L1, "80"),
        ScoringLevel.L2: available(ScoringLevel.L2, "70"),
        ScoringLevel.L3: available(ScoringLevel.L3, "90"),
    }
    levels[failed_level.level] = failed_level

    result = aggregate_level_scores(tuple(levels.values()), standard_weights())

    assert result.final_score is None


def test_aggregation_rejects_missing_and_duplicate_levels() -> None:
    l1 = available(ScoringLevel.L1, "80")
    l2 = available(ScoringLevel.L2, "70")

    with pytest.raises(ScoringInputError, match="exactly"):
        aggregate_level_scores((l1, l2), standard_weights())
    with pytest.raises(ScoringInputError, match="unique"):
        aggregate_level_scores((l1, l1, l2), standard_weights())


def test_level_and_aggregation_results_are_immutable_and_score_bounded() -> None:
    level = available(ScoringLevel.L1, "80")
    result = aggregate_level_scores(
        (
            level,
            available(ScoringLevel.L2, "70"),
            available(ScoringLevel.L3, "90"),
        ),
        standard_weights(),
    )

    with pytest.raises(FrozenInstanceError):
        level.score = Decimal("0")
    with pytest.raises(FrozenInstanceError):
        result.final_score = Decimal("0")
    with pytest.raises(ScoringInputError, match="between"):
        available(ScoringLevel.L1, "100.01")


def test_unavailable_and_invalid_levels_require_reason_and_forbid_scores() -> None:
    with pytest.raises(ScoringInputError, match="reason"):
        LevelAssessment(
            level=ScoringLevel.L2,
            status=LevelScoreStatus.UNAVAILABLE,
            score=None,
        )
    with pytest.raises(ScoringInputError, match="must not include a score"):
        LevelAssessment(
            level=ScoringLevel.L3,
            status=LevelScoreStatus.INVALID,
            score=Decimal("50"),
            reason="Invalid.",
        )


def test_criterion_selector_prefers_l3_and_discloses_provider_level_breakdown() -> None:
    selected = select_result_criterion_assessments(
        (
            l1_with_requirements(EvidenceStatus.SATISFIED),
            provider_level(ScoringLevel.L2, "20", "50"),
            provider_level(ScoringLevel.L3, "25", "60"),
        ),
        criterion_rubric(),
    )

    assert tuple(item.weighted_score for item in selected) == (
        Decimal("25"),
        Decimal("60"),
    )
    assert selected[0].evidence_ids == ("ev-1",)
    assert all(
        "not a decomposition of the hybrid final score" in item.rationale for item in selected
    )
    assert all("L3 provider-level" in item.rationale for item in selected)


def test_criterion_selector_uses_l2_when_l3_is_not_available() -> None:
    selected = select_result_criterion_assessments(
        (
            l1_with_requirements(EvidenceStatus.SATISFIED),
            provider_level(ScoringLevel.L2, "20", "50"),
            LevelAssessment.unavailable(ScoringLevel.L3, "Provider unavailable."),
        ),
        criterion_rubric(),
    )

    assert tuple(item.weighted_score for item in selected) == (
        Decimal("20"),
        Decimal("50"),
    )
    assert all("L2 provider-level" in item.rationale for item in selected)


@pytest.mark.parametrize(
    ("statuses", "expected_status", "expected_ids"),
    [
        (
            (EvidenceStatus.SATISFIED, EvidenceStatus.CONFLICTING),
            EvidenceStatus.CONFLICTING,
            ("ev-2-first", "ev-2-second"),
        ),
        (
            (EvidenceStatus.UNSATISFIED, EvidenceStatus.MISSING),
            EvidenceStatus.MISSING,
            (),
        ),
        (
            (EvidenceStatus.SATISFIED, EvidenceStatus.UNSATISFIED),
            EvidenceStatus.UNSATISFIED,
            ("ev-2",),
        ),
        (
            (EvidenceStatus.SATISFIED, EvidenceStatus.SATISFIED),
            EvidenceStatus.SATISFIED,
            ("ev-1", "ev-2"),
        ),
    ],
)
def test_mandatory_criterion_uses_explicit_l1_status_precedence(
    statuses: tuple[EvidenceStatus, ...],
    expected_status: EvidenceStatus,
    expected_ids: tuple[str, ...],
) -> None:
    selected = select_result_criterion_assessments(
        (
            l1_with_requirements(*statuses),
            provider_level(ScoringLevel.L2, "20", "50"),
            provider_level(ScoringLevel.L3, "25", "60"),
        ),
        criterion_rubric(),
    )

    assert selected[0].evidence_status is expected_status
    assert selected[0].evidence_ids == expected_ids


def test_criterion_selector_returns_empty_when_both_provider_levels_fail() -> None:
    selected = select_result_criterion_assessments(
        (
            l1_with_requirements(EvidenceStatus.SATISFIED),
            LevelAssessment.invalid(ScoringLevel.L2, "Invalid vectors."),
            LevelAssessment.unavailable(ScoringLevel.L3, "Provider unavailable."),
        ),
        criterion_rubric(),
    )

    assert selected == ()


def test_criterion_selector_rejects_incomplete_overweight_or_missing_l1_data() -> None:
    incomplete_l3 = LevelAssessment(
        level=ScoringLevel.L3,
        status=LevelScoreStatus.AVAILABLE,
        score=Decimal("25"),
        criterion_assessments=(criterion("mandatory-requirements", "25", "ev-l3-mandatory"),),
    )
    overweight_l3 = provider_level(ScoringLevel.L3, "31", "60")
    l1_without_requirements = available(ScoringLevel.L1, "50")

    with pytest.raises(ScoringInputError, match="exactly match"):
        select_result_criterion_assessments(
            (
                l1_with_requirements(EvidenceStatus.SATISFIED),
                provider_level(ScoringLevel.L2, "20", "50"),
                incomplete_l3,
            ),
            criterion_rubric(),
        )
    with pytest.raises(ScoringInputError, match="exceeds"):
        select_result_criterion_assessments(
            (
                l1_with_requirements(EvidenceStatus.SATISFIED),
                provider_level(ScoringLevel.L2, "20", "50"),
                overweight_l3,
            ),
            criterion_rubric(),
        )
    with pytest.raises(ScoringInputError, match="critical requirement"):
        select_result_criterion_assessments(
            (
                l1_without_requirements,
                provider_level(ScoringLevel.L2, "20", "50"),
                provider_level(ScoringLevel.L3, "25", "60"),
            ),
            criterion_rubric(),
        )
