from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from ai.agents import AgentCoordinator
from ai.workflows import run_workflow
from api.routes import auth, dashboard, health, modules
from auth.security import verify_token

app = FastAPI(title="Z1 Löwenherz OS API", version="0.1.0")
coordinator = AgentCoordinator()

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(modules.router)


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
