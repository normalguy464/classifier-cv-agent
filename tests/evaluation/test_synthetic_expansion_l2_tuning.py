import asyncio
import json
from datetime import datetime
from pathlib import Path

import pytest

from backend.app.infrastructure.embeddings import HashingEmbeddingAdapter
from evaluation.experiments.run_synthetic_expansion_v2_diagnostic import (
    ExpansionEmbeddingRuntime,
)
from evaluation.experiments.run_synthetic_expansion_v2_l2_tuning import (
    _timestamp,
    run,
    write_report,
)
from evaluation.experiments.synthetic_expansion_l2_config import (
    REMEDIATED_CONFIG_PATH,
    REMEDIATED_V2_3_CONFIG_PATH,
    REMEDIATED_V2_3_1_CONFIG_PATH,
    load_expansion_l2_candidate_set,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
GENERATED_AT = datetime.fromisoformat("2026-07-31T22:00:00+07:00")


def _runtime() -> ExpansionEmbeddingRuntime:
    return ExpansionEmbeddingRuntime(
        adapter=HashingEmbeddingAdapter(dimension=128),
        model_identifier="deterministic-hashing-embedding",
        model_version="test-v1",
        resolved_revision="0" * 40,
        configured_model_executed=False,
    )


def test_l2_candidate_configuration_is_versioned_and_complete() -> None:
    candidate_set = load_expansion_l2_candidate_set(REPOSITORY_ROOT)

    assert candidate_set.candidate_set_version == "1.1.0"
    assert len(candidate_set.candidates) == 6
    assert candidate_set.development_partition_id == ("synthetic-expansion-v2-development-silver")
    assert candidate_set.held_out_partition_id == "synthetic-expansion-v2-held-out-silver"


def test_l2_tuning_runs_all_candidates_on_development_only() -> None:
    report = asyncio.run(run(REPOSITORY_ROOT, GENERATED_AT, _runtime()))

    traceability = report["traceability"]
    assert traceability["development_pair_count"] == 150
    assert traceability["held_out_evaluated"] is False
    assert traceability["original_stage6_frozen_test_evaluated"] is False
    summaries = report["candidate_summaries"]
    assert len(summaries) == 6
    cases_by_candidate = report["cases_by_candidate"]
    assert all(len(cases) == 150 for cases in cases_by_candidate.values())
    assert all(
        len(case["l2_criterion_scores"]) == 5
        for cases in cases_by_candidate.values()
        for case in cases
    )
    assert report["selection"]["hybrid_configuration_freeze_eligible"] is False
    assert "hybrid_freeze_eligible_candidate_ids" not in report["selection"]
    assert all(
        case["l1_score"] is not None and case["l3_score"] is not None
        for cases in cases_by_candidate.values()
        for case in cases
    )


def test_l2_tuning_writer_is_deterministic(tmp_path: Path) -> None:
    first = write_report(
        REPOSITORY_ROOT,
        GENERATED_AT,
        tmp_path / "first.json",
        _runtime(),
    )
    second = write_report(
        REPOSITORY_ROOT,
        GENERATED_AT,
        tmp_path / "second.json",
        _runtime(),
    )

    assert first.read_bytes() == second.read_bytes()


def test_l2_tuning_timestamp_requires_timezone() -> None:
    with pytest.raises(ValueError, match="timezone"):
        _timestamp("2026-07-31T22:00:00")


def test_remediated_l2_configuration_uses_new_development_lineage() -> None:
    candidate_set = load_expansion_l2_candidate_set(REPOSITORY_ROOT, REMEDIATED_CONFIG_PATH)
    report = asyncio.run(
        run(
            REPOSITORY_ROOT,
            GENERATED_AT,
            _runtime(),
            REMEDIATED_CONFIG_PATH,
        )
    )

    assert candidate_set.dataset_version == "2.2.0"
    assert candidate_set.candidate_set_version == "1.2.0"
    assert report["report_id"] == "synthetic-expansion-v2-2-l2-development-tuning-v2"
    assert report["traceability"]["dataset_version"] == "2.2.0"
    assert report["traceability"]["development_pair_count"] == 150
    assert report["traceability"]["held_out_evaluated"] is False
    assert report["traceability"]["original_stage6_frozen_test_evaluated"] is False


def test_v2_3_l2_configuration_uses_qa_remediated_development_only() -> None:
    candidate_set = load_expansion_l2_candidate_set(REPOSITORY_ROOT, REMEDIATED_V2_3_CONFIG_PATH)
    report = asyncio.run(
        run(
            REPOSITORY_ROOT,
            GENERATED_AT,
            _runtime(),
            REMEDIATED_V2_3_CONFIG_PATH,
        )
    )

    assert candidate_set.dataset_version == "2.3.0"
    assert candidate_set.candidate_set_version == "1.3.0"
    assert report["report_id"] == "synthetic-expansion-v2-3-l2-development-tuning-v3"
    assert report["traceability"]["dataset_version"] == "2.3.0"
    assert report["traceability"]["development_pair_count"] == 150
    assert report["traceability"]["held_out_evaluated"] is False
    assert report["traceability"]["original_stage6_frozen_test_evaluated"] is False


def test_v2_3_1_l2_configuration_uses_explicit_negative_patch() -> None:
    candidate_set = load_expansion_l2_candidate_set(REPOSITORY_ROOT, REMEDIATED_V2_3_1_CONFIG_PATH)
    report = asyncio.run(
        run(
            REPOSITORY_ROOT,
            GENERATED_AT,
            _runtime(),
            REMEDIATED_V2_3_1_CONFIG_PATH,
        )
    )

    assert candidate_set.dataset_version == "2.3.1"
    assert candidate_set.candidate_set_version == "1.3.1"
    assert report["traceability"]["development_pair_count"] == 150
    assert report["traceability"]["held_out_evaluated"] is False
    assert report["traceability"]["original_stage6_frozen_test_evaluated"] is False


def test_committed_e5_report_removes_saturation_without_opening_test_data() -> None:
    report = json.loads(
        (REPOSITORY_ROOT / "evaluation/reports/synthetic_expansion_v2_l2_tuning_v1.json").read_text(
            encoding="utf-8"
        )
    )
    recommended_id = report["selection"]["l2_recommended_candidate_id"]
    recommended = next(
        item for item in report["candidate_summaries"] if item["candidate_id"] == recommended_id
    )

    assert report["report_schema_version"] == "1.1.0"
    assert report["traceability"]["development_pair_count"] == 150
    assert report["traceability"]["held_out_evaluated"] is False
    assert report["traceability"]["original_stage6_frozen_test_evaluated"] is False
    assert recommended["l2_score"]["exact_100_count"] == 0
    assert recommended["l2_score"]["standard_deviation"] > 0
    assert recommended["strong_over_hard_negative_role_count"] == 5
    assert all(role["margin"] > 0 for role in recommended["role_contrast"].values())
    assert report["selection"]["hybrid_configuration_freeze_eligible"] is False
