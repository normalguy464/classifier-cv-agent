from __future__ import annotations

from pathlib import Path
from typing import cast

import httpx
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine

from backend.app.agents.classifier.graph import (
    ClassifierDependencies,
    LangGraphClassifierWorkflow,
)
from backend.app.api.app import ShutdownCallback, create_app
from backend.app.api.dependencies import ApplicationContainer
from backend.app.application.classify_candidate import ClassifyCandidate
from backend.app.application.ports import ClassificationRepository
from backend.app.application.review_decision import ReviewClassificationDecision
from backend.app.contracts import ClassificationRequest, ClassificationResult
from backend.app.core.errors import ConfigurationError
from backend.app.core.settings import RuntimeSettings, StorageBackend
from backend.app.infrastructure.config import (
    ConfigurationLoadError,
    LoadedClassifierConfiguration,
    RepositoryConfigurationLoader,
    build_l1_policy,
    build_l2_policy,
    build_routing_policy,
)
from backend.app.infrastructure.calibration import SklearnExtraTreesL2Calibrator
from backend.app.infrastructure.embeddings import (
    CoreEmbeddingAdapterBridge,
    SentenceTransformerEmbeddingAdapter,
)
from backend.app.infrastructure.llm import (
    CoreL3ProviderBridge,
    DeterministicCoreL3Provider,
    OpenAICompatibleLLMAdapter,
)
from backend.app.infrastructure.persistence import (
    SqlAlchemyClassifierRepository,
    create_database_engine,
    create_session_factory,
)
from backend.app.infrastructure.persistence.memory import InMemoryClassifierRepository
from backend.app.infrastructure.runtime import SystemClock, UuidIdentifierGenerator

WorkflowCacheKey = tuple[str, ...]


def _workflow_cache_key(request: ClassificationRequest) -> WorkflowCacheKey:
    configuration = request.configuration
    models = configuration.models
    return (
        request.job_profile.job_profile_id,
        configuration.job_profile_artifact_version,
        request.rubric.rubric_version,
        configuration.configuration_version,
        configuration.l1_rules_configuration_version,
        configuration.models_configuration_version,
        models.embedding_model_identifier,
        models.embedding_model_version,
        models.llm_provider_identifier,
        models.llm_model_identifier,
        models.prompt_version,
    )


