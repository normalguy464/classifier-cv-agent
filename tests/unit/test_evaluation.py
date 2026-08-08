from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.app.contracts import ClassificationDecision
from evaluation.datasets import load_reviewed_pilot
from evaluation.experiments.run_baselines import run
from evaluation.metrics import calculate_metrics

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def test_metrics_are_deterministic_and_bounded() -> None:
    expected = (
        ClassificationDecision.PASS,
        ClassificationDecision.WAITLIST,
        ClassificationDecision.REJECT,
        ClassificationDecision.NEEDS_REVIEW,
    )
    predicted = (
        ClassificationDecision.PASS,
        ClassificationDecision.PASS,
        ClassificationDecision.REJECT,
        ClassificationDecision.NEEDS_REVIEW,
    )

    metrics = calculate_metrics(expected, predicted)

    assert metrics.sample_count == 4
    assert metrics.accuracy == 0.75
    assert 0 <= metrics.macro_f1 <= 1
    assert -1 <= metrics.cohen_kappa <= 1
    assert sum(sum(row) for row in metrics.confusion_matrix) == 4


def test_metrics_reject_empty_and_mismatched_inputs() -> None:
    with pytest.raises(ValueError):
        calculate_metrics((), ())
    with pytest.raises(ValueError):
        calculate_metrics(
            (ClassificationDecision.PASS,),
            (ClassificationDecision.PASS, ClassificationDecision.REJECT),
        )


def test_loader_uses_only_human_approved_pilot_labels(tmp_path: Path) -> None:
    data_directory = tmp_path / "data" / "annotations"
    data_directory.mkdir(parents=True)
    artifact = {
        "annotation_status": "draft",
        "records": [],
    }
    (data_directory / "pilot_annotations_v1.json").write_text(
        json.dumps(artifact),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="reviewed"):
        load_reviewed_pilot(tmp_path)


def test_reviewed_pilot_loader_returns_all_ten_confirmed_examples() -> None:
    examples = load_reviewed_pilot(REPOSITORY_ROOT)

    assert len(examples) == 10
    assert all(example.reviewer_reference == "reviewer-user-001" for example in examples)


def test_baseline_runner_is_scoped_and_does_not_claim_final_performance() -> None:
    report = run(REPOSITORY_ROOT)

    assert report["report_scope"] == "reviewed-pilot-diagnostic-only"
    assert report["is_final_performance"] is False
    assert report["sample_count"] == 10
    assert set(report["baselines"]) == {
        "keyword-rule-v1",
        "tfidf-cosine-v1",
        "embedding-only-deterministic-hashing-1.0.0",
    }
