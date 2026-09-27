"""add pattern discovery tables

Revision ID: 006_add_pattern_discovery_tables
Revises: 005_add_visualization_tables
Create Date: 2026-09-23 13:20:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "006_add_pattern_discovery_tables"
down_revision: Union[str, None] = "005_add_visualization_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create pattern_discovery_runs table
    op.create_table(
        "pattern_discovery_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("processed_dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("processed_checksum", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="PENDING"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("pattern_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["dataset_id"], ["datasets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["processed_dataset_id"], ["datasets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["profile_id"], ["dataset_profiles.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pattern_discovery_runs_dataset_id"), "pattern_discovery_runs", ["dataset_id"], unique=False)
    op.create_index(op.f("ix_pattern_discovery_runs_processed_dataset_id"), "pattern_discovery_runs", ["processed_dataset_id"], unique=False)

    # Create pattern_results table
    op.create_table(
        "pattern_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("processed_dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("pattern_type", sa.String(length=50), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("columns", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("statistics", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("significant", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("strength", sa.String(length=20), nullable=False, server_default="WEAK"),
        sa.Column("sample_size", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("raw_p_value", sa.Float(), nullable=True),
        sa.Column("adjusted_p_value", sa.Float(), nullable=True),
        sa.Column("effect_size", sa.Float(), nullable=True),
        sa.Column("method", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["pattern_discovery_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["dataset_id"], ["datasets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["processed_dataset_id"], ["datasets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pattern_results_run_id"), "pattern_results", ["run_id"], unique=False)
    op.create_index(op.f("ix_pattern_results_dataset_id"), "pattern_results", ["dataset_id"], unique=False)
    op.create_index(op.f("ix_pattern_results_processed_dataset_id"), "pattern_results", ["processed_dataset_id"], unique=False)
    op.create_index(op.f("ix_pattern_results_pattern_type"), "pattern_results", ["pattern_type"], unique=False)
    op.create_index(op.f("ix_pattern_results_rank"), "pattern_results", ["rank"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_pattern_results_rank"), table_name="pattern_results")
    op.drop_index(op.f("ix_pattern_results_pattern_type"), table_name="pattern_results")
    op.drop_index(op.f("ix_pattern_results_processed_dataset_id"), table_name="pattern_results")
    op.drop_index(op.f("ix_pattern_results_dataset_id"), table_name="pattern_results")
    op.drop_index(op.f("ix_pattern_results_run_id"), table_name="pattern_results")
    op.drop_table("pattern_results")

    op.drop_index(op.f("ix_pattern_discovery_runs_processed_dataset_id"), table_name="pattern_discovery_runs")
    op.drop_index(op.f("ix_pattern_discovery_runs_dataset_id"), table_name="pattern_discovery_runs")
    op.drop_table("pattern_discovery_runs")
