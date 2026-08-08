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
SOURCE_DIRECTORY = Path("data/synthetic_expansion/reviewed/v2")
OUTPUT_DIRECTORY = Path("data/synthetic_expansion/reviewed/v2_2")
SOURCE_SPLIT_MANIFEST_PATH = Path("data/synthetic_expansion/splits/v2_silver_split_manifest.json")
OUTPUT_SPLIT_MANIFEST_PATH = Path("data/synthetic_expansion/splits/v2_2_silver_split_manifest.json")
DATASET_ID = "synthetic-cv-jd-expansion-v2-reviewed-silver"
DATASET_VERSION = "2.2.0"
APPROVED_AT = "2026-08-01T13:14:13.491079+07:00"
REVIEW_NOTE = (
    "Người dùng đã phê duyệt sửa thông tin bị rò năng lực trong hồ sơ synthetic, "
    "giữ trạng thái missing_critical, năm nhóm điểm, nhãn và rationale của cặp liên quan."
)
EVIDENCE_TEXT_REPLACEMENTS = {
    "cv-syn-da-missing-v2": {
        "ev-da-missing-technical": (
            "Trong dự án, làm sạch dữ liệu đơn hàng và vận hành bằng pandas rồi xây "
            "dashboard KPI; Các phần còn lại có thao tác kỹ thuật và kiểm tra đầu vào cơ bản."
        ),
        "ev-da-missing-delivery": (
            "Kết quả bàn giao: notebook, data dictionary và dashboard có hướng dẫn refresh; "
            "Có bản chạy thử cùng tệp mẫu."
        ),
    },
    "cv-syn-de-missing-v2": {
        "ev-de-missing-technical": (
            "Trong dự án, xây pipeline nhiều nguồn bằng công cụ ETL và SQL, incremental load "
            "vào star schema cùng data quality checks; Các phần còn lại có thao tác kỹ thuật "
            "và kiểm tra đầu vào cơ bản."
        ),
        "ev-de-missing-delivery": (
            "Kết quả bàn giao: Docker Compose, migration, cấu hình pipeline, test dữ liệu và "
            "runbook vận hành; Có bản chạy thử cùng tệp mẫu."
        ),
    },
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
    replacements = EVIDENCE_TEXT_REPLACEMENTS.get(profile.cv_profile_id)
    if replacements is None:
        return profile
    known_ids = {item.evidence_id for item in profile.evidence}
    if not set(replacements).issubset(known_ids):
        raise ValueError(f"remediation evidence is missing from {profile.cv_profile_id}")
    return profile.model_copy(
        update={
            "evidence": tuple(
                item.model_copy(update={"text": replacements[item.evidence_id]})
                if item.evidence_id in replacements
                else item
                for item in profile.evidence
            )
        }
    )


def _rereview_annotation(
    annotation: SyntheticPairAnnotation,
    approved_at: datetime,
) -> SyntheticPairAnnotation:
    if annotation.cv_profile_id not in EVIDENCE_TEXT_REPLACEMENTS:
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
        or source_manifest.dataset_version != "2.1.0"
        or source_manifest.status != "human_reviewed_silver"
    ):
        raise ValueError("remediation source identity does not match reviewed version 2.1.0")
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
        item.pair_id for item in annotations if item.cv_profile_id in EVIDENCE_TEXT_REPLACEMENTS
    }
    if len(affected_pair_ids) != 10:
        raise ValueError("exactly ten CV-JD pairs must be re-reviewed")
    if not affected_pair_ids.issubset(set(source_split.development.pair_ids)):
        raise ValueError("remediated pairs must remain development-only")
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
                "Version 2.2.0 removes unintended SQL evidence from cv-syn-da-missing-v2.",
                "Version 2.2.0 removes unintended Python evidence from cv-syn-de-missing-v2.",
                "The user approved retaining missing_critical intent, scores, labels and rationales for all ten affected development pairs.",
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
            "split_manifest_id": "synthetic-expansion-v2-2-silver-split-v1",
            "created_at": approved_at,
            "source_dataset_version": DATASET_VERSION,
            "source_directory": OUTPUT_DIRECTORY.as_posix(),
            "source_manifest_sha256": file_sha256(manifest_path),
            "development": source_split.development.model_copy(
                update={
                    "partition_id": "synthetic-expansion-v2-2-development-silver",
                }
            ),
            "held_out": source_split.held_out.model_copy(
                update={
                    "partition_id": "synthetic-expansion-v2-2-held-out-silver",
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
