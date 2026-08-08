from __future__ import annotations

import json
import shutil
from collections import Counter
from pathlib import Path

import pytest

from backend.app.contracts import ClassificationDecision, ScoringRubric
from evaluation.datasets.synthetic_expansion import (
    ApprovedDatasetReview,
    DatasetRole,
    DatasetTier,
    SyntheticExpansionSilverSplitManifest,
    SyntheticPairAnnotation,
    validate_synthetic_expansion,
)
from scripts.approve_synthetic_expansion import (
    REVIEWED_DATASET_ID,
    REVIEWED_DATASET_VERSION,
    REVIEWED_DIRECTORY,
    REVIEW_NOTE,
    SOURCE_DIRECTORY,
    build_reviewed_dataset,
    write_reviewed_dataset,
)
from scripts.create_synthetic_expansion_split import (
    SPLIT_MANIFEST_PATH,
    build_split_manifest,
    write_split_manifest,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
REVIEWER_REFERENCE = "reviewer-user-001"
REVIEWED_AT = "2026-07-31T21:02:39.411161+07:00"
SPLIT_CREATED_AT = "2026-07-31T21:03:39.427432+07:00"
REVIEWED_PATH = REPOSITORY_ROOT / REVIEWED_DIRECTORY


def test_fifth_criterion_uses_cv_specific_clarity_title() -> None:
    rubric_path = REPOSITORY_ROOT / SOURCE_DIRECTORY / "rubrics.jsonl"
    rubrics = tuple(
        ScoringRubric.model_validate_json(line)
        for line in rubric_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )

    assert {rubric.rubric_version for rubric in rubrics} == {"2.0.1"}
    assert {rubric.criteria[4].title for rubric in rubrics} == {
        "Độ rõ ràng và khả năng kiểm tra của thông tin trong CV"
    }


def test_approval_preserves_drafts_and_records_one_human_review() -> None:
    _, _, _, annotations, source_manifest, _, _ = build_reviewed_dataset(
        REPOSITORY_ROOT,
        REVIEWER_REFERENCE,
        REVIEWED_AT,
    )

    assert source_manifest.status == "draft_for_human_review"
    assert len(annotations) == 250
    for annotation in annotations:
        assert annotation.dataset_tier is DatasetTier.SILVER
        assert isinstance(annotation.review, ApprovedDatasetReview)
        assert annotation.review.human_review_count == 1
        assert annotation.review.reviewer_references == (REVIEWER_REFERENCE,)
        assert annotation.review.final_label is annotation.draft_label
        assert annotation.review.criterion_score_overrides == ()
        assert annotation.review.notes == REVIEW_NOTE


def test_approval_rejects_missing_timezone() -> None:
    with pytest.raises(ValueError, match="timezone"):
        build_reviewed_dataset(
            REPOSITORY_ROOT,
            REVIEWER_REFERENCE,
            "2026-07-31T21:02:39",
        )


def test_committed_reviewed_dataset_is_reproducible(tmp_path: Path) -> None:
    source_directory = tmp_path / SOURCE_DIRECTORY
    source_directory.parent.mkdir(parents=True)
    shutil.copytree(REPOSITORY_ROOT / SOURCE_DIRECTORY, source_directory)

    generated_paths = write_reviewed_dataset(
        tmp_path,
        REVIEWER_REFERENCE,
        REVIEWED_AT,
    )
    committed_names = {
        "cv_profiles.jsonl",
        "job_profiles.jsonl",
        "rubrics.jsonl",
        "pairs.jsonl",
        "manifest.json",
        "quality_report.json",
    }

    assert {path.name for path in generated_paths} == committed_names
    for name in committed_names:
        assert (tmp_path / REVIEWED_DIRECTORY / name).read_bytes() == (
            REVIEWED_PATH / name
        ).read_bytes()


def test_reviewed_dataset_passes_qc_and_has_expected_state() -> None:
    report = validate_synthetic_expansion(REVIEWED_PATH)
    manifest = json.loads((REVIEWED_PATH / "manifest.json").read_text(encoding="utf-8"))
    annotations = tuple(
        SyntheticPairAnnotation.model_validate_json(line)
        for line in (REVIEWED_PATH / "pairs.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    )

    assert report.passed
    assert report.errors == ()
    assert report.warnings == ()
    assert report.tier_counts == {DatasetTier.SILVER: 250}
    assert manifest["dataset_id"] == REVIEWED_DATASET_ID
    assert manifest["dataset_version"] == REVIEWED_DATASET_VERSION
    assert manifest["human_reviewed_pair_count"] == 250
    assert manifest["reviewer_references"] == [REVIEWER_REFERENCE]
    assert Counter(
        annotation.review.final_label
        for annotation in annotations
        if isinstance(annotation.review, ApprovedDatasetReview)
    ) == {
        ClassificationDecision.PASS: 50,
        ClassificationDecision.WAITLIST: 25,
        ClassificationDecision.NEEDS_REVIEW: 155,
        ClassificationDecision.REJECT: 20,
    }


def test_reviewed_qc_rejects_invalid_review_count(tmp_path: Path) -> None:
    copied_directory = tmp_path / "reviewed"
    shutil.copytree(REVIEWED_PATH, copied_directory)
    pair_path = copied_directory / "pairs.jsonl"
    lines = pair_path.read_text(encoding="utf-8").splitlines()
    first = json.loads(lines[0])
    first["review"]["human_review_count"] = 2
    lines[0] = json.dumps(first, ensure_ascii=False, sort_keys=True)
    pair_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    report = validate_synthetic_expansion(copied_directory)

    assert not report.passed
    assert any("Dataset loading failed" in error for error in report.errors)


def test_silver_split_is_grouped_balanced_and_not_frozen() -> None:
    split = build_split_manifest(REPOSITORY_ROOT, SPLIT_CREATED_AT)

    assert split.frozen_test_created is False
    assert split.gold_review_required_for_final_evaluation is True
    assert split.development.candidate_count == 30
    assert split.development.pair_count == 150
    assert split.held_out.candidate_count == 20
    assert split.held_out.pair_count == 100
    assert split.development.role_candidate_counts == {role: 6 for role in DatasetRole}
    assert split.held_out.role_candidate_counts == {role: 4 for role in DatasetRole}
    assert split.development.label_pair_counts == {
        ClassificationDecision.PASS: 30,
        ClassificationDecision.WAITLIST: 15,
        ClassificationDecision.NEEDS_REVIEW: 97,
        ClassificationDecision.REJECT: 8,
    }
    assert split.held_out.label_pair_counts == {
        ClassificationDecision.PASS: 20,
        ClassificationDecision.WAITLIST: 10,
        ClassificationDecision.NEEDS_REVIEW: 58,
        ClassificationDecision.REJECT: 12,
    }
    assert not set(split.development.candidate_references).intersection(
        split.held_out.candidate_references
    )
    assert not set(split.development.pair_ids).intersection(split.held_out.pair_ids)


def test_committed_silver_split_matches_deterministic_writer(tmp_path: Path) -> None:
    reviewed_directory = tmp_path / REVIEWED_DIRECTORY
    reviewed_directory.parent.mkdir(parents=True)
    shutil.copytree(REVIEWED_PATH, reviewed_directory)

    generated_path = write_split_manifest(tmp_path, SPLIT_CREATED_AT)
    committed_path = REPOSITORY_ROOT / SPLIT_MANIFEST_PATH

    assert generated_path.read_bytes() == committed_path.read_bytes()
    SyntheticExpansionSilverSplitManifest.model_validate_json(
        committed_path.read_text(encoding="utf-8")
    )


def test_expansion_split_does_not_change_original_stage6_frozen_test() -> None:
    original = json.loads(
        (REPOSITORY_ROOT / "data/splits/stage6_split_manifest_v1.json").read_text(encoding="utf-8")
    )
    expansion = SyntheticExpansionSilverSplitManifest.model_validate_json(
        (REPOSITORY_ROOT / SPLIT_MANIFEST_PATH).read_text(encoding="utf-8")
    )

    assert original["frozen_test"]["sample_count"] == 10
    assert original["frozen_test"]["classifier_results_generated"] is False
    assert expansion.frozen_test_created is False
    assert expansion.held_out.final_performance_allowed is False
