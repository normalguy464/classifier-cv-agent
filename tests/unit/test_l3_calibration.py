from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from backend.app.agents.classifier.scoring import (
    L3CalibrationLevel,
    calibrated_l3_criterion_scores,
)
from backend.app.agents.classifier.scoring.l3_calibration import (
    L3_CALIBRATION_MAPPING_V2,
    L3_CALIBRATION_MAPPING_V3,
)
from backend.app.contracts import EvidenceStatus
from backend.app.infrastructure.config import RepositoryConfigurationLoader

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def _rubric():
    return (
        RepositoryConfigurationLoader(REPOSITORY_ROOT).load_for_job("junior-data-analyst-v1").rubric
    )


def _criterion_levels(level: L3CalibrationLevel) -> dict[str, L3CalibrationLevel]:
    return {item.criterion_id: level for item in _rubric().criteria}


def _criterion_statuses(status: EvidenceStatus) -> dict[str, EvidenceStatus]:
    return {item.criterion_id: status for item in _rubric().criteria}


def _requirement_statuses(status: EvidenceStatus) -> dict[str, EvidenceStatus]:
    return {item: status for item in _rubric().critical_requirement_ids}


def test_l3_calibration_maps_all_satisfied_developing_evidence_deterministically() -> None:
    scores = calibrated_l3_criterion_scores(
        _rubric(),
        _requirement_statuses(EvidenceStatus.SATISFIED),
        _criterion_levels(L3CalibrationLevel.DEVELOPING),
        _criterion_statuses(EvidenceStatus.SATISFIED),
    )

    assert scores == {
        "mandatory-requirements": Decimal("28.0"),
        "technical-analysis": Decimal("15.0"),
        "analytical-reasoning": Decimal("12.0"),
        "projects-and-impact": Decimal("9.0"),
        "communication-and-evidence-quality": Decimal("6.0"),
    }
    assert sum(scores.values()) == Decimal("70.0")


@pytest.mark.parametrize(
    ("statuses", "expected_mandatory_score"),
    [
        (
            {
                "da-sql": EvidenceStatus.UNSATISFIED,
                "da-analysis-language": EvidenceStatus.SATISFIED,
                "da-analytical-project": EvidenceStatus.SATISFIED,
            },
            Decimal("10.0"),
        ),
        (
            {
                "da-sql": EvidenceStatus.MISSING,
                "da-analysis-language": EvidenceStatus.SATISFIED,
                "da-analytical-project": EvidenceStatus.SATISFIED,
            },
            Decimal("20.0"),
        ),
        (
            {
                "da-sql": EvidenceStatus.CONFLICTING,
                "da-analysis-language": EvidenceStatus.SATISFIED,
                "da-analytical-project": EvidenceStatus.SATISFIED,
            },
            Decimal("22.0"),
        ),
        (_requirement_statuses(EvidenceStatus.MISSING), Decimal("14.0")),
    ],
)
def test_l3_calibration_applies_critical_requirement_status_policy(
    statuses: dict[str, EvidenceStatus],
    expected_mandatory_score: Decimal,
) -> None:
    scores = calibrated_l3_criterion_scores(
        _rubric(),
        statuses,
        _criterion_levels(L3CalibrationLevel.EXCEPTIONAL),
        _criterion_statuses(EvidenceStatus.SATISFIED),
    )

    assert scores["mandatory-requirements"] == expected_mandatory_score


def test_l3_calibration_caps_missing_criterion_at_zero() -> None:
    criterion_statuses = _criterion_statuses(EvidenceStatus.SATISFIED)
    criterion_statuses["technical-analysis"] = EvidenceStatus.MISSING
    scores = calibrated_l3_criterion_scores(
        _rubric(),
        _requirement_statuses(EvidenceStatus.SATISFIED),
        _criterion_levels(L3CalibrationLevel.EXCEPTIONAL),
        criterion_statuses,
    )

    assert scores["technical-analysis"] == Decimal("0.0")
    assert scores["mandatory-requirements"] == Decimal("30.0")


@pytest.mark.parametrize(
    ("status", "level", "expected"),
    [
        (EvidenceStatus.MISSING, L3CalibrationLevel.EXCEPTIONAL, Decimal("0.0")),
        (EvidenceStatus.UNSATISFIED, L3CalibrationLevel.UNSUPPORTED, Decimal("10.0")),
        (EvidenceStatus.UNSATISFIED, L3CalibrationLevel.EXCEPTIONAL, Decimal("14.0")),
        (EvidenceStatus.CONFLICTING, L3CalibrationLevel.UNSUPPORTED, Decimal("12.5")),
        (EvidenceStatus.CONFLICTING, L3CalibrationLevel.EXCEPTIONAL, Decimal("17.5")),
        (EvidenceStatus.SATISFIED, L3CalibrationLevel.DEVELOPING, Decimal("15.0")),
    ],
)
def test_l3_calibration_v2_applies_bounded_evidence_status_floors(
    status: EvidenceStatus,
    level: L3CalibrationLevel,
    expected: Decimal,
) -> None:
    criterion_statuses = _criterion_statuses(EvidenceStatus.SATISFIED)
    criterion_statuses["technical-analysis"] = status
    criterion_levels = _criterion_levels(L3CalibrationLevel.DEVELOPING)
    criterion_levels["technical-analysis"] = level

    scores = calibrated_l3_criterion_scores(
        _rubric(),
        _requirement_statuses(EvidenceStatus.SATISFIED),
        criterion_levels,
        criterion_statuses,
        L3_CALIBRATION_MAPPING_V2,
    )

    assert scores["technical-analysis"] == expected


@pytest.mark.parametrize(
    ("statuses", "level", "expected"),
    [
        (
            {
                "da-sql": EvidenceStatus.UNSATISFIED,
                "da-analysis-language": EvidenceStatus.SATISFIED,
                "da-analytical-project": EvidenceStatus.SATISFIED,
            },
            L3CalibrationLevel.DEVELOPING,
            Decimal("18.0"),
        ),
        (
            _requirement_statuses(EvidenceStatus.UNSATISFIED),
            L3CalibrationLevel.EXCEPTIONAL,
            Decimal("5.0"),
        ),
    ],
)
def test_l3_calibration_v3_avoids_double_penalizing_partial_unsatisfied_requirements(
    statuses: dict[str, EvidenceStatus],
    level: L3CalibrationLevel,
    expected: Decimal,
) -> None:
    levels = _criterion_levels(L3CalibrationLevel.DEVELOPING)
    levels["mandatory-requirements"] = level

    scores = calibrated_l3_criterion_scores(
        _rubric(),
        statuses,
        levels,
        _criterion_statuses(EvidenceStatus.SATISFIED),
        L3_CALIBRATION_MAPPING_V3,
    )

    assert scores["mandatory-requirements"] == expected


def test_l3_calibration_rejects_missing_criterion_identifier() -> None:
    levels = _criterion_levels(L3CalibrationLevel.DEVELOPING)
    levels.pop("technical-analysis")

    with pytest.raises(ValueError, match="criterion level identifiers"):
        calibrated_l3_criterion_scores(
            _rubric(),
            _requirement_statuses(EvidenceStatus.SATISFIED),
            levels,
            _criterion_statuses(EvidenceStatus.SATISFIED),
        )
