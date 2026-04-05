from __future__ import annotations

import asyncio
import inspect
import struct
import zlib
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, cast

import torch
from fastapi import FastAPI, File, HTTPException, Request, UploadFile, WebSocket, WebSocketDisconnect

from backend.agents import BaseAgent, CIFAR10_CLASSES, EdenCouncil, load_default_agents
from backend.schemas import EvaluateResponse, EvaluateVote, ManualSocietyTaskRequest
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


def _resize_rgb_bytes(rgb_bytes: bytes, width: int, height: int, target_size: int = 32) -> torch.Tensor:
    resized = bytearray(target_size * target_size * 3)
    for y in range(target_size):
        src_y = min(height - 1, (y * height) // target_size)
        for x in range(target_size):
            src_x = min(width - 1, (x * width) // target_size)
            source_index = (src_y * width + src_x) * 3
            target_index = (y * target_size + x) * 3
            resized[target_index : target_index + 3] = rgb_bytes[source_index : source_index + 3]
    tensor = torch.tensor(list(resized), dtype=torch.float32).view(32, 32, 3)
    return tensor.permute(2, 0, 1).unsqueeze(0) / 255.0


def _decode_png(image_bytes: bytes) -> torch.Tensor:
    png_signature = b"\x89PNG\r\n\x1a\n"
    if not image_bytes.startswith(png_signature):
        raise ValueError("Unsupported format")

    offset = len(png_signature)
    width = 0
    height = 0
    bit_depth = 0
    color_type = 0
    idat_parts: list[bytes] = []

    while offset + 8 <= len(image_bytes):
        length = struct.unpack(">I", image_bytes[offset : offset + 4])[0]
        chunk_type = image_bytes[offset + 4 : offset + 8]
        chunk_data = image_bytes[offset + 8 : offset + 8 + length]
        offset += 12 + length

        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack(
                ">IIBBBBB", chunk_data
            )
            if compression != 0 or filter_method != 0 or interlace != 0:
                raise ValueError("Unsupported PNG encoding")
            if bit_depth != 8 or color_type not in {0, 2, 6}:
                raise ValueError("Unsupported PNG color mode")
        elif chunk_type == b"IDAT":
            idat_parts.append(chunk_data)
        elif chunk_type == b"IEND":
            break

    if width <= 0 or height <= 0 or not idat_parts:
        raise ValueError("Invalid PNG data")

    decompressed = zlib.decompress(b"".join(idat_parts))
    channels = 1 if color_type == 0 else 3 if color_type == 2 else 4
    bytes_per_pixel = channels
    stride = width * channels
    rows: list[bytearray] = []
    cursor = 0
    previous_row = bytearray(stride)

    def paeth(left: int, above: int, upper_left: int) -> int:
        estimate = left + above - upper_left
        left_delta = abs(estimate - left)
        above_delta = abs(estimate - above)
        upper_left_delta = abs(estimate - upper_left)
        if left_delta <= above_delta and left_delta <= upper_left_delta:
            return left
        if above_delta <= upper_left_delta:
            return above
        return upper_left

    while cursor < len(decompressed):
        filter_type = decompressed[cursor]
        cursor += 1
        row = bytearray(decompressed[cursor : cursor + stride])
        cursor += stride

        if filter_type == 1:
            for index in range(bytes_per_pixel, len(row)):
                row[index] = (row[index] + row[index - bytes_per_pixel]) % 256
        elif filter_type == 2:
            for index in range(len(row)):
                row[index] = (row[index] + previous_row[index]) % 256
        elif filter_type == 3:
            for index in range(len(row)):
                left = row[index - bytes_per_pixel] if index >= bytes_per_pixel else 0
                up = previous_row[index]
                row[index] = (row[index] + ((left + up) // 2)) % 256
        elif filter_type == 4:
            for index in range(len(row)):
                left = row[index - bytes_per_pixel] if index >= bytes_per_pixel else 0
                up = previous_row[index]
                up_left = previous_row[index - bytes_per_pixel] if index >= bytes_per_pixel else 0
                row[index] = (row[index] + paeth(left, up, up_left)) % 256
        elif filter_type != 0:
            raise ValueError("Unsupported PNG filter")

        rows.append(row)
        previous_row = row

    rgb_bytes = bytearray(width * height * 3)
    for y, row in enumerate(rows):
        for x in range(width):
            source_index = x * channels
            target_index = (y * width + x) * 3
            if color_type == 0:
                value = row[source_index]
                rgb_bytes[target_index : target_index + 3] = bytes((value, value, value))
            elif color_type == 2:
                rgb_bytes[target_index : target_index + 3] = row[source_index : source_index + 3]
            else:
                rgb_bytes[target_index : target_index + 3] = row[source_index : source_index + 3]

    return _resize_rgb_bytes(bytes(rgb_bytes), width, height)


def _bytes_to_tensor(image_bytes: bytes) -> torch.Tensor:
    if not image_bytes:
        image_bytes = b"\x00"

    try:
        return _decode_png(image_bytes)
    except Exception:
        raw = bytearray(32 * 32 * 3)
        for index in range(len(raw)):
                        raw[index] = image_bytes[index % len(image_bytes)]
        tensor = torch.tensor(list(raw), dtype=torch.float32).view(32, 32, 3)
        return tensor.permute(2, 0, 1).unsqueeze(0) / 255.0


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
async def evaluate(request: Request, image: UploadFile = File(...)) -> EvaluateResponse:
    agents = [agent for agent in request.app.state.agents if agent.modality in {"vision", "image"}]
    if not agents:
        raise HTTPException(status_code=503, detail="No image agents are available for evaluation.")

    try:
        image_bytes = await image.read()
        image_tensor = await asyncio.to_thread(_bytes_to_tensor, image_bytes)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid image upload.") from exc

    tensor_payload = {"image_tensor": image_tensor.tolist()}
    vote_results = await asyncio.gather(
        *[asyncio.to_thread(agent.get_probabilities, tensor_payload) for agent in agents]
    )

    averaged_probabilities = {label: 0.0 for label in CIFAR10_CLASSES}
    for probabilities in vote_results:
        for label, value in probabilities.items():
            averaged_probabilities[label] += float(value)

    vote_count = float(len(vote_results))
    for label in averaged_probabilities:
        averaged_probabilities[label] /= vote_count

    predicted = max(averaged_probabilities, key=averaged_probabilities.get)

    return EvaluateResponse(
        agent_id=agents[0].agent_id,
        agent_name="ensemble",
        agent_ids=[agent.agent_id for agent in agents],
        agent_names=[agent.name for agent in agents],
        predicted=predicted,
        probabilities=averaged_probabilities,
        votes=[
            EvaluateVote(agent_id=agent.agent_id, agent_name=agent.name, probabilities=probabilities)
            for agent, probabilities in zip(agents, vote_results)
        ],
    )


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
