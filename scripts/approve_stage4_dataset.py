from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import cast

from backend.app.contracts import CVProfile, ClassificationDecision

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DRAFT_CV_PATH = Path("data/to_review/stage4_cv_profiles_v1.jsonl")
DRAFT_ANNOTATION_PATH = Path("data/to_review/stage4_annotations_v1.json")
REVIEWED_CV_PATH = Path("data/reviewed/stage4_cv_profiles_v1.jsonl")
REVIEWED_ANNOTATION_PATH = Path("data/reviewed/stage4_annotations_v1.json")
REVIEW_NOTE = (
    "Người dùng đã xác nhận requirement status, năm nhóm điểm, draft label và rationale "
    "cho toàn bộ 30 hồ sơ Stage 4."
)


def _json_object(path: Path) -> dict[str, object]:
    value = cast(object, json.loads(path.read_text(encoding="utf-8")))
    if not isinstance(value, dict):
        raise ValueError(f"JSON artifact must be an object: {path.name}")
    return cast(dict[str, object], value)


def _profiles(path: Path) -> tuple[CVProfile, ...]:
    profiles = tuple(
        CVProfile.model_validate_json(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )
    profile_ids = tuple(profile.cv_profile_id for profile in profiles)
    if len(profiles) != 30 or len(profile_ids) != len(set(profile_ids)):
        raise ValueError("Stage 4 review requires exactly 30 unique CV profiles")
    return profiles


def _reviewed_at(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError("reviewed_at must be an ISO 8601 timestamp") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("reviewed_at must include a timezone")
    return parsed


def build_reviewed_dataset(
    repository_root: Path,
    reviewer_reference: str,
    reviewed_at: str,
) -> tuple[tuple[CVProfile, ...], dict[str, object]]:
    reviewer = reviewer_reference.strip()
    if not reviewer:
        raise ValueError("reviewer_reference must not be empty")
    timestamp = _reviewed_at(reviewed_at).isoformat()
    profiles = _profiles(repository_root / DRAFT_CV_PATH)
    profile_ids = {profile.cv_profile_id for profile in profiles}
    draft = _json_object(repository_root / DRAFT_ANNOTATION_PATH)
    if draft.get("annotation_status") != "draft":
        raise ValueError("Stage 4 source annotations must retain draft status")
    records_value = draft.get("records")
    if not isinstance(records_value, list):
        raise ValueError("Stage 4 review requires exactly 30 annotation records")
    records = cast(list[object], records_value)
    if len(records) != 30:
        raise ValueError("Stage 4 review requires exactly 30 annotation records")
    reviewed_records: list[dict[str, object]] = []
    annotation_profile_ids: set[str] = set()
    for raw_record in records:
        if not isinstance(raw_record, dict):
            raise ValueError("Stage 4 annotation records must be objects")
        record = cast(dict[str, object], raw_record)
        cv_profile_id = record.get("cv_profile_id")
        draft_label = record.get("draft_label")
        review_value = record.get("review")
        if not isinstance(cv_profile_id, str) or cv_profile_id not in profile_ids:
            raise ValueError("Stage 4 annotation references an unknown CV profile")
        if cv_profile_id in annotation_profile_ids:
            raise ValueError("Stage 4 annotation CV references must be unique")
        if not isinstance(draft_label, str):
            raise ValueError("Stage 4 annotation must contain a draft label")
        ClassificationDecision(draft_label)
        if not isinstance(review_value, dict):
            raise ValueError("Stage 4 annotation must contain review fields")
        review = cast(dict[str, object], review_value)
        if review.get("status") != "pending":
            raise ValueError("Stage 4 source annotation reviews must retain pending status")
        if any(
            review.get(field) is not None
            for field in ("reviewer_reference", "final_label", "notes", "reviewed_at")
        ):
            raise ValueError("pending Stage 4 review fields must be empty")
        overrides = review.get("criterion_score_overrides")
        if not isinstance(overrides, list) or overrides:
            raise ValueError("unchanged Stage 4 approval must not contain score overrides")
        reviewed_record = dict(record)
        reviewed_record["source_dataset_file"] = REVIEWED_CV_PATH.as_posix()
        reviewed_record["review"] = {
            "status": "approved",
            "reviewer_reference": reviewer,
            "final_label": draft_label,
            "criterion_score_overrides": [],
            "notes": REVIEW_NOTE,
            "reviewed_at": timestamp,
        }
        reviewed_records.append(reviewed_record)
        annotation_profile_ids.add(cv_profile_id)
    if annotation_profile_ids != profile_ids:
        raise ValueError("Stage 4 annotations must cover every reviewed CV profile")
    reviewed_artifact = dict(draft)
    reviewed_artifact["annotation_status"] = "reviewed"
    reviewed_artifact["source_annotation_file"] = DRAFT_ANNOTATION_PATH.as_posix()
    reviewed_artifact["records"] = reviewed_records
    return profiles, reviewed_artifact


def write_reviewed_dataset(
    repository_root: Path,
    reviewer_reference: str,
    reviewed_at: str,
) -> tuple[Path, Path]:
    profiles, artifact = build_reviewed_dataset(
        repository_root,
        reviewer_reference,
        reviewed_at,
    )
    reviewed_directory = repository_root / "data" / "reviewed"
    reviewed_directory.mkdir(parents=True, exist_ok=True)
    cv_path = repository_root / REVIEWED_CV_PATH
    annotation_path = repository_root / REVIEWED_ANNOTATION_PATH
    cv_path.write_text(
        "".join(f"{profile.model_dump_json()}\n" for profile in profiles),
        encoding="utf-8",
    )
    annotation_path.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return cv_path, annotation_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reviewer-reference", required=True)
    parser.add_argument("--reviewed-at", required=True)
    arguments = parser.parse_args()
    write_reviewed_dataset(
        REPOSITORY_ROOT,
        cast(str, arguments.reviewer_reference),
        cast(str, arguments.reviewed_at),
    )


if __name__ == "__main__":
    main()
