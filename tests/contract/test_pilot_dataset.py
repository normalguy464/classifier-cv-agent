from __future__ import annotations

import json
import re
from collections import Counter
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping, cast

import pytest

from backend.app.contracts import CVProfile

JsonObject = dict[str, Any]

REPOSITORY_ROOT: Path = Path(__file__).resolve().parents[2]
CV_DIRECTORY: Path = REPOSITORY_ROOT / "data" / "samples" / "cvs"
ANNOTATION_FILE: Path = REPOSITORY_ROOT / "data" / "annotations" / "pilot_annotations_v1.json"
SCORING_CONFIG_FILE: Path = REPOSITORY_ROOT / "configs" / "scoring.yaml"
IDENTIFIER_PATTERN: re.Pattern[str] = re.compile(r"^[a-z0-9][a-z0-9-]{2,63}$")
FORBIDDEN_FIELDS: frozenset[str] = frozenset(
    {
        "address",
        "age",
        "date_of_birth",
        "disability",
        "email",
        "ethnicity",
        "gender",
        "hometown",
        "marital_status",
        "phone",
        "religion",
    }
)
ALLOWED_EVIDENCE_STATUSES: frozenset[str] = frozenset(
    {"satisfied", "unsatisfied", "missing", "conflicting"}
)
ALLOWED_LABELS: frozenset[str] = frozenset({"pass", "waitlist", "reject", "needs_review"})
BOUNDARY_BANDS: tuple[tuple[Decimal, Decimal], ...] = (
    (Decimal("58"), Decimal("62")),
    (Decimal("73"), Decimal("77")),
)
PILOT_CONFIG_FILES: tuple[Path, ...] = (
    REPOSITORY_ROOT / "configs" / "job_profiles" / "junior_data_analyst.yaml",
    REPOSITORY_ROOT / "configs" / "job_profiles" / "junior_python_backend_developer.yaml",
    REPOSITORY_ROOT / "configs" / "rubrics" / "junior_data_analyst_rubric.yaml",
    REPOSITORY_ROOT / "configs" / "rubrics" / "junior_python_backend_developer_rubric.yaml",
    REPOSITORY_ROOT / "configs" / "scoring.yaml",
    REPOSITORY_ROOT / "configs" / "models.yaml",
)
EXPECTED_PILOT_RESULTS: Mapping[str, tuple[tuple[str, ...], str, str]] = {
    "cv-pilot-da-001": (("30", "23", "18", "14", "9"), "94", "pass"),
    "cv-pilot-da-002": (("30", "15", "11", "8", "6"), "70", "waitlist"),
    "cv-pilot-da-003": (("20", "18", "14", "11", "7"), "70", "needs_review"),
    "cv-pilot-da-004": (("10", "8", "6", "5", "7"), "36", "reject"),
    "cv-pilot-da-005": (("20", "17", "14", "10", "5"), "66", "needs_review"),
    "cv-pilot-be-001": (("30", "23", "18", "14", "9"), "94", "pass"),
    "cv-pilot-be-002": (("30", "15", "11", "8", "6"), "70", "waitlist"),
    "cv-pilot-be-003": (("23", "18", "14", "10", "7"), "72", "needs_review"),
    "cv-pilot-be-004": (("18", "7", "6", "4", "7"), "42", "reject"),
    "cv-pilot-be-005": (("30", "18", "13", "9", "6"), "76", "needs_review"),
}


@dataclass(frozen=True)
class RoleSpecification:
    rubric_id: str
    critical_requirement_ids: frozenset[str]
    criterion_maximums: Mapping[str, Decimal]
    rubric_file: Path


ROLE_SPECIFICATIONS: Mapping[str, RoleSpecification] = {
    "junior-data-analyst-v1": RoleSpecification(
        rubric_id="junior-data-analyst-rubric-v1",
        critical_requirement_ids=frozenset(
            {"da-sql", "da-analysis-language", "da-analytical-project"}
        ),
        criterion_maximums={
            "mandatory-requirements": Decimal("30"),
            "technical-analysis": Decimal("25"),
            "analytical-reasoning": Decimal("20"),
            "projects-and-impact": Decimal("15"),
            "communication-and-evidence-quality": Decimal("10"),
        },
        rubric_file=REPOSITORY_ROOT / "configs" / "rubrics" / "junior_data_analyst_rubric.yaml",
    ),
    "junior-python-backend-developer-v1": RoleSpecification(
        rubric_id="junior-python-backend-developer-rubric-v1",
        critical_requirement_ids=frozenset(
            {"be-python", "be-rest-api", "be-relational-data", "be-git"}
        ),
        criterion_maximums={
            "mandatory-requirements": Decimal("30"),
            "backend-implementation": Decimal("25"),
            "api-and-data-design": Decimal("20"),
            "projects-and-delivery": Decimal("15"),
            "communication-and-evidence-quality": Decimal("10"),
        },
        rubric_file=REPOSITORY_ROOT
        / "configs"
        / "rubrics"
        / "junior_python_backend_developer_rubric.yaml",
    ),
}


