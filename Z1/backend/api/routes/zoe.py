import time

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from auth.deps import get_current_user
from database.models import AgentMemory, AgentRun, AgentTask
from database.session import get_db
from schemas.zoe import (
    AgentMemoryCreate,
    AgentMemoryResponse,
    AgentMemoryUpdate,
    AgentRunResponse,
    AgentTaskCreate,
    AgentTaskResponse,
    AgentTaskUpdate,
    ZoeDispatchRequest,
    ZoeDispatchResponse,
    ZoeSummary,
)

router = APIRouter(prefix="/zoe", tags=["zoe"])

# Module routing keywords
_MODULE_KEYWORDS: dict[str, list[str]] = {
    "electra": ["energie", "windpark", "strom", "solar", "energy", "wind", "power"],
    "gaia": ["immobilie", "mieter", "wohnung", "haus", "property", "tenant", "maintenance"],
    "fortuna": ["rechnung", "zahlung", "ausgaben", "einnahmen", "finance", "invoice", "budget"],
    "themis": ["vertrag", "frist", "dokument", "contract", "deadline", "legal"],
    "diplomatia": ["memo", "korrespondenz", "diplomatic", "letter", "correspondence"],
    "astraea": ["sicherheit", "audit", "backup", "permission", "security", "log"],
}


def _route_to_module(prompt: str) -> str:
    lower = prompt.lower()
    for module, keywords in _MODULE_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return module
    return "core"


def _generate_response(prompt: str, module: str) -> str:
    responses = {
        "electra": f"Ich analysiere deine Anfrage zum Energiemodul: «{prompt}». Bitte prüfe die Windpark-Übersicht im Electra-Dashboard.",
        "gaia": f"Anfrage zum Immobilienmodul erhalten: «{prompt}». Navigiere zum Gaia-Dashboard für Details.",
        "fortuna": f"Finanzanfrage verarbeitet: «{prompt}». Aktuelle Zahlen findest du im Fortuna-Dashboard.",
        "themis": f"Rechtliche Anfrage analysiert: «{prompt}». Prüfe deine Verträge und Fristen im Themis-Modul.",
        "diplomatia": f"Diplomatische Anfrage: «{prompt}». Dein Korrespondenzarchiv ist im Diplomatia-Modul abrufbar.",
        "astraea": f"Sicherheitsanfrage registriert: «{prompt}». Audit-Logs und Berechtigungen im Astraea-Modul.",
        "core": f"Anfrage erhalten: «{prompt}». Ich bin Zoë, deine KI-Orchestratorin. Wie kann ich dir weiterhelfen?",
    }
    return responses.get(module, responses["core"])


# ── Tasks ─────────────────────────────────────────────────────────────────────

@router.get("/tasks", response_model=list[AgentTaskResponse])
def list_tasks(
    skip: int = 0,
    limit: int = 100,
    status_filter: str | None = None,
    module_filter: str | None = None,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> list[AgentTask]:
    q = select(AgentTask).order_by(AgentTask.created_at.desc())
    if status_filter:
        q = q.where(AgentTask.status == status_filter)
    if module_filter:
        q = q.where(AgentTask.assigned_module == module_filter)
    return list(db.scalars(q.offset(skip).limit(limit)))


@router.post("/tasks", response_model=AgentTaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    data: AgentTaskCreate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> AgentTask:
    task = AgentTask(**data.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/tasks/{task_id}", response_model=AgentTaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> AgentTask:
    task = db.get(AgentTask, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.put("/tasks/{task_id}", response_model=AgentTaskResponse)
def update_task(
    task_id: int,
    data: AgentTaskUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> AgentTask:
    task = db.get(AgentTask, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> None:
    task = db.get(AgentTask, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    db.delete(task)
    db.commit()


# ── Memory ────────────────────────────────────────────────────────────────────

@router.get("/memory", response_model=list[AgentMemoryResponse])
def list_memory(
    context: str | None = None,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> list[AgentMemory]:
    q = select(AgentMemory)
    if context:
        q = q.where(AgentMemory.context == context)
    return list(db.scalars(q))


@router.post("/memory", response_model=AgentMemoryResponse, status_code=status.HTTP_201_CREATED)
def create_memory(
    data: AgentMemoryCreate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> AgentMemory:
    existing = db.scalar(select(AgentMemory).where(AgentMemory.key == data.key))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Memory key '{data.key}' already exists. Use PUT to update.",
        )
    mem = AgentMemory(**data.model_dump())
    db.add(mem)
    db.commit()
    db.refresh(mem)
    return mem


@router.put("/memory/{key}", response_model=AgentMemoryResponse)
def upsert_memory(
    key: str,
    data: AgentMemoryUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> AgentMemory:
    mem = db.scalar(select(AgentMemory).where(AgentMemory.key == key))
    if not mem:
        mem = AgentMemory(key=key, **data.model_dump())
        db.add(mem)
    else:
        mem.value = data.value
        if data.context is not None:
            mem.context = data.context
    db.commit()
    db.refresh(mem)
    return mem


@router.delete("/memory/{key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_memory(
    key: str,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> None:
    mem = db.scalar(select(AgentMemory).where(AgentMemory.key == key))
    if not mem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory key not found")
    db.delete(mem)
    db.commit()


# ── Agent Runs ────────────────────────────────────────────────────────────────

@router.get("/runs", response_model=list[AgentRunResponse])
def list_runs(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> list[AgentRun]:
    return list(db.scalars(select(AgentRun).order_by(AgentRun.created_at.desc()).offset(skip).limit(limit)))


# ── Dispatch (Natural Language → Module) ──────────────────────────────────────

@router.post("/dispatch", response_model=ZoeDispatchResponse)
def dispatch(
    data: ZoeDispatchRequest,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> ZoeDispatchResponse:
    t_start = time.monotonic()
    module = _route_to_module(data.prompt)
    response_text = _generate_response(data.prompt, module)
    duration_ms = int((time.monotonic() - t_start) * 1000)

    run = AgentRun(
        agent_name="zoe",
        input_text=data.prompt,
        output_text=response_text,
        status="completed",
        duration_ms=duration_ms,
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    return ZoeDispatchResponse(
        run_id=run.id,
        routed_to=module,
        response=response_text,
        duration_ms=duration_ms,
    )


# ── Summary ───────────────────────────────────────────────────────────────────

@router.get("/summary", response_model=ZoeSummary)
def get_summary(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> ZoeSummary:
    total_tasks = db.scalar(select(func.count()).select_from(AgentTask)) or 0
    open_tasks = (
        db.scalar(
            select(func.count())
            .select_from(AgentTask)
            .where(AgentTask.status.in_(["todo", "in_progress"]))
        ) or 0
    )
    done_tasks = (
        db.scalar(select(func.count()).select_from(AgentTask).where(AgentTask.status == "done")) or 0
    )
    total_runs = db.scalar(select(func.count()).select_from(AgentRun)) or 0
    memory_entries = db.scalar(select(func.count()).select_from(AgentMemory)) or 0

    return ZoeSummary(
        total_tasks=total_tasks,
        open_tasks=open_tasks,
        completed_tasks=done_tasks,
        total_runs=total_runs,
        memory_entries=memory_entries,
    )
