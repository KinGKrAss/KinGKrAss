from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    category_type: str = Field(..., pattern="^(income|expense)$")
    color: str | None = Field(None, max_length=16)


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


# ---------------------------------------------------------------------------

class TransactionBase(BaseModel):
    transaction_date: date
    description: str = Field(..., min_length=1, max_length=256)
    amount: float = Field(..., gt=0)
    transaction_type: str = Field(..., pattern="^(income|expense)$")
    reference: str | None = Field(None, max_length=128)


class TransactionCreate(TransactionBase):
    category_id: int | None = None


class TransactionUpdate(BaseModel):
    transaction_date: date | None = None
    description: str | None = Field(None, min_length=1, max_length=256)
    amount: float | None = Field(None, gt=0)
    transaction_type: str | None = Field(None, pattern="^(income|expense)$")
    category_id: int | None = None
    reference: str | None = Field(None, max_length=128)


class TransactionResponse(TransactionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int | None
    created_at: datetime


# ---------------------------------------------------------------------------

class FortunaMonthlyBreakdown(BaseModel):
    year: int
    month: int
    income: float
    expenses: float
    profit: float


class FortunaSummary(BaseModel):
    total_income: float
    total_expenses: float
    net_profit: float
    transaction_count: int
    monthly: list[FortunaMonthlyBreakdown]