def load_json_object(path: Path) -> JsonObject:
    value: object = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return cast(JsonObject, value)


def load_cv_profiles() -> dict[str, tuple[Path, CVProfile]]:
    profiles: dict[str, tuple[Path, CVProfile]] = {}
    for path in sorted(CV_DIRECTORY.glob("*.json")):
        profile = CVProfile.model_validate(load_json_object(path))
        assert profile.cv_profile_id not in profiles
        profiles[profile.cv_profile_id] = (path, profile)
    return profiles


def load_annotation_records() -> tuple[JsonObject, list[JsonObject]]:
    artifact = load_json_object(ANNOTATION_FILE)
    records = artifact["records"]
    assert isinstance(records, list)
    return artifact, cast(list[JsonObject], records)


def collect_field_names(value: object) -> set[str]:
    if isinstance(value, dict):
        field_names = {str(key) for key in value}
        for item in value.values():
            field_names.update(collect_field_names(item))
        return field_names
    if isinstance(value, list):
        field_names: set[str] = set()
        for item in value:
            field_names.update(collect_field_names(item))
        return field_names
    return set()


def decimal_value(value: object) -> Decimal:
    return Decimal(str(value))


def is_boundary_score(score: Decimal) -> bool:
    return any(minimum <= score <= maximum for minimum, maximum in BOUNDARY_BANDS)


def expected_decision(record: JsonObject) -> str:
    statuses = {
        str(assessment["evidence_status"])
        for assessment in cast(list[JsonObject], record["critical_requirement_assessments"])
    }
    total_score = decimal_value(record["total_score"])
    if {"missing", "conflicting"}.intersection(statuses) or is_boundary_score(total_score):
        return "needs_review"
    if "unsatisfied" in statuses:
        if total_score < Decimal("60"):
            return "reject"
        return "needs_review"
    if total_score >= Decimal("75"):
        return "pass"
    if total_score >= Decimal("60"):
        return "waitlist"
    return "needs_review"


def decision_record(total_score: str, statuses: tuple[str, ...]) -> JsonObject:
    return {
        "total_score": total_score,
        "critical_requirement_assessments": [{"evidence_status": status} for status in statuses],
    }


def validate_requirement_assessments(
    record: JsonObject,
    profile_evidence_ids: set[str],
    specification: RoleSpecification,
) -> None:
    assessments = cast(list[JsonObject], record["critical_requirement_assessments"])
    requirement_ids = [str(item["requirement_id"]) for item in assessments]
    assert len(requirement_ids) == len(set(requirement_ids))
    assert set(requirement_ids) == specification.critical_requirement_ids
    for assessment in assessments:
        status = str(assessment["evidence_status"])
        evidence_ids = cast(list[str], assessment["evidence_ids"])
        assert status in ALLOWED_EVIDENCE_STATUSES
        assert set(evidence_ids).issubset(profile_evidence_ids)
        if status in {"satisfied", "unsatisfied"}:
            assert evidence_ids
        if status == "missing":
            assert not evidence_ids
        if status == "conflicting":
            assert len(set(evidence_ids)) >= 2
        assert str(assessment["rationale"]).strip()


def validate_criterion_assessments(
    record: JsonObject,
    profile_evidence_ids: set[str],
    specification: RoleSpecification,
) -> None:
    assessments = cast(list[JsonObject], record["criterion_assessments"])
    criterion_ids = [str(item["criterion_id"]) for item in assessments]
    assert len(criterion_ids) == len(set(criterion_ids))
    assert set(criterion_ids) == set(specification.criterion_maximums)
    awarded_total = Decimal("0")
    for assessment in assessments:
        criterion_id = str(assessment["criterion_id"])
        maximum_points = decimal_value(assessment["maximum_points"])
        awarded_points = decimal_value(assessment["awarded_points"])
        evidence_ids = cast(list[str], assessment["evidence_ids"])
        assert maximum_points == specification.criterion_maximums[criterion_id]
        assert Decimal("0") <= awarded_points <= maximum_points
        assert evidence_ids
        assert set(evidence_ids).issubset(profile_evidence_ids)
        assert str(assessment["rationale"]).strip()
        awarded_total += awarded_points
    assert awarded_total == decimal_value(record["total_score"])
    assert Decimal("0") <= awarded_total <= Decimal("100")


