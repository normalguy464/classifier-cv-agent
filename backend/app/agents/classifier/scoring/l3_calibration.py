from __future__ import annotations

from collections.abc import Mapping
from decimal import ROUND_HALF_UP, Decimal
from enum import StrEnum

from backend.app.contracts import EvidenceStatus, ScoringRubric

MANDATORY_CRITERION_ID = "mandatory-requirements"
L3_CALIBRATION_MAPPING_VERSION = "l3-deterministic-level-mapping-v1"
L3_CALIBRATION_MAPPING_V2 = "l3-deterministic-level-mapping-v2"
L3_CALIBRATION_MAPPING_V3 = "l3-deterministic-level-mapping-v3"


class L3CalibrationLevel(StrEnum):
    UNSUPPORTED = "unsupported"
    MINIMAL = "minimal"
    LIMITED = "limited"
    DEVELOPING = "developing"
    COMPETENT = "competent"
    STRONG = "strong"
    EXCEPTIONAL = "exceptional"


LEVEL_FACTORS: Mapping[L3CalibrationLevel, Decimal] = {
    L3CalibrationLevel.UNSUPPORTED: Decimal("0"),
    L3CalibrationLevel.MINIMAL: Decimal("0.20"),
    L3CalibrationLevel.LIMITED: Decimal("0.40"),
    L3CalibrationLevel.DEVELOPING: Decimal("0.60"),
    L3CalibrationLevel.COMPETENT: Decimal("0.75"),
    L3CalibrationLevel.STRONG: Decimal("0.85"),
    L3CalibrationLevel.EXCEPTIONAL: Decimal("1.00"),
}


def calibrated_l3_criterion_scores(
    rubric: ScoringRubric,
    requirement_statuses: Mapping[str, EvidenceStatus],
    criterion_levels: Mapping[str, L3CalibrationLevel],
    criterion_statuses: Mapping[str, EvidenceStatus],
    mapping_version: str = L3_CALIBRATION_MAPPING_VERSION,
) -> dict[str, Decimal]:
    expected_requirement_ids = set(rubric.critical_requirement_ids)
    expected_criterion_ids = {item.criterion_id for item in rubric.criteria}
    if set(requirement_statuses) != expected_requirement_ids:
        raise ValueError("L3 calibration requirement identifiers do not match the rubric")
    if set(criterion_levels) != expected_criterion_ids:
        raise ValueError("L3 calibration criterion level identifiers do not match the rubric")
    if set(criterion_statuses) != expected_criterion_ids:
        raise ValueError("L3 calibration criterion status identifiers do not match the rubric")
    if mapping_version not in {
        L3_CALIBRATION_MAPPING_VERSION,
        L3_CALIBRATION_MAPPING_V2,
        L3_CALIBRATION_MAPPING_V3,
    }:
        raise ValueError("unsupported L3 calibration mapping version")
    scores: dict[str, Decimal] = {}
    for criterion in rubric.criteria:
        level_factor = LEVEL_FACTORS[criterion_levels[criterion.criterion_id]]
        if criterion.criterion_id == MANDATORY_CRITERION_ID:
            factor = (
                _mandatory_factor_v3(tuple(requirement_statuses.values()), level_factor)
                if mapping_version == L3_CALIBRATION_MAPPING_V3
                else _mandatory_factor(tuple(requirement_statuses.values()), level_factor)
            )
        elif mapping_version in {L3_CALIBRATION_MAPPING_V2, L3_CALIBRATION_MAPPING_V3}:
            factor = _criterion_factor_v2(
                criterion_statuses[criterion.criterion_id],
                level_factor,
            )
        else:
            factor = min(
                level_factor,
                _criterion_status_cap(criterion_statuses[criterion.criterion_id]),
            )
        scores[criterion.criterion_id] = _round_to_half_point(criterion.weight * factor)
    return scores


def _mandatory_factor(
    statuses: tuple[EvidenceStatus, ...],
    level_factor: Decimal,
) -> Decimal:
    if statuses and all(status is EvidenceStatus.MISSING for status in statuses):
        return Decimal("0.47")
    if EvidenceStatus.UNSATISFIED in statuses:
        return Decimal("0.33")
    if EvidenceStatus.CONFLICTING in statuses:
        return Decimal("0.73")
    if EvidenceStatus.MISSING in statuses:
        return Decimal("0.67")
    return max(level_factor, Decimal("0.93"))


def _mandatory_factor_v3(
    statuses: tuple[EvidenceStatus, ...],
    level_factor: Decimal,
) -> Decimal:
    if statuses and all(status is EvidenceStatus.MISSING for status in statuses):
        return Decimal("0.47")
    if statuses and all(status is EvidenceStatus.UNSATISFIED for status in statuses):
        return Decimal("0.17")
    if EvidenceStatus.UNSATISFIED in statuses:
        return min(max(level_factor, Decimal("0.53")), Decimal("0.77"))
    if EvidenceStatus.CONFLICTING in statuses:
        return Decimal("0.73")
    if EvidenceStatus.MISSING in statuses:
        return Decimal("0.67")
    return max(level_factor, Decimal("0.93"))


def _criterion_status_cap(status: EvidenceStatus) -> Decimal:
    return {
        EvidenceStatus.MISSING: Decimal("0"),
        EvidenceStatus.UNSATISFIED: Decimal("0.35"),
        EvidenceStatus.CONFLICTING: Decimal("0.60"),
        EvidenceStatus.SATISFIED: Decimal("1"),
    }[status]


def _criterion_factor_v2(status: EvidenceStatus, level_factor: Decimal) -> Decimal:
    if status is EvidenceStatus.MISSING:
        return Decimal("0")
    if status is EvidenceStatus.UNSATISFIED:
        return min(max(level_factor, Decimal("0.40")), Decimal("0.55"))
    if status is EvidenceStatus.CONFLICTING:
        return min(max(level_factor, Decimal("0.50")), Decimal("0.70"))
    return level_factor


def _round_to_half_point(value: Decimal) -> Decimal:
    half_point = Decimal("0.5")
    return (value / half_point).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * half_point
