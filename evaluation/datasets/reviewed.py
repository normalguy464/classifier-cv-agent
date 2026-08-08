from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from backend.app.contracts import CVProfile, ClassificationDecision


@dataclass(frozen=True, slots=True)
class ReviewedExample:
    cv_profile: CVProfile
    job_profile_id: str
    final_label: ClassificationDecision
    reviewer_reference: str


def _json_object(path: Path) -> dict[str, object]:
    value = cast(object, json.loads(path.read_text(encoding="utf-8")))
    if not isinstance(value, dict):
        raise ValueError(f"JSON artifact must be an object: {path.name}")
    return cast(dict[str, object], value)


def load_reviewed_pilot(repository_root: Path) -> tuple[ReviewedExample, ...]:
    annotation_path = repository_root / "data" / "annotations" / "pilot_annotations_v1.json"
    artifact = _json_object(annotation_path)
    if artifact.get("annotation_status") != "reviewed":
        raise ValueError("pilot annotations must be reviewed before evaluation")
    records_value = artifact.get("records")
    if not isinstance(records_value, list):
        raise ValueError("pilot annotation records must be a list")
    records = cast(list[object], records_value)
    examples: list[ReviewedExample] = []
    for raw_record in records:
        if not isinstance(raw_record, dict):
            raise ValueError("pilot annotation record must be an object")
        record = cast(dict[str, object], raw_record)
        review_value = record.get("review")
        if not isinstance(review_value, dict):
            raise ValueError("every pilot label must have approved human review")
        review = cast(dict[str, object], review_value)
        if review.get("status") != "approved":
            raise ValueError("every pilot label must have approved human review")
        reviewer_reference = review.get("reviewer_reference")
        final_label = review.get("final_label")
        source_path = record.get("source_cv_file")
        job_profile_id = record.get("job_profile_id")
        if not isinstance(reviewer_reference, str) or not reviewer_reference:
            raise ValueError("reviewed label must contain reviewer_reference")
        if not isinstance(final_label, str):
            raise ValueError("reviewed label must contain final_label")
        if not isinstance(source_path, str):
            raise ValueError("reviewed label must contain source_cv_file")
        if not isinstance(job_profile_id, str) or not job_profile_id:
            raise ValueError("reviewed label must contain job_profile_id")
        profile = CVProfile.model_validate(_json_object(repository_root / source_path))
        examples.append(
            ReviewedExample(
                cv_profile=profile,
                job_profile_id=job_profile_id,
                final_label=ClassificationDecision(final_label),
                reviewer_reference=reviewer_reference,
            )
        )
    return tuple(examples)
