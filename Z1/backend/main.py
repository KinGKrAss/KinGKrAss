from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from ai.agents import AgentCoordinator
from ai.workflows import run_workflow
from api.routes import auth, dashboard, health, modules
from api.routes import astraea, diplomatia, electra, fortuna, gaia, themis, users, zoe
from auth.security import verify_token
from database.base import Base
from database.bootstrap import ensure_default_admin
from database.session import SessionLocal, engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        ensure_default_admin(session)
    yield


app = FastAPI(title="Z1 Löwenherz OS API", version="1.0.0", lifespan=lifespan)
coordinator = AgentCoordinator()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core routes
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(modules.router)
app.include_router(users.router)

# Module routes
app.include_router(electra.router)
app.include_router(gaia.router)
app.include_router(fortuna.router)
app.include_router(themis.router)
app.include_router(diplomatia.router)
app.include_router(astraea.router)
app.include_router(zoe.router)


@app.get("/")
def root() -> dict:
    return {
        "name": "Z1 Löwenherz Operating System",
        "status": "running",
        "agent_coordinator": coordinator.status(),
    }


@app.post("/workflows/{workflow_name}")
def queue_workflow(workflow_name: str) -> dict:
    result = run_workflow(workflow_name)
    return {"workflow": result.workflow, "status": result.status, "details": result.details}


@app.websocket("/ws/updates")
async def websocket_updates(websocket: WebSocket) -> None:
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return

    try:
        username = verify_token(token)
    except ValueError:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    await websocket.send_json({"message": f"Willkommen {username}", "channel": "updates"})

    try:
        while True:
            payload = await websocket.receive_text()
            await websocket.send_json({"echo": payload})
    except WebSocketDisconnect:
        return
