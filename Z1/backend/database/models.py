from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32), default="viewer")
    email: Mapped[str | None] = mapped_column(String(128), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    permissions: Mapped[list["UserPermission"]] = relationship(
        "UserPermission", back_populates="user", cascade="all, delete-orphan"
    )


class DashboardSnapshot(Base):
    __tablename__ = "dashboard_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    real_estate_count: Mapped[float] = mapped_column(Float, default=0)
    windpark_count: Mapped[float] = mapped_column(Float, default=0)
    energy_production_kwh: Mapped[float] = mapped_column(Float, default=0)
    income_total: Mapped[float] = mapped_column(Float, default=0)
    expense_total: Mapped[float] = mapped_column(Float, default=0)


# ---------------------------------------------------------------------------
# Electra – Energy & Wind Farm Management
# ---------------------------------------------------------------------------

class WindFarm(Base):
    __tablename__ = "wind_farms"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    location: Mapped[str] = mapped_column(String(256))
    capacity_kw: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(32), default="active")  # active | maintenance | offline
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    readings: Mapped[list["EnergyReading"]] = relationship(
        "EnergyReading", back_populates="wind_farm", cascade="all, delete-orphan"
    )
    contracts: Mapped[list["ElectricityContract"]] = relationship(
        "ElectricityContract", back_populates="wind_farm", cascade="all, delete-orphan"
    )


class EnergyReading(Base):
    __tablename__ = "energy_readings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    wind_farm_id: Mapped[int] = mapped_column(ForeignKey("wind_farms.id"))
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    production_kwh: Mapped[float] = mapped_column(Float)
    wind_speed_ms: Mapped[float | None] = mapped_column(Float, nullable=True)

    wind_farm: Mapped["WindFarm"] = relationship("WindFarm", back_populates="readings")


class ElectricityContract(Base):
    __tablename__ = "electricity_contracts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    wind_farm_id: Mapped[int] = mapped_column(ForeignKey("wind_farms.id"))
    name: Mapped[str] = mapped_column(String(128))
    counterparty: Mapped[str] = mapped_column(String(128))
    price_per_kwh: Mapped[float] = mapped_column(Float)
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    wind_farm: Mapped["WindFarm"] = relationship("WindFarm", back_populates="contracts")


# ---------------------------------------------------------------------------
# Gaia – Real Estate Management
# ---------------------------------------------------------------------------

class Property(Base):
    __tablename__ = "properties"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    address: Mapped[str] = mapped_column(String(256))
    city: Mapped[str] = mapped_column(String(64))
    property_type: Mapped[str] = mapped_column(String(32))  # apartment | house | commercial | land
    area_sqm: Mapped[float] = mapped_column(Float)
    purchase_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    monthly_rent: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="available")  # available | rented | maintenance
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    tenants: Mapped[list["Tenant"]] = relationship(
        "Tenant", back_populates="property", cascade="all, delete-orphan"
    )
    maintenance_requests: Mapped[list["MaintenanceRequest"]] = relationship(
        "MaintenanceRequest", back_populates="property", cascade="all, delete-orphan"
    )


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    property_id: Mapped[int] = mapped_column(ForeignKey("properties.id"))
    name: Mapped[str] = mapped_column(String(128))
    email: Mapped[str | None] = mapped_column(String(128), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    lease_start: Mapped[date] = mapped_column(Date)
    lease_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    monthly_rent: Mapped[float] = mapped_column(Float)

    property: Mapped["Property"] = relationship("Property", back_populates="tenants")


class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    property_id: Mapped[int] = mapped_column(ForeignKey("properties.id"))
    title: Mapped[str] = mapped_column(String(128))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="open")  # open | in_progress | resolved
    priority: Mapped[str] = mapped_column(String(16), default="medium")  # low | medium | high | urgent
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    property: Mapped["Property"] = relationship("Property", back_populates="maintenance_requests")


# ---------------------------------------------------------------------------
# Fortuna – Finance
# ---------------------------------------------------------------------------

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(64))
    category_type: Mapped[str] = mapped_column(String(16))  # income | expense
    color: Mapped[str | None] = mapped_column(String(16), nullable=True)

    transactions: Mapped[list["Transaction"]] = relationship("Transaction", back_populates="category")


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    transaction_date: Mapped[date] = mapped_column(Date, index=True)
    description: Mapped[str] = mapped_column(String(256))
    amount: Mapped[float] = mapped_column(Float)
    transaction_type: Mapped[str] = mapped_column(String(16))  # income | expense
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    reference: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    category: Mapped["Category | None"] = relationship("Category", back_populates="transactions")


