from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import cast

from evaluation.datasets import ReviewedStage4Example, load_reviewed_stage4

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SPLIT_MANIFEST_PATH = Path("data/splits/stage6_split_manifest_v1.json")
SOURCE_CV_PATH = Path("data/reviewed/stage4_cv_profiles_v1.jsonl")
SOURCE_ANNOTATION_PATH = Path("data/reviewed/stage4_annotations_v1.json")
SPLIT_SEED_IDENTIFIER = "stage6-role-label-sha256-v1"
FROZEN_ALLOCATION: dict[tuple[str, str], int] = {
    ("junior-data-analyst-v1", "pass"): 1,
    ("junior-data-analyst-v1", "waitlist"): 1,
    ("junior-data-analyst-v1", "reject"): 1,
    ("junior-data-analyst-v1", "needs_review"): 2,
    ("junior-python-backend-developer-v1", "pass"): 1,
    ("junior-python-backend-developer-v1", "waitlist"): 1,
    ("junior-python-backend-developer-v1", "reject"): 0,
    ("junior-python-backend-developer-v1", "needs_review"): 3,
}


def _timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError("frozen_at must be an ISO 8601 timestamp") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("frozen_at must include a timezone")
    return parsed


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def _rank(example: ReviewedStage4Example) -> str:
    value = f"{SPLIT_SEED_IDENTIFIER}:{example.cv_profile.cv_profile_id}"
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _distribution(
    examples: tuple[ReviewedStage4Example, ...],
) -> dict[str, dict[str, int]]:
    role_counts = Counter(example.job_profile_id for example in examples)
    label_counts = Counter(example.final_label.value for example in examples)
    return {
        "roles": dict(sorted(role_counts.items())),
        "labels": dict(sorted(label_counts.items())),
    }


def build_split_manifest(
    repository_root: Path,
    frozen_at: str,
) -> dict[str, object]:
    timestamp = _timestamp(frozen_at).isoformat()
    examples = load_reviewed_stage4(repository_root)
    strata: dict[tuple[str, str], list[ReviewedStage4Example]] = defaultdict(list)
    for example in examples:
        strata[(example.job_profile_id, example.final_label.value)].append(example)
    if set(strata) != set(FROZEN_ALLOCATION):
        raise ValueError("Stage 6 split allocation does not cover the reviewed strata")
    frozen_examples: list[ReviewedStage4Example] = []
    validation_examples: list[ReviewedStage4Example] = []
    for stratum, selected_count in FROZEN_ALLOCATION.items():
        ordered = sorted(strata[stratum], key=_rank)
        if selected_count < 0 or selected_count > len(ordered):
            raise ValueError("Stage 6 frozen allocation exceeds its source stratum")
        frozen_examples.extend(ordered[:selected_count])
        validation_examples.extend(ordered[selected_count:])
    frozen = tuple(sorted(frozen_examples, key=lambda item: item.cv_profile.cv_profile_id))
    validation = tuple(sorted(validation_examples, key=lambda item: item.cv_profile.cv_profile_id))
    if len(validation) != 20 or len(frozen) != 10:
        raise ValueError("Stage 6 split must contain 20 validation and 10 frozen-test cases")
    source_labels = {example.final_label for example in examples}
    if {example.final_label for example in validation} != source_labels or {
        example.final_label for example in frozen
    } != source_labels:
        raise ValueError("both Stage 6 partitions must retain every classification label")
    return {
        "schema_version": "1.0.0",
        "split_manifest_id": "stage6-reviewed-dataset-split-v1",
        "split_policy_version": "1.0.0",
        "selection_method": "stratified-role-label-sha256-ranking",
        "split_seed_identifier": SPLIT_SEED_IDENTIFIER,
        "frozen_at": timestamp,
        "source": {
            "dataset_id": "stage4-review-dataset-v1",
            "dataset_version": "1.0.0",
            "cv_file": SOURCE_CV_PATH.as_posix(),
            "annotation_file": SOURCE_ANNOTATION_PATH.as_posix(),
            "cv_sha256": _sha256(repository_root / SOURCE_CV_PATH),
            "annotation_sha256": _sha256(repository_root / SOURCE_ANNOTATION_PATH),
            "sample_count": len(examples),
        },
        "validation": {
            "partition_id": "stage6-validation-v1",
            "tuning_allowed": True,
            "sample_count": len(validation),
            "distribution": _distribution(validation),
            "cv_profile_ids": [example.cv_profile.cv_profile_id for example in validation],
        },
        "frozen_test": {
            "partition_id": "stage7-frozen-test-v1",
            "tuning_allowed": False,
            "evaluation_allowed_from_stage": 7,
            "classifier_results_generated": False,
            "sample_count": len(frozen),
            "distribution": _distribution(frozen),
            "cv_profile_ids": [example.cv_profile.cv_profile_id for example in frozen],
        },
    }


def write_split_manifest(
    repository_root: Path,
    frozen_at: str,
) -> Path:
    manifest = build_split_manifest(repository_root, frozen_at)
    output_path = repository_root / SPLIT_MANIFEST_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frozen-at", required=True)
    arguments = parser.parse_args()
    write_split_manifest(
        REPOSITORY_ROOT,
        cast(str, arguments.frozen_at),
    )


if __name__ == "__main__":
    main()
