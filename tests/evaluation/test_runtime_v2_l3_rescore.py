from __future__ import annotations

from datetime import datetime
from pathlib import Path

from evaluation.experiments.run_runtime_v2_l3_rescore import build_rescore_report

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def test_runtime_v2_l3_rescore_is_deterministic_and_offline() -> None:
    generated_at = datetime.fromisoformat("2026-08-08T23:30:00+07:00")

    first = build_rescore_report(REPOSITORY_ROOT, generated_at)
    second = build_rescore_report(REPOSITORY_ROOT, generated_at)

    assert first == second
    assert first["score_mapping_version"] == "l3-deterministic-level-mapping-v3"
    assert first["llm_provider_calls_made"] is False
    assert first["valid_output_count"] == 10
    assert first["traceability"]["source_experiment_id"] == ("runtime-v2-l3-fresh-confirmation-v2")


def test_runtime_v2_l3_rescore_supports_prior_development_panels() -> None:
    generated_at = datetime.fromisoformat("2026-08-08T23:35:00+07:00")
    cases = (
        (
            Path("evaluation/configs/runtime_v2_l3_development_panel_v2_rescore_v3.yaml"),
            Path("evaluation/reports/generated/runtime_v2_l3_development_panel_cache_v2.json"),
            20,
        ),
        (
            Path("evaluation/configs/runtime_v2_l3_fresh_confirmation_v1_rescore_v3.yaml"),
            Path(
                "evaluation/reports/generated/"
                "runtime_v2_l3_fresh_confirmation_cache_v1_network_retry.json"
            ),
            10,
        ),
    )

    for configuration_path, cache_path, expected_count in cases:
        report = build_rescore_report(
            REPOSITORY_ROOT,
            generated_at,
            configuration_path,
            cache_path,
        )
        assert report["valid_output_count"] == expected_count
        assert report["llm_provider_calls_made"] is False
