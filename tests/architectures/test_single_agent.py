"""Tests for single agent architecture."""

import pytest
from agent_scaling_laws.architectures.single_agent import SingleAgent


def test_single_agent_initialization():
    """Test single agent initialization."""
    agent = SingleAgent(agent_id="test_single")
    assert agent.agent_id == "test_single"


def test_single_agent_execute_callable():
    """Test single agent executing callable task."""
    agent = SingleAgent(capabilities={"tokens_per_task": 150})
    
    def task_func(ctx):
        return ctx.get("value", 0) * 2
    
    result = agent.execute_task(task_func, {"value": 10})
    
    assert result.success is True
    assert result.output == 20
    assert result.tokens_used == 150
    assert result.metadata["architecture"] == "single"


def test_single_agent_execute_data():
    """Test single agent with data task."""
    agent = SingleAgent()
    
    result = agent.execute_task("test_data")
    
    assert result.success is True
    assert result.output == "test_data"


def test_single_agent_error_handling():
    """Test single agent error handling."""
    agent = SingleAgent()
    
    def failing_task(ctx):
        raise ValueError("Task failed")
    
    result = agent.execute_task(failing_task, {})
    
    assert result.success is False
    assert result.output is None
    assert "Task failed" in result.error
    assert agent.errors_count == 1


def test_single_agent_metrics():
    """Test single agent metrics tracking."""
    agent = SingleAgent(capabilities={"tokens_per_task": 100})
    
    agent.execute_task(lambda ctx: "result1")
    agent.execute_task(lambda ctx: "result2")
    
    metrics = agent.get_metrics()
    assert metrics["tasks_completed"] == 2
    assert metrics["tokens_used"] == 200
    assert metrics["errors_count"] == 0
