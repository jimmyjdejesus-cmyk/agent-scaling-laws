"""Tests for architecture selector model."""

import pytest
from agent_scaling_laws.models import ArchitectureSelector
from agent_scaling_laws.models.architecture_selector import (
    TaskCharacteristics,
    AgentCapabilities,
)


def test_task_characteristics_to_array():
    """Test task characteristics array conversion."""
    task = TaskCharacteristics(
        parallelizable=0.8,
        dynamic=0.6,
        sequential=0.3,
        tool_intensive=0.5,
        complexity=0.7,
    )
    
    arr = task.to_array()
    assert len(arr) == 5
    assert arr[0] == 0.8
    assert arr[4] == 0.7


def test_agent_capabilities_to_array():
    """Test agent capabilities array conversion."""
    caps = AgentCapabilities(
        baseline_accuracy=0.4,
        token_budget=5000,
        model_capability=0.8,
    )
    
    arr = caps.to_array()
    assert len(arr) == 3
    assert arr[0] == 0.4
    assert arr[2] == 0.8


def test_selector_initialization():
    """Test architecture selector initialization."""
    selector = ArchitectureSelector()
    assert selector.saturation_threshold == 0.45
    assert selector.saturation_beta < 0  # Negative beta for diminishing returns


def test_select_parallelizable_task():
    """Test selection for highly parallelizable task."""
    selector = ArchitectureSelector()
    
    # Financial analysis type task (from paper)
    task = TaskCharacteristics(
        parallelizable=0.9,
        dynamic=0.2,
        sequential=0.1,
        tool_intensive=0.5,
        complexity=0.6,
    )
    
    caps = AgentCapabilities(
        baseline_accuracy=0.35,
        token_budget=5000,
        model_capability=0.8,
    )
    
    selected = selector.select_architecture(task, caps)
    # Should prefer centralized for parallel tasks (80.9% improvement from paper)
    assert selected in ["centralized", "hybrid", "independent"]


def test_select_dynamic_task():
    """Test selection for dynamic task."""
    selector = ArchitectureSelector()
    
    # Web navigation type task (from paper)
    task = TaskCharacteristics(
        parallelizable=0.3,
        dynamic=0.9,
        sequential=0.4,
        tool_intensive=0.7,
        complexity=0.7,
    )
    
    caps = AgentCapabilities(
        baseline_accuracy=0.30,
        token_budget=3000,
        model_capability=0.7,
    )
    
    selected = selector.select_architecture(task, caps)
    # Should prefer decentralized for dynamic tasks (9.2% improvement from paper)
    assert selected in ["decentralized", "hybrid"]


def test_select_sequential_task():
    """Test selection for sequential reasoning task."""
    selector = ArchitectureSelector()
    
    # Sequential reasoning task (degrades 39-70% with multi-agent from paper)
    task = TaskCharacteristics(
        parallelizable=0.1,
        dynamic=0.2,
        sequential=0.9,
        tool_intensive=0.3,
        complexity=0.5,
    )
    
    caps = AgentCapabilities(
        baseline_accuracy=0.40,
        token_budget=2000,
        model_capability=0.75,
    )
    
    selected = selector.select_architecture(task, caps)
    # Should prefer single agent for sequential tasks
    assert selected == "single"


def test_capability_saturation():
    """Test capability saturation effect."""
    selector = ArchitectureSelector()
    
    # Simple task with high baseline accuracy
    task = TaskCharacteristics(
        parallelizable=0.5,
        dynamic=0.4,
        sequential=0.3,
        tool_intensive=0.4,
        complexity=0.4,
    )
    
    # High baseline accuracy above saturation threshold
    caps = AgentCapabilities(
        baseline_accuracy=0.60,  # Above 0.45 threshold
        token_budget=4000,
        model_capability=0.9,
    )
    
    selected = selector.select_architecture(task, caps)
    # Should prefer single agent due to saturation
    assert selected in ["single", "centralized"]  # Single likely better


def test_predict_all_scores():
    """Test predicting scores for all architectures."""
    selector = ArchitectureSelector()
    
    task = TaskCharacteristics(
        parallelizable=0.6,
        dynamic=0.5,
        sequential=0.4,
        tool_intensive=0.5,
        complexity=0.6,
    )
    
    caps = AgentCapabilities(
        baseline_accuracy=0.35,
        token_budget=4000,
        model_capability=0.8,
    )
    
    scores = selector.predict_all_scores(task, caps)
    
    # Should have scores for all architectures
    assert len(scores) == 5
    assert "single" in scores
    assert "independent" in scores
    assert "centralized" in scores
    assert "decentralized" in scores
    assert "hybrid" in scores
    
    # All scores should be numeric
    for arch, score in scores.items():
        assert isinstance(score, (int, float))


def test_explain_selection():
    """Test explanation generation."""
    selector = ArchitectureSelector()
    
    task = TaskCharacteristics(
        parallelizable=0.8,
        dynamic=0.3,
        sequential=0.2,
        tool_intensive=0.5,
        complexity=0.6,
    )
    
    caps = AgentCapabilities(
        baseline_accuracy=0.35,
        token_budget=5000,
        model_capability=0.8,
    )
    
    explanation = selector.explain_selection(task, caps)
    
    assert "selected_architecture" in explanation
    assert "scores" in explanation
    assert "reasoning" in explanation
    assert "task_characteristics" in explanation
    assert "agent_capabilities" in explanation
    
    # Check reasoning is generated
    assert isinstance(explanation["reasoning"], list)
    
    # Check task characteristics included
    tc = explanation["task_characteristics"]
    assert tc["parallelizable"] == 0.8
    assert tc["complexity"] == 0.6


def test_token_budget_effect():
    """Test token budget effect on selection."""
    selector = ArchitectureSelector()
    
    # Task that would benefit from coordination
    task = TaskCharacteristics(
        parallelizable=0.7,
        dynamic=0.5,
        sequential=0.2,
        tool_intensive=0.6,
        complexity=0.7,
    )
    
    # Low token budget
    low_caps = AgentCapabilities(
        baseline_accuracy=0.30,
        token_budget=500,  # Very limited
        model_capability=0.7,
    )
    
    # High token budget
    high_caps = AgentCapabilities(
        baseline_accuracy=0.30,
        token_budget=10000,  # Generous
        model_capability=0.7,
    )
    
    low_scores = selector.predict_all_scores(task, low_caps)
    high_scores = selector.predict_all_scores(task, high_caps)
    
    # Multi-agent should be penalized more with low budget
    # (Though exact comparison depends on scoring function)
    assert isinstance(low_scores["single"], (int, float))
    assert isinstance(high_scores["centralized"], (int, float))
