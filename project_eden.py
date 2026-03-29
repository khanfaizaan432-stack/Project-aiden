"""
PROJECT EDEN: The Council of Specialists
Multi-agent collaborative learning with dynamic expertise weighting.

This system takes Genesis graduates and lets them:
1. Debate on new problems
2. Learn from each other's mistakes
3. Develop expertise scores in different domains
4. Vote with weighted influence

🌐 RUN THIS ON GOOGLE COLAB (need internet access for expansion)
"""

import torch
import torch.nn as nn
import numpy as np
from typing import List, Dict, Tuple
import json
from pathlib import Path
import copy


# ============================================================================
# LOAD GENESIS GRADUATES
# ============================================================================

def load_graduates(manifest_path: str) -> List[nn.Module]:
    """
    Load the 4 specialist models from Genesis graduation.
    """
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    agents = []
    print(f"📥 Loading {manifest['num_graduates']} graduates...")
    
    for grad_info in manifest['graduates']:
        # Load checkpoint
        checkpoint = torch.load(grad_info['model_path'])
        
        # Reconstruct agent (you'll need GeneticAgent class)
        from project_genesis import GeneticAgent
        
        agent = GeneticAgent(
            agent_id=grad_info['agent_id'],
            genome=checkpoint['genome']
        )
        agent.load_state_dict(checkpoint['state_dict'])
        agent.specialization_scores = checkpoint['specialization_scores']
        agent.eval()
        
        agents.append(agent)
        print(f"  ✓ Agent {grad_info['agent_id']} loaded")
    
    return agents


# ============================================================================
# EXPERTISE LEDGER: Track Who's Good At What
# ============================================================================

class ExpertiseLedger:
    """
    Dynamic credibility tracking system.
    Each agent has a reputation score for different task types.
    """
    
    def __init__(self, agents: List[nn.Module]):
        self.agents = agents
        self.num_agents = len(agents)
        
        # Initialize ledger from Genesis specializations
        self.ledger = {}
        for idx, agent in enumerate(agents):
            self.ledger[idx] = {
                'pattern_recognition': agent.specialization_scores['pattern_recognition'],
                'edge_cases': agent.specialization_scores['edge_cases'],
                'efficiency': agent.specialization_scores['efficiency'],
                'rare_classes': agent.specialization_scores['rare_classes'],
                'overall': 0.5  # Start neutral
            }
        
        # Performance history
        self.history = {idx: [] for idx in range(self.num_agents)}
    
    def get_weights(self, context: str = 'overall') -> np.ndarray:
        """
        Get voting weights for current context.
        Better experts have louder votes.
        """
        weights = np.array([
            self.ledger[idx][context] 
            for idx in range(self.num_agents)
        ])
        
        # Normalize to sum to 1
        return weights / weights.sum()
    
    def update_expertise(self, agent_idx: int, context: str, 
                        was_correct: bool) -> None:
        """
        Update agent's expertise based on performance.
        Uses exponential moving average.
        """
        alpha = 0.2  # Learning rate
        
        current = self.ledger[agent_idx][context]
        new_value = current + alpha * (1.0 if was_correct else -0.5)
        new_value = max(0.1, min(1.0, new_value))  # Clamp
        
        self.ledger[agent_idx][context] = new_value
        self.history[agent_idx].append({
            'context': context,
            'correct': was_correct,
            'expertise_after': new_value
        })
    
    def get_expert_rankings(self, context: str = 'overall') -> List[Tuple[int, float]]:
        """Get agents sorted by expertise in a context"""
        rankings = [
            (idx, self.ledger[idx][context]) 
            for idx in range(self.num_agents)
        ]
        return sorted(rankings, key=lambda x: x[1], reverse=True)


# ============================================================================
# EDEN COUNCIL: Multi-Agent Debate System
# ============================================================================

