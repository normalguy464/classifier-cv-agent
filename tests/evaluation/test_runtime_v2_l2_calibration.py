from datetime import datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from evaluation.experiments.train_runtime_v2_l2_calibrator import (
    CalibrationConfiguration,
    load_calibration_configuration,
    train_l2_calibrator,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def test_l2_calibration_configuration_separates_training_and_selection() -> None:
    configuration = load_calibration_configuration(REPOSITORY_ROOT)

    assert configuration.training_partition == "development"
    assert configuration.selection_partition == "validation"
    assert configuration.stage7_v1_test_allowed is False
    assert configuration.llm_provider_calls_allowed is False
    assert configuration.selected_candidate_id == "extra-trees-leaf3-v1"


def test_l2_calibration_configuration_rejects_validation_training() -> None:
    payload = load_calibration_configuration(REPOSITORY_ROOT).model_dump(mode="python")
    payload["training_partition"] = "validation"

    with pytest.raises(ValidationError):
        CalibrationConfiguration.model_validate(payload)


def test_l2_calibrator_is_deterministic_and_passes_without_persisting() -> None:
    generated_at = datetime.fromisoformat("2026-08-08T07:00:00+07:00")

    first = train_l2_calibrator(REPOSITORY_ROOT, generated_at, persist_model=False)
    second = train_l2_calibrator(REPOSITORY_ROOT, generated_at, persist_model=False)

    assert first == second
    assert first["llm_provider_calls_made"] is False
    assert first["stage7_v1_test_accessed"] is False
    assert first["selection_passed"] is True
    assert first["model_artifact"]["trained_on_validation"] is False
