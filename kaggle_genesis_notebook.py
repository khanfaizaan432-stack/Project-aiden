# PROJECT GENESIS - KAGGLE NOTEBOOK
# Evolutionary Neural Network Training System
# Copy this into a Kaggle notebook and run!

"""
🧬 WHAT THIS DOES:
1. Spawns 20 neural networks with random architectures
2. Trains them on MNIST (handwritten digits)
3. Kills the bottom 60% each generation
4. Mutates and breeds survivors
5. Graduates top 4 with different specializations

⏱️ RUNTIME: ~15-20 minutes on Kaggle GPU

📦 OUTPUT: 4 specialist models ready for Eden Council
"""

# ============================================================================
# STEP 1: SETUP
# ============================================================================

# Install requirements (Kaggle has most, but just in case)
import sys
!{sys.executable} -m pip install torch torchvision --quiet

# Import the Genesis engine
# (Upload project_genesis.py to Kaggle or paste it in a cell above)
from project_genesis import run_project_genesis, EvolutionEngine, GraduationCeremony

import torch
print(f"🖥️  Device: {'GPU ✅' if torch.cuda.is_available() else 'CPU ⚠️'}")
print(f"    {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'No GPU'}")


# ============================================================================
# STEP 2: CONFIGURE PARAMETERS
# ============================================================================

CONFIG = {
    # Population settings
    'population_size': 20,        # How many agents compete
    'num_generations': 5,         # Evolution cycles (more = better but slower)
    
    # Curriculum settings
    'curriculum_stage': 0,        # 0=MNIST, 1=Fashion-MNIST, 2=CIFAR-10
    
    # Graduation
    'num_graduates': 4,           # How many specialists to select
    
    # Output
    'output_dir': './genesis_graduates'
}

print("\n📋 Configuration:")
for key, val in CONFIG.items():
    print(f"   {key}: {val}")


# ============================================================================
# STEP 3: RUN GENESIS
# ============================================================================

print("\n" + "="*70)
print("🚀 LAUNCHING PROJECT GENESIS")
print("="*70)

graduates, manifest_path = run_project_genesis(
    population_size=CONFIG['population_size'],
    num_generations=CONFIG['num_generations'],
    curriculum_stage=CONFIG['curriculum_stage'],
    num_graduates=CONFIG['num_graduates']
)


# ============================================================================
# STEP 4: INSPECT GRADUATES
# ============================================================================

print("\n" + "="*70)
print("🎓 GRADUATE PROFILE CARDS")
print("="*70 + "\n")

for idx, agent in enumerate(graduates, 1):
    print(f"╔{'═'*66}╗")
    print(f"║ GRADUATE #{idx}: Agent {agent.agent_id} (Generation {agent.generation})".ljust(67) + "║")
    print(f"╠{'═'*66}╣")
    
    # Architecture
    print(f"║ Architecture: {str(agent.genome['hidden_sizes']).ljust(53)}║")
    print(f"║ Parameters: {sum(p.numel() for p in agent.parameters()):,} weights".ljust(67) + "║")
    
    # Specializations
    print(f"║ Specializations:".ljust(67) + "║")
    for spec, score in agent.specialization_scores.items():
        bar_length = int(score * 30)
        bar = "█" * bar_length + "░" * (30 - bar_length)
        print(f"║   {spec.ljust(20)}: {bar} {score:.3f}".ljust(67) + "║")
    
    # Fitness
    peak_fitness = max(agent.fitness_history) if agent.fitness_history else 0
    print(f"║ Peak Fitness: {peak_fitness:.2f}".ljust(67) + "║")
    
    print(f"╚{'═'*66}╝\n")


# ============================================================================
# STEP 5: DOWNLOAD GRADUATES
# ============================================================================

# On Kaggle, create a dataset to save the models
import shutil
import os

# Package everything into a zip
output_zip = '/kaggle/working/genesis_graduates.zip'
shutil.make_archive(
    output_zip.replace('.zip', ''), 
    'zip', 
    CONFIG['output_dir']
)

print("\n✅ DONE! Download 'genesis_graduates.zip' from Kaggle Output")
print("   This contains all 4 specialist models + manifest.json")
print("\n🔜 NEXT STEP: Upload to Google Colab and load into Eden Council")


# ============================================================================
# OPTIONAL: QUICK TEST
# ============================================================================

print("\n" + "="*70)
print("🧪 QUICK TEST: Can the graduates solve new problems?")
print("="*70 + "\n")

from torch.utils.data import DataLoader
import torchvision.transforms as transforms

# Load MNIST test set
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])
test_dataset = torchvision.datasets.MNIST(
    root='./data', train=False, download=True, transform=transform
)
test_loader = DataLoader(test_dataset, batch_size=1000, shuffle=False)

# Get one batch
data, targets = next(iter(test_loader))
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
data, targets = data.to(device), targets.to(device)

# Test each graduate
print("Individual Graduate Performance:")
for idx, agent in enumerate(graduates, 1):
    agent.eval()
    with torch.no_grad():
        outputs = agent(data)
        _, predicted = torch.max(outputs, 1)
        accuracy = (predicted == targets).float().mean().item()
    print(f"  Graduate {idx}: {accuracy*100:.2f}% accuracy")

# Ensemble (majority vote)
print("\nEnsemble Performance (Majority Vote):")
ensemble_votes = []
for agent in graduates:
    agent.eval()
    with torch.no_grad():
        outputs = agent(data)
        _, predicted = torch.max(outputs, 1)
        ensemble_votes.append(predicted)

# Stack and vote
ensemble_votes = torch.stack(ensemble_votes)
ensemble_prediction, _ = torch.mode(ensemble_votes, dim=0)
ensemble_accuracy = (ensemble_prediction == targets).float().mean().item()
print(f"  Ensemble: {ensemble_accuracy*100:.2f}% accuracy")
print(f"  Improvement: +{(ensemble_accuracy - accuracy)*100:.2f}%")


# ============================================================================
# TROUBLESHOOTING
# ============================================================================

"""
❌ COMMON ISSUES:

1. "RuntimeError: CUDA out of memory"
   → Reduce population_size to 10
   → Reduce num_generations to 3
   
2. "ModuleNotFoundError: No module named 'project_genesis'"
   → Make sure project_genesis.py is in the same notebook
   → Or paste the entire code from project_genesis.py above
   
3. "Accuracy is too low"
   → Increase num_generations (try 10)
   → Try curriculum_stage=1 (Fashion-MNIST is easier for some architectures)
   
4. "Taking too long"
   → Reduce population_size to 10
   → Use curriculum_stage=0 (MNIST is fastest)
   → Set epochs_per_gen=2 in the engine

📚 PARAMETER GUIDE:

population_size:
  - 10: Fast, less diversity (~10 min)
  - 20: Balanced (recommended)
  - 50: Slow, maximum diversity (~45 min)

num_generations:
  - 3: Quick test
  - 5: Good results (recommended)
  - 10: Best results, very slow

curriculum_stage:
  - 0 (MNIST): Easiest, fastest
  - 1 (Fashion-MNIST): Medium
  - 2 (CIFAR-10): Hardest, need more generations

🎯 RECOMMENDED CONFIGS:

Fast Test (5 min):
  population_size=10, num_generations=3, stage=0

Balanced (15 min):
  population_size=20, num_generations=5, stage=0

High Quality (45 min):
  population_size=30, num_generations=10, stage=1

Maximum (2+ hours):
  population_size=50, num_generations=15, stage=2
"""
