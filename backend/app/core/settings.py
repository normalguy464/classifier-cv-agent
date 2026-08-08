from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class StorageBackend(StrEnum):
    MEMORY = "memory"
    POSTGRES = "postgres"


class RuntimeSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    classifier_api_key: SecretStr | None = None
    classifier_storage_backend: StorageBackend = StorageBackend.MEMORY
    classifier_database_url: SecretStr | None = None
    classifier_config_directory: Path = Path("configs/runtime/five_role_v1")
    classifier_embedding_adapter: Literal["sentence_transformers"] = "sentence_transformers"
    classifier_llm_adapter: Literal["deterministic_fake", "environment_configured"] = (
        "deterministic_fake"
    )
    classifier_llm_provider: str | None = Field(default=None, min_length=1)
    classifier_llm_model: str | None = Field(default=None, min_length=1)
    classifier_llm_api_key: SecretStr | None = None
    classifier_llm_base_url: str | None = Field(default=None, min_length=1)
    classifier_request_timeout_seconds: float = Field(default=30.0, gt=0, le=300)
