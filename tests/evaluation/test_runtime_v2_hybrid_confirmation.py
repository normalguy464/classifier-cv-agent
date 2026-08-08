from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from evaluation.experiments.run_runtime_v2_hybrid_confirmation import (
    HybridConfirmationConfiguration,
    build_report,
    load_configuration,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
V2_CONFIGURATION_PATH = Path("evaluation/configs/runtime_v2_hybrid_fresh_confirmation_v2.yaml")


def test_runtime_v2_hybrid_confirmation_is_offline_and_does_not_select() -> None:
    configuration = load_configuration(REPOSITORY_ROOT)

    assert configuration.development_selection_allowed is False
    assert configuration.validation_access_allowed is False
    assert configuration.stage7_v1_test_allowed is False
    assert configuration.llm_provider_calls_allowed is False
    assert configuration.selected_candidate.candidate_id == "hybrid-v2-20-30-50"


def test_runtime_v2_hybrid_confirmation_is_deterministic() -> None:
    generated_at = datetime.fromisoformat("2026-08-08T22:30:00+07:00")

    first = build_report(REPOSITORY_ROOT, generated_at)
    second = build_report(REPOSITORY_ROOT, generated_at)

    assert first == second
    assert first["development_selection_performed"] is False
    assert first["validation_accessed"] is False
    assert first["llm_provider_calls_made"] is False
    assert first["stage7_v1_test_accessed"] is False
    assert first["confirmation"]["sample_count"] == 10


def test_runtime_v2_hybrid_confirmation_rejects_validation_access() -> None:
    payload = load_configuration(REPOSITORY_ROOT).model_dump(mode="python")
    payload["validation_access_allowed"] = True

    with pytest.raises(ValidationError):
        HybridConfirmationConfiguration.model_validate(payload)


def test_runtime_v2_hybrid_confirmation_v2_uses_mapping_v3_report() -> None:
    configuration = load_configuration(REPOSITORY_ROOT, V2_CONFIGURATION_PATH)
    report = build_report(
        REPOSITORY_ROOT,
        datetime.fromisoformat("2026-08-08T23:40:00+07:00"),
        V2_CONFIGURATION_PATH,
    )

    assert configuration.experiment_version == "2.0.0"
    assert configuration.selected_candidate.candidate_id == "hybrid-v5-pass82"
    assert report["confirmation"]["sample_count"] == 10
    assert report["validation_accessed"] is False
