from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch
import torch.nn as nn


CIFAR10_CLASSES = [
    "airplane",
    "automobile",
    "bird",
    "cat",
    "deer",
    "dog",
    "frog",
    "horse",
    "ship",
    "truck",
]


class FallbackCNN(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Flatten(),
            nn.Linear(32 * 8 * 8, 128),
            nn.ReLU(),
            nn.Linear(128, 10),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


@dataclass
class BaseAgent:
    agent_id: int
    name: str
    personality: str
    modality: str = "vision"
    health_score: float = 100.0
    total_votes: int = 0

    def __post_init__(self) -> None:
        self.model: nn.Module = FallbackCNN().cpu().eval()
        self.health_score = float(self.health_score)
        self.total_votes = int(self.total_votes)
        self.memory = None

    def get_state_dict(self) -> dict[str, torch.Tensor]:
        if self.model is None:
            raise RuntimeError(f"Agent {self.name} has no model loaded.")
        return {k: v.detach().cpu().clone() for k, v in self.model.state_dict().items()}

    def load_state_dict(self, state_dict: dict[str, torch.Tensor]) -> None:
        if self.model is None:
            raise RuntimeError(f"Agent {self.name} has no model loaded.")
        self.model.load_state_dict(state_dict, strict=False)
        self.model.eval()

    def get_probabilities(self, payload: dict[str, Any]) -> dict[str, float]:
        # Supports either provided tensor-like input or deterministic random fallback.
        image_tensor = payload.get("image_tensor")
        if image_tensor is None:
            torch.manual_seed(self.agent_id + int(self.total_votes))
            x = torch.randn(1, 3, 32, 32)
        else:
            x = torch.tensor(image_tensor, dtype=torch.float32)
            if x.dim() == 3:
                x = x.unsqueeze(0)

        with torch.no_grad():
            logits = self.model(x.cpu())
            probs = torch.softmax(logits[0], dim=-1)

        self.total_votes += 1
        return {label: float(probs[i].item()) for i, label in enumerate(CIFAR10_CLASSES)}


class ImageAgent(BaseAgent):
    @classmethod
    def from_weights(
        cls,
        agent_id: int,
        weights_path: str | Path,
        name: str,
        personality: str,
    ) -> "ImageAgent":
        agent = cls(agent_id=agent_id, name=name, personality=personality, modality="vision")
        try:
            state = torch.load(str(weights_path), map_location="cpu")
            if isinstance(state, dict):
                # Handle checkpoints that wrap the model state dict.
                if "state_dict" in state and isinstance(state["state_dict"], dict):
                    state = state["state_dict"]
                agent.load_state_dict(state)
        except Exception:
            pass
        return agent


class EdenCouncil:
    def __init__(self, agents: list[BaseAgent]) -> None:
        self.agents = agents

    def get_status(self) -> dict[str, Any]:
        return {
            "agents": [
                {
                    "agent_id": a.agent_id,
                    "name": a.name,
                    "personality": a.personality,
                    "modality": a.modality,
                    "health_score": a.health_score,
                    "total_votes": a.total_votes,
                }
                for a in self.agents
            ]
        }


def load_default_agents(base_dir: str | Path) -> list[ImageAgent]:
    base = Path(base_dir)
    weight_files = sorted(base.glob("agent_*.pth"))
    if not weight_files:
        return [
            ImageAgent(agent_id=i, name=f"Agent-{i}", personality="Analytical")
            for i in range(4)
        ]

    names = ["Cipher", "Nyx", "Atlas", "Vesper", "Quill", "Astra"]
    personalities = [
        "coldly logical",
        "audacious and skeptical",
        "stoic strategist",
        "playful contrarian",
        "careful empiricist",
        "dramatic visionary",
    ]

    agents: list[ImageAgent] = []
    for index, path in enumerate(weight_files):
        try:
            agent_id = int(path.stem.split("_")[1])
        except Exception:
            agent_id = index
        agent = ImageAgent.from_weights(
            agent_id=agent_id,
            weights_path=path,
            name=names[index % len(names)],
            personality=personalities[index % len(personalities)],
        )
        agent.health_score = random.uniform(55.0, 100.0)
        agents.append(agent)
    return agents
