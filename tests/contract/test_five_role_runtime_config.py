from __future__ import annotations

import shutil
from decimal import Decimal
from pathlib import Path
import pytest
from pydantic import ValidationError

from backend.app.agents.classifier.scoring.l1 import score_l1
from backend.app.contracts import (
    CVProfile,
    Evidence,
    EvidenceLocation,
    EvidenceSourceType,
    EvidenceStatus,
    JobProfile,
    ScoringRubric,
)
from backend.app.domain import L2ScoringMode, MatchMode
from backend.app.infrastructure.config import (
    ConfigurationLoadError,
    ModelsConfigurationArtifact,
    RepositoryConfigurationLoader,
    build_l2_policy,
)
from backend.app.infrastructure.config.runtime_manifest import RuntimeScoringStrategy

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_CONFIG_DIRECTORY = REPOSITORY_ROOT / "configs" / "runtime" / "five_role_v1"
EXPECTED_JOB_PROFILE_IDS = {
    "junior-data-analyst-std-v2",
    "junior-python-backend-std-v2",
    "junior-frontend-std-v2",
    "junior-qa-engineer-std-v2",
    "junior-data-engineer-std-v2",
}
REVIEWED_DATASET_DIRECTORY = (
    REPOSITORY_ROOT / "data" / "synthetic_expansion" / "reviewed" / "v2_3_1"
)


def _loader() -> RepositoryConfigurationLoader:
    return RepositoryConfigurationLoader(REPOSITORY_ROOT, RUNTIME_CONFIG_DIRECTORY)


def test_five_role_runtime_manifest_links_the_approved_v8_strategy() -> None:
    loader = _loader()
    manifest = loader.runtime_manifest

    assert manifest is not None
    assert manifest.configuration_status == "frozen_for_stage7"
    assert set(manifest.supported_job_profile_ids) == EXPECTED_JOB_PROFILE_IDS
    assert manifest.strategy.aggregation == (
        Decimal("0.40"),
        Decimal("0.20"),
        Decimal("0.40"),
    )
    assert manifest.strategy.thresholds == (Decimal("70"), Decimal("85"))
    assert manifest.strategy.l2_candidate_id == "coverage-70-95-v1"
    assert manifest.strategy.prompt_version == "l3-evidence-rubric-v12"
    assert manifest.strategy.l3_score_mapping_version == "l3-deterministic-level-mapping-v1"
    assert manifest.data_policy.held_out_evaluated is False
    assert manifest.data_policy.original_frozen_test_evaluated is False


@pytest.mark.parametrize(
    ("field", "value", "message"),
    (
        ("disagreement_points", Decimal("34"), "disagreement threshold"),
        ("boundary_offset_points", Decimal("3"), "boundary offset"),
    ),
)
def test_runtime_manifest_rejects_unapproved_review_policy_values(
    field: str,
    value: Decimal,
    message: str,
) -> None:
    manifest = _loader().runtime_manifest
    assert manifest is not None
    payload = manifest.strategy.model_dump(mode="python")
    payload[field] = value

    with pytest.raises(ValidationError, match=message):
        RuntimeScoringStrategy.model_validate(payload)


def test_five_role_runtime_artifacts_are_complete_versioned_and_linked() -> None:
    loader = _loader()
    jobs = loader.load_job_artifacts()
    policies = {item.job_profile_id: item for item in loader.load_l1_policies()}

    assert {item.job_profile_id for item in jobs} == EXPECTED_JOB_PROFILE_IDS
    assert set(policies) == EXPECTED_JOB_PROFILE_IDS
    for job in jobs:
        loaded = loader.load_for_job(job.job_profile_id)
        config = loaded.classification_config
        assert job.artifact_version == "2.0.0"
        assert job.contract_status == "approved_for_runtime"
        assert loaded.rubric.rubric_version == "2.0.1"
        assert loaded.rubric_artifact.contract_status == "approved_for_runtime"
        assert config.configuration_version == "2.0.0"
        assert config.l1_rules_configuration_version == "2.0.0"
        assert config.models_configuration_version == "2.0.0"
        assert config.aggregation.l1_deterministic_rules == Decimal("0.40")
        assert config.aggregation.l2_section_semantic_matching == Decimal("0.20")
        assert config.aggregation.l3_evidence_grounded_reasoning == Decimal("0.40")
        assert config.thresholds.waitlist_minimum == Decimal("70")
        assert config.thresholds.pass_minimum == Decimal("85")
        assert config.needs_review_policy.disagreement_points == Decimal("35")
        assert tuple(
            (item.minimum, item.maximum) for item in config.needs_review_policy.boundary_score_bands
        ) == ((Decimal("68"), Decimal("72")), (Decimal("83"), Decimal("87")))
        assert {item.requirement_id for item in policies[job.job_profile_id].rules} == set(
            loaded.rubric.critical_requirement_ids
        )


