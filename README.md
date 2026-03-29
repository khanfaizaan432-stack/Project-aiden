

# Project Aiden: Multi-Agent Evolution and Collaboration Framework

Project Aiden is a hybrid, multi-agent AI framework that combines genetic neural architecture search, cooperative multi-agent debate, adversarial defense mechanisms, and large language model (LLM) arbitration. 

The system operates in two core phases: **Genesis** (where diverse specialist models are bred via evolution) and **Eden** (where surviving models are formed into a council that debates over ambiguous data, isolates malicious actors, and defers to a heavy reasoning Oracle when consensus cannot be reached).

---

## Architecture Overview

The system is designed to overcome the limitations of standard "black box" neural networks (such as silent hallucinations and lack of explainability) by introducing a society of agents.

### 1. Project Genesis (The Academy)
* **Goal:** To produce specialized neural networks through a guided evolutionary process.
* **Process:** Initial populations of networks with randomized layers, sizes, and activations compete. The weakest are purged, while the strongest are mutated and blended to produce superior offspring.

### 2. Project Eden (The Council)
* **Goal:** To create a self-healing, highly robust decision-making ensemble.
* **Process:** The top survivors from Genesis form the Eden Council. They process incoming data and cast weighted votes. If confidence falls below a set threshold, the system triggers the Reasoning Oracle.

---

## Key Features and Improvements

### Modular Directory Structure
The code is separated into dedicated modules to allow task-agnostic deployment and clean separation of concerns:
* `/core/agent.py`: Handles agent initialization and state.
* `/core/council.py`: Handles weighted voting and ensemble mechanics.
* `/core/evolution.py`: Handles crossover mutation and breeding.
* `/experiments/`: Contains execution scripts, stress tests, and adversarial simulations.

### Exponential Moving Average (EMA) Reputation
To prevent "runaway dominance" where an agent gets lucky once and permanently overrides the rest of the council, agents update their expertise scores using an EMA formula:
`Expertise = (0.9 * Previous Expertise) + (0.1 * Current Performance)`
This ensures that only consistently accurate agents maintain high voting influence.

### Guided Crossover Mutation
Instead of standard "random walk" mutations (adding random noise to weights), the system uses weight interpolation. New agents are spawned as a mathematical blend of a successful parent and the current council leader, pointing the evolution in a productive direction.

### Adversarial Robustness (The Traitor Protocol)
The system has been stress-tested against deliberate poisoning. By injecting a static, malicious model (Agent 666) that confidently lies, the council successfully utilized its active reputation system to identify the drop in accuracy, quarantine the agent, and mute its voting weight automatically.

### Hybrid (Lamarckian) Learning
To avoid evolutionary stagnation on complex datasets like Fashion-MNIST, the framework utilizes a hybrid approach. Agents utilize quick bursts of gradient descent (lifetime learning) to adapt to the data before breeding. This allows the framework to enjoy both the structural discovery of evolution and the operational speed of backpropagation.

### Reasoning Oracle Arbitration
When local models are heavily split or lack confidence on an edge case, the system calls the Gemini 2.5 Flash API. The Oracle analyzes the visual or tabular context, reviews the conflict between the agents, and returns a final tie-breaking decision alongside a natural language explanation of its clinical or visual reasoning.

---

## File Structure

```text
├── core/
│   ├── __init__.py
│   ├── agent.py          # GeneticAgent class and reputation decay
│   ├── council.py        # EdenCouncil class and weighted voting
│   └── evolution.py      # Crossover and weight interpolation logic
├── experiments/
│   ├── adversarial.py    # Traitor agent simulation
│   └── gauntlet.py       # Paced reasoning and Oracle tests
├── genesis_graduates/
│   ├── manifest.json     # Saved metadata of successful agents
│   └── agent_X.pth       # PyTorch weights for council members
└── data/                 # Datasets (MNIST, Fashion-MNIST, etc.)
```

---

## Getting Started

### Prerequisites
* Python 3.10+
* PyTorch 2.0+
* Google GenerativeAI SDK (for Oracle functions)
* torchvision

### Basic Usage
To initialize a council and run a basic evaluation:

```python
import torch
from core.agent import GeneticAgent
from core.council import EdenCouncil

# Load existing graduates or create a new population
config = {'layers': 2, 'hidden': 256, 'activation': 'relu'}
agents = [GeneticAgent(i, config) for i in range(4)]

# Form the Council
council = EdenCouncil(agents, device='cuda' if torch.cuda.is_available() else 'cpu')

# Run a decision round
# data should be your feature tensor
logits, weights = council.debate(data)
predictions = logits.argmax(dim=1)
```

---

## Future Roadmap

* **Universal Data Ingestor:** Abstracting the input dimensions so the council can automatically resize its networks to accept non-image tabular data (CSVs) out of the box.
* **Meta-Model Arbitration:** Training a small, deterministic gating network to learn optimal routing between agents without having to call an external LLM for every edge case.

---

## License

This project is licensed under the MIT License.

## Citation

If you use this system or architecture in your research, please cite it as:

```text
@software{project_aiden,
  title={Project Aiden: Multi-Agent Evolution and Collaboration Framework with LLM Arbitration},
  author={Your Name},
  year={2026},
  url={https://github.com/yourusername/project-aiden}
}
```
