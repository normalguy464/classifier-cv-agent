from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Sequence, cast

from pydantic import BaseModel

from backend.app.contracts import CVProfile, JobProfile, ScoringRubric
from evaluation.datasets.synthetic_expansion import (
    ApprovedDatasetReview,
    DatasetTier,
    FileDigest,
    SyntheticExpansionManifest,
    SyntheticPairAnnotation,
    file_sha256,
    validate_synthetic_expansion,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORY = Path("data/synthetic_expansion/v2")
REVIEWED_DIRECTORY = Path("data/synthetic_expansion/reviewed/v2")
REVIEWED_DATASET_ID = "synthetic-cv-jd-expansion-v2-reviewed-silver"
REVIEWED_DATASET_VERSION = "2.1.0"
REVIEW_NOTE = (
    "Người dùng đã xác nhận yêu cầu, JD, CV, trạng thái yêu cầu, năm nhóm điểm, "
    "draft label và rationale cho toàn bộ 250 cặp của synthetic expansion v2."
)


def _reviewed_at(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError("reviewed_at must be an ISO 8601 timestamp") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("reviewed_at must include a timezone")
    return parsed


def _json_lines(path: Path, model_type: type[BaseModel]) -> tuple[BaseModel, ...]:
    return tuple(
        model_type.model_validate_json(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )


def _write_json_lines(path: Path, records: Sequence[BaseModel]) -> None:
    values = (
        json.dumps(record.model_dump(mode="json"), ensure_ascii=False, sort_keys=True)
        for record in records
    )
    path.write_text("\n".join(values) + "\n", encoding="utf-8")


def build_reviewed_dataset(
    repository_root: Path,
    reviewer_reference: str,
    reviewed_at: str,
) -> tuple[
    tuple[CVProfile, ...],
    tuple[JobProfile, ...],
    tuple[ScoringRubric, ...],
    tuple[SyntheticPairAnnotation, ...],
    SyntheticExpansionManifest,
    datetime,
    str,
]:
    reviewer = reviewer_reference.strip()
    if not reviewer:
        raise ValueError("reviewer_reference must not be empty")
    timestamp = _reviewed_at(reviewed_at)
    source_directory = repository_root / SOURCE_DIRECTORY
    source_report = validate_synthetic_expansion(source_directory)
    if not source_report.passed:
        raise ValueError("source synthetic expansion must pass quality control")
    source_manifest_path = source_directory / "manifest.json"
    source_manifest = SyntheticExpansionManifest.model_validate_json(
        source_manifest_path.read_text(encoding="utf-8")
    )
    if source_manifest.status != "draft_for_human_review":
        raise ValueError("source synthetic expansion must retain draft status")
    profiles = cast(
        tuple[CVProfile, ...], _json_lines(source_directory / "cv_profiles.jsonl", CVProfile)
    )
    jobs = cast(
        tuple[JobProfile, ...],
        _json_lines(source_directory / "job_profiles.jsonl", JobProfile),
    )
    rubrics = cast(
        tuple[ScoringRubric, ...],
        _json_lines(source_directory / "rubrics.jsonl", ScoringRubric),
    )
    source_annotations = cast(
        tuple[SyntheticPairAnnotation, ...],
        _json_lines(source_directory / "pairs.jsonl", SyntheticPairAnnotation),
    )
    reviewed_annotations = tuple(
        SyntheticPairAnnotation.model_validate(
            {
                **annotation.model_dump(mode="json"),
                "dataset_tier": DatasetTier.SILVER,
                "review": ApprovedDatasetReview(
                    human_review_count=1,
                    reviewer_references=(reviewer,),
                    final_label=annotation.draft_label,
                    notes=REVIEW_NOTE,
                    reviewed_at=timestamp,
                ).model_dump(mode="json"),
            }
        )
        for annotation in source_annotations
    )
    return (
        profiles,
        jobs,
        rubrics,
        reviewed_annotations,
        source_manifest,
        timestamp,
        reviewer,
    )


def write_reviewed_dataset(
    repository_root: Path,
    reviewer_reference: str,
    reviewed_at: str,
) -> tuple[Path, ...]:
    (
        profiles,
        jobs,
        rubrics,
        annotations,
        source_manifest,
        timestamp,
        reviewer,
    ) = build_reviewed_dataset(repository_root, reviewer_reference, reviewed_at)
    output_directory = repository_root / REVIEWED_DIRECTORY
    output_directory.mkdir(parents=True, exist_ok=True)
    paths = (
        output_directory / "cv_profiles.jsonl",
        output_directory / "job_profiles.jsonl",
        output_directory / "rubrics.jsonl",
        output_directory / "pairs.jsonl",
    )
    records = (profiles, jobs, rubrics, annotations)
    for path, values in zip(paths, records, strict=True):
        _write_json_lines(path, values)
    source_manifest_path = repository_root / SOURCE_DIRECTORY / "manifest.json"
    manifest = SyntheticExpansionManifest(
        schema_version="1.2.0",
        dataset_id=REVIEWED_DATASET_ID,
        dataset_version=REVIEWED_DATASET_VERSION,
        status="human_reviewed_silver",
        generated_at=timestamp.isoformat(),
        cv_schema_version=source_manifest.cv_schema_version,
        job_profile_schema_version=source_manifest.job_profile_schema_version,
        rubric_schema_version=source_manifest.rubric_schema_version,
        configuration_version=source_manifest.configuration_version,
        roles=source_manifest.roles,
        job_variants=source_manifest.job_variants,
        scenarios=source_manifest.scenarios,
        cv_profile_count=len(profiles),
        job_profile_count=len(jobs),
        rubric_count=len(rubrics),
        pair_count=len(annotations),
        tier_counts={DatasetTier.SILVER: len(annotations)},
        human_reviewed_pair_count=len(annotations),
        split_status="unassigned",
        frozen_test_created=False,
        market_reference_version=source_manifest.market_reference_version,
        reviewer_references=(reviewer,),
        reviewed_at=timestamp,
        source_dataset_id=source_manifest.dataset_id,
        source_dataset_version=source_manifest.dataset_version,
        source_manifest_sha256=file_sha256(source_manifest_path),
        provenance=source_manifest.provenance
        + (
            "All 250 draft annotations were approved unchanged by one pseudonymous human reviewer.",
            "The fifth criterion display title was clarified without changing its identifier, weight, score or meaning.",
        ),
        files=tuple(
            FileDigest(path=path.name, sha256=file_sha256(path), record_count=len(values))
            for path, values in zip(paths, records, strict=True)
        ),
    )
    manifest_path = output_directory / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report = validate_synthetic_expansion(output_directory)
    report_path = output_directory / "quality_report.json"
    report_path.write_text(
        json.dumps(report.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if not report.passed:
        raise ValueError("reviewed synthetic expansion failed quality validation")
    return paths + (manifest_path, report_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reviewer-reference", required=True)
    parser.add_argument("--reviewed-at", required=True)
    arguments = parser.parse_args()
    for path in write_reviewed_dataset(
        REPOSITORY_ROOT,
        cast(str, arguments.reviewer_reference),
        cast(str, arguments.reviewed_at),
    ):
        print(path)


if __name__ == "__main__":
    main()
