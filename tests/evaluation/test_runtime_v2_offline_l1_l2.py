from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from backend.app.infrastructure.embeddings import HashingEmbeddingAdapter
from evaluation.experiments.run_runtime_v2_offline_l1_l2 import (
    OfflineEmbeddingRuntime,
    REPOSITORY_ROOT,
    load_offline_configuration,
    run_offline_evaluation,
)


def test_runtime_v2_offline_configuration_forbids_frozen_test_and_llm() -> None:
    configuration = load_offline_configuration(REPOSITORY_ROOT)

    assert configuration.stage7_v1_test_allowed is False
    assert configuration.llm_provider_calls_allowed is False
    assert configuration.l1_quality_policy.minimum_validation_requirement_accuracy == Decimal(
        "0.90"
    )
    assert configuration.l2_quality_policy.maximum_validation_total_score_mae == Decimal("15")


def test_runtime_v2_offline_runner_uses_only_reviewed_split() -> None:
    adapter = HashingEmbeddingAdapter(dimension=96)
    report = run_offline_evaluation(
        REPOSITORY_ROOT,
        datetime(2026, 8, 8, 1, 0, tzinfo=UTC),
        embedding_runtime=OfflineEmbeddingRuntime(
            adapter=adapter,
            model_identifier=adapter.model_identifier,
            model_version=adapter.model_version,
            configured_model_executed=False,
        ),
    )
    development = report["development"]
    validation = report["validation"]
    traceability = report["traceability"]

    assert isinstance(development, dict)
    assert isinstance(validation, dict)
    assert isinstance(traceability, dict)
    assert development["pair_count"] == 50
    assert validation["pair_count"] == 25
    assert report["llm_provider_calls_made"] is False
    assert report["stage7_v1_test_accessed"] is False
    assert traceability["configured_embedding_model_executed"] is False
    assert len(development["cases"]) == 50
    assert len(validation["cases"]) == 25


def test_runtime_v2_offline_runner_rejects_naive_timestamp() -> None:
    with pytest.raises(ValueError, match="timezone"):
        run_offline_evaluation(REPOSITORY_ROOT, datetime(2026, 8, 8, 1, 0))