class EdenCouncil:
    """
    The senate of AI specialists.
    Agents debate, vote, and learn from disagreements.
    """
    
    def __init__(self, agents: List[nn.Module], device: str = 'cuda'):
        self.agents = agents
        self.device = torch.device(device if torch.cuda.is_available() else 'cpu')
        self.ledger = ExpertiseLedger(agents)
        
        # Move all agents to device
        for agent in self.agents:
            agent.to(self.device)
        
        print(f"🏛️  Eden Council assembled with {len(agents)} specialists")
    
    def debate(self, input_data: torch.Tensor, 
               context: str = 'overall') -> Dict:
        """
        Multi-agent debate process:
        1. Each agent makes a prediction
        2. Weighted voting determines final answer
        3. Agents learn from disagreements
        """
        input_data = input_data.to(self.device)
        
        # Get predictions from each agent
        predictions = []
        confidences = []
        
        for agent in self.agents:
            agent.eval()
            with torch.no_grad():
                output = agent(input_data)
                probs = torch.softmax(output, dim=1)
                confidence, prediction = torch.max(probs, dim=1)
                
                predictions.append(prediction)
                confidences.append(confidence)
        
        predictions = torch.stack(predictions)  # [num_agents, batch_size]
        confidences = torch.stack(confidences)
        
        # Get voting weights from ledger
        weights = self.ledger.get_weights(context)
        weights_tensor = torch.tensor(
            weights, device=self.device, dtype=torch.float32
        ).unsqueeze(1)  # [num_agents, 1]
        
        # Weighted voting
        final_predictions = []
        for i in range(input_data.size(0)):
            # Get votes for this sample
            votes = predictions[:, i]
            
            # Count weighted votes for each class
            num_classes = 10  # Adjust based on task
            vote_counts = torch.zeros(num_classes, device=self.device)
            
            for agent_idx, vote in enumerate(votes):
                vote_counts[vote] += weights[agent_idx]
            
            # Winner takes all
            final_pred = torch.argmax(vote_counts)
            final_predictions.append(final_pred)
        
        final_predictions = torch.stack(final_predictions)
        
        return {
            'predictions': final_predictions,
            'agent_predictions': predictions,
            'confidences': confidences,
            'weights': weights
        }
    
    def learn_from_feedback(self, debate_result: Dict, 
                           ground_truth: torch.Tensor,
                           context: str = 'overall') -> None:
        """
        Post-debate learning:
        - Agents who were correct gain expertise
        - Agents who were wrong lose expertise
        - Agents can copy weights from better performers (cross-learning)
        """
        agent_predictions = debate_result['agent_predictions']
        final_predictions = debate_result['predictions']
        
        ground_truth = ground_truth.to(self.device)
        
        # Evaluate each agent
        for agent_idx in range(len(self.agents)):
            # Was this agent correct?
            agent_correct = (
                agent_predictions[agent_idx] == ground_truth
            ).float().mean().item()
            
            # Update expertise
            self.ledger.update_expertise(
                agent_idx, 
                context, 
                agent_correct > 0.5
            )
        
        # Cross-learning: Weak agents learn from strong ones
        rankings = self.ledger.get_expert_rankings(context)
        best_agent_idx = rankings[0][0]
        worst_agent_idx = rankings[-1][0]
        
        # If gap is large, weak agent copies some weights from strong agent
        best_score = rankings[0][1]
        worst_score = rankings[-1][1]
        
        if best_score - worst_score > 0.3:
            print(f"📚 Agent {worst_agent_idx} learning from Agent {best_agent_idx}")
            
            # Knowledge transfer (copy a fraction of weights)
            alpha = 0.1  # Transfer rate
            best_agent = self.agents[best_agent_idx]
            weak_agent = self.agents[worst_agent_idx]
            
            with torch.no_grad():
                for weak_param, best_param in zip(
                    weak_agent.parameters(), 
                    best_agent.parameters()
                ):
                    weak_param.data = (
                        (1 - alpha) * weak_param.data + 
                        alpha * best_param.data
                    )
    
    def solve(self, input_data: torch.Tensor, 
             ground_truth: torch.Tensor = None,
             context: str = 'overall',
             learn: bool = True) -> torch.Tensor:
        """
        Complete solve pipeline: debate → vote → learn
        """
        # Debate
        result = self.debate(input_data, context)
        
        # Learn from feedback if labels provided
        if learn and ground_truth is not None:
            self.learn_from_feedback(result, ground_truth, context)
        
        return result['predictions']
    
    def get_status_report(self) -> str:
        """Generate human-readable status of the council"""
        report = "\n" + "="*60 + "\n"
        report += "🏛️  EDEN COUNCIL STATUS REPORT\n"
        report += "="*60 + "\n\n"
        
        for agent_idx, agent in enumerate(self.agents):
            report += f"Agent {agent_idx}:\n"
            
            for context, score in self.ledger.ledger[agent_idx].items():
                bar_len = int(score * 30)
                bar = "█" * bar_len + "░" * (30 - bar_len)
                report += f"  {context.ljust(20)}: {bar} {score:.3f}\n"
            
            report += "\n"
        
        return report


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

