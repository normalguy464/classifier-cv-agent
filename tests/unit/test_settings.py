from __future__ import annotations

from pathlib import Path

from pydantic import SecretStr, ValidationError
import pytest

from backend.app.core.settings import RuntimeSettings, StorageBackend


def test_runtime_settings_default_to_offline_safe_adapters() -> None:
    settings = RuntimeSettings(_env_file=None)

    assert settings.classifier_storage_backend is StorageBackend.MEMORY
    assert settings.classifier_embedding_adapter == "sentence_transformers"
    assert settings.classifier_llm_adapter == "deterministic_fake"
    assert settings.classifier_api_key is None
    assert settings.classifier_config_directory == Path("configs/runtime/five_role_v1")


def test_runtime_settings_keep_secrets_out_of_representation() -> None:
    settings = RuntimeSettings(
        _env_file=None,
        classifier_api_key=SecretStr("test-secret-value"),
        classifier_database_url=SecretStr("postgresql+psycopg://user:password@host/database"),
    )

    representation = repr(settings)

    assert "test-secret-value" not in representation
    assert "password" not in representation


def test_runtime_settings_reject_abnormal_timeout() -> None:
    with pytest.raises(ValidationError):
        RuntimeSettings(_env_file=None, classifier_request_timeout_seconds=0)


def test_runtime_settings_load_database_url_from_dotenv(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CLASSIFIER_DATABASE_URL", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "CLASSIFIER_DATABASE_URL="
        "postgresql+psycopg://dotenv-user:dotenv-password@127.0.0.1:55432/runtime-db\n",
        encoding="utf-8",
    )

    settings = RuntimeSettings(_env_file=env_file)

    assert settings.classifier_database_url is not None
    assert (
        settings.classifier_database_url.get_secret_value()
        == "postgresql+psycopg://dotenv-user:dotenv-password@127.0.0.1:55432/runtime-db"
    )


def test_process_database_url_overrides_dotenv(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "CLASSIFIER_DATABASE_URL="
        "postgresql+psycopg://dotenv-user:dotenv-password@127.0.0.1:55432/runtime-db\n",
        encoding="utf-8",
    )
    process_database_url = (
        "postgresql+psycopg://process-user:process-password@127.0.0.1:55432/runtime-db"
    )
    monkeypatch.setenv("CLASSIFIER_DATABASE_URL", process_database_url)

    settings = RuntimeSettings(_env_file=env_file)

    assert settings.classifier_database_url is not None
    assert settings.classifier_database_url.get_secret_value() == process_database_url