def validate_approved_review(record: JsonObject) -> None:
    review = cast(JsonObject, record["review"])
    assert review["status"] == "approved"
    assert review["reviewer_reference"] == "reviewer-user-001"
    assert review["final_label"] == record["draft_label"]
    assert review["criterion_score_overrides"] == []
    assert str(review["notes"]).strip()
    reviewed_at = datetime.fromisoformat(str(review["reviewed_at"]))
    assert reviewed_at.tzinfo is not None
    assert reviewed_at.utcoffset() is not None


def validate_annotation_record(
    record: JsonObject,
    profiles: Mapping[str, tuple[Path, CVProfile]],
) -> None:
    cv_profile_id = str(record["cv_profile_id"])
    assert cv_profile_id in profiles
    cv_path, profile = profiles[cv_profile_id]
    source_path = REPOSITORY_ROOT / str(record["source_cv_file"])
    assert source_path.resolve() == cv_path.resolve()
    job_profile_id = str(record["job_profile_id"])
    specification = ROLE_SPECIFICATIONS[job_profile_id]
    assert record["rubric_id"] == specification.rubric_id
    profile_evidence_ids = {item.evidence_id for item in profile.evidence}
    validate_requirement_assessments(record, profile_evidence_ids, specification)
    validate_criterion_assessments(record, profile_evidence_ids, specification)
    assert record["draft_label"] in ALLOWED_LABELS
    assert record["draft_label"] == expected_decision(record)
    assert str(record["overall_rationale"]).strip()
    validate_approved_review(record)


def test_pilot_contains_ten_valid_unique_cv_profiles() -> None:
    profiles = load_cv_profiles()

    assert len(profiles) == 10
    assert sum(profile_id.startswith("cv-pilot-da-") for profile_id in profiles) == 5
    assert sum(profile_id.startswith("cv-pilot-be-") for profile_id in profiles) == 5

    candidate_references = [profile.candidate_reference for _, profile in profiles.values()]
    assert len(candidate_references) == len(set(candidate_references))
    assert all(value.startswith("candidate-synthetic-") for value in candidate_references)

    all_evidence_ids = [
        evidence.evidence_id for _, profile in profiles.values() for evidence in profile.evidence
    ]
    assert len(all_evidence_ids) == len(set(all_evidence_ids))


def test_pilot_cv_data_excludes_protected_fields_and_direct_contact_data() -> None:
    for path in sorted(CV_DIRECTORY.glob("*.json")):
        payload = load_json_object(path)
        assert not FORBIDDEN_FIELDS.intersection(collect_field_names(payload))
        serialized = json.dumps(payload, ensure_ascii=False).lower()
        assert "@" not in serialized
        assert "http://" not in serialized
        assert "https://" not in serialized


def test_annotation_artifact_is_versioned_and_links_every_cv_once() -> None:
    artifact, records = load_annotation_records()
    profiles = load_cv_profiles()

    assert artifact["schema_version"] == "1.0.0"
    assert artifact["dataset_version"] == "1.0.0"
    assert artifact["cv_schema_version"] == "1.0.0"
    assert artifact["job_profile_artifact_version"] == "1.0.0"
    assert artifact["rubric_version"] == "1.0.0"
    assert artifact["configuration_version"] == "1.1.0"
    assert artifact["l1_rules_configuration_version"] == "1.0.0"
    assert artifact["models_configuration_version"] == "1.1.0"
    assert artifact["annotation_status"] == "reviewed"
    assert len(records) == 10

    annotation_ids = [str(record["annotation_id"]) for record in records]
    cv_profile_ids = [str(record["cv_profile_id"]) for record in records]
    assert len(annotation_ids) == len(set(annotation_ids))
    assert set(cv_profile_ids) == set(profiles)

    for record in records:
        validate_annotation_record(record, profiles)


def test_pilot_label_distribution_covers_required_business_cases() -> None:
    _, records = load_annotation_records()
    distribution = Counter(str(record["draft_label"]) for record in records)
    reasons = {
        str(reason) for record in records for reason in cast(list[str], record["review_reasons"])
    }

    assert distribution == {
        "pass": 2,
        "waitlist": 2,
        "reject": 2,
        "needs_review": 4,
    }
    assert "missing-critical-evidence" in reasons
    assert "conflicting-critical-evidence" in reasons
    assert "upper-threshold-boundary" in reasons


def test_policy_update_preserves_every_pilot_score_and_label() -> None:
    _, records = load_annotation_records()

    actual_results = {
        str(record["cv_profile_id"]): (
            tuple(
                str(decimal_value(assessment["awarded_points"]))
                for assessment in cast(list[JsonObject], record["criterion_assessments"])
            ),
            str(decimal_value(record["total_score"])),
            str(record["draft_label"]),
        )
        for record in records
    }

    assert actual_results == EXPECTED_PILOT_RESULTS