def test_five_role_runtime_job_and_rubric_contracts_match_v8_standard_inputs() -> None:
    loader = _loader()
    jobs = {
        item.job_profile_id: item
        for line in (REVIEWED_DATASET_DIRECTORY / "job_profiles.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if (item := JobProfile.model_validate_json(line)).job_profile_id in EXPECTED_JOB_PROFILE_IDS
    }
    rubrics = {
        item.job_profile_id: item
        for line in (REVIEWED_DATASET_DIRECTORY / "rubrics.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if (item := ScoringRubric.model_validate_json(line)).job_profile_id
        in EXPECTED_JOB_PROFILE_IDS
    }

    assert set(jobs) == EXPECTED_JOB_PROFILE_IDS
    assert set(rubrics) == EXPECTED_JOB_PROFILE_IDS
    for job_profile_id in EXPECTED_JOB_PROFILE_IDS:
        loaded = loader.load_for_job(job_profile_id)
        assert loaded.job_profile == jobs[job_profile_id]
        assert loaded.rubric == rubrics[job_profile_id]


def test_five_role_runtime_builds_the_approved_l2_query_coverage_policy() -> None:
    loader = _loader()
    models = loader.load_models_artifact()

    assert models.embedding.resolved_revision == "d128750597153bb5987e10b1c3493a34e5a4502a"
    assert models.embedding.matching.candidate_id == "coverage-70-95-v1"
    assert models.embedding.matching.similarity_floor == Decimal("0.70")
    assert models.embedding.matching.similarity_ceiling == Decimal("0.95")
    assert models.embedding.matching.top_k == 1
    assert models.embedding.matching.minimum_query_score == Decimal("20")
    for job_profile_id in EXPECTED_JOB_PROFILE_IDS:
        policy = loader.load_for_job(job_profile_id)
        l2_policy = build_l2_policy(policy)
        assert l2_policy.query_count >= 17
        assert all(
            criterion.scoring_mode is L2ScoringMode.QUERY_COVERAGE
            for criterion in l2_policy.criteria
        )
        assert all(criterion.top_k == 1 for criterion in l2_policy.criteria)


def test_five_role_runtime_locks_provider_model_prompt_and_mapping() -> None:
    loader = _loader()
    environment = {
        "CLASSIFIER_LLM_PROVIDER": "openai",
        "CLASSIFIER_LLM_MODEL": "gpt-5.4-mini-2026-03-17",
    }

    loaded = loader.load_for_job("junior-data-analyst-std-v2", environment)

    assert loaded.classification_config.models.llm_provider_identifier == "openai"
    assert loaded.classification_config.models.llm_model_identifier == ("gpt-5.4-mini-2026-03-17")
    assert loaded.classification_config.models.prompt_version == "l3-evidence-rubric-v12"
    assert loaded.models_artifact.llm.score_mapping_version == ("l3-deterministic-level-mapping-v1")


@pytest.mark.parametrize(
    ("provider", "model", "message"),
    (
        ("google_ai_studio", "gpt-5.4-mini-2026-03-17", "provider is not approved"),
        ("openai", "gpt-5.4-mini", "model is not approved"),
    ),
)
def test_five_role_runtime_rejects_unapproved_live_model(
    provider: str,
    model: str,
    message: str,
) -> None:
    with pytest.raises(ConfigurationLoadError, match=message):
        _loader().load_for_job(
            "junior-data-analyst-std-v2",
            {
                "CLASSIFIER_LLM_PROVIDER": provider,
                "CLASSIFIER_LLM_MODEL": model,
            },
        )


def test_query_coverage_artifact_rejects_missing_section_weight() -> None:
    payload = _loader().load_models_artifact().model_dump(mode="python")
    embedding = payload["embedding"]
    assert isinstance(embedding, dict)
    matching = embedding["matching"]
    assert isinstance(matching, dict)
    section_weights = matching["section_weights"]
    assert isinstance(section_weights, tuple)
    matching["section_weights"] = section_weights[:-1]

    with pytest.raises(ValidationError, match="every evidence section"):
        ModelsConfigurationArtifact.model_validate(payload)


def test_role_calibrated_model_artifact_rejects_wrong_score_mapping() -> None:
    payload = _loader().load_models_artifact().model_dump(mode="python")
    llm = payload["llm"]
    assert isinstance(llm, dict)
    llm["score_mapping_version"] = "direct-numeric-scoring-v1"

    with pytest.raises(ValidationError, match="deterministic level mapping"):
        ModelsConfigurationArtifact.model_validate(payload)


def test_every_five_role_l1_rule_handles_all_evidence_states() -> None:
    loader = _loader()
    for policy_artifact in loader.load_l1_policies():
        job_profile_id = policy_artifact.job_profile_id
        loaded = loader.load_for_job(job_profile_id)
        policy = loader.load_l1_policy(job_profile_id)
        for rule in policy.rules:
            positive_text = (
                " ".join(rule.positive_terms)
                if rule.match_mode is MatchMode.ALL
                else rule.positive_terms[0]
            )
            negative_text = rule.explicit_negative_terms[0]
            section = rule.evidence_sections[0]

            def evidence(identifier: str, text: str) -> Evidence:
                return Evidence(
                    evidence_id=identifier,
                    source_type=EvidenceSourceType.MANUAL,
                    section=section,
                    text=text,
                    location=EvidenceLocation(source_record_id=f"record-{identifier}"),
                )

            profiles = {
                EvidenceStatus.SATISFIED: CVProfile(
                    cv_profile_id=f"cv-{rule.requirement_id}-satisfied",
                    candidate_reference=f"candidate-{rule.requirement_id}-satisfied",
                    evidence=(evidence("positive", positive_text),),
                ),
                EvidenceStatus.UNSATISFIED: CVProfile(
                    cv_profile_id=f"cv-{rule.requirement_id}-unsatisfied",
                    candidate_reference=f"candidate-{rule.requirement_id}-unsatisfied",
                    evidence=(evidence("negative", negative_text),),
                ),
                EvidenceStatus.MISSING: CVProfile(
                    cv_profile_id=f"cv-{rule.requirement_id}-missing",
                    candidate_reference=f"candidate-{rule.requirement_id}-missing",
                    evidence=(evidence("unrelated", "Thông tin không liên quan."),),
                ),
                EvidenceStatus.CONFLICTING: CVProfile(
                    cv_profile_id=f"cv-{rule.requirement_id}-conflicting",
                    candidate_reference=f"candidate-{rule.requirement_id}-conflicting",
                    evidence=(
                        evidence("positive", positive_text),
                        evidence("negative", negative_text),
                    ),
                ),
            }
            for expected_status, profile in profiles.items():
                result = score_l1(profile, loaded.rubric, policy)
                actual = next(
                    item.evidence_status
                    for item in result.requirement_assessments
                    if item.requirement_id == rule.requirement_id
                )
                assert actual is expected_status, (
                    job_profile_id,
                    rule.requirement_id,
                    expected_status,
                )


def test_runtime_manifest_rejects_a_modified_artifact(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    configuration = repository / "configs" / "runtime" / "five_role_v1"
    shutil.copytree(RUNTIME_CONFIG_DIRECTORY, configuration)
    for relative_path in (
        Path("evaluation/reports/synthetic_expansion_v2_openai_gpt_5_4_mini_l3_validation_v8.json"),
        Path("evaluation/configs/synthetic_expansion_l3_openai_gpt_5_4_mini_v8.yaml"),
    ):
        destination = repository / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPOSITORY_ROOT / relative_path, destination)
    scoring_path = configuration / "scoring.yaml"
    scoring_path.write_text(
        scoring_path.read_text(encoding="utf-8").replace("pass_minimum: 85", "pass_minimum: 84"),
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationLoadError, match="manifest"):
        RepositoryConfigurationLoader(repository, configuration)
