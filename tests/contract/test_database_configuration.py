from __future__ import annotations

from pathlib import Path
from typing import cast

import yaml

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def environment_values() -> dict[str, str]:
    values: dict[str, str] = {}
    for line in (REPOSITORY_ROOT / ".env.example").read_text(encoding="utf-8").splitlines():
        key, value = line.split("=", maxsplit=1)
        values[key] = value
    return values


def test_environment_example_uses_distinct_runtime_and_test_databases() -> None:
    values = environment_values()

    assert values["CLASSIFIER_POSTGRES_DB"] != values["CLASSIFIER_POSTGRES_TEST_DB"]
    assert values["CLASSIFIER_POSTGRES_DB"] in values["CLASSIFIER_DATABASE_URL"]
    assert values["CLASSIFIER_POSTGRES_TEST_DB"] in values["CLASSIFIER_TEST_DATABASE_URL"]
    assert values["CLASSIFIER_DATABASE_URL"].startswith("postgresql+psycopg://")
    assert values["CLASSIFIER_TEST_DATABASE_URL"].startswith("postgresql+psycopg://")


def test_compose_binds_postgres_to_loopback_and_initializes_test_database() -> None:
    compose = cast(
        dict[str, object],
        yaml.safe_load((REPOSITORY_ROOT / "docker-compose.yml").read_text(encoding="utf-8")),
    )
    services = cast(dict[str, object], compose["services"])
    postgres = cast(dict[str, object], services["postgres"])
    environment = cast(dict[str, str], postgres["environment"])
    ports = cast(list[str], postgres["ports"])
    volumes = cast(list[str], postgres["volumes"])

    assert ports == ["127.0.0.1:${CLASSIFIER_POSTGRES_PORT:-55432}:5432"]
    assert environment["CLASSIFIER_POSTGRES_TEST_DB"] == (
        "${CLASSIFIER_POSTGRES_TEST_DB:?CLASSIFIER_POSTGRES_TEST_DB is required}"
    )
    assert (
        "./scripts/init_test_database.sh:/docker-entrypoint-initdb.d/10-init-test-database.sh:ro"
    ) in volumes


def test_database_init_script_rejects_shared_database_name_and_quotes_identifier() -> None:
    script = (REPOSITORY_ROOT / "scripts" / "init_test_database.sh").read_text(encoding="utf-8")
    attributes = (REPOSITORY_ROOT / ".gitattributes").read_text(encoding="utf-8")

    assert '"$CLASSIFIER_POSTGRES_TEST_DB" = "$POSTGRES_DB"' in script
    assert "format('CREATE DATABASE %I', :'test_database')" in script
    assert "--set=ON_ERROR_STOP=1" in script
    assert "scripts/*.sh text eol=lf" in attributes
