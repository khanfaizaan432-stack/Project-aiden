from __future__ import annotations

import asyncio
import logging
import os
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import torch

from backend.agents import BaseAgent, ImageAgent

from .inheritance import (
    archive_agent,
    compute_inherited_weights,
    select_inheritance_parents,
)
from .memory import AgentMemory
from .messaging import AgentMessage, MessageBus
from .oracle import Oracle
from .task import Task, TaskResult, TaskStatus, TaskType


logger = logging.getLogger(__name__)


class SocietyEventLoop:
    ACTIVE_TICK_INTERVAL = int(os.getenv("SOCIETY_TICK_ACTIVE", "5"))
    IDLE_TICK_INTERVAL = int(os.getenv("SOCIETY_TICK_IDLE", "30"))
    ORACLE_INTERVENTION_HEALTH = 20
    DEATH_HEALTH_THRESHOLD = 0
    MAX_QUEUE_DEPTH = 5

    def __init__(self, agents: list[BaseAgent], oracle: Oracle) -> None:
        self.agents = agents
        self.oracle = oracle

        self.active_users: int = 0
        self.task_queue: asyncio.Queue[Task] = asyncio.Queue()
        self.message_bus: asyncio.Queue[AgentMessage] = asyncio.Queue()
        self.tick_count: int = 0
        self.is_running: bool = False

        self.broadcast_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self.result_history: deque[dict[str, Any]] = deque(maxlen=50)
        self._pending_by_agent: dict[int, deque[Task]] = defaultdict(deque)
        self._loop_task: asyncio.Task[Any] | None = None
        self._wake_event: asyncio.Event = asyncio.Event()
        self._agent_index: dict[int, BaseAgent] = {a.agent_id: a for a in agents}
        self._dead_agent_ids: set[int] = set()
        self.message_store = MessageBus(oracle=oracle)

        for agent in self.agents:
            if getattr(agent, "memory", None) is None:
                agent.memory = AgentMemory(agent.agent_id)

    async def start(self) -> None:
        if self.is_running:
            return
        self.is_running = True
        self._loop_task = asyncio.create_task(self._run(), name="society-event-loop")

    async def stop(self) -> None:
        if not self.is_running:
            return
        self.is_running = False
        if self._loop_task:
            self._loop_task.cancel()
            try:
                await self._loop_task
            except asyncio.CancelledError:
                pass

    async def _run(self) -> None:
        while self.is_running:
            started = asyncio.get_running_loop().time()
            try:
                await self.tick()
            except Exception as exc:
                self._emit_broadcast(
                    {
                        "type": "oracle_proclamation",
                        "payload": {"message": f"The Oracle observes turbulence: {exc}"},
                    }
                )

            elapsed = asyncio.get_running_loop().time() - started
            interval = (
                self.ACTIVE_TICK_INTERVAL if self.active_users > 0 else self.IDLE_TICK_INTERVAL
            )
            timeout = max(0.0, interval - elapsed)
            self._wake_event.clear()
            try:
                await asyncio.wait_for(self._wake_event.wait(), timeout=timeout)
            except TimeoutError:
                pass

    async def tick(self) -> None:
        self.tick_count += 1
        loop = asyncio.get_running_loop()
        logger.info(
            "society_tick tick=%s active_users=%s queue_depth=%s",
            self.tick_count,
            self.active_users,
            self.task_queue.qsize(),
        )

        await self._drain_task_queue_into_pending()
        await self._execute_one_task_per_agent()
        await self._process_inter_agent_messages()

        low_agents = [a for a in self.agents if a.health_score < self.ORACLE_INTERVENTION_HEALTH]
        if low_agents:
            for agent in low_agents:
                message = await loop.run_in_executor(
                    None,
                    self.oracle.generate_intervention,
                    self._agent_status(agent),
                    self._society_status_snapshot(),
                )
                self._emit_broadcast({"type": "oracle_proclamation", "payload": {"message": message}})

        should_generate_task = (
            self.task_queue.empty() and all(len(v) == 0 for v in self._pending_by_agent.values())
        ) or self.tick_count % 10 == 0 or bool(low_agents)

        if should_generate_task:
            try:
                task = await loop.run_in_executor(
                    None,
                    self.oracle.generate_task,
                    self._society_status_snapshot(),
                )
                await self.enqueue_task(task)
            except Exception:
                pass

        for agent in list(self.agents):
            if agent.health_score <= self.DEATH_HEALTH_THRESHOLD and agent.agent_id not in self._dead_agent_ids:
                self._dead_agent_ids.add(agent.agent_id)
                await self.handle_agent_death(agent)

        self._emit_broadcast({"type": "state_update", "payload": self._society_status_snapshot()})

    async def enqueue_task(self, task: Task) -> None:
        await self.task_queue.put(task)
        self._wake_event.set()

    async def _drain_task_queue_into_pending(self) -> None:
        while not self.task_queue.empty():
            task = await self.task_queue.get()
            task_age = datetime.now(timezone.utc) - task.created_at
            if task_age > timedelta(seconds=task.deadline_s):
                task.status = TaskStatus.EXPIRED
                task.error = "Task expired before execution"
                continue

            pending = self._pending_by_agent[task.assigned_to]
            if len(pending) >= self.MAX_QUEUE_DEPTH:
                task.status = TaskStatus.FAILED
                task.error = "Agent queue depth exceeded"
                continue
            pending.append(task)

    async def _execute_one_task_per_agent(self) -> None:
        coroutines: list[asyncio.Task[Any]] = []
        live_agent_ids = {agent.agent_id for agent in self.agents}

        # Drain orphan queues assigned to missing agent ids so they cannot block new work.
        for agent_id, pending in list(self._pending_by_agent.items()):
            if agent_id in live_agent_ids:
                continue
            while pending:
                orphan_task = pending.popleft()
                orphan_task.status = TaskStatus.FAILED
                orphan_task.error = "Assigned agent no longer available"
                self._emit_broadcast(
                    {
                        "type": "task_completed",
                        "payload": {
                            "task_id": orphan_task.id,
                            "agent_id": agent_id,
                            "success": False,
                            "confidence": 0.0,
                            "output": {
                                "error": orphan_task.error,
                                "task_type": orphan_task.type.value,
                            },
                            "reasoning": f"Task failed: {orphan_task.error}",
                            "health_delta": orphan_task.penalty,
                        },
                    }
                )
            del self._pending_by_agent[agent_id]

        for agent in self.agents:
            pending = self._pending_by_agent.get(agent.agent_id)
            if not pending:
                continue
            task = pending.popleft()
            coroutines.append(asyncio.create_task(self._execute_with_timeout(agent, task)))

        if not coroutines:
            return

        await asyncio.gather(*coroutines, return_exceptions=True)

    async def _execute_with_timeout(self, agent: BaseAgent, task: Task) -> None:
        try:
            result = await asyncio.wait_for(self.execute_task(agent, task), timeout=4.5)
            self.result_history.append(result.model_dump())
            self._emit_broadcast({"type": "task_completed", "payload": result.model_dump()})
        except Exception as exc:
            task.status = TaskStatus.FAILED
            task.error = str(exc)
            agent.health_score += task.penalty
            self._emit_broadcast(
                {
                    "type": "task_completed",
                    "payload": {
                        "task_id": task.id,
                        "agent_id": agent.agent_id,
                        "success": False,
                        "confidence": 0.0,
                        "output": {"error": task.error, "task_type": task.type.value},
                        "reasoning": f"Task failed: {task.error}",
                        "health_delta": task.penalty,
                    },
                }
            )

    async def execute_task(self, agent: BaseAgent, task: Task) -> TaskResult:
        task.status = TaskStatus.IN_PROGRESS
        loop = asyncio.get_running_loop()
        success = True
        confidence = 0.5
        output: dict[str, Any] = {"task_type": task.type.value}
        reasoning = ""

        if task.type == TaskType.CLASSIFY:
            probs = await asyncio.to_thread(agent.get_probabilities, task.payload)
            predicted = max(probs, key=probs.get) if probs else "unknown"
            confidence = float(probs.get(predicted, 0.0)) if probs else 0.0
            output.update({"probabilities": probs, "predicted": predicted})
            reasoning = f"Classified input and selected '{predicted}' as most probable class."

        elif task.type == TaskType.BROWSE:
            prompt = (
                "Research this request using available world knowledge. "
                "If web tools are available, prefer web-backed evidence. "
                f"Request: {task.description}\nPayload: {task.payload}"
            )
            data = await loop.run_in_executor(
                None,
                self.oracle.generate_json_response,
                "Return JSON only with keys summary, sources, confidence.\n" + prompt,
            )
            if not data:
                text = await loop.run_in_executor(
                    None,
                    self.oracle.generate_text_response,
                    prompt,
                )
                data = {"summary": text or "No data", "sources": [], "confidence": 0.3}
            confidence = float(data.get("confidence", 0.3))
            output.update(data)
            reasoning = str(data.get("summary", "Browsed external context."))

        elif task.type == TaskType.DEBATE:
            vote_a = task.payload.get("agent_a_vote", {})
            vote_b = task.payload.get("agent_b_vote", {})
            context = task.payload.get("context", {})
            decision = await loop.run_in_executor(
                None,
                self.oracle.evaluate_debate,
                vote_a,
                vote_b,
                context,
            )
            winner_id = int(decision.get("winner_id", -1))
            confidence = float(decision.get("confidence", 0.5))
            reasoning = str(decision.get("reasoning", "Debate adjudicated."))
            output.update(decision)

            a_agent = self._agent_index.get(int(vote_a.get("agent_id", -1)))
            b_agent = self._agent_index.get(int(vote_b.get("agent_id", -1)))
            if a_agent and b_agent:
                if winner_id == a_agent.agent_id:
                    a_agent.health_score += 5
                    b_agent.health_score -= 5
                elif winner_id == b_agent.agent_id:
                    b_agent.health_score += 5
                    a_agent.health_score -= 5

        elif task.type == TaskType.REFLECT:
            mistakes = await agent.memory.aget_mistake_summary(n=10)
            prompt = (
                "You are an AI agent reflecting on failures. Return JSON only with keys "
                "insights (list), action_plan (list), confidence.\n"
                f"Mistakes: {mistakes}"
            )
            reflection = await loop.run_in_executor(
                None,
                self.oracle.generate_json_response,
                prompt,
            )
            if not reflection:
                reflection = {
                    "insights": ["Need more calibration on low-confidence predictions."],
                    "action_plan": ["Defer uncertain decisions to debate tasks."],
                    "confidence": 0.4,
                }
            confidence = float(reflection.get("confidence", 0.4))
            output.update(reflection)
            reasoning = "; ".join(reflection.get("insights", []))

        elif task.type == TaskType.TEACH:
            student_id = int(task.payload.get("student_id", -1))
            student = self._agent_index.get(student_id)
            if student is None:
                success = False
                confidence = 0.0
                reasoning = "Student agent not found."
                output["error"] = reasoning
            else:
                k = int(task.payload.get("top_k", 5))
                teacher_state = agent.get_state_dict()
                student_state = student.get_state_dict()
                scored = []
                for layer_key, tensor in teacher_state.items():
                    if torch.is_tensor(tensor) and tensor.dtype.is_floating_point:
                        scored.append((layer_key, float(tensor.abs().mean().item())))
                scored.sort(key=lambda x: x[1], reverse=True)
                for layer_key, _ in scored[:k]:
                    if layer_key in student_state and torch.is_tensor(student_state[layer_key]):
                        student_state[layer_key] = teacher_state[layer_key].detach().clone()
                student.load_state_dict(student_state)
                confidence = 0.7
                reasoning = f"Transferred top-{k} high-activation weight patterns to student {student_id}."
                output["transferred_layers"] = [layer_key for layer_key, _ in scored[:k]]

        if success:
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now(timezone.utc)
            task.confidence = confidence
            task.outcome = output
            health_delta = task.reward
            agent.health_score += task.reward
        else:
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now(timezone.utc)
            task.confidence = confidence
            task.outcome = output
            health_delta = task.penalty
            agent.health_score += task.penalty

        result = TaskResult(
            task_id=task.id,
            agent_id=agent.agent_id,
            success=success,
            confidence=confidence,
            output=output,
            reasoning=reasoning,
            health_delta=health_delta,
        )

        await agent.memory.astore(result)
        return result

    async def _process_inter_agent_messages(self) -> None:
        while not self.message_bus.empty():
            message = await self.message_bus.get()
            self.message_store.send(message)
            self._emit_broadcast({"type": "agent_message", "payload": message.model_dump()})

    async def handle_agent_death(self, agent: BaseAgent) -> None:
        loop = asyncio.get_running_loop()
        archive_dir = str(Path("models") / "archived")
        archived_path = await asyncio.to_thread(archive_agent, agent, archive_dir)

        living = [a for a in self.agents if a.agent_id != agent.agent_id and a.health_score > 0]
        if not living:
            return

        parent_a, parent_b = select_inheritance_parents(agent, living)
        inherited_state = compute_inherited_weights(
            parent_a.get_state_dict(),
            parent_b.get_state_dict(),
            noise_std=0.01,
        )

        new_id = max(a.agent_id for a in self.agents) + 1
        new_name = f"Agent-{new_id}"
        new_personality = "Adaptive, relentless, and slightly theatrical"

        prompt = (
            "Return JSON only with keys name and personality for a newly spawned AI agent."
            f" Parent A: {parent_a.name}. Parent B: {parent_b.name}."
        )
        data = await loop.run_in_executor(
            None,
            self.oracle.generate_json_response,
            prompt,
        )
        if data:
            new_name = str(data.get("name", new_name))
            new_personality = str(data.get("personality", new_personality))

        newborn = ImageAgent(
            agent_id=new_id,
            name=new_name,
            personality=new_personality,
            modality=agent.modality,
        )
        newborn.load_state_dict(inherited_state)
        newborn.health_score = 50.0
        newborn.total_votes = 0
        newborn.memory = AgentMemory(new_id)

        self.agents.append(newborn)
        self._agent_index[newborn.agent_id] = newborn

        announcement = await loop.run_in_executor(
            None,
            self.oracle.generate_spawn_announcement,
            [self._agent_status(parent_a), self._agent_status(parent_b)],
            self._agent_status(newborn),
        )

        self._emit_broadcast(
            {
                "type": "agent_death",
                "payload": {
                    "agent_id": agent.agent_id,
                    "name": agent.name,
                    "archived_path": archived_path,
                },
            }
        )
        self._emit_broadcast(
            {
                "type": "agent_born",
                "payload": {
                    "agent_id": newborn.agent_id,
                    "name": newborn.name,
                    "personality": newborn.personality,
                    "announcement": announcement,
                },
            }
        )

    def register_user_active(self) -> None:
        self.active_users += 1
        self._wake_event.set()

    def deregister_user_active(self) -> None:
        self.active_users = max(0, self.active_users - 1)

    def get_recent_history(self, n: int = 50) -> list[dict[str, Any]]:
        return list(self.result_history)[-n:]

    def _agent_status(self, agent: BaseAgent) -> dict[str, Any]:
        return {
            "agent_id": agent.agent_id,
            "name": agent.name,
            "personality": agent.personality,
            "modality": agent.modality,
            "health_score": agent.health_score,
            "total_votes": agent.total_votes,
        }

    def _society_status_snapshot(self) -> dict[str, Any]:
        failed_recent = [r for r in self.result_history if not bool(r.get("success", True))][-20:]
        return {
            "tick_count": self.tick_count,
            "active_users": self.active_users,
            "queue_depth": self.task_queue.qsize(),
            "agents": [self._agent_status(a) for a in self.agents],
            "recent_failures": failed_recent,
        }

    def _emit_broadcast(self, event: dict[str, Any]) -> None:
        try:
            self.broadcast_queue.put_nowait(event)
        except asyncio.QueueFull:
            pass
