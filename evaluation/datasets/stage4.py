from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import cast

from backend.app.contracts import (
    CVProfile,
    ClassificationDecision,
    EvidenceStatus,
)

REVIEWED_CV_PATH = Path("data/reviewed/stage4_cv_profiles_v1.jsonl")
REVIEWED_ANNOTATION_PATH = Path("data/reviewed/stage4_annotations_v1.json")


@dataclass(frozen=True, slots=True)
class ReviewedRequirementAssessment:
    requirement_id: str
    evidence_status: EvidenceStatus
    evidence_ids: tuple[str, ...]
    rationale: str


@dataclass(frozen=True, slots=True)
class ReviewedCriterionAssessment:
    criterion_id: str
    awarded_points: Decimal
    maximum_points: Decimal
    evidence_ids: tuple[str, ...]
    rationale: str


@dataclass(frozen=True, slots=True)
class ReviewedStage4Example:
    annotation_id: str
    cv_profile: CVProfile
    job_profile_id: str
    rubric_id: str
    final_label: ClassificationDecision
    draft_label: ClassificationDecision
    reviewer_reference: str
    reviewed_at: datetime
    requirement_assessments: tuple[ReviewedRequirementAssessment, ...]
    criterion_assessments: tuple[ReviewedCriterionAssessment, ...]
    total_score: Decimal
    overall_rationale: str


def _json_object(path: Path) -> dict[str, object]:
    value = cast(object, json.loads(path.read_text(encoding="utf-8")))
    if not isinstance(value, dict):
        raise ValueError(f"JSON artifact must be an object: {path.name}")
    return cast(dict[str, object], value)


