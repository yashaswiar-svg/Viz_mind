"""add profiling tables

Revision ID: 003_add_profiling_tables
Revises: 002_add_checksum_to_datasets
Create Date: 2026-09-22 21:07:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "003_add_profiling_tables"
down_revision: Union[str, None] = "002_add_checksum_to_datasets"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dataset_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("row_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("column_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("duplicate_row_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("duplicate_row_percentage", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("missing_cell_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("missing_cell_percentage", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("memory_usage_bytes", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("sheet_name", sa.String(length=255), nullable=True),
        sa.Column("quality_score", sa.Float(), nullable=False, server_default="100.0"),
        sa.Column("quality_level", sa.String(length=50), nullable=False, server_default="Excellent"),
        sa.Column("quality_issues", sa.JSON(), nullable=True),
        sa.Column("profiled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["dataset_id"], ["datasets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("dataset_id"),
    )
    op.create_index(op.f("ix_dataset_profiles_dataset_id"), "dataset_profiles", ["dataset_id"], unique=True)

    op.create_table(
        "dataset_column_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("column_name", sa.String(length=255), nullable=False),
        sa.Column("column_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("inferred_type", sa.String(length=50), nullable=False),
        sa.Column("pandas_dtype", sa.String(length=50), nullable=False),
        sa.Column("null_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("null_percentage", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("non_null_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("unique_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("unique_percentage", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("is_constant", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("min_value", sa.Float(), nullable=True),
        sa.Column("max_value", sa.Float(), nullable=True),
        sa.Column("mean_value", sa.Float(), nullable=True),
        sa.Column("median_value", sa.Float(), nullable=True),
        sa.Column("std_value", sa.Float(), nullable=True),
        sa.Column("q1_value", sa.Float(), nullable=True),
        sa.Column("q3_value", sa.Float(), nullable=True),
        sa.Column("top_values", sa.JSON(), nullable=True),
        sa.Column("min_length", sa.Integer(), nullable=True),
        sa.Column("max_length", sa.Integer(), nullable=True),
        sa.Column("avg_length", sa.Float(), nullable=True),
        sa.Column("min_datetime", sa.String(length=100), nullable=True),
        sa.Column("max_datetime", sa.String(length=100), nullable=True),
        sa.Column("true_count", sa.Integer(), nullable=True),
        sa.Column("false_count", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["profile_id"], ["dataset_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_dataset_column_profiles_profile_id"), "dataset_column_profiles", ["profile_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_dataset_column_profiles_profile_id"), table_name="dataset_column_profiles")
    op.drop_table("dataset_column_profiles")
    op.drop_index(op.f("ix_dataset_profiles_dataset_id"), table_name="dataset_profiles")
    op.drop_table("dataset_profiles")
