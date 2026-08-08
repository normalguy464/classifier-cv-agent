from __future__ import annotations

from backend.app.application.ports import ClassificationRepository
from backend.app.contracts import ApprovedDecision, ClassificationResult
from backend.app.core.errors import EntityNotFoundError


class ReviewClassificationDecision:
    def __init__(self, repository: ClassificationRepository) -> None:
        self._repository = repository

    async def get_result(self, classification_result_id: str) -> ClassificationResult:
        result = await self._repository.get_classification_result(classification_result_id)
        if result is None:
            raise EntityNotFoundError(
                f"classification result not found: {classification_result_id}"
            )
        return result

    async def record(self, decision: ApprovedDecision) -> ApprovedDecision:
        result = await self.get_result(decision.classification_result_id)
        if result.proposed_decision is not decision.proposed_decision:
            raise ValueError("approved decision must preserve the stored proposed decision")
        await self._repository.save_approved_decision(decision)
        return decision

    async def history(
        self,
        classification_result_id: str,
    ) -> tuple[ApprovedDecision, ...]:
        await self.get_result(classification_result_id)
        return await self._repository.list_approved_decisions(classification_result_id)
