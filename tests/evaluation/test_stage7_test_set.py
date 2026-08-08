from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import cast

import yaml
from pydantic import ValidationError

from backend.app.contracts import CVProfile, ClassificationDecision, JobProfile, ScoringRubric
from backend.app.infrastructure.config import RepositoryConfigurationLoader
from evaluation.datasets.stage7 import (
    Stage7EvaluationProtocol,
    Stage7FrozenManifest,
    Stage7TestManifest,
    validate_stage7_frozen_test_set,
    validate_stage7_test_set,
)
from evaluation.datasets.synthetic_expansion import SyntheticPairAnnotation, SyntheticScenario
from scripts.generate_stage7_test_set import write_stage7_test_set
from scripts.approve_stage7_test_set import write_frozen_stage7_test_set

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DATASET_DIRECTORY = REPOSITORY_ROOT / "data" / "to_review" / "stage7_test_v1"
RUNTIME_DIRECTORY = REPOSITORY_ROOT / "configs" / "runtime" / "five_role_v1"
PROTOCOL_PATH = REPOSITORY_ROOT / "evaluation" / "configs" / "stage7_frozen_evaluation_v1.yaml"


def _json_lines(path: Path, model_type: type[CVProfile]) -> tuple[CVProfile, ...]:
    return tuple(
        model_type.model_validate_json(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )


def _annotations(path: Path) -> tuple[SyntheticPairAnnotation, ...]:
    return tuple(
        SyntheticPairAnnotation.model_validate_json(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )


def test_committed_stage7_test_set_is_reproducible_and_passes_qc(tmp_path: Path) -> None:
    output_directory = tmp_path / "stage7_test_v1"
    generated_paths = write_stage7_test_set(output_directory)

    assert {path.name for path in generated_paths} == {
        "cv_profiles.jsonl",
        "job_profiles.jsonl",
        "rubrics.jsonl",
        "pairs.jsonl",
        "review_sheet.md",
        "manifest.json",
        "quality_report.json",
    }
    for path in generated_paths:
        assert path.read_bytes() == (DATASET_DIRECTORY / path.name).read_bytes()
    report = validate_stage7_test_set(REPOSITORY_ROOT, DATASET_DIRECTORY)
    assert report.passed is True
    assert report.errors == ()
    assert report.warnings == ()


def test_stage7_manifest_keeps_ground_truth_and_evaluation_pending() -> None:
    manifest = Stage7TestManifest.model_validate_json(
        (DATASET_DIRECTORY / "manifest.json").read_text(encoding="utf-8")
    )

    assert manifest.status == "draft_for_human_review"
    assert manifest.ground_truth_status == "pending_human_review"
    assert manifest.locked_for_evaluation is False
    assert manifest.classifier_results_generated is False
    assert manifest.llm_requests_made is False
    assert manifest.candidate_count == 50
    assert manifest.pair_count == 50
    assert manifest.minimum_human_reviewers_for_gold == 2
    assert manifest.dataset_version == "1.0.1"
    assert manifest.source_dataset_version == "1.0.0"


def test_stage7_test_set_has_balanced_role_scenario_and_label_coverage() -> None:
    annotations = _annotations(DATASET_DIRECTORY / "pairs.jsonl")

    assert len(annotations) == 50
    assert {item.role.value for item in annotations} == {
        "data_analyst",
        "python_backend",
        "frontend",
        "qa_engineer",
        "data_engineer",
    }
    for role in {item.role for item in annotations}:
        role_annotations = tuple(item for item in annotations if item.role is role)
        assert len(role_annotations) == 10
        assert {item.scenario for item in role_annotations} == set(SyntheticScenario)
    label_counts = {
        label: sum(item.draft_label is label for item in annotations)
        for label in ClassificationDecision
    }
    assert label_counts == {
        ClassificationDecision.PASS: 10,
        ClassificationDecision.WAITLIST: 10,
        ClassificationDecision.REJECT: 5,
        ClassificationDecision.NEEDS_REVIEW: 25,
    }


def test_stage7_identifiers_do_not_expose_scenario_or_label() -> None:
    annotations = _annotations(DATASET_DIRECTORY / "pairs.jsonl")

    for annotation in annotations:
        identifiers = (
            annotation.pair_id,
            annotation.cv_profile_id,
            annotation.candidate_reference,
        )
        assert all(annotation.scenario.value not in value for value in identifiers)
        assert all(annotation.draft_label.value not in value for value in identifiers)


def test_stage7_remediation_removes_cross_requirement_contradictions() -> None:
    annotations = {item.pair_id: item for item in _annotations(DATASET_DIRECTORY / "pairs.jsonl")}
    profiles = {
        profile.cv_profile_id: profile
        for profile in _json_lines(DATASET_DIRECTORY / "cv_profiles.jsonl", CVProfile)
    }

    expected_statuses = {
        "s7-pair-be-04": {
            "be-python": "satisfied",
            "be-rest-api": "satisfied",
            "be-delivery-workflow": "missing",
        },
        "s7-pair-be-06": {
            "be-python": "satisfied",
            "be-rest-api": "satisfied",
            "be-delivery-workflow": "unsatisfied",
        },
        "s7-pair-fe-06": {
            "fe-web-foundations": "satisfied",
            "fe-language": "satisfied",
            "fe-testing-workflow": "unsatisfied",
        },
        "s7-pair-qa-04": {
            "qa-testing-foundations": "satisfied",
            "qa-test-cases": "satisfied",
            "qa-automation-foundation": "missing",
        },
        "s7-pair-qa-06": {
            "qa-testing-foundations": "satisfied",
            "qa-test-cases": "satisfied",
            "qa-automation-foundation": "unsatisfied",
        },
    }
    for pair_id, expected in expected_statuses.items():
        actual = {
            assessment.requirement_id: assessment.evidence_status.value
            for assessment in annotations[pair_id].critical_requirement_assessments
        }
        assert all(actual[requirement_id] == status for requirement_id, status in expected.items())
    qa_missing_profile = profiles[annotations["s7-pair-qa-04"].cv_profile_id]
    qa_missing_text = " ".join(evidence.text for evidence in qa_missing_profile.evidence)
    assert "tích hợp test trong CI" not in qa_missing_text


def test_stage7_jobs_and_rubrics_equal_the_frozen_runtime() -> None:
    loader = RepositoryConfigurationLoader(REPOSITORY_ROOT, RUNTIME_DIRECTORY)
    jobs = tuple(
        JobProfile.model_validate_json(line)
        for line in (DATASET_DIRECTORY / "job_profiles.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    )
    rubrics = tuple(
        ScoringRubric.model_validate_json(line)
        for line in (DATASET_DIRECTORY / "rubrics.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    )

    for job in jobs:
        loaded = loader.load_for_job(job.job_profile_id)
        assert loaded.job_profile == job
        assert loaded.rubric in rubrics


def test_stage7_qc_detects_prior_evidence_overlap(tmp_path: Path) -> None:
    copied_directory = tmp_path / "stage7_test_v1"
    shutil.copytree(DATASET_DIRECTORY, copied_directory)
    profiles_path = copied_directory / "cv_profiles.jsonl"
    profile_payloads = [
        cast(dict[str, object], json.loads(line))
        for line in profiles_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    prior_profile = _json_lines(
        REPOSITORY_ROOT
        / "data"
        / "synthetic_expansion"
        / "reviewed"
        / "v2_3_1"
        / "cv_profiles.jsonl",
        CVProfile,
    )[0]
    evidence_values = cast(list[dict[str, object]], profile_payloads[0]["evidence"])
    evidence_values[0]["text"] = prior_profile.evidence[0].text
    profiles_path.write_text(
        "\n".join(
            json.dumps(payload, ensure_ascii=False, sort_keys=True) for payload in profile_payloads
        )
        + "\n",
        encoding="utf-8",
    )

    report = validate_stage7_test_set(REPOSITORY_ROOT, copied_directory)

    assert report.passed is False
    assert report.prior_exact_evidence_overlap_count == 1
    assert "Stage 7 evidence text exactly overlaps prior data" in report.errors
    assert any("file digest mismatch" in error for error in report.errors)


def test_stage7_qc_detects_cross_requirement_contradiction(tmp_path: Path) -> None:
    copied_directory = tmp_path / "stage7_test_v1"
    shutil.copytree(DATASET_DIRECTORY, copied_directory)
    pairs_path = copied_directory / "pairs.jsonl"
    pair_payloads = [
        cast(dict[str, object], json.loads(line))
        for line in pairs_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    backend_missing = next(
        payload for payload in pair_payloads if payload["pair_id"] == "s7-pair-be-04"
    )
    assessments = cast(
        list[dict[str, object]],
        backend_missing["critical_requirement_assessments"],
    )
    python_assessment = next(
        assessment for assessment in assessments if assessment["requirement_id"] == "be-python"
    )
    python_assessment["evidence_status"] = "missing"
    python_assessment["evidence_ids"] = []
    pairs_path.write_text(
        "\n".join(
            json.dumps(payload, ensure_ascii=False, sort_keys=True) for payload in pair_payloads
        )
        + "\n",
        encoding="utf-8",
    )

    report = validate_stage7_test_set(REPOSITORY_ROOT, copied_directory)

    assert report.passed is False
    assert "Cross-requirement evidence contradiction: s7-pair-be-04" in report.errors


def test_stage7_manifest_rejects_any_pre_review_evaluation_state() -> None:
    manifest = Stage7TestManifest.model_validate_json(
        (DATASET_DIRECTORY / "manifest.json").read_text(encoding="utf-8")
    )
    payload = manifest.model_dump(mode="python")
    payload["classifier_results_generated"] = True

    try:
        Stage7TestManifest.model_validate(payload)
    except ValidationError:
        return
    raise AssertionError("pre-review Stage 7 manifest accepted classifier output state")


def test_stage7_protocol_locks_safety_metrics_and_api_authorization() -> None:
    protocol = Stage7EvaluationProtocol.model_validate(
        yaml.safe_load(PROTOCOL_PATH.read_text(encoding="utf-8"))
    )

    assert protocol.status == "approved_for_frozen_evaluation"
    assert protocol.tuning_allowed is False
    assert protocol.preconditions.dataset_status == "human_reviewed_gold"
    assert protocol.preconditions.minimum_human_reviewers == 2
    assert protocol.preconditions.human_review_mode == "two_person_consensus_panel"
    assert protocol.preconditions.provider_calls_require_separate_user_authorization is True
    assert protocol.metrics.minimum_needs_review_recall == 1
    assert protocol.metrics.maximum_false_reject_count == 0
    assert protocol.metrics.maximum_unsafe_pass_count == 0
    assert protocol.request_policy.intended_request_count == 55
    assert protocol.request_policy.maximum_http_request_count == 60
    assert protocol.request_policy.persist_raw_provider_response is False
    assert len(protocol.stability_pair_ids) == 5


def test_stage7_joint_review_creates_locked_gold_dataset(tmp_path: Path) -> None:
    output_directory = tmp_path / "stage7_v1"
    paths = write_frozen_stage7_test_set(
        REPOSITORY_ROOT,
        "2026-08-07T18:00:00+07:00",
        output_directory,
    )

    assert {path.name for path in paths} == {
        "cv_profiles.jsonl",
        "job_profiles.jsonl",
        "rubrics.jsonl",
        "pairs.jsonl",
        "review_record.json",
        "manifest.json",
        "quality_report.json",
    }
    manifest = Stage7FrozenManifest.model_validate_json(
        (output_directory / "manifest.json").read_text(encoding="utf-8")
    )
    report = validate_stage7_frozen_test_set(REPOSITORY_ROOT, output_directory)
    annotations = _annotations(output_directory / "pairs.jsonl")

    assert manifest.status == "human_reviewed_gold_locked"
    assert manifest.review_mode == "two_person_consensus_panel"
    assert manifest.locked_for_evaluation is True
    assert manifest.classifier_results_generated_before_lock is False
    assert manifest.llm_requests_made_before_lock is False
    assert all(item.dataset_tier.value == "gold" for item in annotations)
    assert all(item.review.human_review_count == 2 for item in annotations)
    assert report.passed is True
    assert report.errors == ()
    assert report.warnings == ()


def test_stage7_protocol_rejects_weakened_total_score_mae() -> None:
    payload = cast(
        dict[str, object],
        yaml.safe_load(PROTOCOL_PATH.read_text(encoding="utf-8")),
    )
    metrics = cast(dict[str, object], payload["metrics"])
    metrics["maximum_total_score_mae"] = 13

    try:
        Stage7EvaluationProtocol.model_validate(payload)
    except ValidationError:
        return
    raise AssertionError("Stage 7 protocol accepted a weakened total score MAE")
