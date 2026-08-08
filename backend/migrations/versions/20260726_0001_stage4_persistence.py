from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision: str = "20260726_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "classification_runs",
        sa.Column("classification_result_id", sa.String(length=64), nullable=False),
        sa.Column("request_id", sa.String(length=64), nullable=False),
        sa.Column("cv_profile_id", sa.String(length=64), nullable=False),
        sa.Column("job_profile_id", sa.String(length=64), nullable=False),
        sa.Column("proposed_decision", sa.String(length=32), nullable=False),
        sa.Column("final_score", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column(
            "request_snapshot",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "result_snapshot",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "persisted_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "final_score IS NULL OR (final_score >= 0 AND final_score <= 100)",
            name="ck_classification_runs_final_score",
        ),
        sa.CheckConstraint(
            "proposed_decision IN ('pass', 'waitlist', 'reject', 'needs_review')",
            name="ck_classification_runs_proposed_decision",
        ),
        sa.PrimaryKeyConstraint("classification_result_id"),
        sa.UniqueConstraint("request_id", name="uq_classification_runs_request_id"),
    )
    op.create_index(
        "ix_classification_runs_cv_profile_id",
        "classification_runs",
        ["cv_profile_id"],
        unique=False,
    )
    op.create_index(
        "ix_classification_runs_job_profile_id",
        "classification_runs",
        ["job_profile_id"],
        unique=False,
    )
    op.create_table(
        "evidence_embeddings",
        sa.Column(
            "evidence_embedding_id",
            sa.BigInteger(),
            sa.Identity(always=False),
            nullable=False,
        ),
        sa.Column("classification_result_id", sa.String(length=64), nullable=False),
        sa.Column("evidence_id", sa.String(length=64), nullable=False),
        sa.Column("section", sa.String(length=32), nullable=False),
        sa.Column("model_version", sa.String(length=128), nullable=False),
        sa.Column("embedding", Vector(dim=768), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["classification_result_id"],
            ["classification_runs.classification_result_id"],
        ),
        sa.PrimaryKeyConstraint("evidence_embedding_id"),
        sa.UniqueConstraint(
            "classification_result_id",
            "evidence_id",
            "model_version",
            name="uq_evidence_embeddings_result_evidence_model",
        ),
    )
    op.create_index(
        "ix_evidence_embeddings_classification_result_id",
        "evidence_embeddings",
        ["classification_result_id"],
        unique=False,
    )
    op.create_table(
        "approved_decisions",
        sa.Column("approved_decision_id", sa.String(length=64), nullable=False),
        sa.Column("classification_result_id", sa.String(length=64), nullable=False),
        sa.Column("approval_status", sa.String(length=16), nullable=False),
        sa.Column("proposed_decision", sa.String(length=32), nullable=False),
        sa.Column("final_decision", sa.String(length=16), nullable=False),
        sa.Column("reviewer_reference", sa.String(length=64), nullable=False),
        sa.Column(
            "decision_snapshot",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "persisted_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "approval_status IN ('approved', 'overridden')",
            name="ck_approved_decisions_approval_status",
        ),
        sa.CheckConstraint(
            "final_decision IN ('pass', 'waitlist', 'reject')",
            name="ck_approved_decisions_final_decision",
        ),
        sa.CheckConstraint(
            "proposed_decision IN ('pass', 'waitlist', 'reject', 'needs_review')",
            name="ck_approved_decisions_proposed_decision",
        ),
        sa.ForeignKeyConstraint(
            ["classification_result_id"],
            ["classification_runs.classification_result_id"],
        ),
        sa.PrimaryKeyConstraint("approved_decision_id"),
    )
    op.create_index(
        "ix_approved_decisions_classification_result_id",
        "approved_decisions",
        ["classification_result_id"],
        unique=False,
    )
    op.create_table(
        "decision_audit_events",
        sa.Column(
            "audit_event_id",
            sa.BigInteger(),
            sa.Identity(always=False),
            nullable=False,
        ),
        sa.Column("classification_result_id", sa.String(length=64), nullable=False),
        sa.Column("approved_decision_id", sa.String(length=64), nullable=False),
        sa.Column("event_type", sa.String(length=16), nullable=False),
        sa.Column(
            "event_snapshot",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "event_type IN ('approved', 'overridden')",
            name="ck_decision_audit_events_event_type",
        ),
        sa.ForeignKeyConstraint(
            ["approved_decision_id"],
            ["approved_decisions.approved_decision_id"],
        ),
        sa.ForeignKeyConstraint(
            ["classification_result_id"],
            ["classification_runs.classification_result_id"],
        ),
        sa.PrimaryKeyConstraint("audit_event_id"),
        sa.UniqueConstraint(
            "approved_decision_id",
            name="uq_decision_audit_events_approved_decision_id",
        ),
    )
    op.create_index(
        "ix_decision_audit_events_classification_result_id",
        "decision_audit_events",
        ["classification_result_id"],
        unique=False,
    )
    op.execute(
        """
        CREATE FUNCTION prevent_classifier_record_mutation()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            RAISE EXCEPTION 'classifier persistence records are append-only';
        END;
        $$
        """
    )
    for table_name in (
        "classification_runs",
        "approved_decisions",
        "decision_audit_events",
    ):
        op.execute(
            f"""
            CREATE TRIGGER trg_{table_name}_append_only
            BEFORE UPDATE OR DELETE ON {table_name}
            FOR EACH ROW
            EXECUTE FUNCTION prevent_classifier_record_mutation()
            """
        )


def downgrade() -> None:
    op.drop_index(
        "ix_decision_audit_events_classification_result_id",
        table_name="decision_audit_events",
    )
    op.drop_table("decision_audit_events")
    op.drop_index(
        "ix_approved_decisions_classification_result_id",
        table_name="approved_decisions",
    )
    op.drop_table("approved_decisions")
    op.drop_index(
        "ix_evidence_embeddings_classification_result_id",
        table_name="evidence_embeddings",
    )
    op.drop_table("evidence_embeddings")
    op.drop_index(
        "ix_classification_runs_job_profile_id",
        table_name="classification_runs",
    )
    op.drop_index(
        "ix_classification_runs_cv_profile_id",
        table_name="classification_runs",
    )
    op.drop_table("classification_runs")
    op.execute("DROP FUNCTION prevent_classifier_record_mutation()")
    op.execute("DROP EXTENSION IF EXISTS vector")
