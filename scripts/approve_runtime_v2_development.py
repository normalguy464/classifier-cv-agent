from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Sequence, TypeVar, cast

from pydantic import BaseModel

from backend.app.contracts import CVProfile, JobProfile, ScoringRubric
from evaluation.datasets.runtime_v2 import (
    RuntimeV2DevelopmentManifest,
    RuntimeV2FileDigest,
    RuntimeV2HumanReviewRecord,
    RuntimeV2ReviewedManifest,
    file_sha256,
    validate_runtime_v2_development,
    validate_runtime_v2_reviewed,
)
from evaluation.datasets.synthetic_expansion import (
    ApprovedDatasetReview,
    DatasetTier,
    SyntheticPairAnnotation,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORY = Path("data/runtime_v2/to_review/development_v1")
REVIEWED_DIRECTORY = Path("data/runtime_v2/reviewed/development_v1")
REVIEWER_REFERENCE = "reviewer-user-runtime-v2"
USER_STATEMENT = (
    "Tôi duyệt toàn bộ 75 case của five-role-runtime-v2-development-v1, gồm requirement "
    "status, năm nhóm điểm, nhãn và rationale. Hãy chuyển dataset sang Silver và tiếp tục "
    "cải thiện L1/L2; chưa gọi API cho đến khi checkpoint offline đạt."
)
REVIEW_NOTE = (
    "Người dùng đã phê duyệt không sửa đổi requirement status, năm nhóm điểm, nhãn và "
    "rationale của toàn bộ 75 case development Runtime v2."
)
ModelType = TypeVar("ModelType", bound=BaseModel)


def _timestamp(value: str) -> datetime:
    try:
        timestamp = datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError("reviewed_at must be an ISO 8601 timestamp") from error
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("reviewed_at must include a timezone")
    return timestamp


def _load_lines(path: Path, model_type: type[ModelType]) -> tuple[ModelType, ...]:
    return tuple(
        model_type.model_validate_json(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )


def _write_lines(path: Path, records: Sequence[BaseModel]) -> None:
    path.write_text(
        "\n".join(
            json.dumps(item.model_dump(mode="json"), ensure_ascii=False, sort_keys=True)
            for item in records
        )
        + "\n",
        encoding="utf-8",
    )


def write_reviewed_runtime_v2_development(
    repository_root: Path,
    reviewed_at: str,
    reviewer_reference: str = REVIEWER_REFERENCE,
) -> tuple[Path, ...]:
    timestamp = _timestamp(reviewed_at)
    reviewer = reviewer_reference.strip()
    if not reviewer:
        raise ValueError("reviewer_reference must not be empty")
    source_directory = repository_root / SOURCE_DIRECTORY
    source_report = validate_runtime_v2_development(source_directory, repository_root)
    if not source_report.passed or source_report.warnings:
        raise ValueError("Bronze Runtime v2 development must pass QC without warnings")
    source_manifest_path = source_directory / "manifest.json"
    source_manifest = RuntimeV2DevelopmentManifest.model_validate_json(
        source_manifest_path.read_text(encoding="utf-8")
    )
    profiles = _load_lines(source_directory / "cv_profiles.jsonl", CVProfile)
    jobs = _load_lines(source_directory / "job_profiles.jsonl", JobProfile)
    rubrics = _load_lines(source_directory / "rubrics.jsonl", ScoringRubric)
    source_pairs = _load_lines(source_directory / "pairs.jsonl", SyntheticPairAnnotation)
    reviewed_pairs = tuple(
        SyntheticPairAnnotation.model_validate(
            {
                **pair.model_dump(mode="json"),
                "dataset_tier": DatasetTier.SILVER,
                "review": ApprovedDatasetReview(
                    human_review_count=1,
                    reviewer_references=(reviewer,),
                    final_label=pair.draft_label,
                    notes=REVIEW_NOTE,
                    reviewed_at=timestamp,
                ).model_dump(mode="json"),
            }
        )
        for pair in source_pairs
    )
    output_directory = repository_root / REVIEWED_DIRECTORY
    output_directory.mkdir(parents=True, exist_ok=True)
    file_records: tuple[tuple[str, Sequence[BaseModel]], ...] = (
        ("cv_profiles.jsonl", profiles),
        ("job_profiles.jsonl", jobs),
        ("rubrics.jsonl", rubrics),
        ("pairs.jsonl", reviewed_pairs),
    )
    for name, records in file_records:
        output_path = output_directory / name
        if name == "pairs.jsonl":
            _write_lines(output_path, records)
        else:
            shutil.copyfile(source_directory / name, output_path)
    review_record = RuntimeV2HumanReviewRecord(
        dataset_id=source_manifest.dataset_id,
        review_status="approved_unchanged",
        reviewer_reference=reviewer,
        reviewed_at=timestamp,
        approved_pair_count=75,
        approval_scope=(
            "critical requirement status and linked information",
            "five criterion scores and total score",
            "classification label and Needs Review reasons",
            "criterion and overall rationale",
        ),
        user_statement=USER_STATEMENT,
    )
    review_record_path = output_directory / "review_record.json"
    review_record_path.write_text(
        json.dumps(review_record.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    files = tuple(
        RuntimeV2FileDigest(
            path=name,
            sha256=file_sha256(output_directory / name),
            record_count=len(records),
        )
        for name, records in file_records
    ) + (
        RuntimeV2FileDigest(
            path="review_record.json",
            sha256=file_sha256(review_record_path),
            record_count=1,
        ),
    )
    manifest = RuntimeV2ReviewedManifest(
        dataset_id="five-role-runtime-v2-development-v1-reviewed-silver",
        dataset_version="1.1.0",
        status="human_reviewed_silver",
        reviewed_at=timestamp,
        source_dataset_id=source_manifest.dataset_id,
        source_dataset_version=source_manifest.dataset_version,
        source_manifest_sha256=file_sha256(source_manifest_path),
        reviewer_references=(reviewer,),
        roles=source_manifest.roles,
        cv_profile_count=75,
        job_profile_count=5,
        rubric_count=5,
        pair_count=75,
        tier=DatasetTier.SILVER,
        ground_truth_status="human_reviewed_silver",
        split_status="unassigned",
        classifier_results_generated=False,
        llm_requests_made=False,
        provenance=source_manifest.provenance
        + ("All 75 draft annotations were approved unchanged by one pseudonymous human reviewer.",),
        files=files,
    )
    manifest_path = output_directory / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report = validate_runtime_v2_reviewed(output_directory, source_directory, repository_root)
    report_path = output_directory / "quality_report.json"
    report_path.write_text(
        json.dumps(report.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if not report.passed or report.warnings:
        raise ValueError(f"Reviewed Runtime v2 development failed QC: {report.errors}")
    return tuple(output_directory / name for name, _ in file_records) + (
        review_record_path,
        manifest_path,
        report_path,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reviewed-at", required=True)
    parser.add_argument("--reviewer-reference", default=REVIEWER_REFERENCE)
    arguments = parser.parse_args()
    paths = write_reviewed_runtime_v2_development(
        REPOSITORY_ROOT,
        cast(str, arguments.reviewed_at),
        cast(str, arguments.reviewer_reference),
    )
    print(json.dumps({"files": [str(path) for path in paths]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
