from __future__ import annotations

from datetime import datetime
from typing import Protocol

from backend.app.contracts import (
    ApprovedDecision,
    ClassificationRequest,
    ClassificationResult,
)


class ClassifierWorkflow(Protocol):
    async def classify(self, request: ClassificationRequest) -> ClassificationResult: ...


class ClassificationRepository(Protocol):
    async def save_classification(
        self,
        request: ClassificationRequest,
        result: ClassificationResult,
    ) -> None: ...

    async def get_classification_result(
        self,
        classification_result_id: str,
    ) -> ClassificationResult | None: ...

    async def save_approved_decision(self, decision: ApprovedDecision) -> None: ...

    async def list_approved_decisions(
        self,
        classification_result_id: str,
    ) -> tuple[ApprovedDecision, ...]: ...


class IdentifierGenerator(Protocol):
    def new_identifier(self, prefix: str) -> str: ...


class Clock(Protocol):
    def now(self) -> datetime: ...
