from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from backend.app.agents.classifier.scoring import score_l1
from backend.app.contracts import CVProfile
from backend.app.infrastructure.config import RepositoryConfigurationLoader
from scripts.generate_stage4_dataset import build_dataset, write_dataset

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN_FIELD_NAMES = {
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

LEAKAGE_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bpass\b",
        r"\bwaitlist\b",
        r"\breject\b",
        r"\bneeds[\s_-]*review\b",
        r"\bdraft[\s_-]*label\b",
        r"\bfinal[\s_-]*label\b",
        r"\bscore\b",
        r"\bscoring\b",
        r"\brubric\b",
        r"\bthreshold\b",
        r"\bcriterion\b",
        r"\brule\b",
        r"\bsatisfied\b",
        r"\bunsatisfied\b",
        r"\bmissing\b",
        r"\bconflicting\b",
        r"\bđiểm số\b",
        r"\btổng điểm\b",
        r"\bngưỡng\b",
        r"\bvùng biên\b",
        r"\bxếp loại\b",
        r"\bnhãn\b",
        r"\bquy tắc\b",
        r"\btiêu chí chấm\b",
        r"\byêu cầu bắt buộc\b",
    )
)


def collect_field_names(value: object) -> set[str]:
    if isinstance(value, dict):
        names = {str(key) for key in value}
        for item in value.values():
            names.update(collect_field_names(item))
        return names
    if isinstance(value, list):
        names: set[str] = set()
        for item in value:
            names.update(collect_field_names(item))
        return names
    return set()


def profile_source_texts(profile: CVProfile) -> tuple[str, ...]:
    values = [profile.summary or ""]
    values.extend(skill.name for skill in profile.skills)
    values.extend(
        value
        for project in profile.projects
        for value in (project.title, project.summary, *project.technologies)
    )
    values.extend(item.text for item in profile.evidence)
    return tuple(value for value in values if value)


