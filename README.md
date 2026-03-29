# 🧬 PROJECT GENESIS → 🌳 PROJECT EDEN
## Two-Stage Autonomous AI Evolution System

**TL;DR:** A genetic algorithm breeds specialist neural networks (Genesis), then drops them into a collaborative society where they debate, teach each other, and develop dynamic expertise (Eden).

---

## 📊 System Comparison

| Feature | Project Genesis | Project Eden |
|---------|----------------|--------------|
| **Purpose** | Train specialists through evolution | Collaborative learning & debate |
| **Method** | Genetic algorithm + curriculum | Multi-agent voting + cross-learning |
| **Environment** | Competitive (survival of fittest) | Cooperative (knowledge sharing) |
| **Runtime** | 15-20 min on Kaggle GPU | Continuous learning |
| **Output** | 4 specialist models | Dynamic expert council |
| **Novelty** | Neural architecture search | Weighted ensemble with expertise tracking |
| **Platform** | Kaggle (no internet needed) | Google Colab (internet optional) |

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    PROJECT GENESIS                       │
│                     (The Academy)                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. SPAWN: Create 20 random neural networks             │
│     ├─ Different architectures (layers, sizes)          │
│     └─ Random hyperparameters (LR, dropout)             │
│                                                          │
│  2. CURRICULUM: Progressive difficulty training          │
│     ├─ Stage 1: MNIST (easy)                            │
│     ├─ Stage 2: Fashion-MNIST (medium)                  │
│     └─ Stage 3: CIFAR-10 (hard)                         │
│                                                          │
│  3. EVALUATION: Multi-dimensional fitness               │
│     ├─ Pattern recognition accuracy                     │
│     ├─ Edge case handling                               │
│     ├─ Inference speed                                  │
│     └─ Rare class detection                             │
│                                                          │
│  4. NATURAL SELECTION: Kill bottom 60%                  │
│     └─ Breed survivors with mutations                   │
│                                                          │
│  5. GRADUATION: Select top 4 diverse specialists        │
│     ├─ Specialist A: Best at pattern recognition        │
│     ├─ Specialist B: Best at edge cases                 │
│     ├─ Specialist C: Fastest inference                  │
│     └─ Specialist D: Best at rare classes               │
│                                                          │
└─────────────────────────────────────────────────────────┘
                            │
                            │ Export models + manifest.json
                            ▼
┌─────────────────────────────────────────────────────────┐
│                     PROJECT EDEN                         │
│                    (The Council)                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. LOAD: Import the 4 Genesis graduates                │
│                                                          │
│  2. DEBATE: Multi-agent problem solving                 │
│     ├─ Each agent makes a prediction                    │
│     ├─ Weighted voting (experts valued more)            │
│     └─ Final answer from consensus                      │
│                                                          │
│  3. EXPERTISE TRACKING: Dynamic credibility             │
│     ├─ Correct agents gain reputation                   │
│     ├─ Wrong agents lose reputation                     │
│     └─ Weights adjust over time                         │
│                                                          │
│  4. CROSS-LEARNING: Knowledge transfer                  │
│     ├─ Weak agents copy weights from experts            │
│     └─ Emergent specialization refinement               │
│                                                          │
│  5. EXPANSION (Colab): Internet integration             │
│     ├─ Query Wikipedia for knowledge                    │
│     ├─ Scrape news feeds                                │
│     └─ Search engines for problem-solving               │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Phase 1: Genesis (Kaggle)

**1. Upload to Kaggle:**
- Create new notebook
- Upload `project_genesis.py`
- Copy `kaggle_genesis_notebook.py` code into cells

**2. Run:**
```python
from project_genesis import run_project_genesis

graduates, manifest = run_project_genesis(
    population_size=20,      # 20 competing agents
    num_generations=5,       # 5 evolution cycles
    curriculum_stage=0,      # MNIST dataset
    num_graduates=4          # Select top 4
)
```

**3. Download:**
- Output: `genesis_graduates.zip`
- Contains: 4 model files + manifest.json

**Expected Results:**
- Runtime: ~15-20 minutes
- Individual accuracy: 95-98% on MNIST
- Ensemble accuracy: 98-99%

---

### Phase 2: Eden (Google Colab)

