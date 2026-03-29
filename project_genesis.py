"""
PROJECT GENESIS: Evolutionary Neural Architecture Training
A genetic algorithm that spawns, trains, culls, and graduates specialist AI models.

Pipeline:
1. Spawn population of diverse neural networks
2. Train on curriculum (easy → medium → hard)
3. Evaluate fitness and specialization
4. Kill weak performers, mutate survivors
5. Graduate top 4 specialists with different expertise
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Subset
import torchvision
import torchvision.transforms as transforms
import numpy as np
import random
import copy
from typing import List, Dict, Tuple
import json
from pathlib import Path


# ============================================================================
# GENETIC AGENT: Individual Neural Network Citizen
# ============================================================================

class GeneticAgent(nn.Module):
    """
    A single agent in the population.
    Tracks its own fitness, specialization, and evolutionary lineage.
    """
    
    def __init__(self, agent_id: int, genome: Dict):
        super().__init__()
        self.agent_id = agent_id
        self.genome = genome  # Architecture parameters
        self.generation = 0
        self.fitness_history = []
        self.specialization_scores = {
            "pattern_recognition": 0.0,
            "edge_cases": 0.0,
            "efficiency": 0.0,
            "rare_classes": 0.0
        }
        
        # Build network from genome
        self.network = self._build_network()
        
    def _build_network(self) -> nn.Module:
        """Construct neural network from genetic blueprint"""
        layers = []
        in_features = self.genome['input_size']
        
        # Hidden layers
        for hidden_size in self.genome['hidden_sizes']:
            layers.extend([
                nn.Linear(in_features, hidden_size),
                nn.ReLU(),
                nn.Dropout(self.genome['dropout'])
            ])
            in_features = hidden_size
        
        # Output layer
        layers.append(nn.Linear(in_features, self.genome['output_size']))
        
        return nn.Sequential(*layers)
    
    def forward(self, x):
        x = x.view(x.size(0), -1)  # Flatten
        return self.network(x)
    
    def calculate_fitness(self, accuracy: float, speed: float, 
                         edge_case_acc: float, rare_class_acc: float) -> float:
        """
        Multi-objective fitness function.
        Balances accuracy, speed, and specialization.
        """
        # Base fitness from accuracy
        fitness = accuracy * 100
        
        # Bonus for efficiency (faster inference)
        fitness += (1.0 / speed) * 10
        
        # Specialization bonuses
        self.specialization_scores['pattern_recognition'] = accuracy
        self.specialization_scores['edge_cases'] = edge_case_acc
        self.specialization_scores['efficiency'] = 1.0 / speed
        self.specialization_scores['rare_classes'] = rare_class_acc
        
        # Overall fitness is weighted sum
        fitness += edge_case_acc * 20  # Reward handling difficult cases
        fitness += rare_class_acc * 15  # Reward rare class detection
        
        self.fitness_history.append(fitness)
        return fitness
    
    def mutate(self):
        """
        Apply random mutations to genome.
        Simulates genetic variation.
        """
        mutation_rate = 0.2
        
        if random.random() < mutation_rate:
            # Mutate learning rate
            self.genome['learning_rate'] *= random.uniform(0.5, 1.5)
            self.genome['learning_rate'] = max(1e-5, min(0.1, self.genome['learning_rate']))
        
        if random.random() < mutation_rate:
            # Mutate dropout
            self.genome['dropout'] += random.uniform(-0.2, 0.2)
            self.genome['dropout'] = max(0.0, min(0.7, self.genome['dropout']))
        
        if random.random() < mutation_rate and len(self.genome['hidden_sizes']) < 5:
            # Add a layer
            new_size = random.choice([64, 128, 256])
            self.genome['hidden_sizes'].append(new_size)
        
        if random.random() < mutation_rate and len(self.genome['hidden_sizes']) > 1:
            # Remove a layer
            self.genome['hidden_sizes'].pop()
        
        # Rebuild network with mutated genome
        self.network = self._build_network()
        self.generation += 1


# ============================================================================
# CURRICULUM: Progressive Difficulty Training
# ============================================================================

class CurriculumManager:
    """
    Manages staged learning from easy to hard datasets.
    Agents must pass each stage to advance.
    """
    
    def __init__(self, batch_size: int = 128):
        self.batch_size = batch_size
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.stages = self._initialize_stages()
        
    def _initialize_stages(self) -> List[Dict]:
        """Define curriculum stages"""
        # Stage 1: MNIST (Easy - handwritten digits)
        mnist_transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))
        ])
        
        mnist_train = torchvision.datasets.MNIST(
            root='./data', train=True, download=True, transform=mnist_transform
        )
        mnist_test = torchvision.datasets.MNIST(
            root='./data', train=False, download=True, transform=mnist_transform
        )
        
        # Stage 2: Fashion-MNIST (Medium - clothing items)
        fashion_transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.5,), (0.5,))
        ])
        
        fashion_train = torchvision.datasets.FashionMNIST(
            root='./data', train=True, download=True, transform=fashion_transform
        )
        fashion_test = torchvision.datasets.FashionMNIST(
            root='./data', train=False, download=True, transform=fashion_transform
        )
        
        # Stage 3: CIFAR-10 (Hard - color images)
        cifar_transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
        ])
        
        cifar_train = torchvision.datasets.CIFAR10(
            root='./data', train=True, download=True, transform=cifar_transform
        )
        cifar_test = torchvision.datasets.CIFAR10(
            root='./data', train=False, download=True, transform=cifar_transform
        )
        
        return [
            {
                'name': 'MNIST',
                'train': mnist_train,
                'test': mnist_test,
                'input_size': 784,
                'output_size': 10,
                'passing_threshold': 0.95,
                'difficulty': 'easy'
            },
            {
                'name': 'Fashion-MNIST',
                'train': fashion_train,
                'test': fashion_test,
                'input_size': 784,
                'output_size': 10,
                'passing_threshold': 0.85,
                'difficulty': 'medium'
            },
            {
                'name': 'CIFAR-10',
                'train': cifar_train,
                'test': cifar_test,
                'input_size': 3072,  # 32x32x3
                'output_size': 10,
                'passing_threshold': 0.70,
                'difficulty': 'hard'
            }
        ]
    
    def get_stage(self, stage_idx: int) -> Dict:
        """Get curriculum stage by index"""
        return self.stages[stage_idx]
    
    def get_loaders(self, stage_idx: int, subset_ratio: float = 1.0):
        """Get data loaders for a stage (optionally use subset for speed)"""
        stage = self.stages[stage_idx]
        
        if subset_ratio < 1.0:
            # Use subset for faster evolution cycles
            train_size = int(len(stage['train']) * subset_ratio)
            train_indices = random.sample(range(len(stage['train'])), train_size)
            train_dataset = Subset(stage['train'], train_indices)
        else:
            train_dataset = stage['train']
        
        train_loader = DataLoader(
            train_dataset, 
            batch_size=self.batch_size, 
            shuffle=True,
            num_workers=2
        )
        
        test_loader = DataLoader(
            stage['test'], 
            batch_size=self.batch_size, 
            shuffle=False,
            num_workers=2
        )
        
        return train_loader, test_loader


# ============================================================================
# EVOLUTION ENGINE: Natural Selection Core
# ============================================================================

class EvolutionEngine:
    """
    The brutal examination hall.
    Trains, evaluates, culls, and breeds the population.
    """
    
    def __init__(self, population_size: int = 20, survival_rate: float = 0.4):
        self.population_size = population_size
        self.survival_rate = survival_rate
        self.survivors_count = int(population_size * survival_rate)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.curriculum = CurriculumManager()
        self.generation_count = 0
        
    def spawn_population(self, stage_idx: int = 0) -> List[GeneticAgent]:
        """
        Create initial random population.
        Genetic diversity is key.
        """
        stage = self.curriculum.get_stage(stage_idx)
        population = []
        
        for i in range(self.population_size):
            # Random genome
            genome = {
                'input_size': stage['input_size'],
                'output_size': stage['output_size'],
                'hidden_sizes': [
                    random.choice([64, 128, 256]) 
                    for _ in range(random.randint(1, 3))
                ],
                'learning_rate': random.uniform(0.001, 0.01),
                'dropout': random.uniform(0.1, 0.5)
            }
            
            agent = GeneticAgent(agent_id=i, genome=genome)
            agent.to(self.device)
            population.append(agent)
        
        print(f"🧬 Spawned {self.population_size} agents with diverse genomes")
        return population
    
    def train_agent(self, agent: GeneticAgent, train_loader: DataLoader, 
                   epochs: int = 3) -> None:
        """Train a single agent"""
        agent.train()
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(
            agent.parameters(), 
            lr=agent.genome['learning_rate']
        )
        
        for epoch in range(epochs):
            for batch_idx, (data, target) in enumerate(train_loader):
                data, target = data.to(self.device), target.to(self.device)
                
                optimizer.zero_grad()
                output = agent(data)
                loss = criterion(output, target)
                loss.backward()
                optimizer.step()
    
    def evaluate_agent(self, agent: GeneticAgent, test_loader: DataLoader) -> Dict:
        """
        Comprehensive evaluation: accuracy, speed, specialization.
        """
        agent.eval()
        correct = 0
        total = 0
        edge_case_correct = 0
        edge_case_total = 0
        rare_class_correct = 0
        rare_class_total = 0
        
        inference_times = []
        
        # Define rare classes (last 3 classes are "rare")
        rare_classes = [7, 8, 9]
        
        with torch.no_grad():
            for data, target in test_loader:
                data, target = data.to(self.device), target.to(self.device)
                
                # Measure inference speed
                start = torch.cuda.Event(enable_timing=True)
                end = torch.cuda.Event(enable_timing=True)
                start.record()
                
                output = agent(data)
                
                end.record()
                torch.cuda.synchronize()
                inference_times.append(start.elapsed_time(end))
                
                _, predicted = torch.max(output.data, 1)
                
                # Overall accuracy
                total += target.size(0)
                correct += (predicted == target).sum().item()
                
                # Edge case performance (low confidence predictions)
                probs = torch.softmax(output, dim=1)
                max_probs = torch.max(probs, dim=1)[0]
                edge_cases = max_probs < 0.6  # Low confidence
                edge_case_total += edge_cases.sum().item()
                edge_case_correct += ((predicted == target) & edge_cases).sum().item()
                
                # Rare class performance
                rare_mask = torch.zeros_like(target, dtype=torch.bool)
                for rc in rare_classes:
                    rare_mask |= (target == rc)
                rare_class_total += rare_mask.sum().item()
                rare_class_correct += ((predicted == target) & rare_mask).sum().item()
        
        accuracy = correct / total
        avg_speed = np.mean(inference_times)
        edge_case_acc = edge_case_correct / max(edge_case_total, 1)
        rare_class_acc = rare_class_correct / max(rare_class_total, 1)
        
        return {
            'accuracy': accuracy,
            'speed': avg_speed,
            'edge_case_accuracy': edge_case_acc,
            'rare_class_accuracy': rare_class_acc
        }
    
    def selection_and_breeding(self, population: List[GeneticAgent], 
                               fitness_scores: List[float]) -> List[GeneticAgent]:
        """
        Natural selection: Kill the weak, clone and mutate the strong.
        """
        # Sort by fitness
        sorted_pop = [agent for _, agent in sorted(
            zip(fitness_scores, population), 
            key=lambda x: x[0], 
            reverse=True
        )]
        
        # Survivors (top performers)
        survivors = sorted_pop[:self.survivors_count]
        
        print(f"💀 Culled {len(population) - len(survivors)} weak agents")
        print(f"✅ {len(survivors)} survivors advance")
        
        # Breed new generation
        new_population = []
        
        # Keep elite survivors unchanged
        for agent in survivors[:2]:
            new_population.append(agent)
        
        # Clone and mutate survivors to fill population
        while len(new_population) < self.population_size:
            parent = random.choice(survivors)
            child = copy.deepcopy(parent)
            child.agent_id = len(new_population)
            child.mutate()
            child.to(self.device)
            new_population.append(child)
        
        return new_population
    
    def evolve(self, num_generations: int = 5, 
               stage_idx: int = 0, 
               epochs_per_gen: int = 3) -> List[GeneticAgent]:
        """
        Run the full evolutionary cycle.
        """
        print(f"\n{'='*60}")
        print(f"🧬 EVOLUTION ENGINE STARTING")
        print(f"Stage: {self.curriculum.get_stage(stage_idx)['name']}")
        print(f"Population: {self.population_size} | Generations: {num_generations}")
        print(f"{'='*60}\n")
        
        # Initialize population
        population = self.spawn_population(stage_idx)
        train_loader, test_loader = self.curriculum.get_loaders(stage_idx, subset_ratio=0.3)
        
        for gen in range(num_generations):
            self.generation_count = gen
            print(f"\n📍 GENERATION {gen + 1}/{num_generations}")
            print("-" * 60)
            
            fitness_scores = []
            
            # Train and evaluate each agent
            for idx, agent in enumerate(population):
                # Training
                self.train_agent(agent, train_loader, epochs=epochs_per_gen)
                
                # Evaluation
                metrics = self.evaluate_agent(agent, test_loader)
                fitness = agent.calculate_fitness(
                    accuracy=metrics['accuracy'],
                    speed=metrics['speed'],
                    edge_case_acc=metrics['edge_case_accuracy'],
                    rare_class_acc=metrics['rare_class_accuracy']
                )
                fitness_scores.append(fitness)
                
                if idx < 3:  # Show top 3 for debugging
                    print(f"Agent {agent.agent_id}: "
                          f"Acc={metrics['accuracy']:.3f} | "
                          f"Fitness={fitness:.2f} | "
                          f"Layers={len(agent.genome['hidden_sizes'])}")
            
            # Display generation stats
            print(f"\n📊 Generation Stats:")
            print(f"   Best Fitness: {max(fitness_scores):.2f}")
            print(f"   Avg Fitness: {np.mean(fitness_scores):.2f}")
            print(f"   Worst Fitness: {min(fitness_scores):.2f}")
            
            # Natural selection
            if gen < num_generations - 1:
                population = self.selection_and_breeding(population, fitness_scores)
        
        # Return final population sorted by fitness
        final_fitness = []
        for agent in population:
            metrics = self.evaluate_agent(agent, test_loader)
            fitness = agent.calculate_fitness(
                metrics['accuracy'], metrics['speed'],
                metrics['edge_case_accuracy'], metrics['rare_class_accuracy']
            )
            final_fitness.append(fitness)
        
        sorted_pop = [agent for _, agent in sorted(
            zip(final_fitness, population), 
            key=lambda x: x[0], 
            reverse=True
        )]
        
        return sorted_pop


# ============================================================================
# GRADUATION: Select Top 4 Diverse Specialists
# ============================================================================

class GraduationCeremony:
    """
    Select top 4 agents with DIVERSE specializations.
    We want different experts, not 4 clones.
    """
    
    def __init__(self):
        self.specialization_types = [
            'pattern_recognition',
            'edge_cases', 
            'efficiency',
            'rare_classes'
        ]
    
    def select_graduates(self, population: List[GeneticAgent], 
                        top_n: int = 4) -> List[GeneticAgent]:
        """
        Select top N agents with maximum diversity in specializations.
        """
        print(f"\n{'='*60}")
        print("🎓 GRADUATION CEREMONY")
        print(f"{'='*60}\n")
        
        graduates = []
        
        # Strategy: Pick best agent for each specialization
        for spec_type in self.specialization_types[:top_n]:
            # Sort by this specialization
            sorted_by_spec = sorted(
                population,
                key=lambda a: a.specialization_scores[spec_type],
                reverse=True
            )
            
            # Pick best not already selected
            for agent in sorted_by_spec:
                if agent not in graduates:
                    graduates.append(agent)
                    print(f"🎖️  Graduate #{len(graduates)}: Agent {agent.agent_id}")
                    print(f"    Specialization: {spec_type}")
                    print(f"    Score: {agent.specialization_scores[spec_type]:.3f}")
                    print(f"    Architecture: {agent.genome['hidden_sizes']}")
                    print()
                    break
        
        return graduates[:top_n]
    
    def export_graduates(self, graduates: List[GeneticAgent], 
                        output_dir: str = "./genesis_graduates"):
        """
        Save the top models and their metadata.
        Ready for Eden Council.
        """
        Path(output_dir).mkdir(exist_ok=True)
        
        manifest = {
            'graduation_date': str(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'),
            'num_graduates': len(graduates),
            'graduates': []
        }
        
        for idx, agent in enumerate(graduates):
            # Save model weights
            model_path = f"{output_dir}/agent_{agent.agent_id}_gen{agent.generation}.pth"
            torch.save({
                'state_dict': agent.state_dict(),
                'genome': agent.genome,
                'fitness_history': agent.fitness_history,
                'specialization_scores': agent.specialization_scores
            }, model_path)
            
            # Add to manifest
            manifest['graduates'].append({
                'agent_id': agent.agent_id,
                'generation': agent.generation,
                'model_path': model_path,
                'genome': agent.genome,
                'specializations': agent.specialization_scores,
                'fitness_peak': max(agent.fitness_history) if agent.fitness_history else 0
            })
            
            print(f"💾 Saved: {model_path}")
        
        # Save manifest
        manifest_path = f"{output_dir}/manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"\n✅ Graduation complete! Manifest saved to {manifest_path}")
        return manifest_path


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def run_project_genesis(
    population_size: int = 20,
    num_generations: int = 5,
    curriculum_stage: int = 0,
    num_graduates: int = 4
):
    """
    Complete Genesis pipeline.
    """
    print("\n" + "="*60)
    print("🌟 PROJECT GENESIS: AUTONOMOUS NEURAL EVOLUTION 🌟")
    print("="*60)
    
    # Initialize evolution engine
    engine = EvolutionEngine(
        population_size=population_size,
        survival_rate=0.4
    )
    
    # Run evolution
    final_population = engine.evolve(
        num_generations=num_generations,
        stage_idx=curriculum_stage,
        epochs_per_gen=3
    )
    
    # Graduate top performers
    ceremony = GraduationCeremony()
    graduates = ceremony.select_graduates(final_population, top_n=num_graduates)
    
    # Export for Eden Council
    manifest_path = ceremony.export_graduates(graduates)
    
    print("\n" + "="*60)
    print("🎊 GENESIS COMPLETE")
    print(f"📁 {num_graduates} specialist models ready for Eden Council")
    print(f"📋 Manifest: {manifest_path}")
    print("="*60 + "\n")
    
    return graduates, manifest_path


if __name__ == "__main__":
    # Run on easiest stage first (MNIST)
    graduates, manifest = run_project_genesis(
        population_size=20,      # 20 agents compete
        num_generations=5,       # 5 cycles of evolution
        curriculum_stage=0,      # Start with MNIST
        num_graduates=4          # Select top 4 specialists
    )
    
    print("\n🚀 Next step: Load these graduates into Eden Council")
    print("   (Run on Google Colab for internet access)")
