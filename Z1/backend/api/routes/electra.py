from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from auth.deps import get_current_user
from database.models import ElectricityContract, EnergyReading, WindFarm
from database.session import get_db
from schemas.electra import (
    ElectricityContractCreate,
    ElectricityContractResponse,
    ElectricityContractUpdate,
    ElectraSummary,
    EnergyReadingCreate,
    EnergyReadingResponse,
    WindFarmCreate,
    WindFarmResponse,
    WindFarmUpdate,
)

router = APIRouter(prefix="/electra", tags=["electra"])


# ── Wind Farms ──────────────────────────────────────────────────────────────

@router.get("/wind-farms", response_model=list[WindFarmResponse])
def list_wind_farms(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> list[WindFarm]:
    return list(db.scalars(select(WindFarm).offset(skip).limit(limit)))


@router.post("/wind-farms", response_model=WindFarmResponse, status_code=status.HTTP_201_CREATED)
def create_wind_farm(
    data: WindFarmCreate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> WindFarm:
    farm = WindFarm(**data.model_dump())
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return farm


@router.get("/wind-farms/{farm_id}", response_model=WindFarmResponse)
def get_wind_farm(
    farm_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> WindFarm:
    farm = db.get(WindFarm, farm_id)
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wind farm not found")
    return farm


@router.put("/wind-farms/{farm_id}", response_model=WindFarmResponse)
def update_wind_farm(
    farm_id: int,
    data: WindFarmUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> WindFarm:
    farm = db.get(WindFarm, farm_id)
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wind farm not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(farm, field, value)
    db.commit()
    db.refresh(farm)
    return farm


@router.delete("/wind-farms/{farm_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_wind_farm(
    farm_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> None:
    farm = db.get(WindFarm, farm_id)
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wind farm not found")
    db.delete(farm)
    db.commit()


# ── Energy Readings ──────────────────────────────────────────────────────────

@router.get("/wind-farms/{farm_id}/readings", response_model=list[EnergyReadingResponse])
def list_readings(
    farm_id: int,
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> list[EnergyReading]:
    farm = db.get(WindFarm, farm_id)
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wind farm not found")
    return list(
        db.scalars(
            select(EnergyReading)
            .where(EnergyReading.wind_farm_id == farm_id)
            .order_by(EnergyReading.timestamp.desc())
            .offset(skip)
            .limit(limit)
        )
    )


@router.post(
    "/wind-farms/{farm_id}/readings",
    response_model=EnergyReadingResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_reading(
    farm_id: int,
    data: EnergyReadingCreate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> EnergyReading:
    farm = db.get(WindFarm, farm_id)
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wind farm not found")
    reading = EnergyReading(wind_farm_id=farm_id, **data.model_dump())
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return reading


# ── Contracts ────────────────────────────────────────────────────────────────

@router.get("/contracts", response_model=list[ElectricityContractResponse])
def list_contracts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> list[ElectricityContract]:
    return list(db.scalars(select(ElectricityContract).offset(skip).limit(limit)))


@router.post("/contracts", response_model=ElectricityContractResponse, status_code=status.HTTP_201_CREATED)
def create_contract(
    data: ElectricityContractCreate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> ElectricityContract:
    farm = db.get(WindFarm, data.wind_farm_id)
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wind farm not found")
    contract = ElectricityContract(**data.model_dump())
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return contract


@router.get("/contracts/{contract_id}", response_model=ElectricityContractResponse)
def get_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> ElectricityContract:
    contract = db.get(ElectricityContract, contract_id)
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
    return contract


@router.put("/contracts/{contract_id}", response_model=ElectricityContractResponse)
def update_contract(
    contract_id: int,
    data: ElectricityContractUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> ElectricityContract:
    contract = db.get(ElectricityContract, contract_id)
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(contract, field, value)
    db.commit()
    db.refresh(contract)
    return contract


@router.delete("/contracts/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> None:
    contract = db.get(ElectricityContract, contract_id)
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
    db.delete(contract)
    db.commit()


# ── Summary ───────────────────────────────────────────────────────────────────

@router.get("/summary", response_model=ElectraSummary)
def get_summary(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> ElectraSummary:
    total_farms = db.scalar(select(func.count()).select_from(WindFarm)) or 0
    active_farms = db.scalar(select(func.count()).select_from(WindFarm).where(WindFarm.status == "active")) or 0
    total_capacity = db.scalar(select(func.coalesce(func.sum(WindFarm.capacity_kw), 0.0))) or 0.0
    total_production = db.scalar(select(func.coalesce(func.sum(EnergyReading.production_kwh), 0.0))) or 0.0
    active_contracts = db.scalar(select(func.count()).select_from(ElectricityContract)) or 0

    avg_price = db.scalar(select(func.coalesce(func.avg(ElectricityContract.price_per_kwh), 0.0))) or 0.0
    estimated_revenue = total_production * avg_price

    return ElectraSummary(
        total_farms=total_farms,
        active_farms=active_farms,
        total_capacity_kw=total_capacity,
        total_production_kwh=total_production,
        active_contracts=active_contracts,
        estimated_revenue_eur=estimated_revenue,
    )
