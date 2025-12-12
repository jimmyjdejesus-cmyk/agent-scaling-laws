"""Tests for base agent functionality."""

import pytest
from agent_scaling_laws.architectures.base import Agent, TaskResult, Message


class MockAgent(Agent):
    """Mock agent for testing."""
    
    def execute_task(self, task, context=None):
        self.tasks_completed += 1
        self.tokens_used += 50
        return TaskResult(
            success=True,
            output="mock_result",
            tokens_used=50,
        )


def test_agent_initialization():
    """Test agent can be initialized."""
    agent = MockAgent(agent_id="test_agent", capabilities={"model": "test"})
    assert agent.agent_id == "test_agent"
    assert agent.capabilities["model"] == "test"
    assert agent.tokens_used == 0
    assert agent.tasks_completed == 0


def test_agent_execute_task():
    """Test agent can execute tasks."""
    agent = MockAgent(agent_id="test")
    result = agent.execute_task("test_task")
    
    assert result.success is True
    assert result.output == "mock_result"
    assert result.tokens_used == 50
    assert agent.tasks_completed == 1
    assert agent.tokens_used == 50


def test_agent_metrics():
    """Test agent metrics tracking."""
    agent = MockAgent(agent_id="test")
    
    # Execute some tasks
    agent.execute_task("task1")
    agent.execute_task("task2")
    
    metrics = agent.get_metrics()
    assert metrics["agent_id"] == "test"
    assert metrics["tasks_completed"] == 2
    assert metrics["tokens_used"] == 100


def test_agent_messages():
    """Test agent message handling."""
    agent = MockAgent(agent_id="sender")
    
    msg = Message(sender_id="sender", content="test message")
    agent.send_message(msg)
    
    assert len(agent.message_history) == 1
    assert agent.message_history[0].content == "test message"


def test_agent_reset_metrics():
    """Test resetting agent metrics."""
    agent = MockAgent(agent_id="test")
    
    agent.execute_task("task1")
    agent.send_message(Message(sender_id="test", content="msg"))
    
    agent.reset_metrics()
    
    assert agent.tokens_used == 0
    assert agent.tasks_completed == 0
    assert len(agent.message_history) == 0


def test_task_result():
    """Test TaskResult creation."""
    result = TaskResult(
        success=True,
        output="result",
        tokens_used=100,
        metadata={"arch": "test"}
    )
    
    assert result.success is True
    assert result.output == "result"
    assert result.tokens_used == 100
    assert result.metadata["arch"] == "test"


def test_message():
    """Test Message creation."""
    msg = Message(
        sender_id="agent1",
        content="Hello",
        message_type="greeting",
        metadata={"priority": "high"}
    )
    
    assert msg.sender_id == "agent1"
    assert msg.content == "Hello"
    assert msg.message_type == "greeting"
    assert msg.metadata["priority"] == "high"
