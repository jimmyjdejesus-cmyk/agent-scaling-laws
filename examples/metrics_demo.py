"""
Coordination metrics demonstration.

Shows how to compute and interpret coordination metrics for agent systems.
"""

from agent_scaling_laws.metrics import (
    compute_all_metrics,
    calculate_efficiency,
    calculate_overhead,
    calculate_error_amplification,
    calculate_redundancy,
)


def main():
    print("=" * 80)
    print("Agent Scaling Laws - Coordination Metrics Demo")
    print("=" * 80)
    
    # Example 1: Efficient Multi-Agent System
    print("\n" + "=" * 80)
    print("Example 1: Efficient Multi-Agent System")
    print("=" * 80)
    
    metrics1 = compute_all_metrics(
        task_progress=0.90,           # 90% completion
        total_tokens=550,             # Total tokens
        agent_tokens=500,             # Agent work tokens
        coordination_tokens=50,       # Coordination tokens
        single_agent_error_rate=0.15, # 15% baseline error
        multi_agent_error_rate=0.08,  # 8% multi-agent error (improved!)
        unique_actions=18,            # 18 unique actions
        total_actions=20,             # 20 total actions
        baseline_tokens=500,          # Baseline for single agent
    )
    
    print(f"\n{metrics1}")
    print("\nInterpretation:")
    print(f"  - High task progress (90%) with reasonable token usage")
    print(f"  - Low overhead (9.1% coordination cost)")
    print(f"  - Error rate improved vs baseline (0.53x amplification)")
    print(f"  - Low redundancy (10% duplicate actions)")
    print("  → This is an EFFICIENT multi-agent system!")
    
    # Example 2: Independent Agents (High Error Amplification)
    print("\n" + "=" * 80)
    print("Example 2: Independent Agents with Error Amplification")
    print("=" * 80)
    
    metrics2 = compute_all_metrics(
        task_progress=0.65,           # 65% completion
        total_tokens=800,             # High token usage
        agent_tokens=750,             # Mostly agent tokens
        coordination_tokens=50,       # Minimal coordination
        single_agent_error_rate=0.10, # 10% baseline error
        multi_agent_error_rate=0.65,  # 65% multi-agent error (much worse!)
        unique_actions=8,             # Few unique actions
        total_actions=20,             # Many total actions
        baseline_tokens=400,          # Baseline
    )
    
    print(f"\n{metrics2}")
    print("\nInterpretation:")
    print(f"  - Moderate task progress (65%)")
    print(f"  - Low coordination overhead (6.3%)")
    print(f"  - SEVERE error amplification (6.5x - approaching paper's 17.2x)")
    print(f"  - High redundancy (60% duplicate actions)")
    print("  → Independent agents amplify errors without coordination!")
    
    # Example 3: Centralized Coordination
    print("\n" + "=" * 80)
    print("Example 3: Centralized Coordination (Error Containment)")
    print("=" * 80)
    
    metrics3 = compute_all_metrics(
        task_progress=0.85,           # 85% completion
        total_tokens=600,             # Moderate token usage
        agent_tokens=480,             # Agent work
        coordination_tokens=120,      # Significant coordination
        single_agent_error_rate=0.12, # 12% baseline error
        multi_agent_error_rate=0.18,  # 18% multi-agent error
        unique_actions=16,            # Good uniqueness
        total_actions=18,             # Low duplication
        baseline_tokens=450,          # Baseline
    )
    
    print(f"\n{metrics3}")
    print("\nInterpretation:")
    print(f"  - High task progress (85%)")
    print(f"  - Moderate overhead (20% coordination cost)")
    print(f"  - Contained error amplification (1.5x - better than 4.4x from paper)")
    print(f"  - Low redundancy (11% duplicate actions)")
    print("  → Centralized coordination contains errors effectively!")
    
    # Example 4: Overhead-Heavy System
    print("\n" + "=" * 80)
    print("Example 4: Overhead-Heavy System")
    print("=" * 80)
    
    metrics4 = compute_all_metrics(
        task_progress=0.70,           # 70% completion
        total_tokens=1000,            # Very high token usage
        agent_tokens=400,             # Low agent work
        coordination_tokens=600,      # Excessive coordination!
        single_agent_error_rate=0.10, # 10% baseline
        multi_agent_error_rate=0.12,  # 12% multi-agent error
        unique_actions=14,            # Moderate uniqueness
        total_actions=15,             # Low duplication
        baseline_tokens=400,          # Baseline
    )
    
    print(f"\n{metrics4}")
    print("\nInterpretation:")
    print(f"  - Moderate task progress (70%)")
    print(f"  - VERY HIGH overhead (60% coordination cost)")
    print(f"  - Slight error amplification (1.2x)")
    print(f"  - Low redundancy (6.7%)")
    print("  → Excessive coordination overhead hurts efficiency!")
    
    # Example 5: Individual Metric Calculations
    print("\n" + "=" * 80)
    print("Example 5: Individual Metric Calculations")
    print("=" * 80)
    
    print("\nEfficiency Metric:")
    eff = calculate_efficiency(task_progress=0.80, tokens_used=400, baseline_tokens=500)
    print(f"  Task progress: 80%, Tokens: 400 (vs 500 baseline)")
    print(f"  Efficiency: {eff:.3f}")
    print(f"  → {'Good' if eff > 1.0 else 'Needs improvement'} efficiency")
    
    print("\nOverhead Metric:")
    ovh = calculate_overhead(total_tokens=600, agent_tokens=450, coordination_tokens=150)
    print(f"  Total: 600, Agent work: 450, Coordination: 150")
    print(f"  Overhead: {ovh:.1%}")
    print(f"  → {'High' if ovh > 0.3 else 'Moderate' if ovh > 0.15 else 'Low'} overhead")
    
    print("\nError Amplification:")
    print(f"  Independent agents (17.2x from paper):")
    ea_indep = calculate_error_amplification(0.10, 0.10 * 17.2)
    print(f"    Baseline: 10%, Multi-agent: {0.10 * 17.2:.1%}, Amplification: {ea_indep:.1f}x")
    
    print(f"  Centralized agents (4.4x from paper):")
    ea_cent = calculate_error_amplification(0.10, 0.10 * 4.4)
    print(f"    Baseline: 10%, Multi-agent: {0.10 * 4.4:.1%}, Amplification: {ea_cent:.1f}x")
    
    print("\nRedundancy Metric:")
    red = calculate_redundancy(unique_actions=7, total_actions=10)
    print(f"  Unique actions: 7, Total actions: 10")
    print(f"  Redundancy: {red:.1%}")
    print(f"  → {red:.1%} of actions were duplicates")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
