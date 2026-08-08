from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import cast

import pytest

from backend.app.infrastructure.embeddings import HashingEmbeddingAdapter
from backend.app.infrastructure.config import RepositoryConfigurationLoader
from evaluation.experiments.run_stage6_validation import (
    REPORT_PATH,
    EmbeddingRuntime,
    run,
)
from evaluation.experiments.stage6_config import (
    Stage6CandidateSet,
    load_stage6_candidate_set,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
GENERATED_AT = datetime.fromisoformat("2026-07-26T21:30:00+07:00")


def _test_embedding_runtime() -> EmbeddingRuntime:
    return EmbeddingRuntime(
        adapter=HashingEmbeddingAdapter(
            dimension=768,
            model_identifier="stage6-configured-model-test-fake",
            model_version="1.0.0",
        ),
        model_identifier="stage6-configured-model-test-fake",
        configured_model_version="1.0.0",
        resolved_model_revision="0" * 40,
        configured_model_executed=False,
    )


def test_stage6_candidate_configuration_is_versioned_and_valid() -> None:
    candidate_set = load_stage6_candidate_set(REPOSITORY_ROOT)
    loaded = RepositoryConfigurationLoader(REPOSITORY_ROOT).load_for_job("junior-data-analyst-v1")
    current = next(
        candidate
        for candidate in candidate_set.candidates
        if candidate.candidate_id == "approved-current-v1"
    )

    assert candidate_set.candidate_set_version == "1.2.0"
    assert candidate_set.source_configuration_version == "1.1.0"
    assert candidate_set.source_configuration_version == (
        loaded.classification_config.configuration_version
    )
    assert candidate_set.source_models_configuration_version == (
        loaded.models_artifact.configuration_version
    )
    assert candidate_set.candidate_protection_rules_fixed is True
    assert candidate_set.selection_policy.maximum_review_rate == Decimal("0.80")
    assert len(candidate_set.candidates) == 7
    assert candidate_set.model_strategy.embedding_resolved_revision == (
        "d128750597153bb5987e10b1c3493a34e5a4502a"
    )
    assert all(
        candidate.aggregation.l1_deterministic_rules
        + candidate.aggregation.l2_section_semantic_matching
        + candidate.aggregation.l3_evidence_grounded_reasoning
        == 1
        for candidate in candidate_set.candidates
    )
    assert current.aggregation == loaded.classification_config.aggregation
    assert current.thresholds == loaded.classification_config.thresholds
    assert current.disagreement_points == (
        loaded.classification_config.needs_review_policy.disagreement_points
    )
    assert current.l2_matching.similarity_floor == (
        loaded.models_artifact.embedding.matching.similarity_floor
    )
    assert current.l2_matching.similarity_ceiling == (
        loaded.models_artifact.embedding.matching.similarity_ceiling
    )
    assert current.l2_matching.top_k == (loaded.models_artifact.embedding.matching.top_k)
    assert candidate_set.model_strategy.embedding_model_identifier == (
        loaded.models_artifact.embedding.model_identifier
    )
    assert candidate_set.model_strategy.embedding_configured_version == (
        loaded.models_artifact.embedding.model_version
    )
    assert candidate_set.model_strategy.prompt_version == (
        loaded.classification_config.models.prompt_version
    )


def test_stage6_candidate_configuration_rejects_invalid_weight_total() -> None:
    candidate_set = load_stage6_candidate_set(REPOSITORY_ROOT)
    payload = candidate_set.model_dump(mode="python")
    candidates = cast(list[dict[str, object]], payload["candidates"])
    aggregation = cast(dict[str, object], candidates[0]["aggregation"])
    aggregation["l1_deterministic_rules"] = 0.90

    with pytest.raises(ValueError, match="total 1"):
        Stage6CandidateSet.model_validate(payload)


@pytest.mark.asyncio
async def test_stage6_runner_uses_validation_only_and_never_exposes_frozen_ids() -> None:
    report = await run(REPOSITORY_ROOT, GENERATED_AT, _test_embedding_runtime())
    manifest = json.loads(
        (REPOSITORY_ROOT / "data" / "splits" / "stage6_split_manifest_v1.json").read_text(
            encoding="utf-8"
        )
    )
    frozen_ids = cast(list[str], manifest["frozen_test"]["cv_profile_ids"])
    serialized_report = json.dumps(report)
    split = cast(dict[str, object], report["split_traceability"])

    assert split["validation_sample_count"] == 20
    assert split["frozen_test_evaluated"] is False
    assert split["frozen_test_results_generated"] is False
    assert all(cv_profile_id not in serialized_report for cv_profile_id in frozen_ids)


@pytest.mark.asyncio
async def test_stage6_runner_reports_candidate_safety_metrics_and_score_bounds() -> None:
    report = await run(REPOSITORY_ROOT, GENERATED_AT, _test_embedding_runtime())
    candidate_results = cast(list[dict[str, object]], report["candidate_results"])
    recommendation = cast(dict[str, object], report["recommendation"])

    assert len(candidate_results) == 7
    eligible_ids: set[str] = set()
    for result in candidate_results:
        candidate = cast(dict[str, object], result["candidate"])
        safety = cast(dict[str, object], result["safety"])
        metrics = cast(dict[str, object], result["metrics"])
        cases = cast(list[dict[str, object]], result["cases"])
        assert len(cases) == 20
        assert (
            cast(int, result["label_match_count"]) + cast(int, result["label_mismatch_count"]) == 20
        )
        assert 0 <= cast(float, result["review_rate"]) <= 1
        assert 0 <= cast(float, safety["needs_review_recall"]) <= 1
        assert 0 <= cast(float, metrics["accuracy"]) <= 1
        assert 0 <= cast(float, metrics["macro_f1"]) <= 1
        for case in cases:
            for score in cast(
                dict[str, float | None],
                case["level_scores"],
            ).values():
                assert score is None or 0 <= score <= 100
            final_score = case["final_score"]
            assert final_score is None or 0 <= cast(float, final_score) <= 100
        if result["eligible_for_recommendation"] is True:
            eligible_ids.add(cast(str, candidate["candidate_id"]))
    candidate_id = recommendation["candidate_id"]
    assert candidate_id is None or candidate_id in eligible_ids
    assert recommendation["requires_human_approval"] is True


@pytest.mark.asyncio
async def test_stage6_runner_is_deterministic_with_test_adapter() -> None:
    first = await run(REPOSITORY_ROOT, GENERATED_AT, _test_embedding_runtime())
    second = await run(REPOSITORY_ROOT, GENERATED_AT, _test_embedding_runtime())

    assert first == second


def test_committed_stage6_report_records_real_l2_and_unresolved_live_l3() -> None:
    report = json.loads((REPOSITORY_ROOT / REPORT_PATH).read_text(encoding="utf-8"))
    strategy = cast(dict[str, object], report["execution_strategy"])
    readiness = cast(dict[str, object], report["freeze_readiness"])
    split = cast(dict[str, object], report["split_traceability"])

    assert report["is_final_performance"] is False
    assert strategy["configured_multilingual_l2_executed"] is True
    assert strategy["configured_l2_model_identifier"] == ("intfloat/multilingual-e5-base")
    assert strategy["configured_l2_resolved_revision"] == (
        "d128750597153bb5987e10b1c3493a34e5a4502a"
    )
    assert strategy["live_llm_provider_executed"] is False
    assert split["frozen_test_evaluated"] is False
    assert readiness["configuration_frozen"] is False
    assert readiness["live_llm_model_evaluated"] is False


@pytest.mark.asyncio
async def test_stage6_runner_rejects_naive_generation_time() -> None:
    with pytest.raises(ValueError, match="timezone"):
        await run(
            REPOSITORY_ROOT,
            datetime(2026, 7, 26, 21, 30),
            _test_embedding_runtime(),
        )
