from __future__ import annotations

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import cast

from backend.app.contracts import CVProfile, EvidenceStatus
from backend.app.infrastructure.embeddings import HashingEmbeddingAdapter
from backend.app.infrastructure.llm import (
    LLMAdapter,
    LLMProviderResult,
    LLMProviderStatus,
    LLMProviderUsage,
    LLMRequirementAssessment,
    LLMScoringOutput,
    LLMScoringRequest,
    LLMWeightedCriterionAssessment,
)
from evaluation.datasets.synthetic_expansion import SyntheticPairAnnotation
from evaluation.datasets.stage7 import stage7_manifest_sha256
from evaluation.experiments.run_stage7_frozen_evaluation import (
    build_stage7_report,
    collect_stage7_outputs,
)
from evaluation.experiments.run_stage7_runtime_v2_frozen_evaluation import (
    V2_EXECUTION_TARGET,
    verify_stage7_runtime_v2_execution_authorization,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DATASET_DIRECTORY = REPOSITORY_ROOT / "data" / "frozen_test" / "stage7_runtime_v2_v1"
REPORT_PATH = (
    REPOSITORY_ROOT / "evaluation" / "reports" / "stage7_runtime_v2_frozen_evaluation_v1.json"
)
PROTOCOL_PATH = (
    REPOSITORY_ROOT / "evaluation" / "configs" / "stage7_runtime_v2_frozen_evaluation_v1.yaml"
)


def _annotations() -> tuple[SyntheticPairAnnotation, ...]:
    return tuple(
        SyntheticPairAnnotation.model_validate_json(line)
        for line in (DATASET_DIRECTORY / "pairs.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    )


def _profiles() -> tuple[CVProfile, ...]:
    return tuple(
        CVProfile.model_validate_json(line)
        for line in (DATASET_DIRECTORY / "cv_profiles.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    )


class RuntimeV2GroundTruthAdapter(LLMAdapter):
    def __init__(self) -> None:
        annotations = {item.cv_profile_id: item for item in _annotations()}
        self._outputs: dict[frozenset[str], LLMScoringOutput] = {}
        for profile in _profiles():
            annotation = annotations[profile.cv_profile_id]
            self._outputs[frozenset(item.evidence_id for item in profile.evidence)] = (
                LLMScoringOutput(
                    requirement_assessments=tuple(
                        LLMRequirementAssessment(
                            requirement_id=item.requirement_id,
                            evidence_status=item.evidence_status,
                            evidence_ids=(
                                ()
                                if item.evidence_status is EvidenceStatus.MISSING
                                else item.evidence_ids
                            ),
                            rationale=item.rationale,
                        )
                        for item in annotation.critical_requirement_assessments
                    ),
                    criterion_assessments=tuple(
                        LLMWeightedCriterionAssessment(
                            criterion_id=item.criterion_id,
                            score=item.awarded_points,
                            evidence_status=(
                                EvidenceStatus.SATISFIED
                                if item.evidence_ids
                                else EvidenceStatus.MISSING
                            ),
                            evidence_ids=item.evidence_ids,
                            rationale=item.rationale,
                        )
                        for item in annotation.criterion_assessments
                    ),
                    overall_score=annotation.total_score,
                    confidence=0.9,
                )
            )
        self.call_count = 0
        self.authoritative_request_count = 0

    async def score(self, request: LLMScoringRequest) -> LLMProviderResult:
        self.call_count += 1
        if request.authoritative_requirement_assessments:
            self.authoritative_request_count += 1
        output = self._outputs[frozenset(item.evidence_id for item in request.evidence)]
        return LLMProviderResult(
            status=LLMProviderStatus.AVAILABLE,
            provider_identifier="openai",
            model_identifier="gpt-5.4-mini-2026-03-17",
            prompt_version="l3-evidence-rubric-v15",
            output=output,
            usage=LLMProviderUsage(
                input_tokens=100,
                output_tokens=50,
                total_tokens=150,
            ),
        )


async def _no_sleep(_: float) -> None:
    return None


def test_stage7_runtime_v2_execution_authorization_hashes_are_current() -> None:
    verify_stage7_runtime_v2_execution_authorization(REPOSITORY_ROOT)


def test_stage7_runtime_v2_collects_authoritative_v15_requests_and_builds_report(
    tmp_path: Path,
) -> None:
    adapter = RuntimeV2GroundTruthAdapter()
    cache_path = tmp_path / "cache.json"
    cache = asyncio.run(
        collect_stage7_outputs(
            REPOSITORY_ROOT,
            adapter,
            cache_path=cache_path,
            request_interval_seconds=1,
            sleep=_no_sleep,
            target=V2_EXECUTION_TARGET,
        )
    )
    report = asyncio.run(
        build_stage7_report(
            REPOSITORY_ROOT,
            datetime.fromisoformat("2026-08-08T17:00:00+07:00"),
            cache,
            HashingEmbeddingAdapter(dimension=768),
            target=V2_EXECUTION_TARGET,
        )
    )

    assert adapter.call_count == 55
    assert adapter.authoritative_request_count == 55
    assert cache.total_http_request_count == 55
    assert report["report_id"] == "stage7-five-role-runtime-v2-frozen-evaluation-v1"
    assert report["report_scope"] == "gold-frozen-five-role-runtime-v2-final-test"
    assert report["is_final_performance"] is True
    traceability = cast(dict[str, object], report["traceability"])
    assert traceability["prompt_version"] == "l3-evidence-rubric-v15"
    assert traceability["raw_provider_response_persisted"] is False
    cache_text = cache_path.read_text(encoding="utf-8")
    assert "raw_response" not in cache_text
    assert "CLASSIFIER_LLM_API_KEY" not in cache_text


def test_stage7_runtime_v2_cache_contains_only_structured_sanitized_results(
    tmp_path: Path,
) -> None:
    adapter = RuntimeV2GroundTruthAdapter()
    cache_path = tmp_path / "cache.json"

    cache = asyncio.run(
        collect_stage7_outputs(
            REPOSITORY_ROOT,
            adapter,
            cache_path=cache_path,
            maximum_new_requests=1,
            request_interval_seconds=1,
            sleep=_no_sleep,
            target=V2_EXECUTION_TARGET,
        )
    )
    payload = cast(dict[str, object], json.loads(cache_path.read_text(encoding="utf-8")))

    assert cache.total_http_request_count == 1
    assert payload["provider_identifier"] == "openai"
    assert payload["model_identifier"] == "gpt-5.4-mini-2026-03-17"
    assert payload["prompt_version"] == "l3-evidence-rubric-v15"
    assert "raw_response" not in payload


def test_committed_stage7_runtime_v2_report_preserves_the_failed_final_gate() -> None:
    report = cast(dict[str, object], json.loads(REPORT_PATH.read_text(encoding="utf-8")))
    quality = cast(dict[str, object], report["quality_gate"])
    checks = cast(dict[str, bool], quality["checks"])
    hybrid = cast(dict[str, object], report["final_hybrid"])
    metrics = cast(dict[str, object], hybrid["metrics"])
    provider = cast(dict[str, object], report["l3_provider_quality"])
    stability = cast(dict[str, object], report["stability"])
    usage = cast(dict[str, object], report["usage_latency_and_cost"])
    errors = cast(dict[str, object], report["error_analysis"])
    traceability = cast(dict[str, object], report["traceability"])

    assert quality["passed"] is False
    assert metrics["accuracy"] == 0.48
    assert metrics["macro_f1"] == 0.16216216216216214
    assert hybrid["needs_review_recall"] == 0.96
    assert hybrid["review_rate"] == 0.98
    assert hybrid["false_reject_indexes"] == []
    assert hybrid["unsafe_pass_indexes"] == []
    assert provider["valid_output_rate"] == 1
    assert provider["requirement_status_accuracy"] == 0.7958333333333333
    assert provider["unsafe_requirement_mismatch_count"] == 21
    assert provider["criterion_mae"] == 3.038
    assert provider["total_score_mae"] == 11.35
    assert stability["maximum_score_range"] == 14.5
    assert usage["total_http_request_count"] == 56
    assert usage["valid_attempt_count"] == 55
    assert usage["failed_request_count"] == 1
    assert errors["l1_requirement_mismatch_count"] == 49
    assert errors["label_mismatch_count"] == 26
    assert checks["minimum_accuracy"] is False
    assert checks["maximum_false_reject_count"] is True
    assert checks["maximum_unsafe_pass_count"] is True
    assert checks["minimum_valid_output_rate"] is True
    assert traceability["protocol_sha256"] == stage7_manifest_sha256(PROTOCOL_PATH)
    assert traceability["dataset_manifest_sha256"] == stage7_manifest_sha256(
        DATASET_DIRECTORY / "manifest.json"
    )
    assert traceability["raw_provider_response_persisted"] is False
    assert "CLASSIFIER_LLM_API_KEY" not in REPORT_PATH.read_text(encoding="utf-8")
