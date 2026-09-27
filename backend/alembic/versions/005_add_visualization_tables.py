"""add visualization tables

Revision ID: 005_add_visualization_tables
Revises: 004_add_preprocessing_tables
Create Date: 2026-09-22 22:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "005_add_visualization_tables"
down_revision: Union[str, None] = "004_add_preprocessing_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create visualization_runs table
    op.create_table(
        "visualization_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("processed_dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("processed_checksum", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="PENDING"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("recommendation_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["dataset_id"], ["datasets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["processed_dataset_id"], ["datasets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["profile_id"], ["dataset_profiles.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_visualization_runs_dataset_id"), "visualization_runs", ["dataset_id"], unique=False)
    op.create_index(op.f("ix_visualization_runs_processed_dataset_id"), "visualization_runs", ["processed_dataset_id"], unique=False)

    # Create visualization_recommendations table
    op.create_table(
        "visualization_recommendations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("processed_dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("chart_type", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("x_column", sa.String(length=255), nullable=False),
        sa.Column("y_column", sa.String(length=255), nullable=True),
        sa.Column("aggregation", sa.String(length=50), nullable=True),
        sa.Column("score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("chart_spec", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["visualization_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["dataset_id"], ["datasets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["processed_dataset_id"], ["datasets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["profile_id"], ["dataset_profiles.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_visualization_recommendations_run_id"), "visualization_recommendations", ["run_id"], unique=False)
    op.create_index(op.f("ix_visualization_recommendations_dataset_id"), "visualization_recommendations", ["dataset_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_visualization_recommendations_dataset_id"), table_name="visualization_recommendations")
    op.drop_index(op.f("ix_visualization_recommendations_run_id"), table_name="visualization_recommendations")
    op.drop_table("visualization_recommendations")

    op.drop_index(op.f("ix_visualization_runs_processed_dataset_id"), table_name="visualization_runs")
    op.drop_index(op.f("ix_visualization_runs_dataset_id"), table_name="visualization_runs")
    op.drop_table("visualization_runs")