def _mapping(value: object, field_name: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be an object")
    return cast(dict[str, object], value)


def _items(value: object, field_name: str) -> list[object]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list")
    return cast(list[object], value)


def _text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must contain text")
    return value


def _texts(value: object, field_name: str) -> tuple[str, ...]:
    items = _items(value, field_name)
    values = tuple(_text(item, field_name) for item in items)
    if len(values) != len(set(values)):
        raise ValueError(f"{field_name} must contain unique values")
    return values


def _decimal(value: object, field_name: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (Decimal, float, int, str)):
        raise ValueError(f"{field_name} must be numeric")
    try:
        result = Decimal(str(value))
    except ArithmeticError as error:
        raise ValueError(f"{field_name} must be numeric") from error
    if not result.is_finite():
        raise ValueError(f"{field_name} must be finite")
    return result


def _timestamp(value: object, field_name: str) -> datetime:
    text = _text(value, field_name)
    try:
        result = datetime.fromisoformat(text)
    except ValueError as error:
        raise ValueError(f"{field_name} must be an ISO 8601 timestamp") from error
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError(f"{field_name} must include a timezone")
    return result


def _profiles(path: Path) -> dict[str, CVProfile]:
    profiles = tuple(
        CVProfile.model_validate_json(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )
    profiles_by_id = {profile.cv_profile_id: profile for profile in profiles}
    if len(profiles) != 30 or len(profiles_by_id) != len(profiles):
        raise ValueError("reviewed Stage 4 data must contain exactly 30 unique CV profiles")
    return profiles_by_id


def _requirement_assessments(
    value: object,
    evidence_ids: set[str],
) -> tuple[ReviewedRequirementAssessment, ...]:
    assessments: list[ReviewedRequirementAssessment] = []
    for raw_assessment in _items(value, "critical_requirement_assessments"):
        assessment = _mapping(raw_assessment, "critical requirement assessment")
        referenced_ids = _texts(assessment.get("evidence_ids"), "requirement evidence_ids")
        if not set(referenced_ids).issubset(evidence_ids):
            raise ValueError("reviewed requirement references unknown CV evidence")
        assessments.append(
            ReviewedRequirementAssessment(
                requirement_id=_text(assessment.get("requirement_id"), "requirement_id"),
                evidence_status=EvidenceStatus(
                    _text(assessment.get("evidence_status"), "evidence_status")
                ),
                evidence_ids=referenced_ids,
                rationale=_text(assessment.get("rationale"), "requirement rationale"),
            )
        )
    identifiers = tuple(item.requirement_id for item in assessments)
    if not assessments or len(identifiers) != len(set(identifiers)):
        raise ValueError("reviewed requirement assessments must be non-empty and unique")
    return tuple(assessments)


def _criterion_assessments(
    value: object,
    evidence_ids: set[str],
) -> tuple[ReviewedCriterionAssessment, ...]:
    assessments: list[ReviewedCriterionAssessment] = []
    for raw_assessment in _items(value, "criterion_assessments"):
        assessment = _mapping(raw_assessment, "criterion assessment")
        awarded_points = _decimal(assessment.get("awarded_points"), "awarded_points")
        maximum_points = _decimal(assessment.get("maximum_points"), "maximum_points")
        if awarded_points < 0 or awarded_points > maximum_points:
            raise ValueError("reviewed criterion score must be within its maximum")
        referenced_ids = _texts(assessment.get("evidence_ids"), "criterion evidence_ids")
        if not set(referenced_ids).issubset(evidence_ids):
            raise ValueError("reviewed criterion references unknown CV evidence")
        assessments.append(
            ReviewedCriterionAssessment(
                criterion_id=_text(assessment.get("criterion_id"), "criterion_id"),
                awarded_points=awarded_points,
                maximum_points=maximum_points,
                evidence_ids=referenced_ids,
                rationale=_text(assessment.get("rationale"), "criterion rationale"),
            )
        )
    identifiers = tuple(item.criterion_id for item in assessments)
    maximums = tuple(item.maximum_points for item in assessments)
    if len(assessments) != 5 or len(identifiers) != len(set(identifiers)):
        raise ValueError("reviewed Stage 4 records must contain five unique criteria")
    if maximums != (
        Decimal("30"),
        Decimal("25"),
        Decimal("20"),
        Decimal("15"),
        Decimal("10"),
    ):
        raise ValueError("reviewed criterion maximums must match rubric weights")
    return tuple(assessments)


def _example(
    raw_record: object,
    profiles_by_id: dict[str, CVProfile],
) -> ReviewedStage4Example:
    record = _mapping(raw_record, "Stage 4 annotation record")
    cv_profile_id = _text(record.get("cv_profile_id"), "cv_profile_id")
    if cv_profile_id not in profiles_by_id:
        raise ValueError("reviewed annotation references an unknown CV profile")
    if record.get("source_dataset_file") != REVIEWED_CV_PATH.as_posix():
        raise ValueError("reviewed annotation must reference the reviewed CV artifact")
    profile = profiles_by_id[cv_profile_id]
    evidence_ids = {item.evidence_id for item in profile.evidence}
    review = _mapping(record.get("review"), "review")
    if review.get("status") != "approved":
        raise ValueError("every Stage 4 label must have approved human review")
    overrides = _items(review.get("criterion_score_overrides"), "criterion_score_overrides")
    if overrides:
        raise ValueError("this Stage 4 release does not contain score overrides")
    requirements = _requirement_assessments(
        record.get("critical_requirement_assessments"),
        evidence_ids,
    )
    criteria = _criterion_assessments(record.get("criterion_assessments"), evidence_ids)
    total_score = _decimal(record.get("total_score"), "total_score")
    if total_score != sum(
        (item.awarded_points for item in criteria),
        Decimal("0"),
    ):
        raise ValueError("reviewed total_score must equal the criterion score sum")
    return ReviewedStage4Example(
        annotation_id=_text(record.get("annotation_id"), "annotation_id"),
        cv_profile=profile,
        job_profile_id=_text(record.get("job_profile_id"), "job_profile_id"),
        rubric_id=_text(record.get("rubric_id"), "rubric_id"),
        final_label=ClassificationDecision(_text(review.get("final_label"), "review final_label")),
        draft_label=ClassificationDecision(_text(record.get("draft_label"), "draft_label")),
        reviewer_reference=_text(
            review.get("reviewer_reference"),
            "reviewer_reference",
        ),
        reviewed_at=_timestamp(review.get("reviewed_at"), "reviewed_at"),
        requirement_assessments=requirements,
        criterion_assessments=criteria,
        total_score=total_score,
        overall_rationale=_text(record.get("overall_rationale"), "overall_rationale"),
    )


def load_reviewed_stage4(repository_root: Path) -> tuple[ReviewedStage4Example, ...]:
    profiles_by_id = _profiles(repository_root / REVIEWED_CV_PATH)
    artifact = _json_object(repository_root / REVIEWED_ANNOTATION_PATH)
    if artifact.get("annotation_status") != "reviewed":
        raise ValueError("Stage 4 annotations must be reviewed before evaluation")
    if artifact.get("source_annotation_file") != (
        Path("data/to_review/stage4_annotations_v1.json").as_posix()
    ):
        raise ValueError("reviewed Stage 4 data must retain its draft artifact link")
    examples = tuple(
        _example(record, profiles_by_id) for record in _items(artifact.get("records"), "records")
    )
    example_profile_ids = {example.cv_profile.cv_profile_id for example in examples}
    annotation_ids = tuple(example.annotation_id for example in examples)
    if (
        len(examples) != 30
        or len(annotation_ids) != len(set(annotation_ids))
        or example_profile_ids != set(profiles_by_id)
    ):
        raise ValueError("reviewed Stage 4 annotations must cover 30 unique CV profiles")
    return examples
