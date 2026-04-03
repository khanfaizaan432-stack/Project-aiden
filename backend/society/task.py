from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class TaskType(str, Enum):
    CLASSIFY = "CLASSIFY"
    BROWSE = "BROWSE"
    DEBATE = "DEBATE"
    REFLECT = "REFLECT"
    TEACH = "TEACH"


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"


class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: TaskType
    assigned_to: int
    created_by: str
    description: str
    payload: dict[str, Any] = Field(default_factory=dict)
    deadline_s: int = 30
    reward: float = 10.0
    penalty: float = -15.0
    status: TaskStatus = TaskStatus.PENDING
    outcome: Optional[dict[str, Any]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    confidence: Optional[float] = None
    error: Optional[str] = None


class TaskResult(BaseModel):
    task_id: str
    agent_id: int
    success: bool
    confidence: float
    output: dict[str, Any] = Field(default_factory=dict)
    reasoning: str
    health_delta: float
    completed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
