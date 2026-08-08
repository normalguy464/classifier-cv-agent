from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator, Coroutine, Iterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncEngine

from backend.app.contracts import (
    ApprovalStatus,
    ApprovedDecision,
    ClassificationDecision,
    ClassificationRequest,
    ClassificationResult,
    EvidenceSection,
    FinalDecision,
)
from backend.app.infrastructure.persistence import (
    ClassificationRunRow,
    PersistenceConflictError,
    PersistenceInvariantError,
    SqlAlchemyClassifierRepository,
    create_database_engine,
    create_session_factory,
    normalize_database_url,
)
from tests.contract.test_contracts import valid_request, valid_result

TEST_DATABASE_URL: str | None = os.getenv("CLASSIFIER_TEST_DATABASE_URL")
SKIP_REASON: str = "CLASSIFIER_TEST_DATABASE_URL is required for PostgreSQL persistence tests"

pytestmark = pytest.mark.skipif(TEST_DATABASE_URL is None, reason=SKIP_REASON)


def run_async_test(coroutine: Coroutine[object, object, None]) -> None:
    loop_factory = asyncio.SelectorEventLoop if os.name == "nt" else None
    asyncio.run(coroutine, loop_factory=loop_factory)


def database_url() -> str:
    if TEST_DATABASE_URL is None:
        raise RuntimeError(SKIP_REASON)
    return normalize_database_url(TEST_DATABASE_URL)


def migrated_database() -> Iterator[None]:
    config = Config("backend/alembic.ini")
    config.set_main_option("sqlalchemy.url", database_url())
    command.upgrade(config, "head")
    yield


@pytest.fixture(autouse=True, scope="module")
def migration_fixture() -> Iterator[None]:
    yield from migrated_database()


@asynccontextmanager
async def database_engine() -> AsyncIterator[AsyncEngine]:
    engine = create_database_engine(database_url())
    try:
        yield engine
    finally:
        await engine.dispose()


def unique_request_and_result() -> tuple[ClassificationRequest, ClassificationResult]:
    suffix = uuid4().hex
    request_id = f"request-{suffix}"
    cv_profile_id = f"cv-{suffix}"
    result_id = f"result-{suffix}"
    request_template = valid_request()
    result_template = valid_result()
    request = request_template.model_copy(
        update={
            "request_id": request_id,
            "cv_profile": request_template.cv_profile.model_copy(
                update={"cv_profile_id": cv_profile_id}
            ),
        }
    )
    result = result_template.model_copy(
        update={
            "classification_result_id": result_id,
            "request_id": request_id,
            "cv_profile_id": cv_profile_id,
            "created_at": datetime.now(UTC),
        }
    )
    return request, result


async def assert_repository_round_trips_immutable_contract_snapshots(
    database_engine: AsyncEngine,
) -> None:
    repository = SqlAlchemyClassifierRepository(create_session_factory(database_engine))
    request, result = unique_request_and_result()

    await repository.save_classification(request, result)

    stored_request = await repository.get_classification_request(result.classification_result_id)
    stored_result = await repository.get_classification_result(result.classification_result_id)

    assert stored_request == request
    assert stored_result == result

    with pytest.raises(PersistenceConflictError):
        await repository.save_classification(request, result)

    async with database_engine.connect() as connection:
        transaction = await connection.begin()
        with pytest.raises(DBAPIError, match="append-only"):
            await connection.execute(
                sa.update(ClassificationRunRow)
                .where(
                    ClassificationRunRow.classification_result_id == result.classification_result_id
                )
                .values(proposed_decision="reject")
            )
        await transaction.rollback()


def test_repository_round_trips_immutable_contract_snapshots() -> None:
    async def execute() -> None:
        async with database_engine() as engine:
            await assert_repository_round_trips_immutable_contract_snapshots(engine)

    run_async_test(execute())


