from __future__ import annotations

import asyncio
import json
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path
from typing import cast

import pytest

from backend.app.infrastructure.embeddings import (
    EmbeddingInputType,
    EmbeddingResult,
    HashingEmbeddingAdapter,
)
from evaluation.datasets.synthetic_expansion import SyntheticExpansionSilverSplitManifest
from evaluation.experiments.run_synthetic_expansion_v2_diagnostic import (
    ExpansionEmbeddingRuntime,
    run,
    write_report,
)
from scripts.create_synthetic_expansion_split import SPLIT_MANIFEST_PATH

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
GENERATED_AT = datetime.fromisoformat("2026-07-31T21:10:00+07:00")
COMMITTED_REPORT_PATH = (
    REPOSITORY_ROOT / "evaluation/reports/synthetic_expansion_v2_development_diagnostic.json"
)


class UnavailableEmbeddingAdapter:
    @property
    def model_identifier(self) -> str:
        return "unavailable-test-embedding"

    @property
    def model_version(self) -> str:
        return "1.0.0"

    def embed(
        self,
        texts: Sequence[str],
        input_type: EmbeddingInputType,
    ) -> EmbeddingResult:
        raise RuntimeError("embedding unavailable")


def _runtime() -> ExpansionEmbeddingRuntime:
    return ExpansionEmbeddingRuntime(
        adapter=HashingEmbeddingAdapter(
            dimension=768,
            model_identifier="deterministic-hashing-embedding",
            model_version="1.0.0",
        ),
        model_identifier="deterministic-hashing-embedding",
        model_version="1.0.0",
        resolved_revision="deterministic-test-revision",
        configured_model_executed=False,
    )


def test_development_diagnostic_runs_three_levels_without_held_out_data() -> None:
    report = asyncio.run(run(REPOSITORY_ROOT, GENERATED_AT, _runtime()))
    traceability = cast(dict[str, object], report["dataset_traceability"])
    strategy = cast(dict[str, object], report["execution_strategy"])
    summary = cast(dict[str, object], report["summary"])
    cases = cast(list[dict[str, object]], report["cases"])
    split = SyntheticExpansionSilverSplitManifest.model_validate_json(
        (REPOSITORY_ROOT / SPLIT_MANIFEST_PATH).read_text(encoding="utf-8")
    )

    assert report["is_final_performance"] is False
    assert traceability["candidate_count"] == 30
    assert traceability["pair_count"] == 150
    assert traceability["held_out_partition_evaluated"] is False
    assert traceability["held_out_results_generated"] is False
    assert traceability["original_stage6_frozen_test_evaluated"] is False
    assert strategy["configured_multilingual_l2_executed"] is False
    assert strategy["live_llm_provider_executed"] is False
    assert strategy["automatic_pass_gate_applied"] is False
    assert len(cases) == 150
    assert {cast(str, case["pair_id"]) for case in cases} == set(split.development.pair_ids)
    assert not {cast(str, case["pair_id"]) for case in cases}.intersection(split.held_out.pair_ids)
    assert summary["l1_requirement_status_match_rate"] == 1.0
    assert summary["false_reject_count"] == 0
    assert summary["unsafe_pass_count"] == 0


def test_development_diagnostic_reports_every_role_and_score_level() -> None:
    report = asyncio.run(run(REPOSITORY_ROOT, GENERATED_AT, _runtime()))
    summary = cast(dict[str, object], report["summary"])
    role_metrics = cast(dict[str, dict[str, object]], summary["role_metrics"])
    cases = cast(list[dict[str, object]], report["cases"])

    assert set(role_metrics) == {
        "data_analyst",
        "python_backend",
        "frontend",
        "qa_engineer",
        "data_engineer",
    }
    assert all(metrics["sample_count"] == 30 for metrics in role_metrics.values())
    assert all(
        set(cast(dict[str, object], case["level_scores"])) == {"l1", "l2", "l3"} for case in cases
    )
    assert 0 <= cast(float, summary["average_l2_score"]) <= 100
    assert cast(float, summary["deterministic_l3_total_score_mae"]) >= 0


def test_development_diagnostic_writer_creates_traceable_report(tmp_path: Path) -> None:
    output = Path("diagnostic.json")
    path = write_report(
        REPOSITORY_ROOT,
        GENERATED_AT,
        tmp_path / output,
        _runtime(),
    )
    report = json.loads(path.read_text(encoding="utf-8"))

    assert path == tmp_path / output
    assert report["report_id"] == "synthetic-expansion-v2-development-diagnostic"
    assert report["dataset_traceability"]["pair_count"] == 150
    assert len(report["cases"]) == 150


def test_development_diagnostic_rejects_timestamp_without_timezone() -> None:
    with pytest.raises(ValueError, match="timezone"):
        asyncio.run(
            run(
                REPOSITORY_ROOT,
                datetime.fromisoformat("2026-07-31T21:10:00"),
                _runtime(),
            )
        )


def test_configured_multilingual_failure_stops_diagnostic() -> None:
    runtime = ExpansionEmbeddingRuntime(
        adapter=UnavailableEmbeddingAdapter(),
        model_identifier="unavailable-test-embedding",
        model_version="1.0.0",
        resolved_revision="unavailable-test-revision",
        configured_model_executed=True,
    )

    with pytest.raises(RuntimeError, match="configured multilingual L2 failed"):
        asyncio.run(run(REPOSITORY_ROOT, GENERATED_AT, runtime))


def test_committed_local_e5_report_records_known_anomalies_and_isolation() -> None:
    report = json.loads(COMMITTED_REPORT_PATH.read_text(encoding="utf-8"))
    traceability = cast(dict[str, object], report["dataset_traceability"])
    strategy = cast(dict[str, object], report["execution_strategy"])
    summary = cast(dict[str, object], report["summary"])
    split = SyntheticExpansionSilverSplitManifest.model_validate_json(
        (REPOSITORY_ROOT / SPLIT_MANIFEST_PATH).read_text(encoding="utf-8")
    )
    case_ids = {
        cast(str, case["pair_id"]) for case in cast(list[dict[str, object]], report["cases"])
    }

    assert report["is_final_performance"] is False
    assert strategy["configured_multilingual_l2_executed"] is True
    assert strategy["live_llm_provider_executed"] is False
    assert traceability["held_out_partition_evaluated"] is False
    assert traceability["original_stage6_frozen_test_evaluated"] is False
    assert case_ids == set(split.development.pair_ids)
    assert not case_ids.intersection(split.held_out.pair_ids)
    assert summary["l1_requirement_status_match_rate"] == 1.0
    assert summary["average_l2_score"] == 100.0
    assert summary["l2_score_at_100_count"] == 150
    assert summary["deterministic_l3_total_score_mae"] == 27.8
    assert summary["unsafe_pass_count"] == 45
