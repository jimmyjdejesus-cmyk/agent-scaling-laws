"""Tests for all agent architectures and top-level exports."""

import pytest
from agent_scaling_laws import (
    IndependentMultiAgent,
    CentralizedMultiAgent,
    DecentralizedMultiAgent,
    HybridMultiAgent,
    TaskResult,
    Message,
    ArchitectureSelector,
    TaskCharacteristics,
    AgentCapabilities,
)

def test_independent_agent():
    """Test IndependentMultiAgent."""
    agent = IndependentMultiAgent(num_agents=3, capabilities={"tokens_per_task": 10})
    result = agent.execute_task("test_task")
    assert result.success
    metrics = agent.get_metrics()
    assert metrics["total_agent_tokens"] == 30  # 3 agents * 10 tokens

def test_centralized_agent():
    """Test CentralizedMultiAgent."""
    agent = CentralizedMultiAgent(num_agents=3, capabilities={"tokens_per_task": 10, "coordination_tokens_per_task": 5})
    result = agent.execute_task(["task1", "task2", "task3"])
    assert result.success
    # Output should be aggregated
    assert len(result.output) == 3
    metrics = agent.get_metrics()
    # 3 tasks executed by agents + coordination
    assert metrics["total_agent_tokens"] == 30
    assert metrics["coordination_overhead"] == 15 # 3 tasks * 5 tokens

def test_decentralized_agent():
    """Test DecentralizedMultiAgent."""
    agent = DecentralizedMultiAgent(
        num_agents=3,
        capabilities={
            "tokens_per_task": 10,
            "communication_tokens_per_message": 2,
            "coordination_rounds": 1
        }
    )
    result = agent.execute_task("test_task")
    assert result.success
    metrics = agent.get_metrics()
    # 3 agents * 1 round * 10 tokens
    assert metrics["total_agent_tokens"] == 30
    # Communication overhead: 3 agents send result message to 2 peers
    # Broadcast: 3 senders * 2 receivers * 2 tokens = 12 tokens?
    # Let's check logic: _broadcast_message adds tokens_used += comm_tokens * (num_agents - 1)
    # Each agent succeeds in round 0, broadcasts result.
    # 3 broadcasts. Each costs 2 * 2 = 4 tokens. Total 12.
    assert metrics["communication_overhead"] == 12

def test_hybrid_agent():
    """Test HybridMultiAgent."""
    # 4 agents, team size 2 => 2 teams
    agent = HybridMultiAgent(
        num_agents=4,
        team_size=2,
        capabilities={
            "tokens_per_task": 10,
            "strategy_tokens": 5,
            "team_comm_tokens": 2,
            "aggregation_tokens": 5
        }
    )
    result = agent.execute_task(["task1", "task2"]) # 2 tasks, one per team
    assert result.success
    metrics = agent.get_metrics()
    # Strategy: 5
    # Teams: 2 teams.
    # Team 1: 2 agents. Each runs task (10). One success message (2). Total 22?
    # Wait, _team_coordination: each agent executes task.
    # 2 agents * 10 = 20 tokens.
    # If success, sends message. Both succeed. 2 messages * 2 tokens = 4 tokens (added to strategy/hybrid agent? No, added to agent tokens_used?)
    # Wait, Hybrid agent tracks its own tokens_used for strategy/agg/team_comm?
    # _team_coordination: self.tokens_used += comm_tokens. self is HybridAgent.
    # So team comms are counted in hybrid agent overhead.

    # Overhead breakdown:
    # 1. Strategy: 5
    # 2. Team 1 comms: 2 agents succeed -> 2 messages. 2 * 2 = 4.
    # 3. Team 2 comms: 2 agents succeed -> 2 messages. 2 * 2 = 4.
    # 4. Aggregation: 5
    # Total overhead: 5 + 4 + 4 + 5 = 18.

    assert metrics["coordination_overhead"] == 18

def test_architecture_selector():
    """Test ArchitectureSelector and data classes."""
    selector = ArchitectureSelector()

    task = TaskCharacteristics(
        parallelizable=0.9,
        dynamic=0.1,
        sequential=0.1,
        tool_intensive=0.1,
        complexity=0.3
    )

    capabilities = AgentCapabilities(
        baseline_accuracy=0.6,
        token_budget=10000,
        model_capability=0.9
    )

    recommendation = selector.select_architecture(task, capabilities)
    # Highly parallelizable + high accuracy -> Centralized likely (or Independent)
    # But independent has high error amp penalty.
    # Centralized has bonus.
    assert recommendation in ["centralized", "independent", "hybrid"]

    explanation = selector.explain_selection(task, capabilities)
    assert "reasoning" in explanation
    assert "scores" in explanation
