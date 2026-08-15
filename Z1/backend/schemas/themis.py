from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class LegalContractBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=256)
    counterparty: str = Field(..., min_length=1, max_length=128)
    contract_type: str = Field(..., pattern="^(rental|energy|employment|service|other)$")
    status: str = Field("draft", pattern="^(draft|active|expired|terminated)$")
    start_date: date | None = None
    end_date: date | None = None
    value: float | None = Field(None, ge=0)
    notes: str | None = None


class LegalContractCreate(LegalContractBase):
    pass


class LegalContractUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=256)
    counterparty: str | None = Field(None, min_length=1, max_length=128)
    contract_type: str | None = Field(None, pattern="^(rental|energy|employment|service|other)$")
    status: str | None = Field(None, pattern="^(draft|active|expired|terminated)$")
    start_date: date | None = None
    end_date: date | None = None
    value: float | None = Field(None, ge=0)
    notes: str | None = None


class LegalContractResponse(LegalContractBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


# ---------------------------------------------------------------------------

class ContractDeadlineBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=128)
    due_date: date
    status: str = Field("pending", pattern="^(pending|completed|overdue)$")


class ContractDeadlineCreate(ContractDeadlineBase):
    contract_id: int


class ContractDeadlineUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=128)
    due_date: date | None = None
    status: str | None = Field(None, pattern="^(pending|completed|overdue)$")


class ContractDeadlineResponse(ContractDeadlineBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    contract_id: int


# ---------------------------------------------------------------------------

class ThemisSummary(BaseModel):
    total_contracts: int
    active_contracts: int
    expiring_soon: int  # within 30 days
    pending_deadlines: int
    overdue_deadlines: int
    total_contract_value: float
