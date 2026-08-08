from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest
from pydantic import SecretStr

from backend.app.contracts import (
    CVProfile,
    ClassificationRequest,
    Evidence,
    EvidenceLocation,
    EvidenceSection,
    EvidenceSourceType,
    LevelScoreStatus,
)
from backend.app.core.errors import ConfigurationError
from backend.app.core.settings import RuntimeSettings, StorageBackend
from backend.app.infrastructure.bootstrap import (
    ConfiguredClassifierWorkflow,
    _workflow_cache_key,
    build_application,
)
from backend.app.infrastructure.config import RepositoryConfigurationLoader
from backend.app.infrastructure.embeddings import (
    HashingEmbeddingAdapter,
    SentenceTransformerEmbeddingAdapter,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def configured_request() -> ClassificationRequest:
    loader = RepositoryConfigurationLoader(REPOSITORY_ROOT)
    loaded = loader.load_for_job("junior-data-analyst-v1")
    payload = json.loads(
        (REPOSITORY_ROOT / "data" / "samples" / "cvs" / "cv_pilot_da_001.json").read_text(
            encoding="utf-8"
        )
    )
    profile = CVProfile.model_validate(payload)
    return ClassificationRequest(
        request_id="request-runtime-001",
        cv_profile=profile,
        job_profile=loaded.job_profile,
        rubric=loaded.rubric,
        configuration=loaded.classification_config,
    )


def runtime_settings() -> RuntimeSettings:
    return RuntimeSettings(
        _env_file=None,
        classifier_api_key=SecretStr("runtime-test-key"),
        classifier_config_directory=REPOSITORY_ROOT / "configs",
    )


def five_role_runtime_settings() -> RuntimeSettings:
    return RuntimeSettings(
        _env_file=None,
        classifier_api_key=SecretStr("runtime-test-key"),
        classifier_config_directory=(REPOSITORY_ROOT / "configs" / "runtime" / "five_role_v1"),
    )


@pytest.mark.parametrize(
    "field_name",
    (
        "job_profile_artifact_version",
        "l1_rules_configuration_version",
        "models_configuration_version",
    ),
)
def test_workflow_cache_key_changes_with_traceability_version(field_name: str) -> None:
    request = configured_request()
    updated_configuration = request.configuration.model_copy(update={field_name: "9.9.9"})
    updated_request = request.model_copy(update={"configuration": updated_configuration})

    assert _workflow_cache_key(updated_request) != _workflow_cache_key(request)


@pytest.mark.asyncio
async def test_configured_workflow_runs_with_injected_test_embedding(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        SentenceTransformerEmbeddingAdapter,
        "from_configuration",
        classmethod(
            lambda cls, configuration: HashingEmbeddingAdapter(
                dimension=configuration.dimension,
                model_identifier="test-hashing",
                model_version="test-hashing-v1",
            )
        ),
    )
    loader = RepositoryConfigurationLoader(REPOSITORY_ROOT)
    workflow = ConfiguredClassifierWorkflow(runtime_settings(), loader)

    result = await workflow.classify(configured_request())

    assert result.scores.l1.status is LevelScoreStatus.AVAILABLE
    assert result.scores.l2.status is LevelScoreStatus.AVAILABLE
    assert result.scores.l3.status is LevelScoreStatus.AVAILABLE
    assert result.versions.configuration_version == "1.1.0"
    assert result.versions.job_profile_artifact_version == "1.0.0"
    assert result.versions.l1_rules_configuration_version == "1.0.0"
    assert result.versions.models_configuration_version == "1.1.0"
    assert result.versions.embedding_model_identifier == "intfloat/multilingual-e5-base"
    assert result.versions.embedding_model_version == "multilingual-e5-base"
    assert result.versions.llm_provider_identifier == "deterministic_fake"
    assert result.versions.llm_model_identifier == "deterministic-evidence-scorer-v1"


@pytest.mark.asyncio
async def test_configured_workflow_rejects_modified_repository_artifact() -> None:
    loader = RepositoryConfigurationLoader(REPOSITORY_ROOT)
    workflow = ConfiguredClassifierWorkflow(runtime_settings(), loader)
    request = configured_request()
    modified_request = request.model_copy(
        update={"job_profile": request.job_profile.model_copy(update={"title": "Modified title"})}
    )

    with pytest.raises(ConfigurationError, match="job profile"):
        await workflow.classify(modified_request)


def test_postgres_bootstrap_requires_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CLASSIFIER_DATABASE_URL", raising=False)
    settings = RuntimeSettings(
        _env_file=None,
        classifier_storage_backend=StorageBackend.POSTGRES,
        classifier_config_directory=REPOSITORY_ROOT / "configs",
    )

    with pytest.raises(ConfigurationError, match="CLASSIFIER_DATABASE_URL"):
        build_application(settings)


@pytest.mark.asyncio
async def test_bootstrapped_application_health_does_not_load_ml_model() -> None:
    application = build_application(runtime_settings())
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=application),
        base_url="http://classifier.test",
    ) as client:
        response = await client.get("/health")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_five_role_runtime_configuration_executes_a_new_role(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        SentenceTransformerEmbeddingAdapter,
        "from_configuration",
        classmethod(
            lambda cls, configuration: HashingEmbeddingAdapter(
                dimension=configuration.dimension,
                model_identifier="test-hashing",
                model_version="test-hashing-v1",
            )
        ),
    )
    settings = five_role_runtime_settings()
    loader = RepositoryConfigurationLoader(
        REPOSITORY_ROOT,
        settings.classifier_config_directory,
    )
    loaded = loader.load_for_job("junior-frontend-std-v2")
    profile = CVProfile(
        cv_profile_id="cv-five-role-runtime-frontend",
        candidate_reference="candidate-five-role-runtime-frontend",
        evidence=(
            Evidence(
                evidence_id="ev-five-role-runtime-frontend",
                source_type=EvidenceSourceType.MANUAL,
                section=EvidenceSection.PROJECTS,
                text=(
                    "HTML CSS responsive JavaScript TypeScript React; tích hợp API; "
                    "pull request; viết test."
                ),
                location=EvidenceLocation(source_record_id="record-five-role-runtime-frontend"),
            ),
        ),
    )
    request = ClassificationRequest(
        request_id="request-five-role-runtime-frontend",
        cv_profile=profile,
        job_profile=loaded.job_profile,
        rubric=loaded.rubric,
        configuration=loaded.classification_config,
    )
    workflow = ConfiguredClassifierWorkflow(settings, loader)

    result = await workflow.classify(request)

    assert result.scores.l1.status is LevelScoreStatus.AVAILABLE
    assert result.scores.l2.status is LevelScoreStatus.AVAILABLE
    assert result.scores.l3.status is LevelScoreStatus.AVAILABLE
    assert result.versions.configuration_version == "2.0.0"
    assert result.versions.job_profile_artifact_version == "2.0.0"
    assert result.versions.l1_rules_configuration_version == "2.0.0"
    assert result.versions.models_configuration_version == "2.0.0"
    assert result.versions.embedding_model_version == ("d128750597153bb5987e10b1c3493a34e5a4502a")
    assert result.versions.prompt_version == "l3-evidence-rubric-v12"
