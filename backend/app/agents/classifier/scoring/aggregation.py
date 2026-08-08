from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Final

from backend.app.contracts import (
    AggregationWeights,
    EvidenceStatus,
    LevelScoreStatus,
    ScoringRubric,
)
from backend.app.domain import (
    AggregationResult,
    CriterionAssessment,
    LevelAssessment,
    RequirementAssessment,
    ScoringInputError,
    ScoringLevel,
)

SCORE_QUANTUM: Final[Decimal] = Decimal("0.01")
REQUIRED_LEVELS: Final[frozenset[ScoringLevel]] = frozenset(
    {ScoringLevel.L1, ScoringLevel.L2, ScoringLevel.L3}
)
REQUIREMENT_STATUS_PRECEDENCE: Final[tuple[EvidenceStatus, ...]] = (
    EvidenceStatus.CONFLICTING,
    EvidenceStatus.MISSING,
    EvidenceStatus.UNSATISFIED,
    EvidenceStatus.SATISFIED,
)


def aggregate_level_scores(
    level_assessments: tuple[LevelAssessment, ...],
    weights: AggregationWeights,
) -> AggregationResult:
    levels_by_id = {item.level: item for item in level_assessments}
    if len(levels_by_id) != len(level_assessments):
        raise ScoringInputError("aggregation requires unique level assessments")
    if frozenset(levels_by_id) != REQUIRED_LEVELS:
        raise ScoringInputError("aggregation requires exactly L1, L2 and L3 assessments")
    ordered = tuple(levels_by_id[level] for level in ScoringLevel)
    if any(item.status is not LevelScoreStatus.AVAILABLE for item in ordered):
        return AggregationResult(level_assessments=ordered, final_score=None)
    level_weights = {
        ScoringLevel.L1: weights.l1_deterministic_rules,
        ScoringLevel.L2: weights.l2_section_semantic_matching,
        ScoringLevel.L3: weights.l3_evidence_grounded_reasoning,
    }
    raw_score = sum(
        (item.score * level_weights[item.level] for item in ordered if item.score is not None),
        Decimal("0"),
    )
    final_score = raw_score.quantize(SCORE_QUANTUM, rounding=ROUND_HALF_UP)
    return AggregationResult(level_assessments=ordered, final_score=final_score)


def _select_provider_level(
    levels_by_id: dict[ScoringLevel, LevelAssessment],
) -> LevelAssessment | None:
    l3 = levels_by_id.get(ScoringLevel.L3)
    if l3 is not None and l3.status is LevelScoreStatus.AVAILABLE:
        if not l3.criterion_assessments:
            raise ScoringInputError("available L3 assessment must include criterion assessments")
        return l3
    l2 = levels_by_id.get(ScoringLevel.L2)
    if l2 is not None and l2.status is LevelScoreStatus.AVAILABLE:
        if not l2.criterion_assessments:
            raise ScoringInputError("available L2 assessment must include criterion assessments")
        return l2
    return None


def _mandatory_status(
    assessments: tuple[RequirementAssessment, ...],
) -> EvidenceStatus:
    if not assessments:
        raise ScoringInputError(
            "mandatory criterion selection requires L1 critical requirement assessments"
        )
    statuses = {item.evidence_status for item in assessments}
    return next(status for status in REQUIREMENT_STATUS_PRECEDENCE if status in statuses)


def _mandatory_evidence_ids(
    assessments: tuple[RequirementAssessment, ...],
    status: EvidenceStatus,
) -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                evidence_id
                for assessment in assessments
                if assessment.evidence_status is status
                for evidence_id in assessment.evidence_ids
            }
        )
    )


def select_result_criterion_assessments(
    level_assessments: tuple[LevelAssessment, ...],
    rubric: ScoringRubric,
    mandatory_criterion_id: str = "mandatory-requirements",
) -> tuple[CriterionAssessment, ...]:
    levels_by_id = {item.level: item for item in level_assessments}
    if len(levels_by_id) != len(level_assessments):
        raise ScoringInputError("criterion selection requires unique level assessments")
    provider_level = _select_provider_level(levels_by_id)
    if provider_level is None:
        return ()
    criteria_by_id = {item.criterion_id: item for item in rubric.criteria}
    if mandatory_criterion_id not in criteria_by_id:
        raise ScoringInputError("mandatory criterion identifier is not present in the rubric")
    provider_assessments = {
        item.criterion_id: item for item in provider_level.criterion_assessments
    }
    if set(provider_assessments) != set(criteria_by_id):
        raise ScoringInputError("provider criterion assessments must exactly match rubric criteria")
    l1 = levels_by_id.get(ScoringLevel.L1)
    if l1 is None or l1.status is not LevelScoreStatus.AVAILABLE:
        raise ScoringInputError("mandatory criterion selection requires an available L1 assessment")
    mandatory_status = _mandatory_status(l1.requirement_assessments)
    mandatory_evidence_ids = _mandatory_evidence_ids(
        l1.requirement_assessments,
        mandatory_status,
    )
    source_label = provider_level.level.value.upper()
    disclosure = (
        f"This is a {source_label} provider-level criterion breakdown and not a decomposition "
        "of the hybrid final score."
    )
    selected: list[CriterionAssessment] = []
    for rubric_criterion in rubric.criteria:
        provider_assessment = provider_assessments[rubric_criterion.criterion_id]
        if provider_assessment.weighted_score > rubric_criterion.weight:
            raise ScoringInputError(
                f"provider criterion score exceeds rubric weight: {rubric_criterion.criterion_id}"
            )
        if rubric_criterion.criterion_id == mandatory_criterion_id:
            selected.append(
                CriterionAssessment(
                    criterion_id=provider_assessment.criterion_id,
                    weighted_score=provider_assessment.weighted_score,
                    evidence_status=mandatory_status,
                    evidence_ids=mandatory_evidence_ids,
                    rationale=(
                        f"{provider_assessment.rationale} {disclosure} "
                        "Mandatory evidence status and references are derived from L1 critical "
                        "requirement assessments."
                    ),
                )
            )
            continue
        selected.append(
            CriterionAssessment(
                criterion_id=provider_assessment.criterion_id,
                weighted_score=provider_assessment.weighted_score,
                evidence_status=provider_assessment.evidence_status,
                evidence_ids=provider_assessment.evidence_ids,
                rationale=f"{provider_assessment.rationale} {disclosure}",
            )
        )
    return tuple(selected)
