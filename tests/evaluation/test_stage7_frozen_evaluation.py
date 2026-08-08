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
from evaluation.experiments.run_stage7_frozen_evaluation import (
    Stage7ProviderUnavailable,
    build_stage7_report,
    collect_stage7_outputs,
)
from evaluation.datasets.stage7 import stage7_manifest_sha256

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DATASET_DIRECTORY = REPOSITORY_ROOT / "data" / "frozen_test" / "stage7_v1"
REPORT_PATH = REPOSITORY_ROOT / "evaluation" / "reports" / "stage7_frozen_evaluation_v1.json"
PROTOCOL_PATH = REPOSITORY_ROOT / "evaluation" / "configs" / "stage7_frozen_evaluation_v1.yaml"


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


class HumanGroundTruthAdapter(LLMAdapter):
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

    async def score(self, request: LLMScoringRequest) -> LLMProviderResult:
        self.call_count += 1
        output = self._outputs[frozenset(item.evidence_id for item in request.evidence)]
        return LLMProviderResult(
            status=LLMProviderStatus.AVAILABLE,
            provider_identifier="openai",
            model_identifier="gpt-5.4-mini-2026-03-17",
            prompt_version="l3-evidence-rubric-v12",
            output=output,
            usage=LLMProviderUsage(
                input_tokens=100,
                output_tokens=50,
                total_tokens=150,
            ),
        )


class UnavailableStage7Adapter(LLMAdapter):
    async def score(self, request: LLMScoringRequest) -> LLMProviderResult:
        return LLMProviderResult(
            status=LLMProviderStatus.UNAVAILABLE,
            provider_identifier="openai",
            model_identifier="gpt-5.4-mini-2026-03-17",
            prompt_version=request.prompt_version,
            reason="Provider is unavailable.",
        )


async def _no_sleep(_: float) -> None:
    return None


def test_stage7_collects_exact_request_plan_and_builds_sanitized_report(
    tmp_path: Path,
) -> None:
    adapter = HumanGroundTruthAdapter()
    cache_path = tmp_path / "cache.json"
    cache = asyncio.run(
        collect_stage7_outputs(
            REPOSITORY_ROOT,
            adapter,
            cache_path=cache_path,
            request_interval_seconds=1,
            sleep=_no_sleep,
        )
    )
    report = asyncio.run(
        build_stage7_report(
            REPOSITORY_ROOT,
            datetime.fromisoformat("2026-08-07T19:00:00+07:00"),
            cache,
            HashingEmbeddingAdapter(dimension=768),
        )
    )

    assert adapter.call_count == 55
    assert cache.total_http_request_count == 55
    assert len(cache.records) == 50
    assert sum(len(items) for items in cache.records.values()) == 55
    assert report["is_final_performance"] is True
    assert cast(dict[str, object], report["l3_provider_quality"])["valid_output_rate"] == 1
    assert (
        cast(dict[str, object], report["l3_provider_quality"])["requirement_status_accuracy"] == 1
    )
    assert set(cast(dict[str, object], report["ablations"])) == {
        "l1_only",
        "l2_only",
        "l3_only",
        "l1_l2",
        "l1_l3",
        "l2_l3",
        "l1_l2_l3",
    }
    assert (
        cast(dict[str, object], report["traceability"])["raw_provider_response_persisted"] is False
    )
    cache_payload = json.loads(cache_path.read_text(encoding="utf-8"))
    assert "raw_response" not in json.dumps(cache_payload)


def test_stage7_provider_unavailability_fails_fast_and_preserves_failure(
    tmp_path: Path,
) -> None:
    cache_path = tmp_path / "cache.json"

    try:
        asyncio.run(
            collect_stage7_outputs(
                REPOSITORY_ROOT,
                UnavailableStage7Adapter(),
                cache_path=cache_path,
                request_interval_seconds=1,
                sleep=_no_sleep,
            )
        )
    except Stage7ProviderUnavailable:
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
        assert sum(len(items) for items in payload["failures"].values()) == 1
        assert payload["records"] == {}
        return
    raise AssertionError("Stage 7 provider unavailability did not stop collection")


def test_stage7_maximum_new_requests_allows_cost_controlled_resume(tmp_path: Path) -> None:
    adapter = HumanGroundTruthAdapter()
    cache_path = tmp_path / "cache.json"

    first = asyncio.run(
        collect_stage7_outputs(
            REPOSITORY_ROOT,
            adapter,
            cache_path=cache_path,
            maximum_new_requests=3,
            request_interval_seconds=1,
            sleep=_no_sleep,
        )
    )
    second = asyncio.run(
        collect_stage7_outputs(
            REPOSITORY_ROOT,
            adapter,
            cache_path=cache_path,
            maximum_new_requests=2,
            request_interval_seconds=1,
            sleep=_no_sleep,
        )
    )

    assert first.total_http_request_count == 3
    assert second.total_http_request_count == 5
    assert adapter.call_count == 5


def test_committed_stage7_report_preserves_failed_quality_gate_and_traceability() -> None:
    report = cast(dict[str, object], json.loads(REPORT_PATH.read_text(encoding="utf-8")))
    quality_gate = cast(dict[str, object], report["quality_gate"])
    final_hybrid = cast(dict[str, object], report["final_hybrid"])
    metrics = cast(dict[str, object], final_hybrid["metrics"])
    l3_quality = cast(dict[str, object], report["l3_provider_quality"])
    accounting = cast(dict[str, object], report["usage_latency_and_cost"])
    traceability = cast(dict[str, object], report["traceability"])
    error_analysis = cast(dict[str, object], report["error_analysis"])

    assert quality_gate["passed"] is False
    assert metrics["accuracy"] == 0.5
    assert metrics["macro_f1"] == 1 / 6
    assert final_hybrid["needs_review_recall"] == 1
    assert final_hybrid["review_rate"] == 1
    assert l3_quality["requirement_status_accuracy"] == 0.9875
    assert l3_quality["unsafe_requirement_mismatch_count"] == 3
    assert l3_quality["criterion_mae"] == 2.162
    assert l3_quality["total_score_mae"] == 8.55
    assert accounting["total_http_request_count"] == 56
    assert accounting["valid_attempt_count"] == 55
    assert accounting["failed_request_count"] == 1
    assert error_analysis["l1_requirement_mismatch_count"] == 86
    assert traceability["protocol_sha256"] == stage7_manifest_sha256(PROTOCOL_PATH)
    assert traceability["dataset_manifest_sha256"] == stage7_manifest_sha256(
        DATASET_DIRECTORY / "manifest.json"
    )
    assert traceability["raw_provider_response_persisted"] is False
    assert "CLASSIFIER_LLM_API_KEY" not in REPORT_PATH.read_text(encoding="utf-8")