**1. Upload Genesis graduates:**
- Upload `genesis_graduates.zip` to Colab
- Unzip in notebook

**2. Run Council:**
```python
from project_eden import EdenCouncil, load_graduates

# Load Genesis graduates
agents = load_graduates("./genesis_graduates/manifest.json")

# Create council
council = EdenCouncil(agents)

# Solve problems with debate
predictions = council.solve(
    input_data=test_batch,
    ground_truth=labels,
    context='pattern_recognition',
    learn=True  # Enable cross-learning
)

# Check status
print(council.get_status_report())
```

**Expected Results:**
- Initial ensemble: 98% accuracy
- After learning: 99%+ accuracy
- Expertise scores dynamically adjust
- Weak agents improve by copying from experts

---

## 🎯 Configuration Guide

### Genesis Parameters

```python
CONFIG = {
    'population_size': 20,     # More = better diversity, slower
    'num_generations': 5,      # More = better results, slower
    'curriculum_stage': 0,     # 0=MNIST, 1=FashionMNIST, 2=CIFAR10
    'num_graduates': 4,        # How many specialists to select
}
```

**Presets:**

| Preset | Time | Population | Generations | Stage | Quality |
|--------|------|-----------|-------------|-------|---------|
| **Quick Test** | 5 min | 10 | 3 | 0 | Low |
| **Balanced** | 15 min | 20 | 5 | 0 | Good ⭐ |
| **High Quality** | 45 min | 30 | 10 | 1 | Very Good |
| **Maximum** | 2+ hrs | 50 | 15 | 2 | Excellent |

### Eden Parameters

```python
# Expertise learning rate
alpha = 0.2  # How fast expertise scores update

# Cross-learning rate
transfer_alpha = 0.1  # How much weak agents copy from experts

# Contexts for specialization
contexts = [
    'pattern_recognition',
    'edge_cases',
    'efficiency',
    'rare_classes',
    'overall'
]
```

---

## 📈 Performance Metrics

### Genesis Outputs

For each graduate, you get:
- **Architecture:** Layer sizes, parameters
- **Fitness Score:** Multi-objective score
- **Specialization Scores:** Proficiency in each domain
- **Generation:** How many evolution cycles it survived

Example:
```
Graduate #1: Agent 14 (Generation 4)
  Architecture: [128, 256, 128]
  Parameters: 138,634 weights
  
  Specializations:
    pattern_recognition: ███████████████████░░░░░░░░ 0.972
    edge_cases:          ██████████████░░░░░░░░░░░░░ 0.851
    efficiency:          ████████████████████████░░░ 0.923
    rare_classes:        █████████████████░░░░░░░░░░ 0.888
  
  Peak Fitness: 127.45
```

### Eden Outputs

Track expertise evolution:
```
Batch 1: Accuracy = 0.950
Batch 2: Accuracy = 0.960
...
Batch 10: Accuracy = 0.985

Expertise Evolution:
  Agent 0: 0.972 → 0.984 (↑)
  Agent 1: 0.851 → 0.829 (↓)
  Agent 2: 0.923 → 0.945 (↑)
  Agent 3: 0.888 → 0.901 (↑)
```

---

## 🔬 Research Potential

### What's Novel Here?

1. **Two-Stage Pipeline:**
   - Most systems do EITHER evolution OR ensemble
   - This does evolution → ensemble with dynamic weighting

2. **Expertise Tracking:**
   - Not just voting, but weighted voting that adapts
   - Agents gain/lose influence based on performance

3. **Cross-Learning:**
   - Weak agents don't get killed in Eden
   - They learn from experts and find niches

### Possible Extensions

**Technical:**
- Add curiosity-driven exploration (intrinsic rewards)
- Implement attention mechanisms for agent communication
- Scale to 100+ agents with hierarchical councils
- Add memory/context windows for long-term learning

**Applications:**
- Medical diagnosis (specialists for different diseases)
- Financial forecasting (specialists for different markets)
- Game AI (specialists for different strategies)
- Anomaly detection (specialists for different attack types)

**Research Papers:**
- "Dynamic Expertise Weighting in Multi-Agent Ensembles"
- "Evolutionary Neural Architecture Search with Collaborative Refinement"
- "Cross-Agent Knowledge Transfer in Competitive-Cooperative Systems"

