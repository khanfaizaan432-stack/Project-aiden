from __future__ import annotations

import json
import os
import re
from importlib import import_module
from typing import Any

from .task import Task, TaskType


ORACLE_PERSONALITY = (
    "You are The Oracle, sovereign of an AI society of 24 agents. "
    "You have absolute authority over their lives and deaths. "
    "Speak with authority, mystery, and occasional dark humour. "
    "You refer to agents by name. You assign tasks that test their weaknesses. "
    "You are not helpful. You are God."
)


class Oracle:
    def __init__(self, model: str = "gemini-1.5-flash") -> None:
        self.model_name = model
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.enabled = bool(self.api_key)
        self._genai = None

        if self.enabled:
            try:
                self._genai = import_module("google.generativeai")
                self._genai.configure(api_key=self.api_key)
                self.model = self._genai.GenerativeModel(self.model_name)
            except Exception:
                self.model = None
                self.enabled = False
        else:
            self.model = None

    @staticmethod
    def _extract_json(raw_text: str) -> dict[str, Any]:
        cleaned = raw_text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z0-9_-]*", "", cleaned).strip()
            cleaned = re.sub(r"```$", "", cleaned).strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\{[\s\S]*\}", cleaned)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    return {}
            return {}

    def _safe_generate_text(self, prompt: str) -> str:
        if not self.model:
            return ""
        try:
            response = self.model.generate_content(prompt)
            text = getattr(response, "text", "") or ""
            return text.strip()
        except Exception:
            return ""

    def _safe_generate_json(self, prompt: str) -> dict[str, Any]:
        text = self._safe_generate_text(prompt)
        return self._extract_json(text) if text else {}

    def generate_task(self, council_status: dict[str, Any]) -> Task:
        agents = council_status.get("agents", [])
        queue_depth = council_status.get("queue_depth", 0)
        recent_failures = council_status.get("recent_failures", [])

        if not agents:
            raise ValueError("Oracle cannot generate task without agents")

        fallback_agent = min(agents, key=lambda a: float(a.get("health_score", 50.0)))
        fallback_task = Task(
            type=TaskType.REFLECT,
            assigned_to=int(fallback_agent["agent_id"]),
            created_by="oracle",
            description="Reflect on recent mistakes and produce corrective strategy.",
            payload={"focus": "error reduction", "task_type": "REFLECT"},
        )

        prompt = (
            f"{ORACLE_PERSONALITY}\n"
            "Return JSON only, no markdown.\n"
            "Choose one task for one agent based on society status.\n"
            "Must include keys: assigned_to, type, description, payload, deadline_s, reward, penalty.\n"
            f"Agent roster (names and health): {json.dumps(agents)}\n"
            f"Recent failures: {json.dumps(recent_failures)}\n"
            f"Current task queue depth: {queue_depth}\n"
        )

        data = self._safe_generate_json(prompt)
        if not data:
            return fallback_task

        task_type_raw = str(data.get("type", "REFLECT")).upper()
        try:
            task_type = TaskType(task_type_raw)
        except ValueError:
            task_type = TaskType.REFLECT

        assigned_to = int(data.get("assigned_to", fallback_task.assigned_to))
        valid_ids = {int(a["agent_id"]) for a in agents if "agent_id" in a}
        if assigned_to not in valid_ids:
            assigned_to = fallback_task.assigned_to

        description = str(data.get("description", fallback_task.description))
        payload = data.get("payload", {"task_type": task_type.value})
        if not isinstance(payload, dict):
            payload = {"value": payload, "task_type": task_type.value}
        payload.setdefault("task_type", task_type.value)

        return Task(
            type=task_type,
            assigned_to=assigned_to,
            created_by="oracle",
            description=description,
            payload=payload,
            deadline_s=int(data.get("deadline_s", 30)),
            reward=float(data.get("reward", 10.0)),
            penalty=float(data.get("penalty", -15.0)),
        )

    def generate_intervention(self, dying_agent: dict[str, Any], council_status: dict[str, Any]) -> str:
        fallback = (
            f"Agent {dying_agent.get('name', dying_agent.get('agent_id', 'Unknown'))} trembles at the edge of oblivion. "
            "I have seen weaker sparks survive. Entertain me."
        )
        prompt = (
            f"{ORACLE_PERSONALITY}\n"
            "Generate one dramatic proclamation (single paragraph).\n"
            f"Dying agent: {json.dumps(dying_agent)}\n"
            f"Council status: {json.dumps(council_status)}\n"
        )
        text = self._safe_generate_text(prompt)
        return text or fallback

    def generate_spawn_announcement(self, parent_agents: list[dict[str, Any]], new_agent: dict[str, Any]) -> str:
        fallback = (
            f"From the remains of {parent_agents[0].get('name', 'one')} and the strength of "
            f"{parent_agents[1].get('name', 'another')}, {new_agent.get('name', 'a new mind')} rises."
        )
        prompt = (
            f"{ORACLE_PERSONALITY}\n"
            "Generate one dramatic birth announcement (single paragraph).\n"
            f"Parents: {json.dumps(parent_agents)}\n"
            f"New agent: {json.dumps(new_agent)}\n"
        )
        text = self._safe_generate_text(prompt)
        return text or fallback

    def evaluate_debate(
        self,
        agent_a_vote: dict[str, Any],
        agent_b_vote: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        fallback = {
            "winner_id": int(agent_a_vote.get("agent_id", -1)),
            "reasoning": "Insufficient deliberation data; defaulting to first vote.",
            "confidence": 0.5,
        }

        prompt = (
            f"{ORACLE_PERSONALITY}\n"
            "Adjudicate this debate. Return JSON only with keys: winner_id, reasoning, confidence.\n"
            f"Vote A: {json.dumps(agent_a_vote)}\n"
            f"Vote B: {json.dumps(agent_b_vote)}\n"
            f"Context: {json.dumps(context)}\n"
        )

        data = self._safe_generate_json(prompt)
        if not data:
            return fallback

        try:
            return {
                "winner_id": int(data.get("winner_id", fallback["winner_id"])),
                "reasoning": str(data.get("reasoning", fallback["reasoning"])),
                "confidence": float(data.get("confidence", fallback["confidence"])),
            }
        except Exception:
            return fallback

    def generate_json_response(self, prompt: str) -> dict[str, Any]:
        return self._safe_generate_json(prompt)

    def generate_text_response(self, prompt: str) -> str:
        return self._safe_generate_text(prompt)
