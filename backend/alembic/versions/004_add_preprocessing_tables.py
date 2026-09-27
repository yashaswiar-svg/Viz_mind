"""add preprocessing tables

Revision ID: 004_add_preprocessing_tables
Revises: 003_add_profiling_tables
Create Date: 2026-09-22 22:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "004_add_preprocessing_tables"
down_revision: Union[str, None] = "003_add_profiling_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add columns to datasets
    op.add_column(
        "datasets",
        sa.Column("parent_dataset_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "datasets",
        sa.Column("dataset_kind", sa.String(length=50), nullable=False, server_default="SOURCE"),
    )
    op.create_foreign_key(
        "fk_datasets_parent_dataset_id",
        "datasets",
        "datasets",
        ["parent_dataset_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # Create preprocessing_jobs table
    op.create_table(
        "preprocessing_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_profile_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("output_dataset_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="PENDING"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rows_before", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rows_after", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("columns_before", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("columns_after", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("missing_cells_before", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("missing_cells_after", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("duplicate_rows_before", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("duplicate_rows_after", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("source_checksum_before", sa.String(length=64), nullable=True),
        sa.Column("source_checksum_after", sa.String(length=64), nullable=True),
        sa.Column("processed_checksum", sa.String(length=64), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["dataset_id"], ["datasets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_profile_id"], ["dataset_profiles.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["output_dataset_id"], ["datasets.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_preprocessing_jobs_dataset_id"), "preprocessing_jobs", ["dataset_id"], unique=False)

    # Create preprocessing_transformations table
    op.create_table(
        "preprocessing_transformations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("step_order", sa.Integer(), nullable=False),
        sa.Column("transformation_type", sa.String(length=100), nullable=False),
        sa.Column("column_name", sa.String(length=255), nullable=True),
        sa.Column("parameters", sa.JSON(), nullable=True),
        sa.Column("rows_affected", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("values_affected", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["preprocessing_jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_preprocessing_transformations_job_id"),
        "preprocessing_transformations",
        ["job_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_preprocessing_transformations_job_id"), table_name="preprocessing_transformations")
    op.drop_table("preprocessing_transformations")

    op.drop_index(op.f("ix_preprocessing_jobs_dataset_id"), table_name="preprocessing_jobs")
    op.drop_table("preprocessing_jobs")

    op.drop_constraint("fk_datasets_parent_dataset_id", "datasets", type_="foreignkey")
    op.drop_column("datasets", "dataset_kind")
    op.drop_column("datasets", "parent_dataset_id")
