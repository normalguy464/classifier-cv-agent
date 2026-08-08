from __future__ import annotations

import json
import shutil
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import cast

import pytest

from backend.app.contracts import CVProfile
from evaluation.datasets import load_reviewed_stage4
from scripts.approve_stage4_dataset import (
    DRAFT_ANNOTATION_PATH,
    DRAFT_CV_PATH,
    REVIEWED_ANNOTATION_PATH,
    REVIEWED_CV_PATH,
    REVIEW_NOTE,
    build_reviewed_dataset,
    write_reviewed_dataset,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
REVIEWED_AT = "2026-07-26T19:52:02.595577+07:00"
REVIEWER_REFERENCE = "reviewer-user-001"


def test_stage4_approval_preserves_drafts_and_records_human_review() -> None:
    profiles, artifact = build_reviewed_dataset(
        REPOSITORY_ROOT,
        REVIEWER_REFERENCE,
        REVIEWED_AT,
    )
    records = cast(list[dict[str, object]], artifact["records"])

    assert len(profiles) == 30
    assert artifact["annotation_status"] == "reviewed"
    assert artifact["source_annotation_file"] == DRAFT_ANNOTATION_PATH.as_posix()
    assert all(record["source_dataset_file"] == REVIEWED_CV_PATH.as_posix() for record in records)
    for record in records:
        review = cast(dict[str, object], record["review"])
        assert review == {
            "status": "approved",
            "reviewer_reference": REVIEWER_REFERENCE,
            "final_label": record["draft_label"],
            "criterion_score_overrides": [],
            "notes": REVIEW_NOTE,
            "reviewed_at": REVIEWED_AT,
        }


def test_stage4_approval_rejects_missing_timezone() -> None:
    with pytest.raises(ValueError, match="timezone"):
        build_reviewed_dataset(
            REPOSITORY_ROOT,
            REVIEWER_REFERENCE,
            "2026-07-26T19:52:02",
        )


def test_stage4_review_writer_creates_valid_separate_artifacts(tmp_path: Path) -> None:
    draft_cv = tmp_path / DRAFT_CV_PATH
    draft_annotation = tmp_path / DRAFT_ANNOTATION_PATH
    draft_cv.parent.mkdir(parents=True)
    shutil.copyfile(REPOSITORY_ROOT / DRAFT_CV_PATH, draft_cv)
    shutil.copyfile(REPOSITORY_ROOT / DRAFT_ANNOTATION_PATH, draft_annotation)

    cv_path, annotation_path = write_reviewed_dataset(
        tmp_path,
        REVIEWER_REFERENCE,
        REVIEWED_AT,
    )

    profiles = tuple(
        CVProfile.model_validate_json(line)
        for line in cv_path.read_text(encoding="utf-8").splitlines()
        if line
    )
    artifact = json.loads(annotation_path.read_text(encoding="utf-8"))
    assert cv_path == tmp_path / REVIEWED_CV_PATH
    assert annotation_path == tmp_path / REVIEWED_ANNOTATION_PATH
    assert len(profiles) == 30
    assert artifact["annotation_status"] == "reviewed"
    assert (tmp_path / DRAFT_ANNOTATION_PATH).exists()


def test_stage4_reviewed_loader_uses_all_human_confirmed_labels() -> None:
    examples = load_reviewed_stage4(REPOSITORY_ROOT)

    assert len(examples) == 30
    assert all(example.final_label is example.draft_label for example in examples)
    assert {example.reviewer_reference for example in examples} == {REVIEWER_REFERENCE}
    assert all(example.reviewed_at == datetime.fromisoformat(REVIEWED_AT) for example in examples)
    assert Counter(example.job_profile_id for example in examples) == {
        "junior-data-analyst-v1": 15,
        "junior-python-backend-developer-v1": 15,
    }
    assert Counter(example.final_label.value for example in examples) == {
        "needs_review": 16,
        "pass": 6,
        "waitlist": 6,
        "reject": 2,
    }


def test_stage4_reviewed_loader_rejects_non_reviewed_annotation(
    tmp_path: Path,
) -> None:
    reviewed_directory = tmp_path / "data" / "reviewed"
    reviewed_directory.mkdir(parents=True)
    shutil.copyfile(REPOSITORY_ROOT / REVIEWED_CV_PATH, tmp_path / REVIEWED_CV_PATH)
    artifact = json.loads((REPOSITORY_ROOT / REVIEWED_ANNOTATION_PATH).read_text(encoding="utf-8"))
    artifact["annotation_status"] = "draft"
    (tmp_path / REVIEWED_ANNOTATION_PATH).write_text(
        json.dumps(artifact, ensure_ascii=False),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="must be reviewed"):
        load_reviewed_stage4(tmp_path)


def test_committed_stage4_review_artifacts_match_approval_transform() -> None:
    committed = json.loads((REPOSITORY_ROOT / REVIEWED_ANNOTATION_PATH).read_text(encoding="utf-8"))
    records = cast(list[dict[str, object]], committed["records"])
    first_review = cast(dict[str, object], records[0]["review"])
    reviewed_at = cast(str, first_review["reviewed_at"])
    reviewer_reference = cast(str, first_review["reviewer_reference"])
    profiles, expected = build_reviewed_dataset(
        REPOSITORY_ROOT,
        reviewer_reference,
        reviewed_at,
    )
    committed_profiles = tuple(
        CVProfile.model_validate_json(line)
        for line in (REPOSITORY_ROOT / REVIEWED_CV_PATH).read_text(encoding="utf-8").splitlines()
        if line
    )

    assert committed == expected
    assert committed_profiles == profiles
