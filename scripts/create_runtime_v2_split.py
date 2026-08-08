from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import cast

from backend.app.contracts import ClassificationDecision
from evaluation.datasets.runtime_v2 import (
    RuntimeV2Partition,
    RuntimeV2ReviewedManifest,
    RuntimeV2SplitManifest,
    file_sha256,
    validate_runtime_v2_reviewed,
)
from evaluation.datasets.synthetic_expansion import (
    ApprovedDatasetReview,
    DatasetRole,
    SyntheticPairAnnotation,
)
from scripts.approve_runtime_v2_development import REVIEWED_DIRECTORY, SOURCE_DIRECTORY

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SPLIT_MANIFEST_PATH = Path("data/runtime_v2/splits/development_v1_split.json")
SPLIT_SEED_IDENTIFIER = "five-role-runtime-v2-role-label-candidate-sha256-v1"
VALIDATION_COUNT_PER_ROLE_LABEL = {
    ClassificationDecision.PASS: 1,
    ClassificationDecision.WAITLIST: 1,
    ClassificationDecision.REJECT: 1,
    ClassificationDecision.NEEDS_REVIEW: 2,
}


def _timestamp(value: str) -> datetime:
    try:
        timestamp = datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError("created_at must be an ISO 8601 timestamp") from error
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("created_at must include a timezone")
    return timestamp


def _rank(pair: SyntheticPairAnnotation) -> str:
    value = f"{SPLIT_SEED_IDENTIFIER}:{pair.candidate_reference}:{pair.pair_id}"
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _label(pair: SyntheticPairAnnotation) -> ClassificationDecision:
    if not isinstance(pair.review, ApprovedDatasetReview):
        raise ValueError("split requires approved Silver annotations")
    return pair.review.final_label


def _partition(
    partition_id: str,
    intended_use: str,
    pairs: tuple[SyntheticPairAnnotation, ...],
) -> RuntimeV2Partition:
    return RuntimeV2Partition.model_validate(
        {
            "partition_id": partition_id,
            "intended_use": intended_use,
            "tuning_allowed": True,
            "final_performance_reporting_allowed": False,
            "pair_count": len(pairs),
            "role_pair_counts": dict(Counter(pair.role for pair in pairs)),
            "label_pair_counts": dict(Counter(_label(pair) for pair in pairs)),
            "candidate_references": tuple(sorted(pair.candidate_reference for pair in pairs)),
            "pair_ids": tuple(sorted(pair.pair_id for pair in pairs)),
        }
    )


def build_runtime_v2_split(repository_root: Path, created_at: str) -> RuntimeV2SplitManifest:
    timestamp = _timestamp(created_at)
    reviewed_directory = repository_root / REVIEWED_DIRECTORY
    source_directory = repository_root / SOURCE_DIRECTORY
    report = validate_runtime_v2_reviewed(
        reviewed_directory,
        source_directory,
        repository_root,
    )
    if not report.passed or report.warnings:
        raise ValueError("reviewed Runtime v2 development must pass QC without warnings")
    source_manifest_path = reviewed_directory / "manifest.json"
    source_manifest = RuntimeV2ReviewedManifest.model_validate_json(
        source_manifest_path.read_text(encoding="utf-8")
    )
    pairs = tuple(
        SyntheticPairAnnotation.model_validate_json(line)
        for line in (reviewed_directory / "pairs.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    )
    grouped: defaultdict[
        tuple[DatasetRole, ClassificationDecision], list[SyntheticPairAnnotation]
    ] = defaultdict(list)
    for pair in pairs:
        grouped[(pair.role, _label(pair))].append(pair)
    validation_ids: set[str] = set()
    for role in DatasetRole:
        for label, count in VALIDATION_COUNT_PER_ROLE_LABEL.items():
            ordered = sorted(grouped[(role, label)], key=_rank)
            if len(ordered) < count:
                raise ValueError(f"insufficient {label.value} pairs for {role.value}")
            validation_ids.update(pair.pair_id for pair in ordered[:count])
    validation_pairs = tuple(pair for pair in pairs if pair.pair_id in validation_ids)
    development_pairs = tuple(pair for pair in pairs if pair.pair_id not in validation_ids)
    return RuntimeV2SplitManifest(
        split_manifest_id="five-role-runtime-v2-development-split-v1",
        split_policy_version="1.0.0",
        selection_method="role-label-stratified-candidate-sha256-v1",
        split_seed_identifier=SPLIT_SEED_IDENTIFIER,
        created_at=timestamp,
        source_dataset_id=source_manifest.dataset_id,
        source_dataset_version=source_manifest.dataset_version,
        source_manifest_sha256=file_sha256(source_manifest_path),
        frozen_test_created=False,
        stage7_v1_test_excluded=True,
        development=_partition(
            "five-role-runtime-v2-rule-development-v1",
            "rule_and_policy_development",
            development_pairs,
        ),
        validation=_partition(
            "five-role-runtime-v2-configuration-validation-v1",
            "configuration_validation",
            validation_pairs,
        ),
    )


def write_runtime_v2_split(repository_root: Path, created_at: str) -> Path:
    manifest = build_runtime_v2_split(repository_root, created_at)
    output_path = repository_root / SPLIT_MANIFEST_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(manifest.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--created-at", required=True)
    arguments = parser.parse_args()
    print(write_runtime_v2_split(REPOSITORY_ROOT, cast(str, arguments.created_at)))


if __name__ == "__main__":
    main()
