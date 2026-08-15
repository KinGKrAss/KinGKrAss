from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session

from auth.deps import get_current_user
from database.models import Category, Transaction
from database.session import get_db
from schemas.fortuna import (
    CategoryCreate,
    CategoryResponse,
    FortunaMonthlyBreakdown,
    FortunaSummary,
    TransactionCreate,
    TransactionResponse,
    TransactionUpdate,
)

router = APIRouter(prefix="/fortuna", tags=["fortuna"])


# ── Categories ────────────────────────────────────────────────────────────────

@router.get("/categories", response_model=list[CategoryResponse])
def list_categories(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> list[Category]:
    return list(db.scalars(select(Category)))


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> Category:
    cat = Category(**data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> None:
    cat = db.get(Category, category_id)
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    db.delete(cat)
    db.commit()


# ── Transactions ──────────────────────────────────────────────────────────────

@router.get("/transactions", response_model=list[TransactionResponse])
def list_transactions(
    skip: int = 0,
    limit: int = 200,
    transaction_type: str | None = None,
    category_id: int | None = None,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> list[Transaction]:
    q = select(Transaction).order_by(Transaction.transaction_date.desc())
    if transaction_type:
        q = q.where(Transaction.transaction_type == transaction_type)
    if category_id is not None:
        q = q.where(Transaction.category_id == category_id)
    return list(db.scalars(q.offset(skip).limit(limit)))


@router.post("/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    data: TransactionCreate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> Transaction:
    if data.category_id:
        if not db.get(Category, data.category_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    tx = Transaction(**data.model_dump())
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


@router.get("/transactions/{tx_id}", response_model=TransactionResponse)
def get_transaction(
    tx_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> Transaction:
    tx = db.get(Transaction, tx_id)
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return tx


@router.put("/transactions/{tx_id}", response_model=TransactionResponse)
def update_transaction(
    tx_id: int,
    data: TransactionUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> Transaction:
    tx = db.get(Transaction, tx_id)
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(tx, field, value)
    db.commit()
    db.refresh(tx)
    return tx


@router.delete("/transactions/{tx_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    tx_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> None:
    tx = db.get(Transaction, tx_id)
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    db.delete(tx)
    db.commit()


# ── Summary ───────────────────────────────────────────────────────────────────

@router.get("/summary", response_model=FortunaSummary)
def get_summary(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> FortunaSummary:
    total_income = (
        db.scalar(
            select(func.coalesce(func.sum(Transaction.amount), 0.0)).where(
                Transaction.transaction_type == "income"
            )
        ) or 0.0
    )
    total_expenses = (
        db.scalar(
            select(func.coalesce(func.sum(Transaction.amount), 0.0)).where(
                Transaction.transaction_type == "expense"
            )
        ) or 0.0
    )
    tx_count = db.scalar(select(func.count()).select_from(Transaction)) or 0

    # Monthly breakdown – group by year + month
    rows = db.execute(
        select(
            extract("year", Transaction.transaction_date).label("yr"),
            extract("month", Transaction.transaction_date).label("mo"),
            Transaction.transaction_type,
            func.sum(Transaction.amount).label("total"),
        ).group_by("yr", "mo", Transaction.transaction_type)
    ).all()

    buckets: dict[tuple[int, int], dict[str, float]] = {}
    for row in rows:
        key = (int(row.yr), int(row.mo))
        buckets.setdefault(key, {"income": 0.0, "expense": 0.0})
        buckets[key][row.transaction_type] = float(row.total)

    monthly = [
        FortunaMonthlyBreakdown(
            year=y,
            month=m,
            income=vals["income"],
            expenses=vals["expense"],
            profit=vals["income"] - vals["expense"],
        )
        for (y, m), vals in sorted(buckets.items())
    ]

    return FortunaSummary(
        total_income=total_income,
        total_expenses=total_expenses,
        net_profit=total_income - total_expenses,
        transaction_count=tx_count,
        monthly=monthly,
    )
