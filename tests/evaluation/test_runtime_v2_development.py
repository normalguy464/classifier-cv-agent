from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from pathlib import Path

import pytest

from backend.app.contracts import ClassificationDecision, EvidenceStatus
from evaluation.datasets.runtime_v2 import (
    RuntimeV2DevelopmentManifest,
    RuntimeV2ReviewedManifest,
    validate_runtime_v2_development,
    validate_runtime_v2_reviewed,
)
from evaluation.datasets.synthetic_expansion import (
    ApprovedDatasetReview,
    DatasetRole,
    DatasetTier,
    SyntheticPairAnnotation,
)
from scripts import approve_runtime_v2_development, create_runtime_v2_split
from scripts.generate_runtime_v2_development import (
    REPOSITORY_ROOT,
    _decision,
    build_runtime_v2_development,
    write_runtime_v2_development,
)


def test_runtime_v2_development_builds_balanced_review_dataset() -> None:
    profiles, jobs, rubrics, pairs = build_runtime_v2_development()

    assert len(profiles) == 75
    assert len(jobs) == 5
    assert len(rubrics) == 5
    assert len(pairs) == 75
    assert Counter(pair.role for pair in pairs) == Counter({role: 15 for role in DatasetRole})
    assert Counter(pair.draft_label for pair in pairs) == Counter(
        {
            ClassificationDecision.PASS: 15,
            ClassificationDecision.WAITLIST: 10,
            ClassificationDecision.REJECT: 10,
            ClassificationDecision.NEEDS_REVIEW: 40,
        }
    )
    assert all(pair.review.status == "pending" for pair in pairs)
    assert all(pair.partition == "unassigned" for pair in pairs)


def test_runtime_v2_development_qc_passes_without_prior_leakage(tmp_path: Path) -> None:
    output_directory = tmp_path / "development_v1"

    write_runtime_v2_development(output_directory)
    report = validate_runtime_v2_development(output_directory, REPOSITORY_ROOT)
    manifest = RuntimeV2DevelopmentManifest.model_validate_json(
        (output_directory / "manifest.json").read_text(encoding="utf-8")
    )

    assert report.passed is True
    assert report.errors == ()
    assert report.warnings == ()
    assert report.exact_prior_evidence_overlap_count == 0
    assert report.maximum_prior_cv_token_jaccard < 0.82
    assert manifest.tuning_allowed is False
    assert manifest.classifier_results_generated is False
    assert manifest.llm_requests_made is False


def test_runtime_v2_decision_policy_covers_boundaries_and_failure_paths() -> None:
    satisfied = (EvidenceStatus.SATISFIED,)
    unsatisfied = (EvidenceStatus.UNSATISFIED,)
    missing = (EvidenceStatus.MISSING,)
    conflicting = (EvidenceStatus.CONFLICTING, EvidenceStatus.SATISFIED)

    assert _decision(satisfied, 88) is ClassificationDecision.PASS
    assert _decision(satisfied, 82) is ClassificationDecision.WAITLIST
    assert _decision(satisfied, 70) is ClassificationDecision.NEEDS_REVIEW
    assert _decision(satisfied, 68) is ClassificationDecision.NEEDS_REVIEW
    assert _decision(unsatisfied, 67) is ClassificationDecision.REJECT
    assert _decision(unsatisfied, 70) is ClassificationDecision.NEEDS_REVIEW
    assert _decision(missing, 90) is ClassificationDecision.NEEDS_REVIEW
    assert _decision(conflicting, 90) is ClassificationDecision.NEEDS_REVIEW


def test_runtime_v2_qc_rejects_manifest_digest_tampering(tmp_path: Path) -> None:
    output_directory = tmp_path / "development_v1"
    write_runtime_v2_development(output_directory)
    pairs_path = output_directory / "pairs.jsonl"
    lines = pairs_path.read_text(encoding="utf-8").splitlines()
    first = SyntheticPairAnnotation.model_validate_json(lines[0])
    payload = first.model_dump(mode="json")
    payload["overall_rationale"] = "Nội dung đã bị thay đổi sau khi manifest được tạo."
    lines[0] = json.dumps(payload, ensure_ascii=False)
    pairs_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    report = validate_runtime_v2_development(output_directory, REPOSITORY_ROOT)

    assert report.passed is False
    assert "Manifest digest mismatch for pairs.jsonl" in report.errors


