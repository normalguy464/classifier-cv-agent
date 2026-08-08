from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Sequence, cast

from pydantic import BaseModel

from backend.app.contracts import CVProfile, JobProfile, ScoringRubric
from evaluation.datasets.stage7 import (
    Stage7FileDigest,
    Stage7FrozenManifest,
    Stage7HumanReviewRecord,
    Stage7TestManifest,
    stage7_manifest_sha256,
    validate_stage7_frozen_test_set,
    validate_stage7_test_set,
)
from evaluation.datasets.synthetic_expansion import (
    ApprovedDatasetReview,
    DatasetTier,
    SyntheticPairAnnotation,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORY = Path("data/to_review/stage7_runtime_v2_test_v1")
FROZEN_DIRECTORY = Path("data/frozen_test/stage7_runtime_v2_v1")
REVIEWER_REFERENCES = ("reviewer-user-001", "reviewer-peer-001")
APPROVAL_STATEMENT = (
    "Tôi và người thứ hai đã duyệt toàn bộ 50 case của "
    "stage7-five-role-runtime-v2-test-v1 phiên bản 1.0.0, gồm nội dung CV, requirement "
    "status, năm nhóm điểm, tổng điểm, nhãn và rationale; chúng tôi thống nhất dùng kết quả "
    "này làm human review cuối, chấp nhận protocol tối thiểu accuracy 70% cùng các điều kiện "
    "an toàn đã nêu, và cho phép khóa test set thành Gold. Chưa gọi API cho tới khi bước "
    "khóa và preflight hoàn tất."
)
REVIEW_NOTE = (
    "Hai người đã cùng xem, thảo luận và thống nhất nội dung CV, requirement status, năm nhóm "
    "điểm, tổng điểm, nhãn và rationale cho đủ 50 case Runtime v2. Đây là hội đồng đồng thuận "
    "hai người, không được mô tả là hai lượt chấm độc lập."
)


def _reviewed_at(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
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
    path.write_text(
        "\n".join(
            json.dumps(record.model_dump(mode="json"), ensure_ascii=False, sort_keys=True)
            for record in records
        )
        + "\n",
        encoding="utf-8",
    )


def write_frozen_stage7_runtime_v2_test_set(
    repository_root: Path,
    reviewed_at: str,
    output_directory: Path | None = None,
) -> tuple[Path, ...]:
    timestamp = _reviewed_at(reviewed_at)
    source_directory = repository_root / SOURCE_DIRECTORY
    target_directory = output_directory or repository_root / FROZEN_DIRECTORY
    if target_directory.exists() and any(target_directory.iterdir()):
        raise ValueError("frozen Stage 7 Runtime v2 target already contains files")
    source_report = validate_stage7_test_set(repository_root, source_directory)
    if not source_report.passed or source_report.warnings:
        raise ValueError("Stage 7 Runtime v2 source dataset must pass QC without warnings")
    source_manifest_path = source_directory / "manifest.json"
    source_manifest = Stage7TestManifest.model_validate_json(
        source_manifest_path.read_text(encoding="utf-8")
    )
    if (
        source_manifest.dataset_id != "stage7-five-role-runtime-v2-test-v1"
        or source_manifest.dataset_version != "1.0.0"
        or source_manifest.runtime_configuration_set_id != "five-role-runtime-v2"
    ):
        raise ValueError("Stage 7 Runtime v2 approval received an incompatible manifest")
    profiles = cast(
        tuple[CVProfile, ...], _json_lines(source_directory / "cv_profiles.jsonl", CVProfile)
    )
    jobs = cast(
        tuple[JobProfile, ...], _json_lines(source_directory / "job_profiles.jsonl", JobProfile)
    )
    rubrics = cast(
        tuple[ScoringRubric, ...],
        _json_lines(source_directory / "rubrics.jsonl", ScoringRubric),
    )
    source_annotations = cast(
        tuple[SyntheticPairAnnotation, ...],
        _json_lines(source_directory / "pairs.jsonl", SyntheticPairAnnotation),
    )
    frozen_annotations = tuple(
        SyntheticPairAnnotation.model_validate(
            {
                **annotation.model_dump(mode="json"),
                "dataset_tier": DatasetTier.GOLD,
                "review": ApprovedDatasetReview(
                    human_review_count=2,
                    reviewer_references=REVIEWER_REFERENCES,
                    final_label=annotation.draft_label,
                    notes=REVIEW_NOTE,
                    reviewed_at=timestamp,
                ).model_dump(mode="json"),
            }
        )
        for annotation in source_annotations
    )
    target_directory.mkdir(parents=True, exist_ok=True)
    data_paths = tuple(
        target_directory / name
        for name in ("cv_profiles.jsonl", "job_profiles.jsonl", "rubrics.jsonl", "pairs.jsonl")
    )
    for path, records in zip(
        data_paths,
        (profiles, jobs, rubrics, frozen_annotations),
        strict=True,
    ):
        _write_json_lines(path, records)
    review_record = Stage7HumanReviewRecord(
        schema_version="1.0.0",
        dataset_id=source_manifest.dataset_id,
        dataset_version=source_manifest.dataset_version,
        review_mode="two_person_consensus_panel",
        reviewer_references=REVIEWER_REFERENCES,
        reviewed_at=timestamp,
        approved_pair_count=50,
        approved_correction_pair_ids=(),
        approval_statement=APPROVAL_STATEMENT,
    )
    review_record_path = target_directory / "review_record.json"
    review_record_path.write_text(
        json.dumps(review_record.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    runtime_manifest_path = repository_root / source_manifest.runtime_manifest_path
    final_label_counts = Counter(
        cast(ApprovedDatasetReview, annotation.review).final_label
        for annotation in frozen_annotations
    )
    manifest = Stage7FrozenManifest(
        schema_version="1.0.0",
        dataset_id=source_manifest.dataset_id,
        dataset_version=source_manifest.dataset_version,
        status="human_reviewed_gold_locked",
        frozen_at=timestamp,
        runtime_configuration_set_id=source_manifest.runtime_configuration_set_id,
        runtime_manifest_path=source_manifest.runtime_manifest_path,
        runtime_manifest_sha256=stage7_manifest_sha256(runtime_manifest_path),
        source_directory="data/to_review/stage7_runtime_v2_test_v1",
        source_manifest_sha256=stage7_manifest_sha256(source_manifest_path),
        review_record_path="review_record.json",
        review_record_sha256=stage7_manifest_sha256(review_record_path),
        review_mode="two_person_consensus_panel",
        reviewer_references=REVIEWER_REFERENCES,
        reviewed_pair_count=50,
        pair_count=50,
        dataset_tier=DatasetTier.GOLD,
        ground_truth_status="human_reviewed_gold",
        locked_for_evaluation=True,
        classifier_results_generated_before_lock=False,
        llm_requests_made_before_lock=False,
        final_label_counts=dict(final_label_counts),
        files=tuple(
            Stage7FileDigest(
                path=path.name,
                sha256=stage7_manifest_sha256(path),
                record_count=len(records),
            )
            for path, records in zip(
                data_paths,
                (profiles, jobs, rubrics, frozen_annotations),
                strict=True,
            )
        ),
    )
    manifest_path = target_directory / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report = validate_stage7_frozen_test_set(repository_root, target_directory)
    report_path = target_directory / "quality_report.json"
    report_path.write_text(
        json.dumps(report.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if not report.passed or report.warnings:
        raise ValueError("frozen Stage 7 Runtime v2 dataset failed quality control")
    return data_paths + (review_record_path, manifest_path, report_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reviewed-at", required=True)
    arguments = parser.parse_args()
    for path in write_frozen_stage7_runtime_v2_test_set(
        REPOSITORY_ROOT,
        cast(str, arguments.reviewed_at),
    ):
        print(path)


if __name__ == "__main__":
    main()
