"""Tests for coordination metrics."""

import pytest
from agent_scaling_laws.metrics import (
    CoordinationMetrics,
    calculate_efficiency,
    calculate_overhead,
    calculate_error_amplification,
    calculate_redundancy,
    compute_all_metrics,
)


def test_calculate_efficiency():
    """Test efficiency metric calculation."""
    # Perfect efficiency: 100% progress with baseline tokens
    eff = calculate_efficiency(task_progress=1.0, tokens_used=100, baseline_tokens=100)
    assert eff == pytest.approx(1.0)
    
    # Better than baseline
    eff = calculate_efficiency(task_progress=0.8, tokens_used=50, baseline_tokens=100)
    assert eff > 1.0
    
    # Worse than baseline
    eff = calculate_efficiency(task_progress=0.5, tokens_used=200, baseline_tokens=100)
    assert eff < 0.5


def test_calculate_overhead():
    """Test overhead metric calculation."""
    # No overhead
    overhead = calculate_overhead(total_tokens=100, agent_tokens=100, coordination_tokens=0)
    assert overhead == 0.0
    
    # 20% overhead
    overhead = calculate_overhead(total_tokens=100, agent_tokens=80, coordination_tokens=20)
    assert overhead == pytest.approx(0.2)
    
    # 50% overhead
    overhead = calculate_overhead(total_tokens=200, agent_tokens=100, coordination_tokens=100)
    assert overhead == pytest.approx(0.5)


def test_calculate_error_amplification():
    """Test error amplification calculation."""
    # No amplification
    amp = calculate_error_amplification(single_agent_error_rate=0.1, multi_agent_error_rate=0.1)
    assert amp == pytest.approx(1.0)
    
    # Independent agents (17.2x from paper)
    amp = calculate_error_amplification(single_agent_error_rate=0.1, multi_agent_error_rate=0.1 * 17.2)
    assert amp == pytest.approx(17.2, rel=0.01)
    
    # Centralized agents (4.4x from paper)
    amp = calculate_error_amplification(single_agent_error_rate=0.1, multi_agent_error_rate=0.1 * 4.4)
    assert amp == pytest.approx(4.4, rel=0.01)
    
    # Error reduction (< 1.0x)
    amp = calculate_error_amplification(single_agent_error_rate=0.2, multi_agent_error_rate=0.1)
    assert amp == pytest.approx(0.5)


def test_calculate_redundancy():
    """Test redundancy metric calculation."""
    # No redundancy
    red = calculate_redundancy(unique_actions=10, total_actions=10)
    assert red == 0.0
    
    # 50% redundancy
    red = calculate_redundancy(unique_actions=5, total_actions=10)
    assert red == pytest.approx(0.5)
    
    # High redundancy
    red = calculate_redundancy(unique_actions=2, total_actions=10)
    assert red == pytest.approx(0.8)


def test_compute_all_metrics():
    """Test computing all metrics together."""
    metrics = compute_all_metrics(
        task_progress=0.8,
        total_tokens=500,
        agent_tokens=400,
        coordination_tokens=100,
        single_agent_error_rate=0.1,
        multi_agent_error_rate=0.15,
        unique_actions=8,
        total_actions=10,
        baseline_tokens=400,
    )
    
    assert isinstance(metrics, CoordinationMetrics)
    assert metrics.efficiency > 0
    assert metrics.overhead == pytest.approx(0.2)
    assert metrics.error_amplification == pytest.approx(1.5)
    assert metrics.redundancy == pytest.approx(0.2)


def test_coordination_metrics_to_dict():
    """Test converting metrics to dictionary."""
    metrics = CoordinationMetrics(
        efficiency=1.2,
        overhead=0.15,
        error_amplification=2.5,
        redundancy=0.3,
    )
    
    d = metrics.to_dict()
    assert d["efficiency"] == 1.2
    assert d["overhead"] == 0.15
    assert d["error_amplification"] == 2.5
    assert d["redundancy"] == 0.3


def test_coordination_metrics_repr():
    """Test metrics string representation."""
    metrics = CoordinationMetrics(
        efficiency=1.234,
        overhead=0.156,
        error_amplification=3.789,
        redundancy=0.234,
    )
    
    repr_str = repr(metrics)
    assert "efficiency=1.234" in repr_str
    assert "overhead=0.156" in repr_str
    assert "error_amplification=3.789" in repr_str
    assert "redundancy=0.234" in repr_str


def test_edge_cases():
    """Test edge cases in metrics calculation."""
    # Zero tokens
    eff = calculate_efficiency(task_progress=0.5, tokens_used=0, baseline_tokens=100)
    assert eff == 0.0
    
    overhead = calculate_overhead(total_tokens=0, agent_tokens=0, coordination_tokens=0)
    assert overhead == 0.0
    
    # Zero baseline error
    amp = calculate_error_amplification(single_agent_error_rate=0.0, multi_agent_error_rate=0.0)
    assert amp == pytest.approx(1.0)
    
    amp = calculate_error_amplification(single_agent_error_rate=0.0, multi_agent_error_rate=0.1)
    assert amp == pytest.approx(20.0)  # Capped
    
    # Zero actions
    red = calculate_redundancy(unique_actions=0, total_actions=0)
    assert red == 0.0
