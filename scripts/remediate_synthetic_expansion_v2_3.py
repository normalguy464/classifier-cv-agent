from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Sequence, cast

from pydantic import BaseModel

from backend.app.contracts import CVProfile, JobProfile, ScoringRubric
from evaluation.datasets.synthetic_expansion import (
    ApprovedDatasetReview,
    FileDigest,
    SyntheticExpansionManifest,
    SyntheticExpansionSilverSplitManifest,
    SyntheticPairAnnotation,
    file_sha256,
    validate_synthetic_expansion,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORY = Path("data/synthetic_expansion/reviewed/v2_2")
OUTPUT_DIRECTORY = Path("data/synthetic_expansion/reviewed/v2_3")
SOURCE_SPLIT_MANIFEST_PATH = Path("data/synthetic_expansion/splits/v2_2_silver_split_manifest.json")
OUTPUT_SPLIT_MANIFEST_PATH = Path("data/synthetic_expansion/splits/v2_3_silver_split_manifest.json")
DATASET_ID = "synthetic-cv-jd-expansion-v2-reviewed-silver"
DATASET_VERSION = "2.3.0"
APPROVED_AT = "2026-08-01T13:40:06.047788+07:00"
TARGET_PROFILE_ID = "cv-syn-qa-failed-v2"
REVIEW_NOTE = (
    "Người dùng đã phê duyệt bỏ thông tin testing-foundation bị mâu thuẫn, giữ kịch bản "
    "explicit_failure, trạng thái qa-testing-foundations=unsatisfied, điểm, nhãn và rationale."
)
EVIDENCE_TEXT_REPLACEMENTS = {
    "ev-qa-failed-technical": (
        "Trong dự án, thực thi test case có sẵn, kiểm tra API và SQL rồi tự động hóa "
        "regression chính; Chỉ thực hiện tác vụ không liên quan trực tiếp đến yêu cầu chính."
    ),
    "ev-qa-failed-reasoning": (
        "Cách giải quyết: ghi nhận expected, actual và severity theo mẫu có sẵn; "
        "Mô tả kết quả mong muốn nhưng chưa có phương pháp phù hợp."
    ),
    "ev-qa-failed-delivery": (
        "Kết quả bàn giao: bảng test case, Postman collection, automation suite, bug report "
        "và regression report; Bài tập dừng ở bản minh họa một lần."
    ),
}


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


def _remediate_profile(profile: CVProfile) -> CVProfile:
    if profile.cv_profile_id != TARGET_PROFILE_ID:
        return profile
    known_ids = {item.evidence_id for item in profile.evidence}
    if not set(EVIDENCE_TEXT_REPLACEMENTS).issubset(known_ids):
        raise ValueError("QA remediation evidence is incomplete")
    return profile.model_copy(
        update={
            "evidence": tuple(
                item.model_copy(update={"text": EVIDENCE_TEXT_REPLACEMENTS[item.evidence_id]})
                if item.evidence_id in EVIDENCE_TEXT_REPLACEMENTS
                else item
                for item in profile.evidence
            )
        }
    )


def _rereview_annotation(
    annotation: SyntheticPairAnnotation,
    approved_at: datetime,
) -> SyntheticPairAnnotation:
    if annotation.cv_profile_id != TARGET_PROFILE_ID:
        return annotation
    review = cast(ApprovedDatasetReview, annotation.review)
    return annotation.model_copy(
        update={
            "review": review.model_copy(
                update={
                    "notes": REVIEW_NOTE,
                    "reviewed_at": approved_at,
                }
            )
        }
    )


def build_remediated_dataset(
    repository_root: Path,
) -> tuple[
    tuple[CVProfile, ...],
    tuple[JobProfile, ...],
    tuple[ScoringRubric, ...],
    tuple[SyntheticPairAnnotation, ...],
    SyntheticExpansionManifest,
    SyntheticExpansionSilverSplitManifest,
]:
    approved_at = datetime.fromisoformat(APPROVED_AT)
    source_directory = repository_root / SOURCE_DIRECTORY
    source_report = validate_synthetic_expansion(source_directory)
    if not source_report.passed:
        raise ValueError("source reviewed dataset must pass quality control")
    source_manifest_path = source_directory / "manifest.json"
    source_manifest = SyntheticExpansionManifest.model_validate_json(
        source_manifest_path.read_text(encoding="utf-8")
    )
    if (
        source_manifest.dataset_id != DATASET_ID
        or source_manifest.dataset_version != "2.2.0"
        or source_manifest.status != "human_reviewed_silver"
    ):
        raise ValueError("remediation source identity does not match reviewed version 2.2.0")
    profiles = tuple(
        _remediate_profile(profile)
        for profile in cast(
            tuple[CVProfile, ...],
            _json_lines(source_directory / "cv_profiles.jsonl", CVProfile),
        )
    )
    jobs = cast(
        tuple[JobProfile, ...],
        _json_lines(source_directory / "job_profiles.jsonl", JobProfile),
    )
    rubrics = cast(
        tuple[ScoringRubric, ...],
        _json_lines(source_directory / "rubrics.jsonl", ScoringRubric),
    )
    annotations = tuple(
        _rereview_annotation(annotation, approved_at)
        for annotation in cast(
            tuple[SyntheticPairAnnotation, ...],
            _json_lines(source_directory / "pairs.jsonl", SyntheticPairAnnotation),
        )
    )
    source_split = SyntheticExpansionSilverSplitManifest.model_validate_json(
        (repository_root / SOURCE_SPLIT_MANIFEST_PATH).read_text(encoding="utf-8")
    )
    affected_pair_ids = {
        item.pair_id for item in annotations if item.cv_profile_id == TARGET_PROFILE_ID
    }
    if len(affected_pair_ids) != 5:
        raise ValueError("exactly five QA CV-JD pairs must be re-reviewed")
    if not affected_pair_ids.issubset(set(source_split.development.pair_ids)):
        raise ValueError("remediated QA pairs must remain development-only")
    return profiles, jobs, rubrics, annotations, source_manifest, source_split


def write_remediated_dataset(repository_root: Path = REPOSITORY_ROOT) -> tuple[Path, ...]:
    profiles, jobs, rubrics, annotations, source_manifest, source_split = build_remediated_dataset(
        repository_root
    )
    approved_at = datetime.fromisoformat(APPROVED_AT)
    output_directory = repository_root / OUTPUT_DIRECTORY
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
    manifest = source_manifest.model_copy(
        update={
            "dataset_version": DATASET_VERSION,
            "generated_at": approved_at.isoformat(),
            "reviewed_at": approved_at,
            "source_dataset_id": source_manifest.dataset_id,
            "source_dataset_version": source_manifest.dataset_version,
            "source_manifest_sha256": file_sha256(source_manifest_path),
            "provenance": source_manifest.provenance
            + (
                "Version 2.3.0 removes contradictory testing-foundation claims from cv-syn-qa-failed-v2.",
                "The user approved retaining the explicit_failure intent and qa-testing-foundations=unsatisfied status for all five affected development pairs.",
            ),
            "files": tuple(
                FileDigest(path=path.name, sha256=file_sha256(path), record_count=len(values))
                for path, values in zip(paths, records, strict=True)
            ),
        }
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
        raise ValueError("remediated synthetic expansion failed quality validation")
    split = source_split.model_copy(
        update={
            "split_manifest_id": "synthetic-expansion-v2-3-silver-split-v1",
            "created_at": approved_at,
            "source_dataset_version": DATASET_VERSION,
            "source_directory": OUTPUT_DIRECTORY.as_posix(),
            "source_manifest_sha256": file_sha256(manifest_path),
            "development": source_split.development.model_copy(
                update={
                    "partition_id": "synthetic-expansion-v2-3-development-silver",
                }
            ),
            "held_out": source_split.held_out.model_copy(
                update={
                    "partition_id": "synthetic-expansion-v2-3-held-out-silver",
                }
            ),
        }
    )
    split_path = repository_root / OUTPUT_SPLIT_MANIFEST_PATH
    split_path.parent.mkdir(parents=True, exist_ok=True)
    split_path.write_text(
        json.dumps(split.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return paths + (manifest_path, report_path, split_path)


def main() -> None:
    for path in write_remediated_dataset():
        print(path)


if __name__ == "__main__":
    main()