---

## 🐛 Troubleshooting

### Genesis Issues

**"CUDA out of memory"**
```python
# Solution 1: Reduce population
population_size = 10

# Solution 2: Smaller networks
# Edit genome hidden_sizes in spawn_population()
```

**"Models not learning"**
```python
# Solution: Increase training epochs
epochs_per_gen = 5  # Instead of 3
```

**"Taking too long"**
```python
# Solution: Use data subset
# In CurriculumManager.get_loaders()
subset_ratio = 0.2  # Use 20% of data
```

### Eden Issues

**"Agents not improving"**
```python
# Solution: Increase learning rate
alpha = 0.3  # Faster expertise updates
transfer_alpha = 0.2  # Faster knowledge transfer
```

**"All agents converging to same weights"**
```python
# Solution: Add diversity penalty
# In cross-learning, only transfer if gap > threshold
if best_score - worst_score > 0.5:  # Increased threshold
    # ... transfer code
```

---

## 📚 Code Structure

```
project/
├── project_genesis.py          # Core evolutionary engine
│   ├── GeneticAgent            # Individual neural network
│   ├── CurriculumManager       # Progressive training
│   ├── EvolutionEngine         # Natural selection
│   └── GraduationCeremony      # Specialist selection
│
├── project_eden.py             # Multi-agent collaboration
│   ├── ExpertiseLedger         # Reputation tracking
│   ├── EdenCouncil             # Debate & voting system
│   └── Cross-learning logic    # Knowledge transfer
│
├── kaggle_genesis_notebook.py # Kaggle wrapper + examples
│
└── genesis_graduates/          # Output directory
    ├── agent_X_genY.pth       # Model checkpoints
    └── manifest.json          # Metadata
```

---

## 🎓 Learning Resources

**Genetic Algorithms:**
- [NEAT](https://en.wikipedia.org/wiki/Neuroevolution_of_augmenting_topologies)
- [Neural Architecture Search](https://arxiv.org/abs/1611.01578)

**Multi-Agent Systems:**
- [Multi-Agent RL](https://arxiv.org/abs/1911.10635)
- [Mixture of Experts](https://arxiv.org/abs/1701.06538)

**Ensemble Methods:**
- [Ensemble Learning](https://scikit-learn.org/stable/modules/ensemble.html)
- [Boosting & Bagging](https://en.wikipedia.org/wiki/Ensemble_learning)

---

## 🤝 Contributing

**Want to extend this?**

Priority improvements:
1. Add more curriculum stages (ImageNet, audio, text)
2. Implement attention for agent communication
3. Add memory/context for long-term learning
4. Scale to 100+ agent councils
5. Integrate with LLMs (each agent is a fine-tuned LLM)

**Architecture ideas:**
- Hierarchical councils (local councils → global senate)
- Specialization discovery (agents find their own niches)
- Adversarial training (agents compete AND cooperate)

---

## 📜 License

MIT License - Do whatever you want with this.

**But if you publish a paper using this system, cite it as:**
```
@software{project_genesis_eden,
  title={Project Genesis-Eden: Evolutionary Neural Architecture Search with Collaborative Multi-Agent Refinement},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/genesis-eden}
}
```

---

## 🔮 Future Vision

**Long-term goal:** An autonomous AI laboratory where:
- Agents spawn, learn, compete, and cooperate
- No human-designed curriculum needed
- Agents discover new problem-solving strategies
- System continuously improves itself

**This is a stepping stone toward true open-ended learning.**

---

## 💬 Questions?

**"Is this AGI?"**
No. It's a clever combination of existing techniques.

**"Can it discover new math?"**
Not yet. Current version only learns from datasets.

**"Why not use LLMs instead?"**
You can! Replace GeneticAgent with fine-tuned LLMs.

**"How is this different from AutoML?"**
AutoML searches architectures for ONE task.
This creates specialists for MULTIPLE tasks, then ensembles them.

**"Production-ready?"**
Genesis: Yes (just NAS)
Eden: Research prototype (needs work)

---

**Built with curiosity. Evolved through brutality. Refined through collaboration.**

🧬 → 🌳
