from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import cast

import pytest
import yaml
from pydantic import ValidationError

from evaluation.datasets.stage7 import (
    Stage7EvaluationProtocol,
    Stage7FrozenManifest,
    Stage7HumanReviewRecord,
    validate_stage7_frozen_test_set,
)
from evaluation.datasets.synthetic_expansion import (
    ApprovedDatasetReview,
    DatasetTier,
    SyntheticPairAnnotation,
)
from scripts.approve_stage7_runtime_v2_test_set import (
    write_frozen_stage7_runtime_v2_test_set,
)
from scripts.preflight_stage7_runtime_v2 import (
    Stage7PreflightReport,
    run_stage7_runtime_v2_preflight,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DATASET_DIRECTORY = REPOSITORY_ROOT / "data" / "frozen_test" / "stage7_runtime_v2_v1"
PROTOCOL_PATH = (
    REPOSITORY_ROOT / "evaluation" / "configs" / "stage7_runtime_v2_frozen_evaluation_v1.yaml"
)
PREFLIGHT_PATH = REPOSITORY_ROOT / "evaluation" / "reports" / "stage7_runtime_v2_preflight_v1.json"
LOCKED_AT = "2026-08-08T16:00:00+07:00"


def _annotations(path: Path) -> tuple[SyntheticPairAnnotation, ...]:
    return tuple(
        SyntheticPairAnnotation.model_validate_json(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )


def test_stage7_runtime_v2_gold_lock_is_deterministic(tmp_path: Path) -> None:
    output_directory = tmp_path / "stage7_runtime_v2_v1"

    paths = write_frozen_stage7_runtime_v2_test_set(
        REPOSITORY_ROOT,
        LOCKED_AT,
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
    for path in paths:
        assert path.read_bytes() == (DATASET_DIRECTORY / path.name).read_bytes()


def test_stage7_runtime_v2_gold_contains_the_approved_consensus_review() -> None:
    manifest = Stage7FrozenManifest.model_validate_json(
        (DATASET_DIRECTORY / "manifest.json").read_text(encoding="utf-8")
    )
    review_record = Stage7HumanReviewRecord.model_validate_json(
        (DATASET_DIRECTORY / "review_record.json").read_text(encoding="utf-8")
    )
    annotations = _annotations(DATASET_DIRECTORY / "pairs.jsonl")
    report = validate_stage7_frozen_test_set(REPOSITORY_ROOT, DATASET_DIRECTORY)

    assert manifest.dataset_id == "stage7-five-role-runtime-v2-test-v1"
    assert manifest.runtime_configuration_set_id == "five-role-runtime-v2"
    assert manifest.dataset_tier is DatasetTier.GOLD
    assert manifest.locked_for_evaluation is True
    assert manifest.classifier_results_generated_before_lock is False
    assert manifest.llm_requests_made_before_lock is False
    assert review_record.review_mode == "two_person_consensus_panel"
    assert review_record.approved_pair_count == 50
    assert review_record.approved_correction_pair_ids == ()
    assert len(set(review_record.reviewer_references)) == 2
    assert len(annotations) == 50
    assert all(item.dataset_tier is DatasetTier.GOLD for item in annotations)
    assert all(isinstance(item.review, ApprovedDatasetReview) for item in annotations)
    assert all(item.review.human_review_count == 2 for item in annotations)
    assert report.passed is True
    assert report.errors == ()
    assert report.warnings == ()


def test_stage7_runtime_v2_protocol_locks_accepted_metrics_and_request_cap() -> None:
    protocol = Stage7EvaluationProtocol.model_validate(
        cast(dict[str, object], yaml.safe_load(PROTOCOL_PATH.read_text(encoding="utf-8")))
    )

    assert protocol.runtime_configuration_set_id == "five-role-runtime-v2"
    assert protocol.test_dataset_id == "stage7-five-role-runtime-v2-test-v1"
    assert protocol.tuning_allowed is False
    assert protocol.test_output_may_change_runtime is False
    assert protocol.metrics.minimum_accuracy == Decimal("0.70")
    assert protocol.metrics.minimum_needs_review_recall == Decimal("0.80")
    assert protocol.metrics.maximum_false_reject_count == 0
    assert protocol.metrics.maximum_unsafe_pass_count == 0
    assert protocol.metrics.maximum_unsafe_requirement_mismatch_count == 0
    assert protocol.metrics.minimum_valid_output_rate == Decimal("1.00")
    assert protocol.request_policy.intended_request_count == 55
    assert protocol.request_policy.maximum_http_request_count == 60
    assert protocol.preconditions.provider_calls_require_separate_user_authorization is True


def test_stage7_runtime_v2_protocol_rejects_weakened_safety_or_accuracy() -> None:
    payload = cast(dict[str, object], yaml.safe_load(PROTOCOL_PATH.read_text(encoding="utf-8")))
    metrics = cast(dict[str, object], payload["metrics"])
    metrics["minimum_accuracy"] = 0.69

    with pytest.raises(ValidationError):
        Stage7EvaluationProtocol.model_validate(payload)


def test_stage7_runtime_v2_preflight_passes_without_provider_access() -> None:
    report = run_stage7_runtime_v2_preflight(REPOSITORY_ROOT, LOCKED_AT)
    committed = Stage7PreflightReport.model_validate_json(
        PREFLIGHT_PATH.read_text(encoding="utf-8")
    )

    assert report == committed
    assert report.passed is True
    assert report.errors == ()
    assert report.provider_execution_authorized is False
    assert report.provider_requests_made is False
    assert report.api_key_loaded is False
    assert all(check.status == "passed" for check in report.checks)


def test_stage7_runtime_v2_lock_refuses_to_overwrite_existing_target(tmp_path: Path) -> None:
    output_directory = tmp_path / "already_locked"
    output_directory.mkdir()
    (output_directory / "manifest.json").write_text("locked", encoding="utf-8")

    with pytest.raises(ValueError, match="already contains files"):
        write_frozen_stage7_runtime_v2_test_set(
            REPOSITORY_ROOT,
            LOCKED_AT,
            output_directory,
        )
