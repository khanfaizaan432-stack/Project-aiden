from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from backend.agents import ImageAgent
from backend.society.event_loop import SocietyEventLoop
from backend.society.oracle import Oracle
from backend.society.task import Task, TaskType


@pytest.mark.asyncio
async def test_society_engine_smoke(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(tmp_path / "chroma"))

    agent_a = ImageAgent(agent_id=0, name="Cipher", personality="coldly logical")
    agent_b = ImageAgent(agent_id=1, name="Nyx", personality="audacious")
    agents = [agent_a, agent_b]

    oracle = Oracle()

    def fake_generate_task(status: dict):
        return Task(
            type=TaskType.REFLECT,
            assigned_to=0,
            created_by="oracle",
            description="Reflect on recent errors",
            payload={"task_type": "REFLECT"},
        )

    monkeypatch.setattr(oracle, "generate_task", fake_generate_task)
    monkeypatch.setattr(oracle, "generate_json_response", lambda prompt: {"confidence": 0.77, "insights": ["test"], "action_plan": ["test"]})
    monkeypatch.setattr(oracle, "generate_text_response", lambda prompt: "oracle-text")
    monkeypatch.setattr(oracle, "generate_intervention", lambda dying, status: "intervention")
    monkeypatch.setattr(oracle, "generate_spawn_announcement", lambda parents, new_agent: "born")

    loop = SocietyEventLoop(agents=agents, oracle=oracle)

    classify_task = Task(
        type=TaskType.CLASSIFY,
        assigned_to=0,
        created_by="oracle",
        description="Classify synthetic sample",
        payload={"image_tensor": [[[
            [0.1] * 32 for _ in range(32)
        ] for _ in range(3)]], "task_type": "CLASSIFY"},
    )
    await loop.enqueue_task(classify_task)

    await loop.tick()
    history = loop.get_recent_history()
    assert history, "Expected at least one completed task result after tick"
    assert history[-1]["agent_id"] == 0

    # Trigger death and rebirth path.
    agent_a.health_score = -100.0
    await loop.tick()

    assert len(loop.agents) >= 3, "Expected a newborn agent after death handling"
    assert any(evt.get("type") == "agent_born" for evt in list(loop.broadcast_queue._queue))