def test_eden_council():
    """
    Example: Load Genesis graduates and run Eden Council
    """
    print("\n" + "="*60)
    print("🌳 PROJECT EDEN: COUNCIL TEST")
    print("="*60 + "\n")
    
    # Load graduates from Genesis
    manifest_path = "./genesis_graduates/manifest.json"
    agents = load_graduates(manifest_path)
    
    # Create council
    council = EdenCouncil(agents)
    
    # Load test data
    import torchvision
    import torchvision.transforms as transforms
    
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    test_dataset = torchvision.datasets.MNIST(
        root='./data', train=False, download=True, transform=transform
    )
    test_loader = torch.utils.data.DataLoader(
        test_dataset, batch_size=100, shuffle=True
    )
    
    # Test on multiple batches (council learns over time)
    print("🧪 Testing council on 10 batches...")
    print("    (Watch expertise scores evolve)\n")
    
    for batch_idx, (data, target) in enumerate(test_loader):
        if batch_idx >= 10:
            break
        
        # Council debates and learns
        predictions = council.solve(
            data, 
            ground_truth=target,
            context='pattern_recognition',
            learn=True
        )
        
        accuracy = (predictions == target.to(council.device)).float().mean()
        print(f"Batch {batch_idx + 1}: Accuracy = {accuracy:.3f}")
    
    # Show final status
    print(council.get_status_report())
    
    # Show how weights changed
    print("\n📊 Expertise Evolution:")
    for agent_idx in range(len(agents)):
        history = council.ledger.history[agent_idx]
        if history:
            scores = [h['expertise_after'] for h in history if h['context'] == 'pattern_recognition']
            print(f"  Agent {agent_idx}: {scores[0]:.3f} → {scores[-1]:.3f} "
                  f"({'↑' if scores[-1] > scores[0] else '↓'})")


# ============================================================================
# INTERNET EXPANSION (COLAB ONLY)
# ============================================================================

"""
🌐 NEXT LEVEL: Add Internet Learning

On Google Colab, you can expand Eden Council to:
1. Query Wikipedia API for knowledge
2. Scrape news feeds for current events
3. Use search engines for problem-solving

Example expansion:

def add_internet_learning(council):
    import requests
    
    # Wikipedia integration
    def query_wikipedia(topic):
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}"
        response = requests.get(url)
        return response.json()['extract']
    
    # Teach agents new concepts
    for agent in council.agents:
        knowledge = query_wikipedia("Neural_network")
        # Convert text to embedding and fine-tune agent
        # (Implementation depends on your architecture)

Run this on Colab with:
!pip install wikipedia-api beautifulsoup4 requests
"""


if __name__ == "__main__":
    test_eden_council()
