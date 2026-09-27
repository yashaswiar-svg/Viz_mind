"""add phase8 insight tables

Revision ID: 008_add_phase8_insight_tables
Revises: 007_add_phase7_anomaly_prediction_tables
Create Date: 2026-09-23 23:20:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "008_add_phase8_insight_tables"
down_revision: Union[str, None] = "007_add_phase7_anomaly_prediction_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create insight_runs table
    op.create_table(
        "insight_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("processed_dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("processed_checksum", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="RUNNING"),
        sa.Column("provider", sa.String(length=50), nullable=False, server_default="mock"),
        sa.Column("model", sa.String(length=100), nullable=True),
        sa.Column("fallback_used", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("evidence_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("candidate_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("insight_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["dataset_id"], ["datasets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["processed_dataset_id"], ["datasets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["profile_id"], ["dataset_profiles.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_insight_runs_dataset_id"), "insight_runs", ["dataset_id"], unique=False)
    op.create_index(op.f("ix_insight_runs_processed_dataset_id"), "insight_runs", ["processed_dataset_id"], unique=False)
    op.create_index(op.f("ix_insight_runs_status"), "insight_runs", ["status"], unique=False)

    # 2. Create insights table
    op.create_table(
        "insights",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("processed_dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("insight_type", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("importance_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("importance_level", sa.String(length=20), nullable=False, server_default="MEDIUM"),
        sa.Column("evidence_strength", sa.String(length=20), nullable=False, server_default="MODERATE"),
        sa.Column("columns", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("statistics", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("limitations", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("generation_mode", sa.String(length=50), nullable=False, server_default="LLM"),
        sa.Column("validation_status", sa.String(length=50), nullable=False, server_default="VALIDATED"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["insight_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["dataset_id"], ["datasets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["processed_dataset_id"], ["datasets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_insights_run_id"), "insights", ["run_id"], unique=False)
    op.create_index(op.f("ix_insights_dataset_id"), "insights", ["dataset_id"], unique=False)
    op.create_index(op.f("ix_insights_processed_dataset_id"), "insights", ["processed_dataset_id"], unique=False)
    op.create_index(op.f("ix_insights_insight_type"), "insights", ["insight_type"], unique=False)
    op.create_index(op.f("ix_insights_importance_score"), "insights", ["importance_score"], unique=False)
    op.create_index(op.f("ix_insights_importance_level"), "insights", ["importance_level"], unique=False)

    # 3. Create insight_evidences table
    op.create_table(
        "insight_evidences",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("insight_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("evidence_id", sa.String(length=50), nullable=False),
        sa.Column("source_phase", sa.String(length=50), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("source_id", sa.String(length=100), nullable=True),
        sa.Column("metrics", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["insight_id"], ["insights.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_insight_evidences_insight_id"), "insight_evidences", ["insight_id"], unique=False)
    op.create_index(op.f("ix_insight_evidences_evidence_id"), "insight_evidences", ["evidence_id"], unique=False)
    op.create_index(op.f("ix_insight_evidences_source_phase"), "insight_evidences", ["source_phase"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_insight_evidences_source_phase"), table_name="insight_evidences")
    op.drop_index(op.f("ix_insight_evidences_evidence_id"), table_name="insight_evidences")
    op.drop_index(op.f("ix_insight_evidences_insight_id"), table_name="insight_evidences")
    op.drop_table("insight_evidences")

    op.drop_index(op.f("ix_insights_importance_level"), table_name="insights")
    op.drop_index(op.f("ix_insights_importance_score"), table_name="insights")
    op.drop_index(op.f("ix_insights_insight_type"), table_name="insights")
    op.drop_index(op.f("ix_insights_processed_dataset_id"), table_name="insights")
    op.drop_index(op.f("ix_insights_dataset_id"), table_name="insights")
    op.drop_index(op.f("ix_insights_run_id"), table_name="insights")
    op.drop_table("insights")

    op.drop_index(op.f("ix_insight_runs_status"), table_name="insight_runs")
    op.drop_index(op.f("ix_insight_runs_processed_dataset_id"), table_name="insight_runs")
    op.drop_index(op.f("ix_insight_runs_dataset_id"), table_name="insight_runs")
    op.drop_table("insight_runs")