def profile_feature_fingerprint(profile: CVProfile) -> str:
    payload: dict[str, object] = {
        "summary": profile.summary,
        "skills": sorted(skill.name for skill in profile.skills),
        "projects": sorted(
            (
                project.title,
                project.summary,
                tuple(sorted(project.technologies)),
            )
            for project in profile.projects
        ),
        "evidence": sorted(
            (
                item.source_type.value,
                item.section.value,
                item.text,
                None if item.extraction_confidence is None else str(item.extraction_confidence),
                item.is_verified,
                item.location.page_number,
                item.location.character_start,
                item.location.character_end,
            )
            for item in profile.evidence
        ),
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def draft_assessment_signature(record: dict[str, Any]) -> str:
    payload = {
        "critical_requirement_assessments": [
            {
                "requirement_id": item["requirement_id"],
                "evidence_status": item["evidence_status"],
            }
            for item in record["critical_requirement_assessments"]
        ],
        "criterion_scores": [
            {
                "criterion_id": item["criterion_id"],
                "awarded_points": item["awarded_points"],
                "maximum_points": item["maximum_points"],
            }
            for item in record["criterion_assessments"]
        ],
        "total_score": record["total_score"],
        "draft_label": record["draft_label"],
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def annotation_rationale_texts(record: dict[str, Any]) -> tuple[str, ...]:
    values = [str(record["overall_rationale"])]
    values.extend(str(value) for value in record["ambiguity_notes"])
    values.extend(str(item["rationale"]) for item in record["critical_requirement_assessments"])
    values.extend(str(item["rationale"]) for item in record["criterion_assessments"])
    return tuple(values)


def test_stage4_dataset_contains_thirty_valid_profiles_for_both_roles() -> None:
    profiles, annotations = build_dataset()

    assert len(profiles) == 30
    assert len(annotations) == 30
    assert all(isinstance(profile, CVProfile) for profile in profiles)
    assert len({profile.cv_profile_id for profile in profiles}) == 30
    assert len({profile.candidate_reference for profile in profiles}) == 30
    role_distribution = Counter(record["job_profile_id"] for record in annotations)
    assert role_distribution == {
        "junior-data-analyst-v1": 15,
        "junior-python-backend-developer-v1": 15,
    }


def test_stage4_dataset_excludes_protected_fields_and_contact_data() -> None:
    profiles, _ = build_dataset()

    for profile in profiles:
        payload = profile.model_dump(mode="json")
        assert not FORBIDDEN_FIELD_NAMES.intersection(collect_field_names(payload))
        serialized = profile.model_dump_json().lower()
        assert "@" not in serialized
        assert "http://" not in serialized
        assert "https://" not in serialized


def test_stage4_annotations_have_valid_scores_versions_and_pending_review() -> None:
    profiles, annotations = build_dataset()
    profile_ids = {profile.cv_profile_id for profile in profiles}
    labels = Counter()

    for record in annotations:
        assert record["cv_profile_id"] in profile_ids
        scores = [Decimal(str(item["awarded_points"])) for item in record["criterion_assessments"]]
        maximums = [
            Decimal(str(item["maximum_points"])) for item in record["criterion_assessments"]
        ]
        assert maximums == [
            Decimal("30"),
            Decimal("25"),
            Decimal("20"),
            Decimal("15"),
            Decimal("10"),
        ]
        assert all(Decimal("0") <= score <= maximum for score, maximum in zip(scores, maximums))
        assert sum(scores) == Decimal(str(record["total_score"]))
        assert record["review"]["status"] == "pending"
        assert record["review"]["reviewer_reference"] is None
        assert record["review"]["final_label"] is None
        assert record["review"]["reviewed_at"] is None
        labels.update((record["draft_label"],))

    assert set(labels) == {"pass", "waitlist", "reject", "needs_review"}


def test_stage4_dataset_covers_both_candidate_protection_fallback_rules() -> None:
    _, annotations = build_dataset()
    reasons = {reason for record in annotations for reason in record["review_reasons"]}

    assert "low-score-without-explicit-critical-unsatisfied" in reasons
    assert "critical-unsatisfied-at-or-above-waitlist-threshold" in reasons


def test_stage4_cv_content_does_not_leak_labels_rules_or_scores() -> None:
    profiles, _ = build_dataset()

    for profile in profiles:
        for text in profile_source_texts(profile):
            matches = tuple(pattern.pattern for pattern in LEAKAGE_PATTERNS if pattern.search(text))
            assert not matches, (profile.cv_profile_id, text, matches)


def test_stage4_duplicate_features_cannot_have_different_draft_assessments() -> None:
    profiles, annotations = build_dataset()
    annotations_by_profile_id = {record["cv_profile_id"]: record for record in annotations}
    signatures_by_feature: dict[tuple[str, str], str] = {}

    for profile in profiles:
        record = annotations_by_profile_id[profile.cv_profile_id]
        key = (
            record["job_profile_id"],
            profile_feature_fingerprint(profile),
        )
        signature = draft_assessment_signature(record)
        if key in signatures_by_feature:
            assert signatures_by_feature[key] == signature
        signatures_by_feature[key] = signature

    assert len(signatures_by_feature) == len(profiles)


def test_stage4_annotation_rationales_are_not_copied_from_cv_source_text() -> None:
    profiles, annotations = build_dataset()
    profiles_by_id = {profile.cv_profile_id: profile for profile in profiles}

    for record in annotations:
        source_texts = {
            value.casefold()
            for value in profile_source_texts(profiles_by_id[record["cv_profile_id"]])
        }
        rationales = annotation_rationale_texts(record)
        assert source_texts.isdisjoint(value.casefold() for value in rationales)
        for rationale in rationales:
            matches = tuple(
                pattern.pattern for pattern in LEAKAGE_PATTERNS[:6] if pattern.search(rationale)
            )
            assert not matches, (record["annotation_id"], rationale, matches)


def test_stage4_l1_statuses_match_draft_annotations_for_all_profiles() -> None:
    profiles, annotations = build_dataset()
    profiles_by_id = {profile.cv_profile_id: profile for profile in profiles}
    loader = RepositoryConfigurationLoader(REPOSITORY_ROOT)

    for record in annotations:
        job_profile_id = record["job_profile_id"]
        loaded = loader.load_for_job(job_profile_id)
        assessment = score_l1(
            profiles_by_id[record["cv_profile_id"]],
            loaded.rubric,
            loader.load_l1_policy(job_profile_id),
        )
        actual = {
            item.requirement_id: item.evidence_status.value
            for item in assessment.requirement_assessments
        }
        expected = {
            item["requirement_id"]: item["evidence_status"]
            for item in record["critical_requirement_assessments"]
        }

        assert actual == expected, record["annotation_id"]


def test_stage4_annotation_artifact_records_traceability_versions(
    tmp_path: Path,
) -> None:
    _, annotation_path = write_dataset(tmp_path)
    artifact = json.loads(annotation_path.read_text(encoding="utf-8"))

    assert artifact["job_profile_artifact_version"] == "1.0.0"
    assert artifact["l1_rules_configuration_version"] == "1.0.0"


def test_stage4_committed_artifacts_match_generator_output() -> None:
    profiles, annotations = build_dataset()
    cv_path = REPOSITORY_ROOT / "data" / "to_review" / "stage4_cv_profiles_v1.jsonl"
    annotation_path = REPOSITORY_ROOT / "data" / "to_review" / "stage4_annotations_v1.json"
    committed_profiles = [
        json.loads(line) for line in cv_path.read_text(encoding="utf-8").splitlines() if line
    ]
    committed_annotations = json.loads(annotation_path.read_text(encoding="utf-8"))["records"]

    assert committed_profiles == [profile.model_dump(mode="json") for profile in profiles]
    assert committed_annotations == list(annotations)


def test_review_timestamp_shape_is_reserved_for_human_review() -> None:
    timestamp = datetime.fromisoformat("2026-07-26T16:00:00+07:00")

    assert timestamp.tzinfo is not None
