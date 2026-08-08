from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from typing import Protocol, cast

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from backend.app.contracts import (
    ApprovedDecision,
    ClassificationRequest,
    ClassificationResult,
    EvidenceSection,
)
from backend.app.infrastructure.persistence.models import (
    EMBEDDING_DIMENSION,
    ApprovedDecisionRow,
    ClassificationRunRow,
    DecisionAuditEventRow,
    EvidenceEmbeddingRow,
    JsonObject,
)
from backend.app.infrastructure.persistence.session import AsyncSessionFactory


class PersistenceConflictError(Exception):
    pass


class PersistenceInvariantError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class DecisionAuditEvent:
    audit_event_id: int
    classification_result_id: str
    approved_decision_id: str
    event_type: str
    event_snapshot: JsonObject
    occurred_at: datetime


class ClassificationRunRepository(Protocol):
    async def save_classification(
        self,
        request: ClassificationRequest,
        result: ClassificationResult,
    ) -> None: ...

    async def get_classification_request(
        self,
        classification_result_id: str,
    ) -> ClassificationRequest | None: ...

    async def get_classification_result(
        self,
        classification_result_id: str,
    ) -> ClassificationResult | None: ...


class ApprovedDecisionRepository(Protocol):
    async def save_approved_decision(self, decision: ApprovedDecision) -> None: ...

    async def get_approved_decision(
        self,
        classification_result_id: str,
    ) -> ApprovedDecision | None: ...

    async def list_approved_decisions(
        self,
        classification_result_id: str,
    ) -> tuple[ApprovedDecision, ...]: ...

    async def list_decision_audit_events(
        self,
        classification_result_id: str,
    ) -> tuple[DecisionAuditEvent, ...]: ...


class EvidenceEmbeddingRepository(Protocol):
    async def save_evidence_embedding(
        self,
        classification_result_id: str,
        evidence_id: str,
        section: EvidenceSection,
        model_version: str,
        embedding: tuple[float, ...],
    ) -> None: ...


