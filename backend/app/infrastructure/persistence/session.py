from __future__ import annotations

from typing import TypeAlias

from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

AsyncSessionFactory: TypeAlias = async_sessionmaker[AsyncSession]


def normalize_database_url(database_url: str) -> str:
    url = make_url(database_url)
    if url.drivername in {"postgres", "postgresql"}:
        url = url.set(drivername="postgresql+psycopg")
    if url.drivername != "postgresql+psycopg":
        raise ValueError("database URL must use PostgreSQL with the psycopg driver")
    return url.render_as_string(hide_password=False)


def create_database_engine(database_url: str, *, echo: bool = False) -> AsyncEngine:
    normalized_url = normalize_database_url(database_url)
    return create_async_engine(normalized_url, echo=echo, pool_pre_ping=True)


def create_session_factory(engine: AsyncEngine) -> AsyncSessionFactory:
    return async_sessionmaker(engine, expire_on_commit=False)
