"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-07-16
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False, server_default="viewer"),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table(
        "dashboard_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("real_estate_count", sa.Float(), nullable=False, server_default="0"),
        sa.Column("windpark_count", sa.Float(), nullable=False, server_default="0"),
        sa.Column("energy_production_kwh", sa.Float(), nullable=False, server_default="0"),
        sa.Column("income_total", sa.Float(), nullable=False, server_default="0"),
        sa.Column("expense_total", sa.Float(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_table("dashboard_snapshots")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_table("users")
