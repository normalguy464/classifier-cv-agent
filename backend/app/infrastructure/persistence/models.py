from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TypeAlias

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Numeric,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

EMBEDDING_DIMENSION: int = 768
JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]


class Base(DeclarativeBase):
    pass


class ClassificationRunRow(Base):
    __tablename__ = "classification_runs"
    __table_args__ = (
        CheckConstraint(
            "proposed_decision IN ('pass', 'waitlist', 'reject', 'needs_review')",
            name="ck_classification_runs_proposed_decision",
        ),
        CheckConstraint(
            "final_score IS NULL OR (final_score >= 0 AND final_score <= 100)",
            name="ck_classification_runs_final_score",
        ),
        Index("ix_classification_runs_cv_profile_id", "cv_profile_id"),
        Index("ix_classification_runs_job_profile_id", "job_profile_id"),
    )

    classification_result_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    request_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    cv_profile_id: Mapped[str] = mapped_column(String(64), nullable=False)
    job_profile_id: Mapped[str] = mapped_column(String(64), nullable=False)
    proposed_decision: Mapped[str] = mapped_column(String(32), nullable=False)
    final_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    request_snapshot: Mapped[JsonObject] = mapped_column(JSONB, nullable=False)
    result_snapshot: Mapped[JsonObject] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    persisted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )


class EvidenceEmbeddingRow(Base):
    __tablename__ = "evidence_embeddings"
    __table_args__ = (
        UniqueConstraint(
            "classification_result_id",
            "evidence_id",
            "model_version",
            name="uq_evidence_embeddings_result_evidence_model",
        ),
        Index("ix_evidence_embeddings_classification_result_id", "classification_result_id"),
    )

    evidence_embedding_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(),
        primary_key=True,
    )
    classification_result_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("classification_runs.classification_result_id"),
        nullable=False,
    )
    evidence_id: Mapped[str] = mapped_column(String(64), nullable=False)
    section: Mapped[str] = mapped_column(String(32), nullable=False)
    model_version: Mapped[str] = mapped_column(String(128), nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIMENSION), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )


class ApprovedDecisionRow(Base):
    __tablename__ = "approved_decisions"
    __table_args__ = (
        CheckConstraint(
            "approval_status IN ('approved', 'overridden')",
            name="ck_approved_decisions_approval_status",
        ),
        CheckConstraint(
            "proposed_decision IN ('pass', 'waitlist', 'reject', 'needs_review')",
            name="ck_approved_decisions_proposed_decision",
        ),
        CheckConstraint(
            "final_decision IN ('pass', 'waitlist', 'reject')",
            name="ck_approved_decisions_final_decision",
        ),
        Index(
            "ix_approved_decisions_classification_result_id",
            "classification_result_id",
        ),
    )

    approved_decision_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    classification_result_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("classification_runs.classification_result_id"),
        nullable=False,
    )
    approval_status: Mapped[str] = mapped_column(String(16), nullable=False)
    proposed_decision: Mapped[str] = mapped_column(String(32), nullable=False)
    final_decision: Mapped[str] = mapped_column(String(16), nullable=False)
    reviewer_reference: Mapped[str] = mapped_column(String(64), nullable=False)
    decision_snapshot: Mapped[JsonObject] = mapped_column(JSONB, nullable=False)
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    persisted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )


class DecisionAuditEventRow(Base):
    __tablename__ = "decision_audit_events"
    __table_args__ = (
        CheckConstraint(
            "event_type IN ('approved', 'overridden')",
            name="ck_decision_audit_events_event_type",
        ),
        Index(
            "ix_decision_audit_events_classification_result_id",
            "classification_result_id",
        ),
    )

    audit_event_id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    classification_result_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("classification_runs.classification_result_id"),
        nullable=False,
    )
    approved_decision_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("approved_decisions.approved_decision_id"),
        nullable=False,
        unique=True,
    )
    event_type: Mapped[str] = mapped_column(String(16), nullable=False)
    event_snapshot: Mapped[JsonObject] = mapped_column(JSONB, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
