"""add phase7 anomaly and prediction tables

Revision ID: 007_add_phase7_anomaly_prediction_tables
Revises: 006_add_pattern_discovery_tables
Create Date: 2026-09-23 19:34:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "007_add_phase7_anomaly_prediction_tables"
down_revision: Union[str, None] = "006_add_pattern_discovery_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create anomaly_detection_runs table
    op.create_table(
        "anomaly_detection_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("processed_dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("processed_checksum", sa.String(length=64), nullable=True),
        sa.Column("method", sa.String(length=50), nullable=False, server_default="UNIVARIATE_COMBINED"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="PENDING"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("total_observations", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("anomaly_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("anomaly_percentage", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("results_truncated", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("method_summary", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["dataset_id"], ["datasets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["processed_dataset_id"], ["datasets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["profile_id"], ["dataset_profiles.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_anomaly_detection_runs_dataset_id"), "anomaly_detection_runs", ["dataset_id"], unique=False)
    op.create_index(op.f("ix_anomaly_detection_runs_processed_dataset_id"), "anomaly_detection_runs", ["processed_dataset_id"], unique=False)

    # 2. Create anomaly_results table
    op.create_table(
        "anomaly_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("processed_dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("observation_reference", sa.String(length=100), nullable=False),
        sa.Column("column_name", sa.String(length=100), nullable=False),
        sa.Column("value", sa.Float(), nullable=True),
        sa.Column("expected_range", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("anomaly_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("severity", sa.String(length=20), nullable=False, server_default="NORMAL"),
        sa.Column("methods_detected", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("evidence", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("statistics", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["anomaly_detection_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["dataset_id"], ["datasets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["processed_dataset_id"], ["datasets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_anomaly_results_run_id"), "anomaly_results", ["run_id"], unique=False)
    op.create_index(op.f("ix_anomaly_results_dataset_id"), "anomaly_results", ["dataset_id"], unique=False)
    op.create_index(op.f("ix_anomaly_results_processed_dataset_id"), "anomaly_results", ["processed_dataset_id"], unique=False)
    op.create_index(op.f("ix_anomaly_results_observation_reference"), "anomaly_results", ["observation_reference"], unique=False)
    op.create_index(op.f("ix_anomaly_results_column_name"), "anomaly_results", ["column_name"], unique=False)
    op.create_index(op.f("ix_anomaly_results_anomaly_score"), "anomaly_results", ["anomaly_score"], unique=False)
    op.create_index(op.f("ix_anomaly_results_severity"), "anomaly_results", ["severity"], unique=False)

    # 3. Create prediction_runs table
    op.create_table(
        "prediction_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("processed_dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("processed_checksum", sa.String(length=64), nullable=True),
        sa.Column("problem_type", sa.String(length=50), nullable=False),
        sa.Column("target_column", sa.String(length=100), nullable=False),
        sa.Column("model_name", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="PENDING"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("training_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("validation_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("test_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("feature_columns", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("metrics", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("baseline_metrics", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("model_parameters", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("random_state", sa.Integer(), nullable=False, server_default="42"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["dataset_id"], ["datasets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["processed_dataset_id"], ["datasets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["profile_id"], ["dataset_profiles.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_prediction_runs_dataset_id"), "prediction_runs", ["dataset_id"], unique=False)
    op.create_index(op.f("ix_prediction_runs_processed_dataset_id"), "prediction_runs", ["processed_dataset_id"], unique=False)
    op.create_index(op.f("ix_prediction_runs_problem_type"), "prediction_runs", ["problem_type"], unique=False)
    op.create_index(op.f("ix_prediction_runs_target_column"), "prediction_runs", ["target_column"], unique=False)

    # 4. Create prediction_results table
    op.create_table(
        "prediction_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("observation_reference", sa.String(length=100), nullable=False),
        sa.Column("actual_value", sa.String(length=255), nullable=True),
        sa.Column("predicted_value", sa.String(length=255), nullable=True),
        sa.Column("prediction_error", sa.Float(), nullable=True),
        sa.Column("lower_bound", sa.Float(), nullable=True),
        sa.Column("upper_bound", sa.Float(), nullable=True),
        sa.Column("split", sa.String(length=20), nullable=False, server_default="TEST"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["prediction_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_prediction_results_run_id"), "prediction_results", ["run_id"], unique=False)
    op.create_index(op.f("ix_prediction_results_observation_reference"), "prediction_results", ["observation_reference"], unique=False)
    op.create_index(op.f("ix_prediction_results_split"), "prediction_results", ["split"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_prediction_results_split"), table_name="prediction_results")
    op.drop_index(op.f("ix_prediction_results_observation_reference"), table_name="prediction_results")
    op.drop_index(op.f("ix_prediction_results_run_id"), table_name="prediction_results")
    op.drop_table("prediction_results")

    op.drop_index(op.f("ix_prediction_runs_target_column"), table_name="prediction_runs")
    op.drop_index(op.f("ix_prediction_runs_problem_type"), table_name="prediction_runs")
    op.drop_index(op.f("ix_prediction_runs_processed_dataset_id"), table_name="prediction_runs")
    op.drop_index(op.f("ix_prediction_runs_dataset_id"), table_name="prediction_runs")
    op.drop_table("prediction_runs")

    op.drop_index(op.f("ix_anomaly_results_severity"), table_name="anomaly_results")
    op.drop_index(op.f("ix_anomaly_results_anomaly_score"), table_name="anomaly_results")
    op.drop_index(op.f("ix_anomaly_results_column_name"), table_name="anomaly_results")
    op.drop_index(op.f("ix_anomaly_results_observation_reference"), table_name="anomaly_results")
    op.drop_index(op.f("ix_anomaly_results_processed_dataset_id"), table_name="anomaly_results")
    op.drop_index(op.f("ix_anomaly_results_dataset_id"), table_name="anomaly_results")
    op.drop_index(op.f("ix_anomaly_results_run_id"), table_name="anomaly_results")
    op.drop_table("anomaly_results")

    op.drop_index(op.f("ix_anomaly_detection_runs_processed_dataset_id"), table_name="anomaly_detection_runs")
    op.drop_index(op.f("ix_anomaly_detection_runs_dataset_id"), table_name="anomaly_detection_runs")
    op.drop_table("anomaly_detection_runs")
