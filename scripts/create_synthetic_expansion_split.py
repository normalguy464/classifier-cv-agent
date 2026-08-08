from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Literal, cast

from evaluation.datasets.synthetic_expansion import (
    ApprovedDatasetReview,
    DatasetRole,
    DatasetTier,
    SyntheticExpansionManifest,
    SyntheticExpansionPartition,
    SyntheticExpansionSilverSplitManifest,
    SyntheticPairAnnotation,
    file_sha256,
    validate_synthetic_expansion,
)
from scripts.approve_synthetic_expansion import REVIEWED_DIRECTORY

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SPLIT_MANIFEST_PATH = Path("data/synthetic_expansion/splits/v2_silver_split_manifest.json")
SPLIT_SEED_IDENTIFIER = "synthetic-expansion-v2-role-candidate-sha256-v1"


def _timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError("created_at must be an ISO 8601 timestamp") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("created_at must include a timezone")
    return parsed


def _rank(candidate_reference: str) -> str:
    value = f"{SPLIT_SEED_IDENTIFIER}:{candidate_reference}"
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _partition(
    partition_id: str,
    intended_use: Literal["development_validation", "held_out_diagnostic"],
    tuning_allowed: bool,
    annotations: tuple[SyntheticPairAnnotation, ...],
) -> SyntheticExpansionPartition:
    candidate_roles = {
        annotation.candidate_reference: annotation.role for annotation in annotations
    }
    labels = Counter(
        cast(ApprovedDatasetReview, annotation.review).final_label for annotation in annotations
    )
    return SyntheticExpansionPartition(
        partition_id=partition_id,
        intended_use=intended_use,
        tuning_allowed=tuning_allowed,
        candidate_count=len(candidate_roles),
        pair_count=len(annotations),
        role_candidate_counts=dict(Counter(candidate_roles.values())),
        label_pair_counts=dict(labels),
        candidate_references=tuple(sorted(candidate_roles)),
        pair_ids=tuple(sorted(annotation.pair_id for annotation in annotations)),
    )


def build_split_manifest(
    repository_root: Path,
    created_at: str,
) -> SyntheticExpansionSilverSplitManifest:
    timestamp = _timestamp(created_at)
    source_directory = repository_root / REVIEWED_DIRECTORY
    report = validate_synthetic_expansion(source_directory)
    if not report.passed:
        raise ValueError("reviewed synthetic expansion must pass quality control")
    source_manifest_path = source_directory / "manifest.json"
    source_manifest = SyntheticExpansionManifest.model_validate_json(
        source_manifest_path.read_text(encoding="utf-8")
    )
    if source_manifest.status != "human_reviewed_silver":
        raise ValueError("split source must be a human-reviewed silver dataset")
    annotations = tuple(
        SyntheticPairAnnotation.model_validate_json(line)
        for line in (source_directory / "pairs.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    )
    candidate_groups: dict[str, list[SyntheticPairAnnotation]] = defaultdict(list)
    for annotation in annotations:
        candidate_groups[annotation.candidate_reference].append(annotation)
    if any(len(values) != 5 for values in candidate_groups.values()):
        raise ValueError("every candidate must have exactly five CV-JD pairs")
    candidates_by_role: dict[DatasetRole, list[str]] = defaultdict(list)
    for candidate_reference, values in candidate_groups.items():
        roles = {value.role for value in values}
        if len(roles) != 1:
            raise ValueError("each candidate must belong to exactly one role")
        candidates_by_role[next(iter(roles))].append(candidate_reference)
    if set(candidates_by_role) != set(DatasetRole):
        raise ValueError("split source must cover all dataset roles")
    held_out_references: set[str] = set()
    for role in DatasetRole:
        ordered = sorted(candidates_by_role[role], key=_rank)
        if len(ordered) != 10:
            raise ValueError("each role must contain exactly ten candidates")
        held_out_references.update(ordered[:4])
    held_out_annotations = tuple(
        annotation
        for annotation in annotations
        if annotation.candidate_reference in held_out_references
    )
    development_annotations = tuple(
        annotation
        for annotation in annotations
        if annotation.candidate_reference not in held_out_references
    )
    development = _partition(
        "synthetic-expansion-v2-development-silver",
        "development_validation",
        True,
        development_annotations,
    )
    held_out = _partition(
        "synthetic-expansion-v2-held-out-silver",
        "held_out_diagnostic",
        False,
        held_out_annotations,
    )
    return SyntheticExpansionSilverSplitManifest(
        split_manifest_id="synthetic-expansion-v2-silver-split-v1",
        split_policy_version="1.0.0",
        selection_method="role-grouped-candidate-sha256-ranking",
        split_seed_identifier=SPLIT_SEED_IDENTIFIER,
        created_at=timestamp,
        source_dataset_id=source_manifest.dataset_id,
        source_dataset_version=source_manifest.dataset_version,
        source_dataset_tier=DatasetTier.SILVER,
        source_directory=REVIEWED_DIRECTORY.as_posix(),
        source_manifest_sha256=file_sha256(source_manifest_path),
        frozen_test_created=False,
        gold_review_required_for_final_evaluation=True,
        development=development,
        held_out=held_out,
    )


def write_split_manifest(repository_root: Path, created_at: str) -> Path:
    manifest = build_split_manifest(repository_root, created_at)
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
    print(write_split_manifest(REPOSITORY_ROOT, cast(str, arguments.created_at)))


if __name__ == "__main__":
    main()
