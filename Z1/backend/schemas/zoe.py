from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class AgentTaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=256)
    description: str | None = None
    status: str = Field("todo", pattern="^(todo|in_progress|done|cancelled)$")
    priority: str = Field("medium", pattern="^(low|medium|high|urgent)$")
    assigned_module: str | None = Field(None, max_length=32)
    due_date: date | None = None


class AgentTaskCreate(AgentTaskBase):
    pass


class AgentTaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=256)
    description: str | None = None
    status: str | None = Field(None, pattern="^(todo|in_progress|done|cancelled)$")
    priority: str | None = Field(None, pattern="^(low|medium|high|urgent)$")
    assigned_module: str | None = Field(None, max_length=32)
    due_date: date | None = None


class AgentTaskResponse(AgentTaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    completed_at: datetime | None


# ---------------------------------------------------------------------------

class AgentMemoryCreate(BaseModel):
    key: str = Field(..., min_length=1, max_length=128)
    value: str = Field(..., min_length=1)
    context: str | None = Field(None, max_length=64)


class AgentMemoryUpdate(BaseModel):
    value: str = Field(..., min_length=1)
    context: str | None = Field(None, max_length=64)


class AgentMemoryResponse(AgentMemoryCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------

class AgentRunCreate(BaseModel):
    agent_name: str = Field(..., min_length=1, max_length=64)
    input_text: str = Field(..., min_length=1)


class AgentRunResponse(AgentRunCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    output_text: str | None
    status: str
    duration_ms: int | None
    created_at: datetime


# ---------------------------------------------------------------------------

class ZoeDispatchRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    context: str | None = None


class ZoeDispatchResponse(BaseModel):
    run_id: int
    routed_to: str
    response: str
    duration_ms: int


# ---------------------------------------------------------------------------

class ZoeSummary(BaseModel):
    total_tasks: int
    open_tasks: int
    completed_tasks: int
    total_runs: int
    memory_entries: int
