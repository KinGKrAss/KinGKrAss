"""add module tables

Revision ID: 0002_module_tables
Revises: 0001_initial
Create Date: 2026-07-16
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_module_tables"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # users – new columns
    op.add_column("users", sa.Column("email", sa.String(length=128), nullable=True))
    op.add_column("users", sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))

    # Electra
    op.create_table(
        "wind_farms",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("location", sa.String(length=256), nullable=False),
        sa.Column("capacity_kw", sa.Float(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_wind_farms_id", "wind_farms", ["id"])

    op.create_table(
        "energy_readings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("wind_farm_id", sa.Integer(), sa.ForeignKey("wind_farms.id"), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("production_kwh", sa.Float(), nullable=False),
        sa.Column("wind_speed_ms", sa.Float(), nullable=True),
    )
    op.create_index("ix_energy_readings_id", "energy_readings", ["id"])
    op.create_index("ix_energy_readings_timestamp", "energy_readings", ["timestamp"])

    op.create_table(
        "electricity_contracts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("wind_farm_id", sa.Integer(), sa.ForeignKey("wind_farms.id"), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("counterparty", sa.String(length=128), nullable=False),
        sa.Column("price_per_kwh", sa.Float(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
    )
    op.create_index("ix_electricity_contracts_id", "electricity_contracts", ["id"])

    # Gaia
    op.create_table(
        "properties",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("address", sa.String(length=256), nullable=False),
        sa.Column("city", sa.String(length=64), nullable=False),
        sa.Column("property_type", sa.String(length=32), nullable=False),
        sa.Column("area_sqm", sa.Float(), nullable=False),
        sa.Column("purchase_price", sa.Float(), nullable=True),
        sa.Column("monthly_rent", sa.Float(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="available"),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_properties_id", "properties", ["id"])

    op.create_table(
        "tenants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("property_id", sa.Integer(), sa.ForeignKey("properties.id"), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("email", sa.String(length=128), nullable=True),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("lease_start", sa.Date(), nullable=False),
        sa.Column("lease_end", sa.Date(), nullable=True),
        sa.Column("monthly_rent", sa.Float(), nullable=False),
    )
    op.create_index("ix_tenants_id", "tenants", ["id"])

    op.create_table(
        "maintenance_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("property_id", sa.Integer(), sa.ForeignKey("properties.id"), nullable=False),
        sa.Column("title", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="open"),
        sa.Column("priority", sa.String(length=16), nullable=False, server_default="medium"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_maintenance_requests_id", "maintenance_requests", ["id"])

    # Fortuna
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("category_type", sa.String(length=16), nullable=False),
        sa.Column("color", sa.String(length=16), nullable=True),
    )
    op.create_index("ix_categories_id", "categories", ["id"])

    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("transaction_date", sa.Date(), nullable=False),
        sa.Column("description", sa.String(length=256), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("transaction_type", sa.String(length=16), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id"), nullable=True),
        sa.Column("reference", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_transactions_id", "transactions", ["id"])
    op.create_index("ix_transactions_date", "transactions", ["transaction_date"])

    # Themis
    op.create_table(
        "legal_contracts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("counterparty", sa.String(length=128), nullable=False),
        sa.Column("contract_type", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("value", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_legal_contracts_id", "legal_contracts", ["id"])

    op.create_table(
        "contract_deadlines",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("contract_id", sa.Integer(), sa.ForeignKey("legal_contracts.id"), nullable=False),
        sa.Column("title", sa.String(length=128), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
    )
    op.create_index("ix_contract_deadlines_id", "contract_deadlines", ["id"])
    op.create_index("ix_contract_deadlines_due_date", "contract_deadlines", ["due_date"])

    # Diplomatia
    op.create_table(
        "diplomatic_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("language", sa.String(length=8), nullable=False),
        sa.Column("document_type", sa.String(length=64), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("tags", sa.String(length=256), nullable=True),
        sa.Column("is_archived", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_diplomatic_documents_id", "diplomatic_documents", ["id"])

    op.create_table(
        "correspondence",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("subject", sa.String(length=256), nullable=False),
        sa.Column("sender", sa.String(length=128), nullable=False),
        sa.Column("recipient", sa.String(length=128), nullable=False),
        sa.Column("sent_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column(
            "document_id", sa.Integer(), sa.ForeignKey("diplomatic_documents.id"), nullable=True
        ),
        sa.Column("body", sa.Text(), nullable=True),
    )
    op.create_index("ix_correspondence_id", "correspondence", ["id"])
    op.create_index("ix_correspondence_date", "correspondence", ["sent_date"])

    # Astraea
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("user", sa.String(length=64), nullable=False),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column("resource", sa.String(length=64), nullable=False),
        sa.Column("resource_id", sa.String(length=64), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("success", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_audit_logs_id", "audit_logs", ["id"])
    op.create_index("ix_audit_logs_timestamp", "audit_logs", ["timestamp"])

    op.create_table(
        "user_permissions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("resource", sa.String(length=64), nullable=False),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column("granted", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_user_permissions_id", "user_permissions", ["id"])

    op.create_table(
        "backup_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("filename", sa.String(length=256), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_backup_records_id", "backup_records", ["id"])

    # Zoë
    op.create_table(
        "agent_tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="todo"),
        sa.Column("priority", sa.String(length=16), nullable=False, server_default="medium"),
        sa.Column("assigned_module", sa.String(length=32), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_agent_tasks_id", "agent_tasks", ["id"])

    op.create_table(
        "agent_memories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("context", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_agent_memories_id", "agent_memories", ["id"])
    op.create_index("ix_agent_memories_key", "agent_memories", ["key"], unique=True)

    op.create_table(
        "agent_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("agent_name", sa.String(length=64), nullable=False),
        sa.Column("input_text", sa.Text(), nullable=False),
        sa.Column("output_text", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="running"),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_agent_runs_id", "agent_runs", ["id"])


def downgrade() -> None:
    op.drop_table("agent_runs")
    op.drop_table("agent_memories")
    op.drop_table("agent_tasks")
    op.drop_table("backup_records")
    op.drop_table("user_permissions")
    op.drop_table("audit_logs")
    op.drop_table("correspondence")
    op.drop_table("diplomatic_documents")
    op.drop_table("contract_deadlines")
    op.drop_table("legal_contracts")
    op.drop_table("transactions")
    op.drop_table("categories")
    op.drop_table("maintenance_requests")
    op.drop_table("tenants")
    op.drop_table("properties")
    op.drop_table("electricity_contracts")
    op.drop_table("energy_readings")
    op.drop_table("wind_farms")
    op.drop_column("users", "is_active")
    op.drop_column("users", "email")