def test_runtime_v2_approval_preserves_approved_content(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_directory = REPOSITORY_ROOT / "data/runtime_v2/to_review/development_v1"
    reviewed_directory = tmp_path / "reviewed"
    monkeypatch.setattr(
        approve_runtime_v2_development,
        "SOURCE_DIRECTORY",
        source_directory,
    )
    monkeypatch.setattr(
        approve_runtime_v2_development,
        "REVIEWED_DIRECTORY",
        reviewed_directory,
    )

    approve_runtime_v2_development.write_reviewed_runtime_v2_development(
        REPOSITORY_ROOT,
        "2026-08-08T10:00:00+07:00",
    )
    report = validate_runtime_v2_reviewed(
        reviewed_directory,
        source_directory,
        REPOSITORY_ROOT,
    )
    pairs = tuple(
        SyntheticPairAnnotation.model_validate_json(line)
        for line in (reviewed_directory / "pairs.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    )
    manifest = RuntimeV2ReviewedManifest.model_validate_json(
        (reviewed_directory / "manifest.json").read_text(encoding="utf-8")
    )

    assert report.passed is True
    assert report.warnings == ()
    assert manifest.status == "human_reviewed_silver"
    assert all(pair.dataset_tier is DatasetTier.SILVER for pair in pairs)
    assert all(isinstance(pair.review, ApprovedDatasetReview) for pair in pairs)
    assert all(
        isinstance(pair.review, ApprovedDatasetReview)
        and pair.review.final_label is pair.draft_label
        for pair in pairs
    )


def test_runtime_v2_split_is_stratified_and_candidate_disjoint(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_directory = REPOSITORY_ROOT / "data/runtime_v2/to_review/development_v1"
    reviewed_directory = tmp_path / "reviewed"
    monkeypatch.setattr(
        approve_runtime_v2_development,
        "SOURCE_DIRECTORY",
        source_directory,
    )
    monkeypatch.setattr(
        approve_runtime_v2_development,
        "REVIEWED_DIRECTORY",
        reviewed_directory,
    )
    approve_runtime_v2_development.write_reviewed_runtime_v2_development(
        REPOSITORY_ROOT,
        "2026-08-08T10:00:00+07:00",
    )
    monkeypatch.setattr(create_runtime_v2_split, "SOURCE_DIRECTORY", source_directory)
    monkeypatch.setattr(create_runtime_v2_split, "REVIEWED_DIRECTORY", reviewed_directory)

    first = create_runtime_v2_split.build_runtime_v2_split(
        REPOSITORY_ROOT,
        "2026-08-08T10:05:00+07:00",
    )
    second = create_runtime_v2_split.build_runtime_v2_split(
        REPOSITORY_ROOT,
        "2026-08-08T10:05:00+07:00",
    )

    assert first == second
    assert first.development.pair_count == 50
    assert first.validation.pair_count == 25
    assert first.stage7_v1_test_excluded is True
    assert not set(first.development.candidate_references).intersection(
        first.validation.candidate_references
    )
    assert first.validation.label_pair_counts == {
        ClassificationDecision.PASS: 5,
        ClassificationDecision.WAITLIST: 5,
        ClassificationDecision.REJECT: 5,
        ClassificationDecision.NEEDS_REVIEW: 10,
    }


def test_runtime_v2_approval_rejects_naive_timestamp() -> None:
    with pytest.raises(ValueError, match="timezone"):
        approve_runtime_v2_development.write_reviewed_runtime_v2_development(
            REPOSITORY_ROOT,
            datetime(2026, 8, 8, 10, 0).isoformat(),
        )
