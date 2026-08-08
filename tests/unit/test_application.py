from __future__ import annotations

from datetime import UTC, datetime
from typing import cast

import pytest

from backend.app.application.classify_candidate import ClassifyCandidate
from backend.app.application.ports import ClassificationRepository, ClassifierWorkflow
from backend.app.application.review_decision import ReviewClassificationDecision
from backend.app.contracts import (
    ApprovalStatus,
    ApprovedDecision,
    ClassificationDecision,
    ClassificationRequest,
    ClassificationResult,
    FinalDecision,
)
from backend.app.core.errors import EntityNotFoundError
from tests.contract.test_contracts import valid_request, valid_result


class FakeWorkflow:
    def __init__(self, result: ClassificationResult) -> None:
        self.result = result
        self.requests: list[ClassificationRequest] = []

    async def classify(self, request: ClassificationRequest) -> ClassificationResult:
        self.requests.append(request)
        return self.result


class MemoryRepository:
    def __init__(self) -> None:
        self.requests: dict[str, ClassificationRequest] = {}
        self.results: dict[str, ClassificationResult] = {}
        self.decisions: dict[str, list[ApprovedDecision]] = {}

    async def save_classification(
        self,
        request: ClassificationRequest,
        result: ClassificationResult,
    ) -> None:
        self.requests[result.classification_result_id] = request
        self.results[result.classification_result_id] = result

    async def get_classification_result(
        self,
        classification_result_id: str,
    ) -> ClassificationResult | None:
        return self.results.get(classification_result_id)

    async def save_approved_decision(self, decision: ApprovedDecision) -> None:
        self.decisions.setdefault(decision.classification_result_id, []).append(decision)

    async def list_approved_decisions(
        self,
        classification_result_id: str,
    ) -> tuple[ApprovedDecision, ...]:
        return tuple(self.decisions.get(classification_result_id, ()))


@pytest.mark.asyncio
async def test_classify_candidate_runs_workflow_and_persists_result() -> None:
    request = valid_request()
    result = valid_result()
    workflow = FakeWorkflow(result)
    repository = MemoryRepository()
    use_case = ClassifyCandidate(
        cast(ClassifierWorkflow, workflow),
        cast(ClassificationRepository, repository),
    )

    actual = await use_case.execute(request)

    assert actual == result
    assert workflow.requests == [request]
    assert repository.results[result.classification_result_id] == result


@pytest.mark.asyncio
async def test_review_decision_rejects_unknown_result() -> None:
    use_case = ReviewClassificationDecision(cast(ClassificationRepository, MemoryRepository()))

    with pytest.raises(EntityNotFoundError):
        await use_case.get_result("result-missing")


@pytest.mark.asyncio
async def test_review_decision_rejects_mismatched_proposed_decision() -> None:
    repository = MemoryRepository()
    result = valid_result()
    await repository.save_classification(valid_request(), result)
    decision = ApprovedDecision(
        approved_decision_id="approved-mismatch-001",
        classification_result_id=result.classification_result_id,
        approval_status=ApprovalStatus.APPROVED,
        proposed_decision=ClassificationDecision.WAITLIST,
        final_decision=FinalDecision.WAITLIST,
        reviewer_reference="reviewer-001",
        decision_reason="This valid contract does not match the stored proposal.",
        decided_at=datetime.now(UTC),
    )
    use_case = ReviewClassificationDecision(cast(ClassificationRepository, repository))

    with pytest.raises(ValueError):
        await use_case.record(decision)
