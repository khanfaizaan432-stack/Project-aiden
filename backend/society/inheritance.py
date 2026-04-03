from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Tuple

import torch

from backend.agents import BaseAgent


def compute_inherited_weights(
    parent_a_state_dict: Dict[str, Any],
    parent_b_state_dict: Dict[str, Any],
    noise_std: float = 0.01,
) -> Dict[str, Any]:
    inherited: Dict[str, Any] = {}
    keys = set(parent_a_state_dict.keys()).intersection(set(parent_b_state_dict.keys()))

    for key in keys:
        tensor_a = parent_a_state_dict[key]
        tensor_b = parent_b_state_dict[key]

        if torch.is_tensor(tensor_a) and torch.is_tensor(tensor_b):
            # Ensure CPU tensors before arithmetic to satisfy deterministic CPU-only inheritance.
            tensor_a = tensor_a.detach().to("cpu")
            tensor_b = tensor_b.detach().to("cpu")
            if tensor_a.dtype.is_floating_point and tensor_b.dtype.is_floating_point:
                mixed = (0.7 * tensor_a) + (0.3 * tensor_b)
                mixed = mixed + (torch.randn_like(mixed) * noise_std)
                inherited[key] = mixed
            else:
                inherited[key] = tensor_a.clone()
        else:
            inherited[key] = tensor_a

    return inherited


def archive_agent(agent: BaseAgent, archive_dir: str) -> str:
    archive_path = Path(archive_dir)
    archive_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    weights_file = archive_path / f"agent_{agent.agent_id}_{timestamp}.pth"
    metadata_file = archive_path / f"agent_{agent.agent_id}_{timestamp}.json"

    torch.save(agent.get_state_dict(), str(weights_file))

    metadata: Dict[str, Any] = {
        "agent_id": agent.agent_id,
        "name": agent.name,
        "personality": agent.personality,
        "final_health": agent.health_score,
        "total_votes": agent.total_votes,
        "archived_at": datetime.now(timezone.utc).isoformat(),
    }
    metadata_file.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    return str(weights_file)


def select_inheritance_parents(
    dead_agent: BaseAgent,
    living_agents: list[BaseAgent],
) -> Tuple[BaseAgent, BaseAgent]:
    same_modality = [a for a in living_agents if a.modality == dead_agent.modality and a.health_score > 0]
    if same_modality:
        parent_b = max(same_modality, key=lambda a: a.health_score)
    else:
        parent_b = max(living_agents, key=lambda a: a.health_score)

    return dead_agent, parent_b
