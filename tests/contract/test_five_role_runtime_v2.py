from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

from backend.app.infrastructure.config import RepositoryConfigurationLoader

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CONFIGURATION_DIRECTORY = REPOSITORY_ROOT / "configs" / "runtime" / "five_role_v2"


def test_five_role_runtime_v2_is_approved_and_frozen_for_stage7() -> None:
    loader = RepositoryConfigurationLoader(REPOSITORY_ROOT, CONFIGURATION_DIRECTORY)
    manifest = loader.runtime_manifest

    assert manifest is not None
    assert manifest.configuration_set_id == "five-role-runtime-v2"
    assert manifest.configuration_status == "frozen_for_stage7"
    assert manifest.user_approval_date == date(2026, 8, 8)
    assert manifest.approved_experiment_id == "runtime-v2-hybrid-waitlist-tuning-v6"
    assert manifest.data_policy.held_out_evaluated is False
    assert manifest.data_policy.original_frozen_test_evaluated is False


def test_five_role_runtime_v2_loads_the_approved_strategy_for_every_role() -> None:
    loader = RepositoryConfigurationLoader(REPOSITORY_ROOT, CONFIGURATION_DIRECTORY)
    jobs = loader.load_job_artifacts()

    assert len(jobs) == 5
    for job in jobs:
        loaded = loader.load_for_job(job.job_profile_id)
        configuration = loaded.classification_config
        assert loaded.scoring_artifact.contract_status == "approved_for_runtime"
        assert loaded.models_artifact.contract_status == "approved_for_runtime"
        assert loaded.l1_rules_artifact.contract_status == "approved_for_runtime"
        assert configuration.configuration_version == "3.0.0"
        assert configuration.aggregation.l1_deterministic_rules == Decimal("0.20")
        assert configuration.aggregation.l2_section_semantic_matching == Decimal("0.30")
        assert configuration.aggregation.l3_evidence_grounded_reasoning == Decimal("0.50")
        assert configuration.thresholds.waitlist_minimum == Decimal("67")
        assert configuration.thresholds.pass_minimum == Decimal("82")
        assert configuration.needs_review_policy.disagreement_points == Decimal("45")
        assert loaded.models_artifact.llm.prompt_version == "l3-evidence-rubric-v15"
        assert loaded.models_artifact.llm.score_mapping_version == (
            "l3-deterministic-level-mapping-v3"
        )
