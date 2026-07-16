from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class PropertyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    address: str = Field(..., min_length=1, max_length=256)
    city: str = Field(..., min_length=1, max_length=64)
    property_type: str = Field(..., pattern="^(apartment|house|commercial|land)$")
    area_sqm: float = Field(..., gt=0)
    purchase_price: float | None = Field(None, ge=0)
    monthly_rent: float | None = Field(None, ge=0)
    status: str = Field("available", pattern="^(available|rented|maintenance)$")
    latitude: float | None = None
    longitude: float | None = None


class PropertyCreate(PropertyBase):
    pass


class PropertyUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=128)
    address: str | None = Field(None, min_length=1, max_length=256)
    city: str | None = Field(None, min_length=1, max_length=64)
    property_type: str | None = Field(None, pattern="^(apartment|house|commercial|land)$")
    area_sqm: float | None = Field(None, gt=0)
    purchase_price: float | None = Field(None, ge=0)
    monthly_rent: float | None = Field(None, ge=0)
    status: str | None = Field(None, pattern="^(available|rented|maintenance)$")
    latitude: float | None = None
    longitude: float | None = None


class PropertyResponse(PropertyBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


# ---------------------------------------------------------------------------

class TenantBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    email: str | None = Field(None, max_length=128)
    phone: str | None = Field(None, max_length=32)
    lease_start: date
    lease_end: date | None = None
    monthly_rent: float = Field(..., gt=0)


class TenantCreate(TenantBase):
    property_id: int


class TenantUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=128)
    email: str | None = Field(None, max_length=128)
    phone: str | None = Field(None, max_length=32)
    lease_start: date | None = None
    lease_end: date | None = None
    monthly_rent: float | None = Field(None, gt=0)


class TenantResponse(TenantBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    property_id: int


# ---------------------------------------------------------------------------

class MaintenanceRequestBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=128)
    description: str | None = None
    status: str = Field("open", pattern="^(open|in_progress|resolved)$")
    priority: str = Field("medium", pattern="^(low|medium|high|urgent)$")


class MaintenanceRequestCreate(MaintenanceRequestBase):
    property_id: int


class MaintenanceRequestUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=128)
    description: str | None = None
    status: str | None = Field(None, pattern="^(open|in_progress|resolved)$")
    priority: str | None = Field(None, pattern="^(low|medium|high|urgent)$")


class MaintenanceRequestResponse(MaintenanceRequestBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    property_id: int
    created_at: datetime
    resolved_at: datetime | None


# ---------------------------------------------------------------------------

class GaiaSummary(BaseModel):
    total_properties: int
    rented_properties: int
    available_properties: int
    total_rent_income: float
    open_maintenance_requests: int
