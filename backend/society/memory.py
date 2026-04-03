from __future__ import annotations

import asyncio
import os
from statistics import mean
from typing import Any

from .task import TaskResult


class AgentMemory:
    def __init__(self, agent_id: int, persist_directory: str = "./chroma_db") -> None:
        self.agent_id = agent_id
        self._in_memory_events: list[dict[str, Any]] = []
        self.collection = None
        persist_dir = os.getenv("CHROMA_PERSIST_DIR", persist_directory)

        try:
            import chromadb  # type: ignore

            client = chromadb.PersistentClient(path=persist_dir)
            self.collection = client.get_or_create_collection(
                name=f"agent_{agent_id}_memory"
            )
        except Exception:
            self.collection = None

    def store(self, task_result: TaskResult) -> None:
        output_summary = str(task_result.output)[:500]
        task_type = task_result.output.get("task_type", "unknown")
        doc_id = f"{task_result.task_id}:{task_result.completed_at.isoformat()}"
        metadata = {
            "task_id": task_result.task_id,
            "agent_id": task_result.agent_id,
            "task_type": task_type,
            "success": bool(task_result.success),
            "confidence": float(task_result.confidence),
            "timestamp": task_result.completed_at.isoformat(),
            "output_summary": output_summary,
        }

        if self.collection is not None:
            self.collection.add(
                ids=[doc_id],
                documents=[task_result.reasoning],
                metadatas=[metadata],
            )
            return

        self._in_memory_events.append(
            {
                "id": doc_id,
                "reasoning": task_result.reasoning,
                "metadata": metadata,
            }
        )

    def recall(self, query: str, n_results: int = 5) -> list[dict[str, Any]]:
        if self.collection is None:
            # Simple local fallback retrieval by keyword overlap.
            scored: list[tuple[int, dict[str, Any]]] = []
            query_terms = set(query.lower().split())
            for item in self._in_memory_events:
                reason = item["reasoning"].lower()
                score = sum(1 for t in query_terms if t in reason)
                scored.append((score, item))
            scored.sort(key=lambda x: x[0], reverse=True)
            return [
                {
                    "reasoning": i["reasoning"],
                    "metadata": i["metadata"],
                    "distance": None,
                }
                for _, i in scored[:n_results]
            ]

        result = self.collection.query(query_texts=[query], n_results=n_results)
        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0] if "distances" in result else []

        experiences: list[dict[str, Any]] = []
        for idx, doc in enumerate(docs):
            meta = metas[idx] if idx < len(metas) else {}
            distance = distances[idx] if idx < len(distances) else None
            experiences.append(
                {
                    "reasoning": doc,
                    "metadata": meta,
                    "distance": distance,
                }
            )
        return experiences

    def get_mistake_summary(self, n: int = 10) -> list[dict[str, Any]]:
        if self.collection is None:
            failed = [
                i
                for i in self._in_memory_events
                if not bool(i.get("metadata", {}).get("success", False))
            ]
            return [
                {"reasoning": i["reasoning"], "metadata": i.get("metadata", {})}
                for i in failed[-n:]
            ]

        data = self.collection.get(include=["documents", "metadatas"])
        docs = data.get("documents", [])
        metas = data.get("metadatas", [])

        def is_failure(meta: dict[str, Any]) -> bool:
            success = meta.get("success", True)
            if isinstance(success, bool):
                return not success
            if isinstance(success, str):
                return success.strip().lower() not in {"true", "1", "yes"}
            return not bool(success)

        failed_pairs = [
            (doc, meta if isinstance(meta, dict) else {})
            for doc, meta in zip(docs, metas)
            if is_failure(meta if isinstance(meta, dict) else {})
        ]
        failed_pairs = failed_pairs[-n:]

        summary: list[dict[str, Any]] = []
        for doc, meta in failed_pairs:
            summary.append(
                {
                    "reasoning": doc,
                    "metadata": meta,
                }
            )
        return summary

    def get_stats(self) -> dict[str, Any]:
        if self.collection is None:
            metas = [i.get("metadata", {}) for i in self._in_memory_events]
            total = len(metas)
            if total == 0:
                return {"total_tasks": 0, "success_rate": 0.0, "avg_confidence": 0.0}
            success_rate = sum(1 for m in metas if bool(m.get("success", False))) / total
            avg_confidence = mean(float(m.get("confidence", 0.0)) for m in metas)
            return {
                "total_tasks": total,
                "success_rate": success_rate,
                "avg_confidence": avg_confidence,
            }

        data = self.collection.get(include=["metadatas"])
        metas = data.get("metadatas", [])
        total = len(metas)
        if total == 0:
            return {"total_tasks": 0, "success_rate": 0.0, "avg_confidence": 0.0}

        success_values = [1.0 for m in metas if bool(m.get("success"))]
        confidence_values = [float(m.get("confidence", 0.0)) for m in metas]
        success_rate = len(success_values) / total
        avg_confidence = mean(confidence_values) if confidence_values else 0.0
        return {
            "total_tasks": total,
            "success_rate": success_rate,
            "avg_confidence": avg_confidence,
        }

    async def astore(self, task_result: TaskResult) -> None:
        await asyncio.to_thread(self.store, task_result)

    async def arecall(self, query: str, n_results: int = 5) -> list[dict[str, Any]]:
        return await asyncio.to_thread(self.recall, query, n_results)

    async def aget_mistake_summary(self, n: int = 10) -> list[dict[str, Any]]:
        return await asyncio.to_thread(self.get_mistake_summary, n)

    async def aget_stats(self) -> dict[str, Any]:
        return await asyncio.to_thread(self.get_stats)