class ConfiguredClassifierWorkflow:
    def __init__(
        self,
        settings: RuntimeSettings,
        loader: RepositoryConfigurationLoader,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._settings = settings
        self._loader = loader
        self._http_client = http_client
        self._workflows: dict[WorkflowCacheKey, LangGraphClassifierWorkflow] = {}

    async def classify(self, request: ClassificationRequest) -> ClassificationResult:
        loaded = self._load_configuration(request.job_profile.job_profile_id)
        self._validate_request_configuration(request, loaded)
        cache_key = _workflow_cache_key(request)
        workflow = self._workflows.get(cache_key)
        if workflow is None:
            workflow = self._build_workflow(loaded)
            self._workflows[cache_key] = workflow
        return await workflow.classify(request)

    def _load_configuration(self, job_profile_id: str) -> LoadedClassifierConfiguration:
        try:
            if self._settings.classifier_llm_adapter == "deterministic_fake":
                return self._loader.load_for_job(job_profile_id)
            models = self._loader.load_models_artifact()
            provider = self._settings.classifier_llm_provider
            model = self._settings.classifier_llm_model
            if provider is None or model is None:
                raise ConfigurationError("Runtime LLM provider and model must be configured.")
            environment = {
                models.llm.runtime_provider.provider_environment_variable: provider,
                models.llm.runtime_provider.model_environment_variable: model,
            }
            return self._loader.load_for_job(job_profile_id, environment)
        except ConfigurationLoadError as error:
            raise ConfigurationError(str(error)) from error

    @staticmethod
    def _validate_request_configuration(
        request: ClassificationRequest,
        loaded: LoadedClassifierConfiguration,
    ) -> None:
        if request.job_profile != loaded.job_profile:
            raise ConfigurationError("Request job profile does not match the repository artifact.")
        if request.rubric != loaded.rubric:
            raise ConfigurationError("Request rubric does not match the repository artifact.")
        if request.configuration != loaded.classification_config:
            raise ConfigurationError(
                "Request classification configuration does not match the runtime artifact."
            )

    def _build_workflow(
        self,
        loaded: LoadedClassifierConfiguration,
    ) -> LangGraphClassifierWorkflow:
        policies = {policy.job_profile_id: policy for policy in loaded.l1_rules_artifact.policies}
        policy_artifact = policies.get(loaded.job_profile.job_profile_id)
        if policy_artifact is None:
            raise ConfigurationError("Runtime L1 policy is unavailable for the job profile.")
        l1_policy = build_l1_policy(policy_artifact)
        l2_policy = build_l2_policy(loaded)
        embedding = SentenceTransformerEmbeddingAdapter.from_configuration(
            loaded.models_artifact.embedding
        )
        embedding_bridge = CoreEmbeddingAdapterBridge(
            embedding,
            query_count=l2_policy.query_count,
        )
        calibration_artifact = loaded.models_artifact.embedding.calibration
        l2_score_calibrator = (
            None
            if calibration_artifact is None
            else SklearnExtraTreesL2Calibrator(
                self._loader.repository_root,
                calibration_artifact,
            )
        )
        if self._settings.classifier_llm_adapter == "deterministic_fake":
            l3_provider = DeterministicCoreL3Provider(
                l1_policy,
                prompt_version=loaded.models_artifact.llm.prompt_version,
            )
        else:
            if self._http_client is None:
                raise ConfigurationError("Runtime LLM HTTP client is unavailable.")
            provider = self._settings.classifier_llm_provider
            model = self._settings.classifier_llm_model
            api_key = self._settings.classifier_llm_api_key
            base_url = self._settings.classifier_llm_base_url
            if provider is None or model is None or api_key is None or base_url is None:
                raise ConfigurationError("Runtime LLM configuration is incomplete.")
            adapter = OpenAICompatibleLLMAdapter(
                provider_identifier=provider,
                model_identifier=model,
                api_key=api_key.get_secret_value(),
                base_url=base_url,
                prompt_version=loaded.models_artifact.llm.prompt_version,
                client=self._http_client,
                score_mapping_version=loaded.models_artifact.llm.score_mapping_version,
            )
            l3_provider = CoreL3ProviderBridge(adapter, l1_policy)
        return LangGraphClassifierWorkflow(
            ClassifierDependencies(
                l1_policy=l1_policy,
                l2_policy=l2_policy,
                routing_policy=build_routing_policy(loaded),
                embedding_adapter=embedding_bridge,
                l3_provider=l3_provider,
                identifier_generator=UuidIdentifierGenerator(),
                clock=SystemClock(),
                l2_score_calibrator=l2_score_calibrator,
            )
        )


def _repository_root(config_directory: Path) -> Path:
    resolved = config_directory.resolve()
    for candidate in (resolved, *resolved.parents):
        if (candidate / "pyproject.toml").is_file() and (candidate / "AGENTS.md").is_file():
            return candidate
    raise ConfigurationError("Classifier config directory is not inside the repository.")


def _build_repository(
    settings: RuntimeSettings,
) -> tuple[ClassificationRepository, tuple[ShutdownCallback, ...]]:
    if settings.classifier_storage_backend is StorageBackend.MEMORY:
        repository = InMemoryClassifierRepository()
        return cast(ClassificationRepository, repository), ()
    database_url = settings.classifier_database_url
    if database_url is None:
        raise ConfigurationError("PostgreSQL storage requires CLASSIFIER_DATABASE_URL.")
    engine: AsyncEngine = create_database_engine(database_url.get_secret_value())
    repository = SqlAlchemyClassifierRepository(create_session_factory(engine))
    return cast(ClassificationRepository, repository), (engine.dispose,)


def build_application(settings: RuntimeSettings) -> FastAPI:
    repository, shutdown_callbacks = _build_repository(settings)
    http_client: httpx.AsyncClient | None = None
    if settings.classifier_llm_adapter == "environment_configured":
        http_client = httpx.AsyncClient(timeout=settings.classifier_request_timeout_seconds)
        shutdown_callbacks = (*shutdown_callbacks, http_client.aclose)
    loader = RepositoryConfigurationLoader(
        _repository_root(settings.classifier_config_directory),
        settings.classifier_config_directory,
    )
    workflow = ConfiguredClassifierWorkflow(settings, loader, http_client)
    container = ApplicationContainer(
        classify_candidate=ClassifyCandidate(workflow, repository),
        review_decision=ReviewClassificationDecision(repository),
        api_key=settings.classifier_api_key,
    )
    return create_app(container, shutdown_callbacks)
