from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class AgentMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    from_agent_id: int
    to_agent_id: int
    content: str
    message_type: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    read: bool = False


class MessageBus:
    def __init__(self, oracle: Any | None = None, max_messages: int = 500) -> None:
        self.oracle = oracle
        self.messages: deque[AgentMessage] = deque(maxlen=max_messages)

    def send(self, message: AgentMessage) -> None:
        self.messages.append(message)

    def get_messages(self, agent_id: int, unread_only: bool = True) -> list[AgentMessage]:
        out: list[AgentMessage] = []
        for message in self.messages:
            if message.to_agent_id not in (-1, agent_id):
                continue
            if unread_only and message.read:
                continue
            out.append(message)
        return out

    def get_recent_broadcast(self, n: int = 20) -> list[AgentMessage]:
        broadcasts = [m for m in self.messages if m.to_agent_id == -1]
        return broadcasts[-n:]

    def mark_read(self, message_id: str) -> None:
        for message in self.messages:
            if message.id == message_id:
                message.read = True
                return

    def generate_agent_message(
        self,
        from_agent: Any,
        context: dict[str, Any],
        message_type: str,
    ) -> AgentMessage:
        to_agent_id = int(context.get("to_agent_id", -1))
        fallback_content = (
            f"[{message_type}] {from_agent.name}: observing state shift at tick "
            f"{context.get('tick_count', 'unknown')}."
        )

        content = fallback_content
        if self.oracle is not None:
            prompt = (
                "Write a single short in-character message for an AI agent. "
                "No markdown, no quotes.\n"
                f"Agent profile: name={from_agent.name}, personality={from_agent.personality}\n"
                f"Message type: {message_type}\n"
                f"Context: {context}"
            )
            try:
                text = self.oracle.generate_text_response(prompt)
                if text:
                    content = text
            except Exception:
                content = fallback_content

        return AgentMessage(
            from_agent_id=from_agent.agent_id,
            to_agent_id=to_agent_id,
            content=content,
            message_type=message_type,
        )
