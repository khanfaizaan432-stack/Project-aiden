from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class EvaluateRequest(BaseModel):
    agent_id: int
    payload: dict[str, Any] = Field(default_factory=dict)


class EvaluateVote(BaseModel):
    agent_id: int
    agent_name: str
    probabilities: dict[str, float]


class EvaluateResponse(BaseModel):
    agent_id: int
    agent_name: str
    agent_ids: list[int] = Field(default_factory=list)
    agent_names: list[str] = Field(default_factory=list)
    predicted: str
    probabilities: dict[str, float]
    votes: list[EvaluateVote] = Field(default_factory=list)


class ManualSocietyTaskRequest(BaseModel):
    description: str
    modality: str
    payload: dict[str, Any] = Field(default_factory=dict)
