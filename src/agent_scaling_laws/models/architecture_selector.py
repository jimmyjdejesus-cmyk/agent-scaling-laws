"""
Predictive model for selecting optimal agent architecture.

Based on "Towards a Science of Scaling Agent Systems" (arXiv 2512.08296v1).
Uses empirical coordination metrics to predict best architecture for a task.
"""

from typing import Dict, Any, Optional, Literal, List
from dataclasses import dataclass
import numpy as np


ArchitectureType = Literal["single", "independent", "centralized", "decentralized", "hybrid"]


@dataclass
class TaskCharacteristics:
    """Characteristics of a task that influence architecture selection."""
    
    parallelizable: float  # 0.0 to 1.0: degree of parallelizability
    dynamic: float  # 0.0 to 1.0: degree of dynamic adaptation needed
    sequential: float  # 0.0 to 1.0: degree of sequential reasoning required
    tool_intensive: float  # 0.0 to 1.0: degree of tool usage required
    complexity: float  # 0.0 to 1.0: overall task complexity
    
    def to_array(self) -> np.ndarray:
        """Convert to numpy array for model input."""
        return np.array([
            self.parallelizable,
            self.dynamic,
            self.sequential,
            self.tool_intensive,
            self.complexity,
        ])


@dataclass
class AgentCapabilities:
    """Capabilities of the agent/model being used."""
    
    baseline_accuracy: float  # Single agent accuracy on task (0.0 to 1.0)
    token_budget: int  # Total token budget available
    model_capability: float  # 0.0 to 1.0: relative capability of LLM
    
    def to_array(self) -> np.ndarray:
        """Convert to numpy array for model input."""
        return np.array([
            self.baseline_accuracy,
            np.log10(self.token_budget + 1) / 5.0,  # Normalize log scale
            self.model_capability,
        ])


