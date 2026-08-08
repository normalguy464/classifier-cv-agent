from __future__ import annotations

import json
import shutil
from collections import Counter
from decimal import Decimal
from pathlib import Path

from backend.app.contracts import ClassificationDecision, EvidenceStatus
from evaluation.datasets.synthetic_expansion import (
    DatasetRole,
    DatasetTier,
    JobVariant,
    SyntheticScenario,
    validate_synthetic_expansion,
)
from scripts.generate_synthetic_expansion import (
    DATASET_ID,
    DATASET_VERSION,
    MARKET_REFERENCE_VERSION,
    build_dataset,
    write_dataset,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DATASET_DIRECTORY = REPOSITORY_ROOT / "data" / "synthetic_expansion" / "v2"
EXPECTED_MAXIMUMS = (
    Decimal("30"),
    Decimal("25"),
    Decimal("20"),
    Decimal("15"),
    Decimal("10"),
)


def test_synthetic_expansion_has_requested_scale_and_balanced_roles() -> None:
    profiles, jobs, rubrics, annotations = build_dataset()

    assert len(profiles) == 50
    assert len(jobs) == 25
    assert len(rubrics) == 25
    assert len(annotations) == 250
    assert Counter(annotation.role for annotation in annotations) == {
        role: 50 for role in DatasetRole
    }
    assert Counter(annotation.job_variant for annotation in annotations) == {
        variant: 50 for variant in JobVariant
    }
    assert Counter(annotation.scenario for annotation in annotations) == {
        scenario: 25 for scenario in SyntheticScenario
    }


def test_every_role_contains_complete_cv_job_cross_product() -> None:
    _, _, _, annotations = build_dataset()

    for role in DatasetRole:
        role_annotations = tuple(item for item in annotations if item.role is role)
        profile_ids = {item.cv_profile_id for item in role_annotations}
        job_ids = {item.job_profile_id for item in role_annotations}
        combinations = {(item.cv_profile_id, item.job_profile_id) for item in role_annotations}
        assert len(profile_ids) == 10
        assert len(job_ids) == 5
        assert len(combinations) == 50


def test_annotations_use_canonical_weights_and_valid_score_sums() -> None:
    _, _, rubrics, annotations = build_dataset()
    rubric_by_id = {rubric.rubric_id: rubric for rubric in rubrics}

    for annotation in annotations:
        rubric = rubric_by_id[annotation.rubric_id]
        assert tuple(item.weight for item in rubric.criteria) == EXPECTED_MAXIMUMS
        assert (
            tuple(item.maximum_points for item in annotation.criterion_assessments)
            == EXPECTED_MAXIMUMS
        )
        assert all(
            Decimal("0") <= item.awarded_points <= item.maximum_points
            for item in annotation.criterion_assessments
        )
        assert (
            sum(
                (item.awarded_points for item in annotation.criterion_assessments),
                Decimal("0"),
            )
            == annotation.total_score
        )


def test_job_profiles_use_market_calibrated_junior_requirements() -> None:
    _, jobs, _, _ = build_dataset()
    expected_critical_ids = {
        DatasetRole.DATA_ANALYST: {
            "da-sql",
            "da-analysis-language",
            "da-bi-reporting",
            "da-business-analysis",
        },
        DatasetRole.PYTHON_BACKEND: {
            "be-python",
            "be-rest-api",
            "be-relational-data",
            "be-testing",
            "be-delivery-workflow",
        },
        DatasetRole.FRONTEND: {
            "fe-web-foundations",
            "fe-language",
            "fe-framework",
            "fe-api",
            "fe-testing-workflow",
        },
        DatasetRole.QA_ENGINEER: {
            "qa-testing-foundations",
            "qa-test-cases",
            "qa-api-testing",
            "qa-data-check",
            "qa-automation-foundation",
        },
        DatasetRole.DATA_ENGINEER: {
            "de-python",
            "de-sql",
            "de-pipeline",
            "de-data-model-quality",
            "de-delivery-workflow",
        },
    }

    for role, expected_ids in expected_critical_ids.items():
        role_token = role.value.replace("_", "-")
        standard_job = next(
            job
            for job in jobs
            if role_token in job.job_profile_id and "-std-" in job.job_profile_id
        )
        critical_ids = {
            requirement.requirement_id
            for requirement in standard_job.requirements
            if requirement.is_critical
        }
        assert critical_ids == expected_ids
        assert all(
            len(requirement.accepted_evidence) >= 2
            for requirement in standard_job.requirements
            if requirement.is_critical
        )


def test_generated_profiles_use_v2_identifiers_and_detailed_practice_context() -> None:
    profiles, _, _, _ = build_dataset()
    strong_profiles = tuple(
        profile for profile in profiles if "-strong-v2" in profile.cv_profile_id
    )

    assert len(strong_profiles) == 5
    assert all(profile.candidate_reference.endswith("-v2") for profile in profiles)
    assert all(len(profile.evidence) >= 10 for profile in strong_profiles)
    assert all(
        any(
            marker in " ".join(evidence.text for evidence in profile.evidence)
            for marker in ("window function", "pytest", "TypeScript", "Postman", "incremental")
        )
        for profile in strong_profiles
    )


def test_draft_labels_follow_candidate_protection_policy() -> None:
    _, _, _, annotations = build_dataset()

    assert Counter(annotation.draft_label for annotation in annotations) == {
        ClassificationDecision.PASS: 50,
        ClassificationDecision.WAITLIST: 25,
        ClassificationDecision.NEEDS_REVIEW: 155,
        ClassificationDecision.REJECT: 20,
    }
    for annotation in annotations:
        statuses = {item.evidence_status for item in annotation.critical_requirement_assessments}
        if EvidenceStatus.MISSING in statuses or EvidenceStatus.CONFLICTING in statuses:
            assert annotation.draft_label is ClassificationDecision.NEEDS_REVIEW
        if annotation.draft_label is ClassificationDecision.REJECT:
            assert annotation.total_score < Decimal("60")
            assert EvidenceStatus.UNSATISFIED in statuses


def test_all_generated_pairs_remain_bronze_and_pending_human_review() -> None:
    _, _, _, annotations = build_dataset()

    for annotation in annotations:
        assert annotation.dataset_tier is DatasetTier.BRONZE
        assert annotation.partition == "unassigned"
        assert annotation.review.status == "pending"
        assert annotation.review.human_review_count == 0
        assert annotation.review.label_finalized is False
        assert annotation.review.final_label is None


def test_dataset_inputs_do_not_contain_outcome_leakage_or_contact_data() -> None:
    profiles, _, _, _ = build_dataset()
    forbidden_values = (
        "draft_label",
        "final_label",
        "needs_review",
        "waitlist",
        "total_score",
        "review_reason",
        "@",
        "http://",
        "https://",
    )

    for profile in profiles:
        serialized = profile.model_dump_json().casefold()
        assert not any(value in serialized for value in forbidden_values)


def test_committed_dataset_matches_deterministic_generator(tmp_path: Path) -> None:
    generated_directory = tmp_path / "v2"
    generated_paths = write_dataset(generated_directory)
    committed_names = {
        "cv_profiles.jsonl",
        "job_profiles.jsonl",
        "rubrics.jsonl",
        "pairs.jsonl",
        "manifest.json",
        "quality_report.json",
    }

    assert {path.name for path in generated_paths} == committed_names
    for name in committed_names:
        assert (generated_directory / name).read_bytes() == (DATASET_DIRECTORY / name).read_bytes()


def test_quality_control_passes_committed_dataset() -> None:
    report = validate_synthetic_expansion(DATASET_DIRECTORY)

    assert report.passed
    assert report.errors == ()
    assert report.warnings == ()
    assert report.cv_profile_count == 50
    assert report.job_profile_count == 25
    assert report.rubric_count == 25
    assert report.pair_count == 250


def test_quality_control_detects_tampered_score_and_manifest_hash(tmp_path: Path) -> None:
    copied_directory = tmp_path / "tampered"
    shutil.copytree(DATASET_DIRECTORY, copied_directory)
    pair_path = copied_directory / "pairs.jsonl"
    lines = pair_path.read_text(encoding="utf-8").splitlines()
    first = json.loads(lines[0])
    first["total_score"] = "1"
    lines[0] = json.dumps(first, ensure_ascii=False, sort_keys=True)
    pair_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    report = validate_synthetic_expansion(copied_directory)

    assert not report.passed
    assert any("Dataset loading failed" in error for error in report.errors)


def test_dataset_does_not_modify_stage6_frozen_split() -> None:
    manifest = json.loads((DATASET_DIRECTORY / "manifest.json").read_text(encoding="utf-8"))

    assert manifest["schema_version"] == "1.1.0"
    assert manifest["dataset_id"] == DATASET_ID
    assert manifest["dataset_version"] == DATASET_VERSION
    assert manifest["market_reference_version"] == MARKET_REFERENCE_VERSION
    assert manifest["split_status"] == "unassigned"
    assert manifest["frozen_test_created"] is False
    assert manifest["human_reviewed_pair_count"] == 0
