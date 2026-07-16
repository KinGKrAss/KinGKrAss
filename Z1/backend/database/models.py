from datetime import datetime

from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32), default="viewer")


class DashboardSnapshot(Base):
    __tablename__ = "dashboard_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    real_estate_count: Mapped[float] = mapped_column(Float, default=0)
    windpark_count: Mapped[float] = mapped_column(Float, default=0)
    energy_production_kwh: Mapped[float] = mapped_column(Float, default=0)
    income_total: Mapped[float] = mapped_column(Float, default=0)
    expense_total: Mapped[float] = mapped_column(Float, default=0)
