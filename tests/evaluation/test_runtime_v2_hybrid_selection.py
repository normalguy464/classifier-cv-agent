from __future__ import annotations

from datetime import datetime
from pathlib import Path

from evaluation.experiments.run_runtime_v2_hybrid_selection import (
    _timestamp,
    build_report,
    load_configuration,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEVELOPMENT_TUNING_PATH = Path("evaluation/configs/runtime_v2_hybrid_development_tuning_v2.yaml")
THRESHOLD_TUNING_PATH = Path("evaluation/configs/runtime_v2_hybrid_threshold_tuning_v3.yaml")
OFFSET_TUNING_PATH = Path("evaluation/configs/runtime_v2_hybrid_offset_tuning_v4.yaml")
EXPANDED_DEVELOPMENT_PATH = Path(
    "evaluation/configs/runtime_v2_hybrid_expanded_development_v5.yaml"
)
WAITLIST_TUNING_PATH = Path("evaluation/configs/runtime_v2_hybrid_waitlist_tuning_v6.yaml")


def test_runtime_v2_hybrid_selection_is_offline_and_bounded() -> None:
    configuration = load_configuration(REPOSITORY_ROOT)

    assert configuration.llm_provider_calls_allowed is False
    assert configuration.stage7_v1_test_allowed is False
    assert len(configuration.candidates) == 2
    assert {item.disagreement_points for item in configuration.candidates} == {35, 45}


def test_runtime_v2_hybrid_selection_is_deterministic() -> None:
    generated_at = datetime.fromisoformat("2026-08-08T21:00:00+07:00")

    first = build_report(REPOSITORY_ROOT, generated_at)
    second = build_report(REPOSITORY_ROOT, generated_at)

    assert first == second
    assert first["llm_provider_calls_made"] is False
    assert first["stage7_v1_test_accessed"] is False
    assert len(first["development_candidates"]) == 2
    assert first["validation"]["sample_count"] == 25


def test_runtime_v2_hybrid_tuning_does_not_read_validation() -> None:
    configuration = load_configuration(REPOSITORY_ROOT, DEVELOPMENT_TUNING_PATH)
    report = build_report(
        REPOSITORY_ROOT,
        datetime.fromisoformat("2026-08-08T21:30:00+07:00"),
        DEVELOPMENT_TUNING_PATH,
    )

    assert configuration.validation_evaluation_allowed is False
    assert len(configuration.candidates) == 4
    assert report["validation"] is None
    assert report["traceability"]["validation_l3_report_sha256"] is None


def test_runtime_v2_hybrid_timestamp_requires_timezone() -> None:
    try:
        _timestamp("2026-08-08T21:30:00")
    except ValueError as error:
        assert str(error) == "generated_at must include a timezone"
    else:
        raise AssertionError("timezone-free timestamp was accepted")


def test_runtime_v2_hybrid_threshold_tuning_is_development_only() -> None:
    configuration = load_configuration(REPOSITORY_ROOT, THRESHOLD_TUNING_PATH)
    report = build_report(
        REPOSITORY_ROOT,
        datetime.fromisoformat("2026-08-08T22:40:00+07:00"),
        THRESHOLD_TUNING_PATH,
    )

    assert configuration.experiment_id == "runtime-v2-hybrid-threshold-tuning-v3"
    assert configuration.validation_evaluation_allowed is False
    assert len(configuration.candidates) == 6
    assert report["validation"] is None
    assert report["llm_provider_calls_made"] is False


def test_runtime_v2_hybrid_offset_tuning_is_bounded_and_development_only() -> None:
    configuration = load_configuration(REPOSITORY_ROOT, OFFSET_TUNING_PATH)
    report = build_report(
        REPOSITORY_ROOT,
        datetime.fromisoformat("2026-08-08T22:50:00+07:00"),
        OFFSET_TUNING_PATH,
    )

    assert configuration.experiment_id == "runtime-v2-hybrid-offset-tuning-v4"
    assert configuration.validation_evaluation_allowed is False
    assert {item.l3_score_offset for item in configuration.candidates} == {
        0,
        5,
        8,
        10,
        12,
        15,
    }
    assert report["validation"] is None


def test_runtime_v2_hybrid_expanded_development_uses_disjoint_l3_panels() -> None:
    configuration = load_configuration(REPOSITORY_ROOT, EXPANDED_DEVELOPMENT_PATH)
    report = build_report(
        REPOSITORY_ROOT,
        datetime.fromisoformat("2026-08-08T23:00:00+07:00"),
        EXPANDED_DEVELOPMENT_PATH,
    )

    assert configuration.validation_evaluation_allowed is False
    assert len(configuration.additional_development_l3_report_paths) == 1
    assert all(item["sample_count"] == 30 for item in report["development_candidates"])
    assert report["validation"] is None


def test_runtime_v2_hybrid_waitlist_tuning_uses_mapping_v3_panels_only() -> None:
    configuration = load_configuration(REPOSITORY_ROOT, WAITLIST_TUNING_PATH)
    report = build_report(
        REPOSITORY_ROOT,
        datetime.fromisoformat("2026-08-08T23:50:00+07:00"),
        WAITLIST_TUNING_PATH,
    )

    assert configuration.experiment_id == "runtime-v2-hybrid-waitlist-tuning-v6"
    assert len(configuration.additional_development_l3_report_paths) == 2
    assert all(
        "rescore_v3" in path.name
        for path in (
            configuration.development_l3_report_path,
            *configuration.additional_development_l3_report_paths,
        )
    )
    assert all(item["sample_count"] == 40 for item in report["development_candidates"])
    assert report["validation"] is None
