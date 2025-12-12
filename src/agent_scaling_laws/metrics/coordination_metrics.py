"""
Coordination metrics for agent systems.

Based on "Towards a Science of Scaling Agent Systems" (arXiv 2512.08296v1).
Implements empirical coordination metrics: Efficiency, Overhead, Error Amplification, and Redundancy.
"""

from typing import Dict, Any, List
from dataclasses import dataclass
import numpy as np


@dataclass
class CoordinationMetrics:
    """
    Container for coordination metrics.
    
    Based on the paper's empirical coordination metrics framework.
    """
    
    efficiency: float
    overhead: float
    error_amplification: float
    redundancy: float
    
    def to_dict(self) -> Dict[str, float]:
        """Convert metrics to dictionary."""
        return {
            "efficiency": self.efficiency,
            "overhead": self.overhead,
            "error_amplification": self.error_amplification,
            "redundancy": self.redundancy,
        }
    
    def __repr__(self) -> str:
        return (
            f"CoordinationMetrics(\n"
            f"  efficiency={self.efficiency:.3f},\n"
            f"  overhead={self.overhead:.3f},\n"
            f"  error_amplification={self.error_amplification:.3f},\n"
            f"  redundancy={self.redundancy:.3f}\n"
            f")"
        )


def calculate_efficiency(
    task_progress: float,
    tokens_used: int,
    baseline_tokens: int = 100
) -> float:
    """
    Calculate efficiency metric.
    
    Measures actual useful task progress per unit computation,
    normalized to single-agent baseline.
    
    Args:
        task_progress: Progress made on task (0.0 to 1.0)
        tokens_used: Total tokens consumed
        baseline_tokens: Baseline token usage for single agent
        
    Returns:
        Efficiency score (higher is better)
    """
    if tokens_used == 0:
        return 0.0
    
    # Efficiency = (task progress) / (normalized token usage)
    normalized_tokens = tokens_used / baseline_tokens
    efficiency = task_progress / max(normalized_tokens, 0.01)
    
    return float(efficiency)


def calculate_overhead(
    total_tokens: int,
    agent_tokens: int,
    coordination_tokens: int
) -> float:
    """
    Calculate overhead metric.
    
    Quantifies additional computational cost due to multi-agent coordination
    beyond what is strictly necessary for the task.
    
    Args:
        total_tokens: Total tokens used by system
        agent_tokens: Tokens used by agents for actual task work
        coordination_tokens: Tokens used for coordination (messages, planning)
        
    Returns:
        Overhead ratio (0.0 = no overhead, higher = more overhead)
    """
    if total_tokens == 0:
        return 0.0
    
    # Overhead = coordination tokens / total tokens
    overhead = coordination_tokens / total_tokens
    
    return float(overhead)


def calculate_error_amplification(
    single_agent_error_rate: float,
    multi_agent_error_rate: float
) -> float:
    """
    Calculate error amplification metric.
    
    Measures multiplicative increase in error rate caused by unchecked
    propagation between agents.
    
    From paper:
    - Independent agents: 17.2x amplification
    - Centralized agents: 4.4x amplification
    
    Args:
        single_agent_error_rate: Baseline error rate for single agent (0.0 to 1.0)
        multi_agent_error_rate: Error rate for multi-agent system (0.0 to 1.0)
        
    Returns:
        Error amplification factor (1.0 = no amplification, higher = more amplification)
    """
    if single_agent_error_rate == 0:
        # If baseline has no errors, any errors in multi-agent is infinite amplification
        # Cap at a reasonable value
        return 20.0 if multi_agent_error_rate > 0 else 1.0
    
    # Amplification = multi-agent error rate / single-agent error rate
    amplification = multi_agent_error_rate / single_agent_error_rate
    
    return float(amplification)


def calculate_redundancy(
    unique_actions: int,
    total_actions: int
) -> float:
    """
    Calculate redundancy metric.
    
    Captures duplication of agent actions or decisions, leading to inefficiencies.
    
    Args:
        unique_actions: Number of unique actions taken
        total_actions: Total number of actions taken by all agents
        
    Returns:
        Redundancy ratio (0.0 = no redundancy, 1.0 = maximum redundancy)
    """
    if total_actions == 0:
        return 0.0
    
    # Redundancy = 1 - (unique actions / total actions)
    redundancy = 1.0 - (unique_actions / total_actions)
    
    return float(redundancy)


def compute_all_metrics(
    task_progress: float,
    total_tokens: int,
    agent_tokens: int,
    coordination_tokens: int,
    single_agent_error_rate: float,
    multi_agent_error_rate: float,
    unique_actions: int,
    total_actions: int,
    baseline_tokens: int = 100
) -> CoordinationMetrics:
    """
    Compute all coordination metrics at once.
    
    Args:
        task_progress: Progress made on task (0.0 to 1.0)
        total_tokens: Total tokens used by system
        agent_tokens: Tokens used by agents for actual task work
        coordination_tokens: Tokens used for coordination
        single_agent_error_rate: Baseline error rate for single agent
        multi_agent_error_rate: Error rate for multi-agent system
        unique_actions: Number of unique actions taken
        total_actions: Total actions by all agents
        baseline_tokens: Baseline token usage for single agent
        
    Returns:
        CoordinationMetrics object with all metrics
    """
    return CoordinationMetrics(
        efficiency=calculate_efficiency(task_progress, total_tokens, baseline_tokens),
        overhead=calculate_overhead(total_tokens, agent_tokens, coordination_tokens),
        error_amplification=calculate_error_amplification(
            single_agent_error_rate, multi_agent_error_rate
        ),
        redundancy=calculate_redundancy(unique_actions, total_actions),
    )


def metrics_from_results(
    results: List[Dict[str, Any]],
    baseline_metrics: Dict[str, Any]
) -> CoordinationMetrics:
    """
    Extract coordination metrics from task results.
    
    Args:
        results: List of task results from agents
        baseline_metrics: Baseline metrics from single agent
        
    Returns:
        CoordinationMetrics computed from results
    """
    # Extract data from results
    total_tokens = sum(r.get("tokens_used", 0) for r in results)
    successful_results = [r for r in results if r.get("success", False)]
    failed_results = [r for r in results if not r.get("success", False)]
    
    task_progress = len(successful_results) / max(len(results), 1)
    
    # Estimate coordination vs agent tokens
    coordination_tokens = sum(
        r.get("metadata", {}).get("coordination_overhead", 0) for r in results
    )
    agent_tokens = total_tokens - coordination_tokens
    
    # Error rates
    single_agent_error_rate = baseline_metrics.get("error_rate", 0.1)
    multi_agent_error_rate = len(failed_results) / max(len(results), 1)
    
    # Action counting (simplified)
    unique_actions = len(set(str(r.get("output")) for r in successful_results))
    total_actions = len(results)
    
    return compute_all_metrics(
        task_progress=task_progress,
        total_tokens=total_tokens,
        agent_tokens=agent_tokens,
        coordination_tokens=coordination_tokens,
        single_agent_error_rate=single_agent_error_rate,
        multi_agent_error_rate=multi_agent_error_rate,
        unique_actions=unique_actions,
        total_actions=total_actions,
        baseline_tokens=baseline_metrics.get("baseline_tokens", 100),
    )
