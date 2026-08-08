from __future__ import annotations

from backend.app.application.ports import ClassificationRepository, ClassifierWorkflow
from backend.app.contracts import ClassificationRequest, ClassificationResult


class ClassifyCandidate:
    def __init__(
        self,
        workflow: ClassifierWorkflow,
        repository: ClassificationRepository,
    ) -> None:
        self._workflow = workflow
        self._repository = repository

    async def execute(self, request: ClassificationRequest) -> ClassificationResult:
        result = await self._workflow.classify(request)
        await self._repository.save_classification(request, result)
        return result
