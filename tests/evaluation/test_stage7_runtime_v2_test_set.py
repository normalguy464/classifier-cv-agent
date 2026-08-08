from __future__ import annotations

import json
from collections import Counter
from decimal import Decimal
from pathlib import Path
from typing import cast

from backend.app.contracts import ClassificationDecision
from evaluation.datasets.stage7 import Stage7TestManifest, validate_stage7_test_set
from evaluation.datasets.synthetic_expansion import SyntheticPairAnnotation, SyntheticScenario
from scripts.generate_stage7_runtime_v2_test_set import write_stage7_runtime_v2_test_set

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DATASET_DIRECTORY = REPOSITORY_ROOT / "data" / "to_review" / "stage7_runtime_v2_test_v1"


def _annotations(path: Path) -> tuple[SyntheticPairAnnotation, ...]:
    return tuple(
        SyntheticPairAnnotation.model_validate(cast(dict[str, object], json.loads(line)))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )


def test_stage7_runtime_v2_generation_is_deterministic(tmp_path: Path) -> None:
    output_directory = tmp_path / "stage7_runtime_v2_test_v1"

    paths = write_stage7_runtime_v2_test_set(output_directory)

    assert {path.name for path in paths} == {
        "cv_profiles.jsonl",
        "job_profiles.jsonl",
        "rubrics.jsonl",
        "pairs.jsonl",
        "review_sheet.md",
        "manifest.json",
        "quality_report.json",
    }
    for path in paths:
        assert path.read_bytes() == (DATASET_DIRECTORY / path.name).read_bytes()


def test_stage7_runtime_v2_manifest_keeps_evaluation_unopened() -> None:
    manifest = Stage7TestManifest.model_validate_json(
        (DATASET_DIRECTORY / "manifest.json").read_text(encoding="utf-8")
    )

    assert manifest.dataset_id == "stage7-five-role-runtime-v2-test-v1"
    assert manifest.dataset_version == "1.0.0"
    assert manifest.runtime_configuration_set_id == "five-role-runtime-v2"
    assert manifest.status == "draft_for_human_review"
    assert manifest.dataset_tier.value == "bronze"
    assert manifest.ground_truth_status == "pending_human_review"
    assert manifest.locked_for_evaluation is False
    assert manifest.classifier_results_generated is False
    assert manifest.llm_requests_made is False


def test_stage7_runtime_v2_has_balanced_roles_scenarios_and_labels() -> None:
    annotations = _annotations(DATASET_DIRECTORY / "pairs.jsonl")

    assert len(annotations) == 50
    assert Counter(item.role for item in annotations) == {
        role: 10 for role in {item.role for item in annotations}
    }
    assert Counter(item.scenario for item in annotations) == {
        scenario: 5 for scenario in SyntheticScenario
    }
    assert Counter(item.draft_label for item in annotations) == {
        ClassificationDecision.PASS: 10,
        ClassificationDecision.WAITLIST: 10,
        ClassificationDecision.REJECT: 5,
        ClassificationDecision.NEEDS_REVIEW: 25,
    }


def test_stage7_runtime_v2_boundary_cases_match_the_frozen_policy() -> None:
    annotations = _annotations(DATASET_DIRECTORY / "pairs.jsonl")
    lower_cases = tuple(
        item for item in annotations if item.scenario is SyntheticScenario.LOWER_BOUNDARY
    )
    upper_cases = tuple(
        item for item in annotations if item.scenario is SyntheticScenario.UPPER_BOUNDARY
    )

    assert {item.total_score for item in lower_cases} == {Decimal("67")}
    assert {item.draft_label for item in lower_cases} == {ClassificationDecision.NEEDS_REVIEW}
    assert all("lower-threshold-boundary" in item.review_reasons for item in lower_cases)
    assert {item.total_score for item in upper_cases} == {Decimal("82")}
    assert {item.draft_label for item in upper_cases} == {ClassificationDecision.NEEDS_REVIEW}
    assert all("upper-threshold-boundary" in item.review_reasons for item in upper_cases)


def test_stage7_runtime_v2_passes_qc_and_prior_data_leakage_checks() -> None:
    report = validate_stage7_test_set(REPOSITORY_ROOT, DATASET_DIRECTORY)

    assert report.passed is True
    assert report.errors == ()
    assert report.warnings == ()
    assert report.prior_candidate_overlap_count == 0
    assert report.prior_profile_id_overlap_count == 0
    assert report.prior_exact_evidence_overlap_count == 0
    assert report.maximum_prior_cv_token_jaccard < Decimal("0.82")
    assert report.classifier_results_generated is False
