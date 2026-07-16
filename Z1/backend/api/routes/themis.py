from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from auth.deps import get_current_user
from database.models import ContractDeadline, LegalContract
from database.session import get_db
from schemas.themis import (
    ContractDeadlineCreate,
    ContractDeadlineResponse,
    ContractDeadlineUpdate,
    LegalContractCreate,
    LegalContractResponse,
    LegalContractUpdate,
    ThemisSummary,
)

router = APIRouter(prefix="/themis", tags=["themis"])


# ── Contracts ─────────────────────────────────────────────────────────────────

@router.get("/contracts", response_model=list[LegalContractResponse])
def list_contracts(
    skip: int = 0,
    limit: int = 100,
    status_filter: str | None = None,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> list[LegalContract]:
    q = select(LegalContract)
    if status_filter:
        q = q.where(LegalContract.status == status_filter)
    return list(db.scalars(q.offset(skip).limit(limit)))


@router.post("/contracts", response_model=LegalContractResponse, status_code=status.HTTP_201_CREATED)
def create_contract(
    data: LegalContractCreate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> LegalContract:
    contract = LegalContract(**data.model_dump())
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return contract


@router.get("/contracts/{contract_id}", response_model=LegalContractResponse)
def get_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> LegalContract:
    contract = db.get(LegalContract, contract_id)
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
    return contract


@router.put("/contracts/{contract_id}", response_model=LegalContractResponse)
def update_contract(
    contract_id: int,
    data: LegalContractUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> LegalContract:
    contract = db.get(LegalContract, contract_id)
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
    contract = db.get(LegalContract, contract_id)
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
    db.delete(contract)
    db.commit()


# ── Deadlines ─────────────────────────────────────────────────────────────────

@router.get("/contracts/{contract_id}/deadlines", response_model=list[ContractDeadlineResponse])
def list_deadlines(
    contract_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> list[ContractDeadline]:
    contract = db.get(LegalContract, contract_id)
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
    return list(
        db.scalars(
            select(ContractDeadline)
            .where(ContractDeadline.contract_id == contract_id)
            .order_by(ContractDeadline.due_date)
        )
    )


@router.post(
    "/contracts/{contract_id}/deadlines",
    response_model=ContractDeadlineResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_deadline(
    contract_id: int,
    data: ContractDeadlineCreate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> ContractDeadline:
    contract = db.get(LegalContract, contract_id)
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
    dl = ContractDeadline(contract_id=contract_id, **data.model_dump(exclude={"contract_id"}))
    db.add(dl)
    db.commit()
    db.refresh(dl)
    return dl


@router.put("/deadlines/{deadline_id}", response_model=ContractDeadlineResponse)
def update_deadline(
    deadline_id: int,
    data: ContractDeadlineUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> ContractDeadline:
    dl = db.get(ContractDeadline, deadline_id)
    if not dl:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deadline not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(dl, field, value)
    db.commit()
    db.refresh(dl)
    return dl


@router.delete("/deadlines/{deadline_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deadline(
    deadline_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> None:
    dl = db.get(ContractDeadline, deadline_id)
    if not dl:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deadline not found")
    db.delete(dl)
    db.commit()


# ── Upcoming Deadlines ────────────────────────────────────────────────────────

@router.get("/deadlines/upcoming", response_model=list[ContractDeadlineResponse])
def upcoming_deadlines(
    days: int = 30,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> list[ContractDeadline]:
    today = date.today()
    cutoff = today + timedelta(days=days)
    return list(
        db.scalars(
            select(ContractDeadline)
            .where(ContractDeadline.due_date >= today)
            .where(ContractDeadline.due_date <= cutoff)
            .where(ContractDeadline.status == "pending")
            .order_by(ContractDeadline.due_date)
        )
    )


# ── Summary ───────────────────────────────────────────────────────────────────

@router.get("/summary", response_model=ThemisSummary)
def get_summary(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> ThemisSummary:
    today = date.today()
    soon = today + timedelta(days=30)

    total = db.scalar(select(func.count()).select_from(LegalContract)) or 0
    active = (
        db.scalar(select(func.count()).select_from(LegalContract).where(LegalContract.status == "active")) or 0
    )
    expiring = (
        db.scalar(
            select(func.count())
            .select_from(LegalContract)
            .where(LegalContract.status == "active")
            .where(LegalContract.end_date >= today)
            .where(LegalContract.end_date <= soon)
        ) or 0
    )
    pending_dl = (
        db.scalar(
            select(func.count()).select_from(ContractDeadline).where(ContractDeadline.status == "pending")
        ) or 0
    )
    overdue_dl = (
        db.scalar(
            select(func.count())
            .select_from(ContractDeadline)
            .where(ContractDeadline.status == "pending")
            .where(ContractDeadline.due_date < today)
        ) or 0
    )
    total_value = (
        db.scalar(select(func.coalesce(func.sum(LegalContract.value), 0.0))) or 0.0
    )

    return ThemisSummary(
        total_contracts=total,
        active_contracts=active,
        expiring_soon=expiring,
        pending_deadlines=pending_dl,
        overdue_deadlines=overdue_dl,
        total_contract_value=total_value,
    )