class ArchitectureSelector:
    """
    Predictive model for selecting optimal agent architecture.
    
    Based on the paper's framework that achieves:
    - R² = 0.513 for cross-validated predictions
    - 87% accuracy in predicting optimal coordination strategy
    
    Key insights from paper:
    - Capability saturation: diminishing returns when baseline > 45% (β=-0.408, p<0.001)
    - Parallelizable tasks: centralized coordination +80.9%
    - Dynamic tasks: decentralized coordination +9.2%
    - Sequential tasks: multi-agent degrades by 39-70%
    - Tool-heavy tasks: multi-agent overhead hurts under fixed budgets
    """
    
    def __init__(self):
        """Initialize the architecture selector with empirical coefficients."""
        # Coefficients derived from paper's empirical study
        # These are simplified versions - real implementation would use full regression model
        
        # Capability saturation threshold
        self.saturation_threshold = 0.45
        self.saturation_beta = -0.408
        
        # Architecture performance modifiers by task type
        self.architecture_modifiers = {
            "single": {
                "base": 1.0,
                "sequential_bonus": 0.3,
                "simple_task_bonus": 0.2,
            },
            "independent": {
                "base": 0.7,
                "error_amplification": -0.172,  # 17.2x amplification
                "parallel_bonus": 0.4,
            },
            "centralized": {
                "base": 0.9,
                "error_amplification": -0.044,  # 4.4x amplification
                "parallel_bonus": 0.809,  # 80.9% improvement
                "overhead_penalty": -0.2,
            },
            "decentralized": {
                "base": 0.85,
                "dynamic_bonus": 0.092,  # 9.2% improvement
                "coordination_cost": -0.15,
            },
            "hybrid": {
                "base": 0.88,
                "complex_bonus": 0.3,
                "balanced_bonus": 0.15,
            },
        }
    
    def _calculate_architecture_score(
        self,
        architecture: ArchitectureType,
        task: TaskCharacteristics,
        capabilities: AgentCapabilities,
    ) -> float:
        """
        Calculate predicted performance score for an architecture.
        
        Args:
            architecture: Architecture type to evaluate
            task: Task characteristics
            capabilities: Agent capabilities
            
        Returns:
            Predicted performance score (0.0 to 1.0+)
        """
        mods = self.architecture_modifiers[architecture]
        score = mods["base"]
        
        # Apply capability saturation effect
        if capabilities.baseline_accuracy > self.saturation_threshold:
            saturation_penalty = self.saturation_beta * (
                capabilities.baseline_accuracy - self.saturation_threshold
            )
            if architecture != "single":
                score += saturation_penalty
        
        # Architecture-specific scoring
        if architecture == "single":
            score += mods["sequential_bonus"] * task.sequential
            if task.complexity < 0.5:
                score += mods["simple_task_bonus"]
        
        elif architecture == "independent":
            score += mods["parallel_bonus"] * task.parallelizable
            # Error amplification hurts performance
            score += mods["error_amplification"] * (1.0 - capabilities.baseline_accuracy)
        
        elif architecture == "centralized":
            score += mods["parallel_bonus"] * task.parallelizable
            # Overhead penalty for tool-intensive tasks
            score += mods["overhead_penalty"] * task.tool_intensive
            # Error containment helps
            score += mods["error_amplification"]
        
        elif architecture == "decentralized":
            score += mods["dynamic_bonus"] * task.dynamic
            score += mods["coordination_cost"] * (1.0 - task.parallelizable)
            # Penalty for sequential tasks
            if task.sequential > 0.6:
                score -= 0.4
        
        elif architecture == "hybrid":
            score += mods["complex_bonus"] * task.complexity
            # Hybrid works well for balanced tasks
            balance = 1.0 - np.std([task.parallelizable, task.dynamic, task.sequential])
            score += mods["balanced_bonus"] * balance
        
        # Token budget considerations
        if capabilities.token_budget < 1000 and architecture != "single":
            score -= 0.2  # Coordination overhead hurts with limited budget
        
        # Model capability boost
        score *= (0.8 + 0.4 * capabilities.model_capability)
        
        return float(score)
    
    def select_architecture(
        self,
        task: TaskCharacteristics,
        capabilities: AgentCapabilities,
    ) -> ArchitectureType:
        """
        Select optimal architecture for given task and capabilities.
        
        Args:
            task: Task characteristics
            capabilities: Agent capabilities
            
        Returns:
            Recommended architecture type
        """
        architectures: list[ArchitectureType] = [
            "single",
            "independent",
            "centralized",
            "decentralized",
            "hybrid",
        ]
        
        scores = {
            arch: self._calculate_architecture_score(arch, task, capabilities)
            for arch in architectures
        }
        
        # Select architecture with highest score
        best_architecture = max(scores.items(), key=lambda x: x[1])[0]
        
        return best_architecture
    
    def predict_all_scores(
        self,
        task: TaskCharacteristics,
        capabilities: AgentCapabilities,
    ) -> Dict[ArchitectureType, float]:
        """
        Predict performance scores for all architectures.
        
        Args:
            task: Task characteristics
            capabilities: Agent capabilities
            
        Returns:
            Dictionary mapping architecture to predicted score
        """
        architectures: List[ArchitectureType] = [
            "single",
            "independent",
            "centralized",
            "decentralized",
            "hybrid",
        ]
        
        scores = {
            arch: self._calculate_architecture_score(arch, task, capabilities)
            for arch in architectures
        }
        
        return scores
    
    def explain_selection(
        self,
        task: TaskCharacteristics,
        capabilities: AgentCapabilities,
    ) -> Dict[str, Any]:
        """
        Explain the architecture selection with reasoning.
        
        Args:
            task: Task characteristics
            capabilities: Agent capabilities
            
        Returns:
            Dictionary with selection, scores, and reasoning
        """
        selected = self.select_architecture(task, capabilities)
        scores = self.predict_all_scores(task, capabilities)
        
        # Generate reasoning
        reasoning = []
        
        if capabilities.baseline_accuracy > self.saturation_threshold:
            reasoning.append(
                f"Single agent baseline accuracy ({capabilities.baseline_accuracy:.1%}) "
                f"exceeds saturation threshold ({self.saturation_threshold:.1%}). "
                f"Multi-agent coordination may have diminishing returns."
            )
        
        if task.parallelizable > 0.7:
            reasoning.append(
                "Task is highly parallelizable. Centralized coordination "
                "may provide significant improvement (up to 80.9%)."
            )
        
        if task.dynamic > 0.7:
            reasoning.append(
                "Task requires dynamic adaptation. Decentralized coordination "
                "provides robustness (9.2% improvement)."
            )
        
        if task.sequential > 0.6:
            reasoning.append(
                "Task requires sequential reasoning. Multi-agent architectures "
                "may degrade performance by 39-70%."
            )
        
        if task.tool_intensive > 0.7 and capabilities.token_budget < 5000:
            reasoning.append(
                "Task is tool-intensive with limited token budget. "
                "Multi-agent overhead may hurt performance."
            )
        
        return {
            "selected_architecture": selected,
            "scores": scores,
            "reasoning": reasoning,
            "task_characteristics": {
                "parallelizable": task.parallelizable,
                "dynamic": task.dynamic,
                "sequential": task.sequential,
                "tool_intensive": task.tool_intensive,
                "complexity": task.complexity,
            },
            "agent_capabilities": {
                "baseline_accuracy": capabilities.baseline_accuracy,
                "token_budget": capabilities.token_budget,
                "model_capability": capabilities.model_capability,
            },
        }