def test_reject_annotations_have_explicit_unsatisfied_critical_evidence() -> None:
    _, records = load_annotation_records()
    reject_records = [record for record in records if record["draft_label"] == "reject"]

    assert reject_records
    for record in reject_records:
        assert decimal_value(record["total_score"]) < Decimal("58")
        assessments = cast(list[JsonObject], record["critical_requirement_assessments"])
        assert any(item["evidence_status"] == "unsatisfied" for item in assessments)


def test_pilot_configs_are_approved_and_rubric_ids_are_contract_compatible() -> None:
    for config_file in PILOT_CONFIG_FILES:
        assert "contract_status: approved_for_pilot" in config_file.read_text(encoding="utf-8")

    for specification in ROLE_SPECIFICATIONS.values():
        content = specification.rubric_file.read_text(encoding="utf-8")
        criterion_ids = set(re.findall(r"criterion_id: ([a-z0-9-]+)", content))
        assert criterion_ids == set(specification.criterion_maximums)
        assert all(IDENTIFIER_PATTERN.fullmatch(value) for value in criterion_ids)

    scoring_content = SCORING_CONFIG_FILE.read_text(encoding="utf-8")
    assert "configuration_version: 1.1.0" in scoring_content
    assert "rule_id: low-score-without-explicit-critical-unsatisfied" in scoring_content
    assert "rule_id: critical-unsatisfied-at-or-above-waitlist-threshold" in scoring_content

    linked_config_files = tuple(path for path in PILOT_CONFIG_FILES if path != SCORING_CONFIG_FILE)
    for config_file in linked_config_files:
        assert "scoring_configuration_version: 1.1.0" in config_file.read_text(encoding="utf-8")


def test_low_score_without_explicit_critical_failure_needs_review() -> None:
    record = decision_record("57.99", ("satisfied", "satisfied"))

    assert expected_decision(record) == "needs_review"


@pytest.mark.parametrize("total_score", ["60", "63", "78", "100"])
def test_unsatisfied_critical_requirement_outside_reject_range_needs_review(
    total_score: str,
) -> None:
    record = decision_record(total_score, ("satisfied", "unsatisfied"))

    assert expected_decision(record) == "needs_review"


@pytest.mark.parametrize(
    ("total_score", "statuses", "decision"),
    [
        ("0", ("unsatisfied",), "reject"),
        ("57.99", ("unsatisfied",), "reject"),
        ("58", ("unsatisfied",), "needs_review"),
        ("62", ("satisfied",), "needs_review"),
        ("62.01", ("satisfied",), "waitlist"),
        ("72.99", ("satisfied",), "waitlist"),
        ("73", ("satisfied",), "needs_review"),
        ("77", ("satisfied",), "needs_review"),
        ("77.01", ("satisfied",), "pass"),
        ("100", ("satisfied",), "pass"),
    ],
)
def test_decision_policy_boundaries(
    total_score: str,
    statuses: tuple[str, ...],
    decision: str,
) -> None:
    record = decision_record(total_score, statuses)

    assert expected_decision(record) == decision


def test_validation_detects_abnormal_criterion_points() -> None:
    profiles = load_cv_profiles()
    _, records = load_annotation_records()
    record = deepcopy(records[0])
    assessment = cast(list[JsonObject], record["criterion_assessments"])[0]
    assessment["awarded_points"] = 31
    record["total_score"] = 95

    with pytest.raises(AssertionError):
        validate_annotation_record(record, profiles)


def test_validation_detects_unknown_annotation_evidence() -> None:
    profiles = load_cv_profiles()
    _, records = load_annotation_records()
    record = deepcopy(records[0])
    assessment = cast(list[JsonObject], record["critical_requirement_assessments"])[0]
    assessment["evidence_ids"] = ["ev-does-not-exist"]

    with pytest.raises(AssertionError):
        validate_annotation_record(record, profiles)


@pytest.mark.parametrize(
    ("cv_profile_id", "invalid_label"),
    [
        ("cv-pilot-da-003", "reject"),
        ("cv-pilot-da-005", "waitlist"),
        ("cv-pilot-be-005", "pass"),
    ],
)
def test_validation_detects_labels_that_bypass_needs_review(
    cv_profile_id: str,
    invalid_label: str,
) -> None:
    profiles = load_cv_profiles()
    _, records = load_annotation_records()
    record = deepcopy(next(item for item in records if item["cv_profile_id"] == cv_profile_id))
    record["draft_label"] = invalid_label

    with pytest.raises(AssertionError):
        validate_annotation_record(record, profiles)


def test_review_timestamp_example_requires_timezone() -> None:
    reviewed_at = datetime.fromisoformat("2026-07-25T15:00:00+07:00")

    assert reviewed_at.tzinfo is not None
    assert reviewed_at.utcoffset() is not None
