from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class WindFarmBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    location: str = Field(..., min_length=1, max_length=256)
    capacity_kw: float = Field(..., gt=0)
    status: str = Field("active", pattern="^(active|maintenance|offline)$")
    latitude: float | None = None
    longitude: float | None = None


class WindFarmCreate(WindFarmBase):
    pass


class WindFarmUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=128)
    location: str | None = Field(None, min_length=1, max_length=256)
    capacity_kw: float | None = Field(None, gt=0)
    status: str | None = Field(None, pattern="^(active|maintenance|offline)$")
    latitude: float | None = None
    longitude: float | None = None


class WindFarmResponse(WindFarmBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


# ---------------------------------------------------------------------------

class EnergyReadingCreate(BaseModel):
    timestamp: datetime
    production_kwh: float = Field(..., ge=0)
    wind_speed_ms: float | None = Field(None, ge=0)


class EnergyReadingResponse(EnergyReadingCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    wind_farm_id: int


# ---------------------------------------------------------------------------

class ElectricityContractBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    counterparty: str = Field(..., min_length=1, max_length=128)
    price_per_kwh: float = Field(..., gt=0)
    start_date: date
    end_date: date | None = None


class ElectricityContractCreate(ElectricityContractBase):
    wind_farm_id: int


class ElectricityContractUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=128)
    counterparty: str | None = Field(None, min_length=1, max_length=128)
    price_per_kwh: float | None = Field(None, gt=0)
    start_date: date | None = None
    end_date: date | None = None


class ElectricityContractResponse(ElectricityContractBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    wind_farm_id: int


# ---------------------------------------------------------------------------

class ElectraSummary(BaseModel):
    total_farms: int
    active_farms: int
    total_capacity_kw: float
    total_production_kwh: float
    active_contracts: int
    estimated_revenue_eur: float
