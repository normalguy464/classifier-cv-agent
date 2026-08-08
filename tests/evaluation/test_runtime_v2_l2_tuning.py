from datetime import datetime
from pathlib import Path

import pytest

from evaluation.experiments.run_runtime_v2_l2_tuning import (
    L2Candidate,
    load_tuning_configuration,
    run_l2_tuning,
)
from evaluation.experiments.run_runtime_v2_offline_l1_l2 import OfflineEmbeddingRuntime
from backend.app.infrastructure.embeddings import HashingEmbeddingAdapter

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def test_l2_tuning_configuration_is_bounded_and_offline() -> None:
    configuration = load_tuning_configuration(REPOSITORY_ROOT)

    assert configuration.stage7_v1_test_allowed is False
    assert configuration.llm_provider_calls_allowed is False
    assert len(configuration.candidates) == 8
    assert len({item.candidate_id for item in configuration.candidates}) == 8


def test_l2_candidate_rejects_invalid_similarity_interval() -> None:
    with pytest.raises(ValueError, match="similarity_ceiling"):
        L2Candidate(
            candidate_id="invalid",
            similarity_floor="0.9",
            similarity_ceiling="0.8",
            minimum_query_score="20",
        )


def test_l2_tuning_uses_fake_runtime_without_api_or_frozen_test() -> None:
    runtime = OfflineEmbeddingRuntime(
        adapter=HashingEmbeddingAdapter(dimension=64),
        model_identifier="hashing-test",
        model_version="1",
        configured_model_executed=False,
    )

    report = run_l2_tuning(
        REPOSITORY_ROOT,
        datetime.fromisoformat("2026-08-08T03:00:00+07:00"),
        runtime,
    )

    assert report["llm_provider_calls_made"] is False
    assert report["stage7_v1_test_accessed"] is False
    assert report["configured_embedding_model_executed"] is False
    assert len(report["candidate_results"]) == 8
