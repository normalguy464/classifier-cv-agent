from __future__ import annotations

import asyncio
import os
from logging.config import fileConfig

from alembic import context
from alembic.config import Config
from sqlalchemy import Connection, MetaData, pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from backend.app.core.settings import RuntimeSettings
from backend.app.infrastructure.persistence.models import Base
from backend.app.infrastructure.persistence.session import normalize_database_url

config: Config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata: MetaData = Base.metadata


def configured_database_url() -> str:
    explicit_database_url = (config.get_main_option("sqlalchemy.url") or "").strip()
    if explicit_database_url:
        return normalize_database_url(explicit_database_url)
    database_url = RuntimeSettings().classifier_database_url
    if database_url is None:
        raise RuntimeError(
            "CLASSIFIER_DATABASE_URL must be configured in the process environment or .env"
        )
    return normalize_database_url(database_url.get_secret_value())


def run_migrations_offline() -> None:
    context.configure(
        url=configured_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def apply_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    section = config.get_section(config.config_ini_section)
    if section is None:
        raise RuntimeError("Alembic configuration section is unavailable")
    section["sqlalchemy.url"] = configured_database_url()
    connectable = async_engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(apply_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    loop_factory = asyncio.SelectorEventLoop if os.name == "nt" else None
    asyncio.run(run_async_migrations(), loop_factory=loop_factory)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
