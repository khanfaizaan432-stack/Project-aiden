from __future__ import annotations

import asyncio
import inspect
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, cast

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect

from backend.agents import BaseAgent, EdenCouncil, load_default_agents
from backend.schemas import EvaluateRequest, EvaluateResponse, ManualSocietyTaskRequest
from backend.society.event_loop import SocietyEventLoop
from backend.society.oracle import Oracle
from backend.society.task import Task, TaskType


def _build_runtime() -> tuple[list[BaseAgent], Oracle, SocietyEventLoop, EdenCouncil]:
    root = Path(__file__).resolve().parent.parent
    agents = cast(list[BaseAgent], load_default_agents(root / "backend" / "models"))
    oracle = Oracle()
    loop = SocietyEventLoop(agents=agents, oracle=oracle)
    council = EdenCouncil(agents)
    return agents, oracle, loop, council


def _as_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return cast(dict[str, Any], value)
    return {}


def _to_int(value: Any, default: int = -1) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _normalise_society_event(event: dict[str, Any], agents: list[BaseAgent]) -> dict[str, Any]:
    event_type = str(event.get("type", ""))
    payload_dict = _as_dict(event.get("payload"))
    agent_index = {agent.agent_id: agent for agent in agents}

    if event_type == "oracle_proclamation":
        return {
            "type": "oracle_proclamation",
            "message": str(payload_dict.get("message", "")),
        }

    if event_type == "agent_message":
        from_agent_id = _to_int(payload_dict.get("from_agent_id"), -1)
        sender = agent_index.get(from_agent_id)
        return {
            "type": "agent_message",
            "agent_id": from_agent_id,
            "agent_name": sender.name if sender else f"Agent-{from_agent_id}",
            "tribe": sender.modality if sender else "text",
            "message": str(payload_dict.get("content", "")),
        }

    if event_type == "task_completed":
        agent_id = _to_int(payload_dict.get("agent_id"), -1)
        agent = agent_index.get(agent_id)
        output_dict = _as_dict(payload_dict.get("output"))
        task_text = str(output_dict.get("predicted") or payload_dict.get("reasoning") or "Task completed")
        return {
            "type": "task_completed",
            "agent_id": agent_id,
            "agent_name": agent.name if agent else f"Agent-{agent_id}",
            "tribe": agent.modality if agent else "text",
            "task": task_text,
            "health_delta": _to_float(payload_dict.get("health_delta"), 0.0),
        }

    if event_type == "agent_death":
        agent_id = _to_int(payload_dict.get("agent_id"), -1)
        agent = agent_index.get(agent_id)
        agent_name = str(payload_dict.get("name") or (agent.name if agent else f"Agent-{agent_id}"))
        return {
            "type": "agent_death",
            "agent_id": agent_id,
            "agent_name": agent_name,
            "tribe": agent.modality if agent else "text",
            "message": f"{agent_name} has perished.",
        }

    if event_type == "agent_born":
        agent_id = _to_int(payload_dict.get("agent_id"), -1)
        agent = agent_index.get(agent_id)
        agent_name = str(payload_dict.get("name") or (agent.name if agent else f"Agent-{agent_id}"))
        return {
            "type": "agent_born",
            "agent_id": agent_id,
            "agent_name": agent_name,
            "tribe": agent.modality if agent else "text",
            "message": f"{agent_name} has been reborn!",
        }

    return event


@asynccontextmanager
async def lifespan(app: FastAPI):
    agents, oracle, society_loop, council = _build_runtime()

    app.state.council = council
    app.state.oracle = oracle
    app.state.society_loop = society_loop
    app.state.agents = agents

    initialise = getattr(council, "initialise", None)
    if callable(initialise):
        maybe_result = initialise()
        if inspect.isawaitable(maybe_result):
            await maybe_result

    await app.state.society_loop.start()
    yield
    await app.state.society_loop.stop()


app = FastAPI(title="AI Society Backend", lifespan=lifespan)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "service": "ai-society-backend",
        "status": "ok",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/evaluate", response_model=EvaluateResponse)
async def evaluate(payload: EvaluateRequest, request: Request) -> EvaluateResponse:
    agents = request.app.state.agents
    agent = next((a for a in agents if a.agent_id == payload.agent_id), None)
    if agent is None:
        agent = agents[0]
    probs = await asyncio.to_thread(agent.get_probabilities, payload.payload)
    return EvaluateResponse(agent_id=agent.agent_id, probabilities=probs)


@app.get("/api/status")
async def api_status(request: Request) -> dict[str, Any]:
    return request.app.state.council.get_status()


@app.websocket("/ws/society")
async def ws_society(websocket: WebSocket) -> None:
    await websocket.accept()
    society_loop = websocket.app.state.society_loop
    agents = websocket.app.state.agents
    society_loop.register_user_active()

    try:
        await websocket.send_json(
            {
                "type": "oracle_proclamation",
                "message": "THE ORACLE OBSERVES. THE SOCIETY AWAKENS.",
            }
        )
        await websocket.send_json(
            {
                "type": "state_update",
                "payload": society_loop._society_status_snapshot(),
            }
        )
        while True:
            event = await society_loop.broadcast_queue.get()
            await websocket.send_json(_normalise_society_event(event, agents))
    except WebSocketDisconnect:
        pass
    finally:
        society_loop.deregister_user_active()


@app.post("/api/society/task")
async def submit_society_task(payload: ManualSocietyTaskRequest, request: Request) -> dict[str, Any]:
    society_loop = request.app.state.society_loop
    oracle = request.app.state.oracle
    agents = request.app.state.agents

    status = society_loop._society_status_snapshot()
    status["manual_request"] = {
        "description": payload.description,
        "modality": payload.modality,
        "payload": payload.payload,
    }

    oracle_task = oracle.generate_task(status)
    task = Task(
        type=TaskType.CLASSIFY,
        assigned_to=oracle_task.assigned_to,
        created_by="oracle",
        description=payload.description,
        payload={**payload.payload, "modality": payload.modality, "task_type": TaskType.CLASSIFY.value},
        deadline_s=oracle_task.deadline_s,
        reward=oracle_task.reward,
        penalty=oracle_task.penalty,
    )

    eligible_agents = [a for a in agents if a.modality == payload.modality]
    if eligible_agents:
        eligible_ids = {a.agent_id for a in eligible_agents}
        if task.assigned_to not in eligible_ids:
            selected = min(eligible_agents, key=lambda a: a.health_score)
            task.assigned_to = selected.agent_id

    await society_loop.enqueue_task(task)
    return {
        "task_id": task.id,
        "assigned_to": task.assigned_to,
        "status": task.status.value,
    }


@app.get("/api/society/history")
async def society_history(request: Request) -> list[dict[str, Any]]:
    society_loop = request.app.state.society_loop
    return society_loop.get_recent_history(50)
