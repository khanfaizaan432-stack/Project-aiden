from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class EvaluateRequest(BaseModel):
    agent_id: int
    payload: dict[str, Any] = Field(default_factory=dict)


class EvaluateResponse(BaseModel):
    agent_id: int
    probabilities: dict[str, float]


class ManualSocietyTaskRequest(BaseModel):
    description: str
    modality: str
    payload: dict[str, Any] = Field(default_factory=dict)
