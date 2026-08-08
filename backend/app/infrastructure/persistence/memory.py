from __future__ import annotations

from backend.app.contracts import (
    ApprovedDecision,
    ClassificationRequest,
    ClassificationResult,
)
from backend.app.infrastructure.persistence.repositories import (
    PersistenceConflictError,
    PersistenceInvariantError,
)


class InMemoryClassifierRepository:
    def __init__(self) -> None:
        self._requests: dict[str, ClassificationRequest] = {}
        self._results: dict[str, ClassificationResult] = {}
        self._decisions: dict[str, list[ApprovedDecision]] = {}
        self._decision_ids: set[str] = set()

    async def save_classification(
        self,
        request: ClassificationRequest,
        result: ClassificationResult,
    ) -> None:
        if result.classification_result_id in self._results:
            raise PersistenceConflictError("classification snapshot already exists")
        if result.request_id != request.request_id:
            raise PersistenceInvariantError("classification result request does not match")
        if result.cv_profile_id != request.cv_profile.cv_profile_id:
            raise PersistenceInvariantError("classification result CV profile does not match")
        if result.job_profile_id != request.job_profile.job_profile_id:
            raise PersistenceInvariantError("classification result job profile does not match")
        self._requests[result.classification_result_id] = request
        self._results[result.classification_result_id] = result

    async def get_classification_request(
        self,
        classification_result_id: str,
    ) -> ClassificationRequest | None:
        return self._requests.get(classification_result_id)

    async def get_classification_result(
        self,
        classification_result_id: str,
    ) -> ClassificationResult | None:
        return self._results.get(classification_result_id)

    async def save_approved_decision(self, decision: ApprovedDecision) -> None:
        result = self._results.get(decision.classification_result_id)
        if result is None:
            raise PersistenceInvariantError(
                "approved decision must reference a persisted classification"
            )
        if result.proposed_decision is not decision.proposed_decision:
            raise PersistenceInvariantError(
                "approved decision must preserve the persisted proposed decision"
            )
        if decision.approved_decision_id in self._decision_ids:
            raise PersistenceConflictError("approved decision already exists")
        self._decision_ids.add(decision.approved_decision_id)
        self._decisions.setdefault(decision.classification_result_id, []).append(decision)

    async def list_approved_decisions(
        self,
        classification_result_id: str,
    ) -> tuple[ApprovedDecision, ...]:
        decisions = self._decisions.get(classification_result_id, ())
        return tuple(
            sorted(decisions, key=lambda item: (item.decided_at, item.approved_decision_id))
        )
