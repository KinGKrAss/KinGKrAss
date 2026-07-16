from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from auth.deps import get_current_user
from database.models import MaintenanceRequest, Property, Tenant
from database.session import get_db
from schemas.gaia import (
    GaiaSummary,
    MaintenanceRequestCreate,
    MaintenanceRequestResponse,
    MaintenanceRequestUpdate,
    PropertyCreate,
    PropertyResponse,
    PropertyUpdate,
    TenantCreate,
    TenantResponse,
    TenantUpdate,
)

router = APIRouter(prefix="/gaia", tags=["gaia"])


# ── Properties ───────────────────────────────────────────────────────────────

@router.get("/properties", response_model=list[PropertyResponse])
def list_properties(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> list[Property]:
    return list(db.scalars(select(Property).offset(skip).limit(limit)))


@router.post("/properties", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED)
def create_property(
    data: PropertyCreate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> Property:
    prop = Property(**data.model_dump())
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return prop


@router.get("/properties/{property_id}", response_model=PropertyResponse)
def get_property(
    property_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> Property:
    prop = db.get(Property, property_id)
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
    return prop


@router.put("/properties/{property_id}", response_model=PropertyResponse)
def update_property(
    property_id: int,
    data: PropertyUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> Property:
    prop = db.get(Property, property_id)
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(prop, field, value)
    db.commit()
    db.refresh(prop)
    return prop


@router.delete("/properties/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_property(
    property_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> None:
    prop = db.get(Property, property_id)
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
    db.delete(prop)
    db.commit()


# ── Tenants ───────────────────────────────────────────────────────────────────

@router.get("/properties/{property_id}/tenants", response_model=list[TenantResponse])
def list_tenants(
    property_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> list[Tenant]:
    prop = db.get(Property, property_id)
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
    return list(db.scalars(select(Tenant).where(Tenant.property_id == property_id)))


@router.post(
    "/properties/{property_id}/tenants",
    response_model=TenantResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_tenant(
    property_id: int,
    data: TenantCreate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> Tenant:
    prop = db.get(Property, property_id)
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
    tenant = Tenant(property_id=property_id, **data.model_dump(exclude={"property_id"}))
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


@router.put("/tenants/{tenant_id}", response_model=TenantResponse)
def update_tenant(
    tenant_id: int,
    data: TenantUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> Tenant:
    tenant = db.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(tenant, field, value)
    db.commit()
    db.refresh(tenant)
    return tenant


@router.delete("/tenants/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> None:
    tenant = db.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    db.delete(tenant)
    db.commit()


# ── Maintenance Requests ─────────────────────────────────────────────────────

@router.get("/maintenance", response_model=list[MaintenanceRequestResponse])
def list_maintenance_requests(
    skip: int = 0,
    limit: int = 100,
    status_filter: str | None = None,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> list[MaintenanceRequest]:
    q = select(MaintenanceRequest)
    if status_filter:
        q = q.where(MaintenanceRequest.status == status_filter)
    return list(db.scalars(q.offset(skip).limit(limit)))


@router.post("/maintenance", response_model=MaintenanceRequestResponse, status_code=status.HTTP_201_CREATED)
def create_maintenance_request(
    data: MaintenanceRequestCreate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> MaintenanceRequest:
    prop = db.get(Property, data.property_id)
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
    req = MaintenanceRequest(**data.model_dump())
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


@router.put("/maintenance/{req_id}", response_model=MaintenanceRequestResponse)
def update_maintenance_request(
    req_id: int,
    data: MaintenanceRequestUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> MaintenanceRequest:
    req = db.get(MaintenanceRequest, req_id)
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(req, field, value)
    if data.status == "resolved" and not req.resolved_at:
        req.resolved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(req)
    return req


@router.delete("/maintenance/{req_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_maintenance_request(
    req_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> None:
    req = db.get(MaintenanceRequest, req_id)
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    db.delete(req)
    db.commit()


# ── Summary ───────────────────────────────────────────────────────────────────

@router.get("/summary", response_model=GaiaSummary)
def get_summary(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> GaiaSummary:
    total = db.scalar(select(func.count()).select_from(Property)) or 0
    rented = db.scalar(select(func.count()).select_from(Property).where(Property.status == "rented")) or 0
    available = db.scalar(select(func.count()).select_from(Property).where(Property.status == "available")) or 0
    rent_income = db.scalar(select(func.coalesce(func.sum(Tenant.monthly_rent), 0.0))) or 0.0
    open_maint = (
        db.scalar(
            select(func.count()).select_from(MaintenanceRequest).where(MaintenanceRequest.status == "open")
        ) or 0
    )
    return GaiaSummary(
        total_properties=total,
        rented_properties=rented,
        available_properties=available,
        total_rent_income=rent_income,
        open_maintenance_requests=open_maint,
    )
