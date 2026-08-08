from __future__ import annotations

import json
import shutil
from decimal import Decimal
from pathlib import Path
from typing import Any, cast

import pytest
import yaml

from backend.app.agents.classifier.scoring.l1 import score_l1
from backend.app.contracts import CVProfile, EvidenceSection, RequirementPriority
from backend.app.infrastructure.config import (
    ConfigurationLoadError,
    JobProfileArtifact,
    RepositoryConfigurationLoader,
    build_l2_policy,
    build_routing_policy,
    load_yaml_artifact,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def test_repository_loader_maps_both_reviewed_roles_to_frozen_contracts() -> None:
    loader = RepositoryConfigurationLoader(REPOSITORY_ROOT)

    analyst = loader.load_for_job("junior-data-analyst-v1")
    backend = loader.load_for_job("junior-python-backend-developer-v1")

    assert analyst.job_profile.schema_version == "1.0.0"
    assert analyst.rubric.schema_version == "1.0.0"
    assert analyst.classification_config.schema_version == "1.1.0"
    assert analyst.classification_config.configuration_version == "1.1.0"
    assert analyst.classification_config.job_profile_artifact_version == "1.0.0"
    assert analyst.classification_config.l1_rules_configuration_version == "1.0.0"
    assert analyst.classification_config.models_configuration_version == "1.1.0"
    assert analyst.rubric.job_profile_id == analyst.job_profile.job_profile_id
    assert backend.rubric.job_profile_id == backend.job_profile.job_profile_id
    assert len(analyst.job_profile.requirements) == 7
    assert len(backend.job_profile.requirements) == 9
    assert (
        sum(
            requirement.priority is RequirementPriority.REQUIRED
            for requirement in analyst.job_profile.requirements
        )
        == 3
    )
    assert (
        sum(
            requirement.priority is RequirementPriority.REQUIRED
            for requirement in backend.job_profile.requirements
        )
        == 4
    )


def test_repository_loader_maps_review_policy_and_fake_model_metadata() -> None:
    loaded = RepositoryConfigurationLoader(REPOSITORY_ROOT).load_for_job("junior-data-analyst-v1")
    config = loaded.classification_config

    assert config.aggregation.l1_deterministic_rules == Decimal("0.45")
    assert config.aggregation.l2_section_semantic_matching == Decimal("0.25")
    assert config.aggregation.l3_evidence_grounded_reasoning == Decimal("0.30")
    assert config.thresholds.pass_minimum == Decimal("75")
    assert config.thresholds.waitlist_minimum == Decimal("60")
    assert config.needs_review_policy.disagreement_points == Decimal("25")
    assert tuple(
        (band.minimum, band.maximum) for band in config.needs_review_policy.boundary_score_bands
    ) == (
        (Decimal("58"), Decimal("62")),
        (Decimal("73"), Decimal("77")),
    )
    assert config.models.embedding_model_identifier == "intfloat/multilingual-e5-base"
    assert config.models_configuration_version == loaded.models_artifact.configuration_version
    assert config.l1_rules_configuration_version == loaded.l1_rules_artifact.configuration_version
    assert config.models.llm_provider_identifier == "deterministic_fake"
    assert config.models.llm_model_identifier == "deterministic-evidence-scorer-v1"
    assert config.models.prompt_version == "l3-evidence-rubric-v1"


def test_repository_loader_uses_runtime_provider_metadata_without_api_key() -> None:
    loaded = RepositoryConfigurationLoader(REPOSITORY_ROOT).load_for_job(
        "junior-data-analyst-v1",
        runtime_environment={
            "CLASSIFIER_LLM_PROVIDER": "openai-compatible-test",
            "CLASSIFIER_LLM_MODEL": "test-model",
            "CLASSIFIER_LLM_API_KEY": "must-not-enter-contract",
        },
    )

    dumped = loaded.classification_config.model_dump_json()
    assert loaded.classification_config.models.llm_provider_identifier == "openai-compatible-test"
    assert loaded.classification_config.models.llm_model_identifier == "test-model"
    assert "must-not-enter-contract" not in dumped


def test_repository_loader_rejects_incomplete_runtime_metadata() -> None:
    loader = RepositoryConfigurationLoader(REPOSITORY_ROOT)

    with pytest.raises(ConfigurationLoadError, match="metadata is incomplete"):
        loader.load_for_job(
            "junior-data-analyst-v1",
            runtime_environment={"CLASSIFIER_LLM_PROVIDER": "provider-only"},
        )


def test_repository_loader_rejects_l1_rules_version_link_mismatch(tmp_path: Path) -> None:
    shutil.copytree(REPOSITORY_ROOT / "configs", tmp_path / "configs")
    scoring_path = tmp_path / "configs" / "scoring.yaml"
    payload = cast(dict[str, Any], yaml.safe_load(scoring_path.read_text(encoding="utf-8")))
    artifact_links = cast(dict[str, object], payload["artifact_links"])
    artifact_links["l1_rules_configuration_version"] = "9.9.9"
    scoring_path.write_text(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationLoadError, match="L1 rules configuration"):
        RepositoryConfigurationLoader(tmp_path).load_for_job("junior-data-analyst-v1")


def test_l1_rule_artifact_covers_every_critical_requirement_once() -> None:
    loader = RepositoryConfigurationLoader(REPOSITORY_ROOT)
    policies = {policy.job_profile_id: policy for policy in loader.load_l1_policies()}

    assert set(policies) == {
        "junior-data-analyst-v1",
        "junior-python-backend-developer-v1",
    }
    assert {rule.requirement_id for rule in policies["junior-data-analyst-v1"].rules} == {
        "da-sql",
        "da-analysis-language",
        "da-analytical-project",
    }
    assert {
        rule.requirement_id for rule in policies["junior-python-backend-developer-v1"].rules
    } == {
        "be-python",
        "be-rest-api",
        "be-relational-data",
        "be-git",
    }
    assert all(rule.positive_terms for policy in policies.values() for rule in policy.rules)
    assert all(
        rule.explicit_negative_terms for policy in policies.values() for rule in policy.rules
    )


def test_loader_builds_versioned_l2_policy_from_reviewed_artifacts() -> None:
    loader = RepositoryConfigurationLoader(REPOSITORY_ROOT)
    loaded = loader.load_for_job("junior-data-analyst-v1")
    policy = build_l2_policy(loaded)
    embedding = loaded.models_artifact.embedding

    assert loaded.models_artifact.configuration_version == "1.1.0"
    assert embedding.dimension == 768
    assert embedding.query_prefix == "query"
    assert embedding.passage_prefix == "passage"
    assert policy.job_profile_id == loaded.rubric.job_profile_id
    assert {item.criterion_id for item in policy.criteria} == {
        item.criterion_id for item in loaded.rubric.criteria
    }
    assert all(item.top_k == 2 for item in policy.criteria)
    assert all(item.similarity_floor == Decimal("0.20") for item in policy.criteria)
    assert all(item.similarity_ceiling == Decimal("0.80") for item in policy.criteria)
    assert all(
        item.evidence_sections
        == (
            EvidenceSection.SKILLS,
            EvidenceSection.WORK_EXPERIENCE,
            EvidenceSection.PROJECTS,
            EvidenceSection.EDUCATION,
        )
        for item in policy.criteria
    )
    assert all(item.query_text for item in policy.criteria)


def test_loader_builds_complete_core_routing_policy() -> None:
    loaded = RepositoryConfigurationLoader(REPOSITORY_ROOT).load_for_job("junior-data-analyst-v1")
    policy = build_routing_policy(loaded)

    assert policy.pass_minimum == Decimal("75")
    assert policy.waitlist_minimum == Decimal("60")
    assert policy.disagreement_points == Decimal("25")
    assert policy.low_score_without_explicit_critical_unsatisfied is True
    assert policy.critical_unsatisfied_at_or_above_waitlist_threshold is True
    assert policy.reject_requires_explicit_unsatisfied_critical is True
    assert tuple((rule.rule_id, rule.minimum, rule.maximum) for rule in policy.boundary_rules) == (
        ("lower-threshold-boundary", Decimal("58"), Decimal("62")),
        ("upper-threshold-boundary", Decimal("73"), Decimal("77")),
    )


def test_configured_l1_rules_preserve_reviewed_pilot_requirement_statuses() -> None:
    loader = RepositoryConfigurationLoader(REPOSITORY_ROOT)
    annotation = cast(
        dict[str, Any],
        json.loads(
            (REPOSITORY_ROOT / "data" / "annotations" / "pilot_annotations_v1.json").read_text(
                encoding="utf-8"
            )
        ),
    )

    for raw_record in cast(list[dict[str, Any]], annotation["records"]):
        cv_profile = CVProfile.model_validate_json(
            (REPOSITORY_ROOT / cast(str, raw_record["source_cv_file"])).read_text(encoding="utf-8")
        )
        job_profile_id = cast(str, raw_record["job_profile_id"])
        loaded = loader.load_for_job(job_profile_id)
        assessment = score_l1(
            cv_profile,
            loaded.rubric,
            loader.load_l1_policy(job_profile_id),
        )
        actual = {
            item.requirement_id: item.evidence_status.value
            for item in assessment.requirement_assessments
        }
        expected = {
            cast(str, item["requirement_id"]): cast(str, item["evidence_status"])
            for item in cast(
                list[dict[str, object]],
                raw_record["critical_requirement_assessments"],
            )
        }

        assert actual == expected


def test_yaml_loader_rejects_unknown_fields(tmp_path: Path) -> None:
    path = tmp_path / "invalid_job.yaml"
    path.write_text(
        "\n".join(
            (
                "artifact_kind: job_profile_draft",
                "artifact_version: 1.0.0",
                "contract_status: approved_for_pilot",
                "job_profile_id: invalid-job-v1",
                "title: Invalid",
                "language: vi",
                "unexpected: true",
            )
        ),
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationLoadError, match="invalid configuration artifact"):
        load_yaml_artifact(path, JobProfileArtifact)


def test_yaml_loader_uses_safe_loader(tmp_path: Path) -> None:
    path = tmp_path / "unsafe.yaml"
    path.write_text("!!python/object/apply:os.system ['echo unsafe']", encoding="utf-8")

    with pytest.raises(ConfigurationLoadError, match="cannot load configuration artifact"):
        load_yaml_artifact(path, JobProfileArtifact)


def test_repository_loader_rejects_unknown_job_profile() -> None:
    loader = RepositoryConfigurationLoader(REPOSITORY_ROOT)

    with pytest.raises(ConfigurationLoadError, match="unknown job profile"):
        loader.load_for_job("unknown-job-profile")
