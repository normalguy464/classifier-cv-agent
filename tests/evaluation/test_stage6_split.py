from __future__ import annotations

import json
import shutil
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import cast

import pytest

from evaluation.datasets import load_stage6_validation
from scripts.create_stage6_split import (
    SOURCE_ANNOTATION_PATH,
    SOURCE_CV_PATH,
    SPLIT_MANIFEST_PATH,
    build_split_manifest,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def _manifest() -> dict[str, object]:
    value = json.loads((REPOSITORY_ROOT / SPLIT_MANIFEST_PATH).read_text(encoding="utf-8"))
    return cast(dict[str, object], value)


def test_stage6_split_is_complete_disjoint_and_stratified() -> None:
    manifest = _manifest()
    validation = cast(dict[str, object], manifest["validation"])
    frozen = cast(dict[str, object], manifest["frozen_test"])
    validation_ids = cast(list[str], validation["cv_profile_ids"])
    frozen_ids = cast(list[str], frozen["cv_profile_ids"])

    assert len(validation_ids) == 20
    assert len(frozen_ids) == 10
    assert len(set(validation_ids)) == 20
    assert len(set(frozen_ids)) == 10
    assert set(validation_ids).isdisjoint(frozen_ids)
    assert len(set(validation_ids).union(frozen_ids)) == 30
    assert validation["distribution"] == {
        "roles": {
            "junior-data-analyst-v1": 10,
            "junior-python-backend-developer-v1": 10,
        },
        "labels": {
            "needs_review": 11,
            "pass": 4,
            "reject": 1,
            "waitlist": 4,
        },
    }
    assert frozen["distribution"] == {
        "roles": {
            "junior-data-analyst-v1": 5,
            "junior-python-backend-developer-v1": 5,
        },
        "labels": {
            "needs_review": 5,
            "pass": 2,
            "reject": 1,
            "waitlist": 2,
        },
    }


def test_stage6_frozen_partition_disallows_tuning_and_has_no_results() -> None:
    frozen = cast(dict[str, object], _manifest()["frozen_test"])

    assert frozen["tuning_allowed"] is False
    assert frozen["evaluation_allowed_from_stage"] == 7
    assert frozen["classifier_results_generated"] is False


def test_stage6_loader_returns_validation_only() -> None:
    manifest = _manifest()
    frozen = cast(dict[str, object], manifest["frozen_test"])
    frozen_ids = set(cast(list[str], frozen["cv_profile_ids"]))
    examples = load_stage6_validation(REPOSITORY_ROOT)

    assert len(examples) == 20
    assert not {example.cv_profile.cv_profile_id for example in examples}.intersection(frozen_ids)
    assert Counter(example.job_profile_id for example in examples) == {
        "junior-data-analyst-v1": 10,
        "junior-python-backend-developer-v1": 10,
    }
    assert Counter(example.final_label.value for example in examples) == {
        "needs_review": 11,
        "pass": 4,
        "waitlist": 4,
        "reject": 1,
    }


def test_stage6_loader_detects_reviewed_source_changes(tmp_path: Path) -> None:
    for relative_path in (
        SOURCE_CV_PATH,
        SOURCE_ANNOTATION_PATH,
        SPLIT_MANIFEST_PATH,
    ):
        destination = tmp_path / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPOSITORY_ROOT / relative_path, destination)
    annotation_path = tmp_path / SOURCE_ANNOTATION_PATH
    annotation_path.write_text(
        annotation_path.read_text(encoding="utf-8") + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="changed after"):
        load_stage6_validation(tmp_path)


def test_committed_stage6_split_matches_deterministic_generator() -> None:
    committed = _manifest()
    frozen_at = cast(str, committed["frozen_at"])

    assert datetime.fromisoformat(frozen_at).utcoffset() is not None
    assert committed == build_split_manifest(REPOSITORY_ROOT, frozen_at)
