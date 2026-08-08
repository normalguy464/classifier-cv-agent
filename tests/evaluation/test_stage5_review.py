from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import cast

import pytest

from backend.app.contracts import ClassificationDecision
from evaluation.experiments.run_stage5_review import REPORT_PATH, run

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
GENERATED_AT = datetime.fromisoformat("2026-07-26T20:00:00+07:00")


@pytest.mark.asyncio
async def test_stage5_report_runs_full_classifier_on_thirty_reviewed_cases() -> None:
    report = await run(REPOSITORY_ROOT, GENERATED_AT)
    dataset = cast(dict[str, object], report["dataset"])
    strategy = cast(dict[str, object], report["execution_strategy"])
    summary = cast(dict[str, object], report["summary"])
    cases = cast(list[dict[str, object]], report["cases"])

    assert report["report_scope"] == "reviewed-stage4-controlled-diagnostic"
    assert report["is_final_performance"] is False
    assert dataset["sample_count"] == 30
    assert dataset["annotation_status"] == "reviewed"
    assert len(cases) == 30
    assert strategy["configured_production_l2_executed"] is False
    assert strategy["live_llm_provider_executed"] is False
    assert (
        cast(int, summary["label_match_count"]) + cast(int, summary["label_mismatch_count"]) == 30
    )


@pytest.mark.asyncio
async def test_stage5_report_scores_versions_and_queues_are_consistent() -> None:
    report = await run(REPOSITORY_ROOT, GENERATED_AT)
    cases = cast(list[dict[str, object]], report["cases"])
    queue = cast(dict[str, object], report["review_queue"])
    actual_mismatches: list[str] = []
    actual_needs_review: list[str] = []
    actual_disagreements: list[str] = []

    for case in cases:
        cv_profile_id = cast(str, case["cv_profile_id"])
        ground_truth = cast(dict[str, object], case["ground_truth"])
        result = cast(dict[str, object], case["classifier_result"])
        comparison = cast(dict[str, object], case["comparison"])
        level_scores = cast(dict[str, dict[str, object]], result["level_scores"])
        versions = cast(dict[str, object], result["versions"])
        criterion_scores = cast(list[dict[str, object]], comparison["criterion_scores"])

        assert ground_truth["final_label"] in {
            decision.value for decision in ClassificationDecision
        }
        assert result["proposed_decision"] in {
            decision.value for decision in ClassificationDecision
        }
        assert comparison["requirement_status_match"] is True
        assert len(criterion_scores) == 5
        assert versions["embedding_model_identifier"] == "deterministic-hashing-embedding"
        assert versions["embedding_model_version"] == "1.0.0"
        assert versions["llm_provider_identifier"] == "deterministic_fake"
        for level in level_scores.values():
            value = level["value"]
            assert value is None or 0 <= cast(float, value) <= 100
        final_score = result["final_score"]
        assert final_score is None or 0 <= cast(float, final_score) <= 100
        for criterion in criterion_scores:
            human_score = cast(float, criterion["human_score"])
            classifier_score = cast(float, criterion["classifier_l3_weighted_score"])
            maximum = cast(float, criterion["maximum_points"])
            difference = cast(float, criterion["absolute_difference"])
            assert 0 <= human_score <= maximum
            assert 0 <= classifier_score <= maximum
            assert Decimal(str(difference)) == abs(
                Decimal(str(human_score)) - Decimal(str(classifier_score))
            )
        if comparison["label_match"] is False:
            actual_mismatches.append(cv_profile_id)
        if result["proposed_decision"] == ClassificationDecision.NEEDS_REVIEW.value:
            actual_needs_review.append(cv_profile_id)
        flags = cast(list[str], comparison["flags"])
        if "large-level-disagreement" in flags:
            actual_disagreements.append(cv_profile_id)

    assert queue["label_mismatch_case_ids"] == actual_mismatches
    assert queue["needs_review_case_ids"] == actual_needs_review
    assert queue["large_disagreement_case_ids"] == actual_disagreements
    representative_ids = cast(list[str], queue["representative_case_ids"])
    assert set(actual_mismatches).issubset(representative_ids)
    assert len(representative_ids) <= 20


@pytest.mark.asyncio
async def test_stage5_report_is_deterministic_for_fixed_inputs_and_time() -> None:
    first = await run(REPOSITORY_ROOT, GENERATED_AT)
    second = await run(REPOSITORY_ROOT, GENERATED_AT)

    assert first == second


@pytest.mark.asyncio
async def test_committed_stage5_report_matches_runner() -> None:
    committed = json.loads((REPOSITORY_ROOT / REPORT_PATH).read_text(encoding="utf-8"))
    generated_at = datetime.fromisoformat(cast(str, committed["generated_at"]))

    assert committed == await run(REPOSITORY_ROOT, generated_at)


@pytest.mark.asyncio
async def test_stage5_report_rejects_naive_generation_time() -> None:
    with pytest.raises(ValueError, match="timezone"):
        await run(REPOSITORY_ROOT, datetime(2026, 7, 26, 20, 0))