class SqlAlchemyClassifierRepository:
    def __init__(self, session_factory: AsyncSessionFactory) -> None:
        self._session_factory = session_factory

    async def save_classification(
        self,
        request: ClassificationRequest,
        result: ClassificationResult,
    ) -> None:
        self._validate_classification_links(request, result)
        row = ClassificationRunRow(
            classification_result_id=result.classification_result_id,
            request_id=request.request_id,
            cv_profile_id=request.cv_profile.cv_profile_id,
            job_profile_id=request.job_profile.job_profile_id,
            proposed_decision=result.proposed_decision.value,
            final_score=result.scores.final_score,
            request_snapshot=self._snapshot(request),
            result_snapshot=self._snapshot(result),
            created_at=result.created_at,
        )
        try:
            async with self._session_factory() as session, session.begin():
                session.add(row)
        except IntegrityError as error:
            raise PersistenceConflictError("classification snapshot already exists") from error

    async def get_classification_request(
        self,
        classification_result_id: str,
    ) -> ClassificationRequest | None:
        async with self._session_factory() as session:
            row = await session.get(ClassificationRunRow, classification_result_id)
            if row is None:
                return None
            return ClassificationRequest.model_validate(row.request_snapshot)

    async def get_classification_result(
        self,
        classification_result_id: str,
    ) -> ClassificationResult | None:
        async with self._session_factory() as session:
            row = await session.get(ClassificationRunRow, classification_result_id)
            if row is None:
                return None
            return ClassificationResult.model_validate(row.result_snapshot)

    async def save_approved_decision(self, decision: ApprovedDecision) -> None:
        snapshot = self._snapshot(decision)
        try:
            async with self._session_factory() as session, session.begin():
                run = await session.get(
                    ClassificationRunRow,
                    decision.classification_result_id,
                )
                if run is None:
                    raise PersistenceInvariantError(
                        "approved decision must reference a persisted classification"
                    )
                if run.proposed_decision != decision.proposed_decision.value:
                    raise PersistenceInvariantError(
                        "approved decision must preserve the persisted proposed decision"
                    )
                decision_row = ApprovedDecisionRow(
                    approved_decision_id=decision.approved_decision_id,
                    classification_result_id=decision.classification_result_id,
                    approval_status=decision.approval_status.value,
                    proposed_decision=decision.proposed_decision.value,
                    final_decision=decision.final_decision.value,
                    reviewer_reference=decision.reviewer_reference,
                    decision_snapshot=snapshot,
                    decided_at=decision.decided_at,
                )
                session.add(decision_row)
                await session.flush()
                session.add(
                    DecisionAuditEventRow(
                        classification_result_id=decision.classification_result_id,
                        approved_decision_id=decision.approved_decision_id,
                        event_type=decision.approval_status.value,
                        event_snapshot=snapshot,
                        occurred_at=decision.decided_at,
                    )
                )
        except IntegrityError as error:
            raise PersistenceConflictError(
                "approved decision or audit event already exists"
            ) from error

    async def get_approved_decision(
        self,
        classification_result_id: str,
    ) -> ApprovedDecision | None:
        statement = (
            select(ApprovedDecisionRow)
            .where(ApprovedDecisionRow.classification_result_id == classification_result_id)
            .order_by(
                ApprovedDecisionRow.decided_at.desc(),
                ApprovedDecisionRow.approved_decision_id.desc(),
            )
            .limit(1)
        )
        async with self._session_factory() as session:
            row = await session.scalar(statement)
            if row is None:
                return None
            return ApprovedDecision.model_validate(row.decision_snapshot)

    async def list_approved_decisions(
        self,
        classification_result_id: str,
    ) -> tuple[ApprovedDecision, ...]:
        statement = (
            select(ApprovedDecisionRow)
            .where(ApprovedDecisionRow.classification_result_id == classification_result_id)
            .order_by(
                ApprovedDecisionRow.decided_at,
                ApprovedDecisionRow.approved_decision_id,
            )
        )
        async with self._session_factory() as session:
            rows = tuple((await session.scalars(statement)).all())
        return tuple(ApprovedDecision.model_validate(row.decision_snapshot) for row in rows)

    async def list_decision_audit_events(
        self,
        classification_result_id: str,
    ) -> tuple[DecisionAuditEvent, ...]:
        statement = (
            select(DecisionAuditEventRow)
            .where(DecisionAuditEventRow.classification_result_id == classification_result_id)
            .order_by(DecisionAuditEventRow.audit_event_id)
        )
        async with self._session_factory() as session:
            rows = tuple((await session.scalars(statement)).all())
        return tuple(
            DecisionAuditEvent(
                audit_event_id=row.audit_event_id,
                classification_result_id=row.classification_result_id,
                approved_decision_id=row.approved_decision_id,
                event_type=row.event_type,
                event_snapshot=row.event_snapshot,
                occurred_at=row.occurred_at,
            )
            for row in rows
        )

    async def save_evidence_embedding(
        self,
        classification_result_id: str,
        evidence_id: str,
        section: EvidenceSection,
        model_version: str,
        embedding: tuple[float, ...],
    ) -> None:
        if len(embedding) != EMBEDDING_DIMENSION:
            raise PersistenceInvariantError(
                f"embedding must contain exactly {EMBEDDING_DIMENSION} values"
            )
        if not all(isfinite(value) for value in embedding):
            raise PersistenceInvariantError("embedding values must be finite")
        row = EvidenceEmbeddingRow(
            classification_result_id=classification_result_id,
            evidence_id=evidence_id,
            section=section.value,
            model_version=model_version,
            embedding=list(embedding),
        )
        try:
            async with self._session_factory() as session, session.begin():
                session.add(row)
        except IntegrityError as error:
            raise PersistenceConflictError("evidence embedding could not be persisted") from error

    @staticmethod
    def _snapshot(
        contract: ClassificationRequest | ClassificationResult | ApprovedDecision,
    ) -> JsonObject:
        return cast(JsonObject, contract.model_dump(mode="json"))

    @staticmethod
    def _validate_classification_links(
        request: ClassificationRequest,
        result: ClassificationResult,
    ) -> None:
        expected_links = (
            (result.request_id, request.request_id, "request"),
            (result.cv_profile_id, request.cv_profile.cv_profile_id, "CV profile"),
            (result.job_profile_id, request.job_profile.job_profile_id, "job profile"),
            (
                result.versions.rubric_version,
                request.rubric.rubric_version,
                "rubric version",
            ),
            (
                result.versions.job_profile_artifact_version,
                request.configuration.job_profile_artifact_version,
                "job profile artifact version",
            ),
            (
                result.versions.configuration_version,
                request.configuration.configuration_version,
                "configuration version",
            ),
            (
                result.versions.l1_rules_configuration_version,
                request.configuration.l1_rules_configuration_version,
                "L1 rules configuration version",
            ),
            (
                result.versions.models_configuration_version,
                request.configuration.models_configuration_version,
                "models configuration version",
            ),
            (
                result.versions.embedding_model_identifier,
                request.configuration.models.embedding_model_identifier,
                "embedding model identifier",
            ),
            (
                result.versions.embedding_model_version,
                request.configuration.models.embedding_model_version,
                "embedding model version",
            ),
            (
                result.versions.llm_provider_identifier,
                request.configuration.models.llm_provider_identifier,
                "LLM provider identifier",
            ),
            (
                result.versions.llm_model_identifier,
                request.configuration.models.llm_model_identifier,
                "LLM model identifier",
            ),
            (
                result.versions.prompt_version,
                request.configuration.models.prompt_version,
                "prompt version",
            ),
        )
        for actual, expected, label in expected_links:
            if actual != expected:
                raise PersistenceInvariantError(
                    f"classification result {label} does not match its request"
                )
