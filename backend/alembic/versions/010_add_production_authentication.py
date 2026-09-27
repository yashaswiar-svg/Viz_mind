"""add production authentication and user dataset ownership

Revision ID: 010_add_production_authentication
Revises: 009_add_phase9_analyst_tables
Create Date: 2026-09-24 00:30:00.000000

"""
from typing import Sequence, Union
import uuid
from datetime import datetime, timezone
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "010_add_production_authentication"
down_revision: Union[str, None] = "009_add_phase9_analyst_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SYSTEM_USER_ID = "00000000-0000-0000-0000-000000000000"


def upgrade() -> None:
    # 1. Create users table
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False, server_default="VizMind User"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"])

    # 2. Insert system migration user for legacy datasets backfill
    now = datetime.now(timezone.utc)
    op.execute(
        f"""
        INSERT INTO users (id, email, password_hash, full_name, is_active, is_verified, created_at, updated_at)
        VALUES ('{SYSTEM_USER_ID}', 'system@vizmind.internal', 'SYSTEM_ACCOUNT_LOCKED', 'System Migration User', true, true, '{now.isoformat()}', '{now.isoformat()}')
        ON CONFLICT (email) DO NOTHING;
        """
    )

    # 3. Add user_id column to datasets
    op.add_column("datasets", sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True))

    # 4. Backfill legacy datasets with system user ID
    op.execute(f"UPDATE datasets SET user_id = '{SYSTEM_USER_ID}' WHERE user_id IS NULL;")

    # 5. Enforce NOT NULL on user_id
    op.alter_column("datasets", "user_id", nullable=False)

    # 6. Add index and foreign key
    op.create_index("ix_datasets_user_id", "datasets", ["user_id"])
    op.create_foreign_key("fk_datasets_user_id", "datasets", "users", ["user_id"], ["id"], ondelete="CASCADE")


def downgrade() -> None:
    op.drop_constraint("fk_datasets_user_id", "datasets", type_="foreignkey")
    op.drop_index("ix_datasets_user_id", table_name="datasets")
    op.drop_column("datasets", "user_id")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
