"""
Basic usage example for agent scaling laws.

Demonstrates how to use different agent architectures and compare their performance.
"""

from agent_scaling_laws import (
    SingleAgent,
    IndependentMultiAgent,
    CentralizedMultiAgent,
    DecentralizedMultiAgent,
    HybridMultiAgent,
)


def simple_math_task(context):
    """Example task: simple computation."""
    x = context.get("x", 10)
    return x * 2 + 5


def main():
    print("=" * 60)
    print("Agent Scaling Laws - Basic Usage Example")
    print("=" * 60)
    
    # Define task context
    task_context = {"x": 15}
    
    # Configure capabilities
    capabilities = {
        "tokens_per_task": 100,
        "coordination_tokens_per_task": 10,
        "communication_tokens_per_message": 5,
    }
    
    # Test 1: Single Agent
    print("\n1. Single Agent Architecture")
    print("-" * 60)
    single_agent = SingleAgent(capabilities=capabilities)
    result = single_agent.execute_task(simple_math_task, task_context)
    print(f"Result: {result.output}")
    print(f"Success: {result.success}")
    print(f"Tokens used: {result.tokens_used}")
    print(f"Metrics: {single_agent.get_metrics()}")
    
    # Test 2: Independent Multi-Agent
    print("\n2. Independent Multi-Agent Architecture")
    print("-" * 60)
    independent = IndependentMultiAgent(num_agents=3, capabilities=capabilities)
    result = independent.execute_task(simple_math_task, task_context)
    print(f"Result: {result.output}")
    print(f"Success: {result.success}")
    print(f"Tokens used: {result.tokens_used}")
    print(f"Metadata: {result.metadata}")
    
    # Test 3: Centralized Multi-Agent
    print("\n3. Centralized Multi-Agent Architecture")
    print("-" * 60)
    centralized = CentralizedMultiAgent(num_agents=3, capabilities=capabilities)
    
    # Test with multiple tasks
    tasks = [
        lambda ctx: simple_math_task({"x": 10}),
        lambda ctx: simple_math_task({"x": 20}),
        lambda ctx: simple_math_task({"x": 30}),
    ]
    
    result = centralized.execute_task(tasks, task_context)
    print(f"Results: {result.output}")
    print(f"Success: {result.success}")
    print(f"Tokens used: {result.tokens_used}")
    print(f"Metadata: {result.metadata}")
    
    # Test 4: Decentralized Multi-Agent
    print("\n4. Decentralized Multi-Agent Architecture")
    print("-" * 60)
    decentralized = DecentralizedMultiAgent(
        num_agents=3,
        capabilities={
            **capabilities,
            "coordination_rounds": 2,
        }
    )
    result = decentralized.execute_task(simple_math_task, task_context)
    print(f"Result: {result.output}")
    print(f"Success: {result.success}")
    print(f"Tokens used: {result.tokens_used}")
    print(f"Metadata: {result.metadata}")
    
    # Test 5: Hybrid Multi-Agent
    print("\n5. Hybrid Multi-Agent Architecture")
    print("-" * 60)
    hybrid = HybridMultiAgent(
        num_agents=6,
        team_size=2,
        capabilities={
            **capabilities,
            "strategy_tokens": 20,
            "aggregation_tokens": 15,
            "team_comm_tokens": 3,
        }
    )
    
    # Multiple tasks for teams
    tasks = [
        lambda ctx: simple_math_task({"x": 5}),
        lambda ctx: simple_math_task({"x": 10}),
        lambda ctx: simple_math_task({"x": 15}),
    ]
    
    result = hybrid.execute_task(tasks, task_context)
    print(f"Results: {result.output}")
    print(f"Success: {result.success}")
    print(f"Tokens used: {result.tokens_used}")
    print(f"Metadata: {result.metadata}")
    
    print("\n" + "=" * 60)
    print("Comparison Summary")
    print("=" * 60)
    
    architectures = [
        ("Single", single_agent),
        ("Independent", independent),
        ("Centralized", centralized),
        ("Decentralized", decentralized),
        ("Hybrid", hybrid),
    ]
    
    for name, agent in architectures:
        metrics = agent.get_metrics()
        print(f"\n{name}:")
        print(f"  Tokens used: {metrics['tokens_used']}")
        print(f"  Tasks completed: {metrics['tasks_completed']}")
        print(f"  Errors: {metrics['errors_count']}")


if __name__ == "__main__":
    main()