async def assert_repository_persists_approved_decision_and_audit_event_atomically(
    database_engine: AsyncEngine,
) -> None:
    repository = SqlAlchemyClassifierRepository(create_session_factory(database_engine))
    request, result = unique_request_and_result()
    await repository.save_classification(request, result)
    decision = ApprovedDecision(
        approved_decision_id=f"approved-{uuid4().hex}",
        classification_result_id=result.classification_result_id,
        approval_status=ApprovalStatus.APPROVED,
        proposed_decision=result.proposed_decision,
        final_decision=FinalDecision.PASS,
        reviewer_reference="reviewer-stage-four",
        decision_reason="The reviewer confirmed the evidence and proposed decision.",
        decided_at=datetime.now(UTC),
    )
    override = ApprovedDecision(
        approved_decision_id=f"approved-{uuid4().hex}",
        classification_result_id=result.classification_result_id,
        approval_status=ApprovalStatus.OVERRIDDEN,
        proposed_decision=result.proposed_decision,
        final_decision=FinalDecision.WAITLIST,
        reviewer_reference="reviewer-stage-four",
        decision_reason="A second review changed the downstream decision.",
        override_reason="The reviewer found a material ambiguity requiring a waitlist.",
        decided_at=decision.decided_at + timedelta(seconds=1),
    )

    await repository.save_approved_decision(decision)
    await repository.save_approved_decision(override)

    stored_decision = await repository.get_approved_decision(result.classification_result_id)
    stored_decisions = await repository.list_approved_decisions(result.classification_result_id)
    events = await repository.list_decision_audit_events(result.classification_result_id)

    assert stored_decision == override
    assert stored_decisions == (decision, override)
    assert len(events) == 2
    assert events[0].approved_decision_id == decision.approved_decision_id
    assert events[0].event_type == ApprovalStatus.APPROVED.value
    assert ApprovedDecision.model_validate(events[0].event_snapshot) == decision
    assert events[1].approved_decision_id == override.approved_decision_id
    assert events[1].event_type == ApprovalStatus.OVERRIDDEN.value
    assert ApprovedDecision.model_validate(events[1].event_snapshot) == override

    with pytest.raises(PersistenceConflictError):
        await repository.save_approved_decision(decision)


def test_repository_persists_approved_decision_and_audit_event_atomically() -> None:
    async def execute() -> None:
        async with database_engine() as engine:
            await assert_repository_persists_approved_decision_and_audit_event_atomically(engine)

    run_async_test(execute())


async def assert_repository_rejects_cross_run_decisions_and_invalid_embeddings(
    database_engine: AsyncEngine,
) -> None:
    repository = SqlAlchemyClassifierRepository(create_session_factory(database_engine))
    request, result = unique_request_and_result()
    await repository.save_classification(request, result)
    mismatched_decision = ApprovedDecision(
        approved_decision_id=f"approved-{uuid4().hex}",
        classification_result_id=result.classification_result_id,
        approval_status=ApprovalStatus.APPROVED,
        proposed_decision=ClassificationDecision.WAITLIST,
        final_decision=FinalDecision.WAITLIST,
        reviewer_reference="reviewer-stage-four",
        decision_reason="This intentionally mismatches the persisted proposal.",
        decided_at=datetime.now(UTC),
    )
    mismatched_result = result.model_copy(update={"request_id": f"request-{uuid4().hex}"})

    with pytest.raises(PersistenceInvariantError, match="request"):
        await repository.save_classification(request, mismatched_result)

    for field_name, expected_message in (
        ("job_profile_artifact_version", "job profile artifact version"),
        ("l1_rules_configuration_version", "L1 rules configuration version"),
        ("models_configuration_version", "models configuration version"),
        ("embedding_model_identifier", "embedding model identifier"),
        ("llm_provider_identifier", "LLM provider identifier"),
    ):
        mismatched_versions = result.versions.model_copy(update={field_name: "9.9.9"})
        mismatched_version_result = result.model_copy(update={"versions": mismatched_versions})
        with pytest.raises(PersistenceInvariantError, match=expected_message):
            await repository.save_classification(request, mismatched_version_result)

    with pytest.raises(PersistenceInvariantError, match="proposed decision"):
        await repository.save_approved_decision(mismatched_decision)

    with pytest.raises(PersistenceInvariantError, match="exactly 768"):
        await repository.save_evidence_embedding(
            classification_result_id=result.classification_result_id,
            evidence_id="ev-sql",
            section=EvidenceSection.SKILLS,
            model_version="multilingual-e5-base",
            embedding=(0.0,) * 767,
        )

    with pytest.raises(PersistenceInvariantError, match="finite"):
        await repository.save_evidence_embedding(
            classification_result_id=result.classification_result_id,
            evidence_id="ev-sql",
            section=EvidenceSection.SKILLS,
            model_version="multilingual-e5-base",
            embedding=(float("nan"),) + (0.0,) * 767,
        )

    await repository.save_evidence_embedding(
        classification_result_id=result.classification_result_id,
        evidence_id="ev-sql",
        section=EvidenceSection.SKILLS,
        model_version="multilingual-e5-base",
        embedding=(0.0,) * 768,
    )


def test_repository_rejects_cross_run_decisions_and_invalid_embeddings() -> None:
    async def execute() -> None:
        async with database_engine() as engine:
            await assert_repository_rejects_cross_run_decisions_and_invalid_embeddings(engine)

    run_async_test(execute())
