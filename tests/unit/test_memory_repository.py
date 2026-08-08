from __future__ import annotations

from datetime import UTC, datetime

import pytest

from backend.app.contracts import (
    ApprovalStatus,
    ApprovedDecision,
    ClassificationDecision,
    FinalDecision,
)
from backend.app.infrastructure.persistence.memory import InMemoryClassifierRepository
from backend.app.infrastructure.persistence.repositories import (
    PersistenceConflictError,
    PersistenceInvariantError,
)
from tests.contract.test_contracts import valid_request, valid_result


def approved_decision() -> ApprovedDecision:
    return ApprovedDecision(
        approved_decision_id="approved-memory-001",
        classification_result_id="result-001",
        approval_status=ApprovalStatus.APPROVED,
        proposed_decision=ClassificationDecision.PASS,
        final_decision=FinalDecision.PASS,
        reviewer_reference="reviewer-001",
        decision_reason="The reviewer confirmed the result.",
        decided_at=datetime.now(UTC),
    )


@pytest.mark.asyncio
async def test_memory_repository_round_trip_and_audit_history() -> None:
    repository = InMemoryClassifierRepository()
    request = valid_request()
    result = valid_result()
    decision = approved_decision()

    await repository.save_classification(request, result)
    await repository.save_approved_decision(decision)

    assert await repository.get_classification_request(result.classification_result_id) == request
    assert await repository.get_classification_result(result.classification_result_id) == result
    assert await repository.list_approved_decisions(result.classification_result_id) == (decision,)


@pytest.mark.asyncio
async def test_memory_repository_rejects_duplicate_classification() -> None:
    repository = InMemoryClassifierRepository()
    request = valid_request()
    result = valid_result()
    await repository.save_classification(request, result)

    with pytest.raises(PersistenceConflictError):
        await repository.save_classification(request, result)


@pytest.mark.asyncio
async def test_memory_repository_rejects_decision_for_missing_result() -> None:
    repository = InMemoryClassifierRepository()

    with pytest.raises(PersistenceInvariantError):
        await repository.save_approved_decision(approved_decision())
