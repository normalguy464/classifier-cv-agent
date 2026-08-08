from __future__ import annotations

import os
from pathlib import Path

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config

from backend.app.infrastructure.persistence.session import normalize_database_url

TEST_DATABASE_URL: str | None = os.getenv("CLASSIFIER_TEST_DATABASE_URL")
SKIP_REASON: str = "CLASSIFIER_TEST_DATABASE_URL is required for PostgreSQL migration tests"

pytestmark = pytest.mark.skipif(TEST_DATABASE_URL is None, reason=SKIP_REASON)


def migration_config(database_url: str | None = None) -> Config:
    if TEST_DATABASE_URL is None:
        raise RuntimeError(SKIP_REASON)
    root = Path(__file__).resolve().parents[2]
    config = Config(str(root / "backend" / "alembic.ini"))
    config.set_main_option(
        "sqlalchemy.url",
        normalize_database_url(database_url or TEST_DATABASE_URL),
    )
    return config


def synchronous_database_url() -> str:
    if TEST_DATABASE_URL is None:
        raise RuntimeError(SKIP_REASON)
    return normalize_database_url(TEST_DATABASE_URL)


def test_upgrade_creates_pgvector_schema_and_matches_metadata() -> None:
    config = migration_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")

    engine = sa.create_engine(synchronous_database_url())
    with engine.connect() as connection:
        table_names = set(sa.inspect(connection).get_table_names())
        vector_type = connection.scalar(
            sa.text(
                """
                SELECT format_type(attribute.atttypid, attribute.atttypmod)
                FROM pg_attribute AS attribute
                JOIN pg_class AS relation ON relation.oid = attribute.attrelid
                WHERE relation.relname = 'evidence_embeddings'
                  AND attribute.attname = 'embedding'
                """
            )
        )
        extension_version = connection.scalar(
            sa.text("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
        )
        append_only_triggers = connection.scalar(
            sa.text(
                """
                SELECT count(*)
                FROM pg_trigger
                WHERE tgname IN (
                    'trg_classification_runs_append_only',
                    'trg_approved_decisions_append_only',
                    'trg_decision_audit_events_append_only'
                )
                  AND NOT tgisinternal
                """
            )
        )
    engine.dispose()

    assert {
        "alembic_version",
        "approved_decisions",
        "classification_runs",
        "decision_audit_events",
        "evidence_embeddings",
    }.issubset(table_names)
    assert vector_type == "vector(768)"
    assert isinstance(extension_version, str)
    assert append_only_triggers == 3
    command.check(config)


def test_downgrade_removes_stage_4_schema_and_upgrade_restores_it() -> None:
    config = migration_config()
    command.downgrade(config, "base")

    engine = sa.create_engine(synchronous_database_url())
    with engine.connect() as connection:
        table_names = set(sa.inspect(connection).get_table_names())
        extension_version = connection.scalar(
            sa.text("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
        )
    engine.dispose()

    assert "approved_decisions" not in table_names
    assert "classification_runs" not in table_names
    assert "decision_audit_events" not in table_names
    assert "evidence_embeddings" not in table_names
    assert extension_version is None

    command.upgrade(config, "head")


def test_explicit_test_database_url_overrides_runtime_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "CLASSIFIER_DATABASE_URL",
        "postgresql+psycopg://invalid:invalid@127.0.0.1:1/must-not-be-used",
    )

    command.current(migration_config())


def test_runtime_database_url_can_be_loaded_from_dotenv(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CLASSIFIER_DATABASE_URL", raising=False)
    monkeypatch.delenv("CLASSIFIER_TEST_DATABASE_URL", raising=False)
    (tmp_path / ".env").write_text(
        f"CLASSIFIER_DATABASE_URL={synchronous_database_url()}\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    root = Path(__file__).resolve().parents[2]
    config = Config(str(root / "backend" / "alembic.ini"))

    command.current(config)
