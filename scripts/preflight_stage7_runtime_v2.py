from __future__ import annotations

import argparse
import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Literal, cast

import yaml
from pydantic import BaseModel, ConfigDict, Field

from backend.app.infrastructure.config import RepositoryConfigurationLoader
from evaluation.datasets.stage7 import (
    Stage7EvaluationProtocol,
    Stage7FrozenManifest,
    Stage7HumanReviewRecord,
    stage7_manifest_sha256,
    validate_stage7_frozen_test_set,
)
from evaluation.datasets.synthetic_expansion import SyntheticPairAnnotation

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIRECTORY = REPOSITORY_ROOT / "configs" / "runtime" / "five_role_v2"
DATASET_DIRECTORY = REPOSITORY_ROOT / "data" / "frozen_test" / "stage7_runtime_v2_v1"
PROTOCOL_PATH = (
    REPOSITORY_ROOT / "evaluation" / "configs" / "stage7_runtime_v2_frozen_evaluation_v1.yaml"
)
REPORT_PATH = REPOSITORY_ROOT / "evaluation" / "reports" / "stage7_runtime_v2_preflight_v1.json"


class Stage7PreflightCheck(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    check_id: str = Field(min_length=1)
    status: Literal["passed", "failed"]
    detail: str = Field(min_length=1)


class Stage7PreflightReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["1.0.0"]
    report_id: Literal["stage7-runtime-v2-preflight-v1"]
    generated_at: datetime
    passed: bool
    runtime_configuration_set_id: Literal["five-role-runtime-v2"]
    runtime_manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    dataset_id: Literal["stage7-five-role-runtime-v2-test-v1"]
    dataset_version: Literal["1.0.0"]
    dataset_manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    protocol_id: Literal["stage7-five-role-runtime-v2-frozen-evaluation-v1"]
    protocol_version: Literal["1.0.0"]
    protocol_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    provider_execution_authorized: Literal[False]
    provider_requests_made: Literal[False]
    api_key_loaded: Literal[False]
    checks: tuple[Stage7PreflightCheck, ...]
    errors: tuple[str, ...]


def _timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("generated_at must include a timezone")
    return parsed


def _annotations(path: Path) -> tuple[SyntheticPairAnnotation, ...]:
    return tuple(
        SyntheticPairAnnotation.model_validate_json(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )


def run_stage7_runtime_v2_preflight(
    repository_root: Path,
    generated_at: str,
) -> Stage7PreflightReport:
    timestamp = _timestamp(generated_at)
    runtime_directory = repository_root / RUNTIME_DIRECTORY.relative_to(REPOSITORY_ROOT)
    dataset_directory = repository_root / DATASET_DIRECTORY.relative_to(REPOSITORY_ROOT)
    protocol_path = repository_root / PROTOCOL_PATH.relative_to(REPOSITORY_ROOT)
    runtime_manifest_path = runtime_directory / "runtime_manifest.yaml"
    dataset_manifest_path = dataset_directory / "manifest.json"
    checks: list[Stage7PreflightCheck] = []
    errors: list[str] = []

    def record(check_id: str, passed: bool, detail: str) -> None:
        checks.append(
            Stage7PreflightCheck(
                check_id=check_id,
                status="passed" if passed else "failed",
                detail=detail,
            )
        )
        if not passed:
            errors.append(detail)

    loader = RepositoryConfigurationLoader(repository_root, runtime_directory)
    runtime_manifest = loader.runtime_manifest
    record(
        "runtime-frozen",
        runtime_manifest is not None
        and runtime_manifest.configuration_set_id == "five-role-runtime-v2"
        and runtime_manifest.configuration_status == "frozen_for_stage7",
        "Runtime manifest must be five-role-runtime-v2 with frozen_for_stage7 status.",
    )
    loaded_jobs = loader.load_job_artifacts()
    record(
        "runtime-role-coverage",
        len(loaded_jobs) == 5,
        "Runtime must load exactly five approved Job Profiles and linked rubrics.",
    )

    manifest = Stage7FrozenManifest.model_validate_json(
        dataset_manifest_path.read_text(encoding="utf-8")
    )
    review_record = Stage7HumanReviewRecord.model_validate_json(
        (dataset_directory / "review_record.json").read_text(encoding="utf-8")
    )
    quality_report = validate_stage7_frozen_test_set(repository_root, dataset_directory)
    record(
        "gold-dataset-locked",
        manifest.locked_for_evaluation
        and manifest.ground_truth_status == "human_reviewed_gold"
        and manifest.reviewed_pair_count == 50,
        "Test dataset must be a locked, human-reviewed Gold set with 50 pairs.",
    )
    record(
        "two-person-consensus",
        review_record.review_mode == "two_person_consensus_panel"
        and len(set(review_record.reviewer_references)) == 2
        and review_record.approved_pair_count == 50,
        "Review record must contain two distinct reviewers and all 50 approved pairs.",
    )
    record(
        "dataset-quality-control",
        quality_report.passed and not quality_report.warnings,
        "Frozen dataset QC must contain zero errors and zero warnings.",
    )
    record(
        "no-pre-lock-classifier-output",
        not manifest.classifier_results_generated_before_lock
        and not manifest.llm_requests_made_before_lock,
        "No classifier result or LLM request may exist before the dataset lock.",
    )

    protocol_payload = cast(dict[str, object], yaml.safe_load(protocol_path.read_text("utf-8")))
    protocol = Stage7EvaluationProtocol.model_validate(protocol_payload)
    annotations = _annotations(dataset_directory / "pairs.jsonl")
    pair_ids = {annotation.pair_id for annotation in annotations}
    record(
        "protocol-identity",
        protocol.runtime_configuration_set_id == manifest.runtime_configuration_set_id
        and protocol.test_dataset_id == manifest.dataset_id,
        "Protocol runtime and dataset identifiers must match the frozen artifacts.",
    )
    record(
        "protocol-safety-gates",
        protocol.metrics.minimum_accuracy == Decimal("0.70")
        and protocol.metrics.maximum_false_reject_count == 0
        and protocol.metrics.maximum_unsafe_pass_count == 0
        and protocol.metrics.maximum_unsafe_requirement_mismatch_count == 0,
        "Protocol must retain the approved accuracy floor and zero unsafe decisions.",
    )
    record(
        "stability-case-coverage",
        set(protocol.stability_pair_ids).issubset(pair_ids),
        "Every preselected stability pair must exist in the frozen test dataset.",
    )
    record(
        "provider-execution-separated",
        protocol.preconditions.provider_calls_require_separate_user_authorization
        and protocol.request_policy.maximum_http_request_count == 60
        and not protocol.request_policy.persist_raw_provider_response,
        "Provider execution must remain separately authorized, capped and sanitized.",
    )

    return Stage7PreflightReport(
        schema_version="1.0.0",
        report_id="stage7-runtime-v2-preflight-v1",
        generated_at=timestamp,
        passed=not errors,
        runtime_configuration_set_id="five-role-runtime-v2",
        runtime_manifest_sha256=stage7_manifest_sha256(runtime_manifest_path),
        dataset_id="stage7-five-role-runtime-v2-test-v1",
        dataset_version="1.0.0",
        dataset_manifest_sha256=stage7_manifest_sha256(dataset_manifest_path),
        protocol_id="stage7-five-role-runtime-v2-frozen-evaluation-v1",
        protocol_version="1.0.0",
        protocol_sha256=stage7_manifest_sha256(protocol_path),
        provider_execution_authorized=False,
        provider_requests_made=False,
        api_key_loaded=False,
        checks=tuple(checks),
        errors=tuple(errors),
    )


def write_stage7_runtime_v2_preflight_report(
    repository_root: Path,
    generated_at: str,
    output_path: Path | None = None,
) -> Path:
    report = run_stage7_runtime_v2_preflight(repository_root, generated_at)
    if not report.passed:
        raise ValueError(f"Stage 7 Runtime v2 preflight failed: {report.errors}")
    target = output_path or repository_root / REPORT_PATH.relative_to(REPOSITORY_ROOT)
    target.write_text(
        json.dumps(report.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return target


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated-at", required=True)
    arguments = parser.parse_args()
    print(
        write_stage7_runtime_v2_preflight_report(
            REPOSITORY_ROOT,
            cast(str, arguments.generated_at),
        )
    )


if __name__ == "__main__":
    main()