# ---------------------------------------------------------------------------
# Themis – Legal & Contracts
# ---------------------------------------------------------------------------

class LegalContract(Base):
    __tablename__ = "legal_contracts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(256))
    counterparty: Mapped[str] = mapped_column(String(128))
    contract_type: Mapped[str] = mapped_column(String(64))  # rental | energy | employment | other
    status: Mapped[str] = mapped_column(String(32), default="draft")  # draft | active | expired | terminated
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    value: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    deadlines: Mapped[list["ContractDeadline"]] = relationship(
        "ContractDeadline", back_populates="contract", cascade="all, delete-orphan"
    )


class ContractDeadline(Base):
    __tablename__ = "contract_deadlines"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("legal_contracts.id"))
    title: Mapped[str] = mapped_column(String(128))
    due_date: Mapped[date] = mapped_column(Date, index=True)
    status: Mapped[str] = mapped_column(String(32), default="pending")  # pending | completed | overdue

    contract: Mapped["LegalContract"] = relationship("LegalContract", back_populates="deadlines")


# ---------------------------------------------------------------------------
# Diplomatia – Diplomatic Document Management
# ---------------------------------------------------------------------------

class DiplomaticDocument(Base):
    __tablename__ = "diplomatic_documents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(256))
    language: Mapped[str] = mapped_column(String(8))  # ISO 639-1: de | en | fr | es | ...
    document_type: Mapped[str] = mapped_column(String(64))  # memo | treaty | letter | report | note
    content: Mapped[str] = mapped_column(Text)
    tags: Mapped[str | None] = mapped_column(String(256), nullable=True)  # comma-separated
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    correspondence: Mapped[list["Correspondence"]] = relationship(
        "Correspondence", back_populates="document", cascade="all, delete-orphan"
    )


class Correspondence(Base):
    __tablename__ = "correspondence"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    subject: Mapped[str] = mapped_column(String(256))
    sender: Mapped[str] = mapped_column(String(128))
    recipient: Mapped[str] = mapped_column(String(128))
    sent_date: Mapped[date] = mapped_column(Date, index=True)
    status: Mapped[str] = mapped_column(String(32), default="draft")  # draft | sent | received | archived
    document_id: Mapped[int | None] = mapped_column(ForeignKey("diplomatic_documents.id"), nullable=True)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)

    document: Mapped["DiplomaticDocument | None"] = relationship(
        "DiplomaticDocument", back_populates="correspondence"
    )


# ---------------------------------------------------------------------------
# Astraea – Security, Audit & Permissions
# ---------------------------------------------------------------------------

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, index=True, default=lambda: datetime.now(timezone.utc)
    )
    user: Mapped[str] = mapped_column(String(64))
    action: Mapped[str] = mapped_column(String(32))  # create | read | update | delete
    resource: Mapped[str] = mapped_column(String(64))
    resource_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, default=True)


class UserPermission(Base):
    __tablename__ = "user_permissions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    resource: Mapped[str] = mapped_column(String(64))
    action: Mapped[str] = mapped_column(String(32))  # read | write | admin
    granted: Mapped[bool] = mapped_column(Boolean, default=True)

    user: Mapped["User"] = relationship("User", back_populates="permissions")


class BackupRecord(Base):
    __tablename__ = "backup_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(256))
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="pending")  # pending | completed | failed
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


# ---------------------------------------------------------------------------
# Zoë – AI Orchestration
# ---------------------------------------------------------------------------

class AgentTask(Base):
    __tablename__ = "agent_tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(256))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="todo")  # todo | in_progress | done | cancelled
    priority: Mapped[str] = mapped_column(String(16), default="medium")  # low | medium | high | urgent
    assigned_module: Mapped[str | None] = mapped_column(String(32), nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class AgentMemory(Base):
    __tablename__ = "agent_memories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    key: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    value: Mapped[str] = mapped_column(Text)
    context: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    agent_name: Mapped[str] = mapped_column(String(64))
    input_text: Mapped[str] = mapped_column(Text)
    output_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="running")  # running | completed | failed
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
