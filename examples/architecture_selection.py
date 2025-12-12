"""
Architecture selection example.

Demonstrates how to use the predictive model to select optimal architectures
for different task types.
"""

from agent_scaling_laws.models import ArchitectureSelector
from agent_scaling_laws.models.architecture_selector import (
    TaskCharacteristics,
    AgentCapabilities,
)


def main():
    print("=" * 80)
    print("Agent Scaling Laws - Architecture Selection Example")
    print("=" * 80)
    
    selector = ArchitectureSelector()
    
    # Example 1: Financial Analysis (Parallelizable Task)
    print("\n" + "=" * 80)
    print("Example 1: Financial Analysis Task")
    print("=" * 80)
    
    financial_task = TaskCharacteristics(
        parallelizable=0.9,   # Highly parallelizable
        dynamic=0.2,          # Low dynamic adaptation
        sequential=0.1,       # Minimal sequential reasoning
        tool_intensive=0.5,   # Moderate tool usage
        complexity=0.6,       # Moderate complexity
    )
    
    financial_capabilities = AgentCapabilities(
        baseline_accuracy=0.35,  # 35% single-agent accuracy
        token_budget=5000,       # Generous token budget
        model_capability=0.8,    # High capability model
    )
    
    result = selector.explain_selection(financial_task, financial_capabilities)
    print(f"\nRecommended Architecture: {result['selected_architecture'].upper()}")
    print(f"\nScores:")
    for arch, score in sorted(result['scores'].items(), key=lambda x: -x[1]):
        print(f"  {arch:15s}: {score:.3f}")
    
    print(f"\nReasoning:")
    for reason in result['reasoning']:
        print(f"  - {reason}")
    
    # Example 2: Web Navigation (Dynamic Task)
    print("\n" + "=" * 80)
    print("Example 2: Web Navigation Task")
    print("=" * 80)
    
    web_task = TaskCharacteristics(
        parallelizable=0.3,   # Low parallelizability
        dynamic=0.9,          # High dynamic adaptation
        sequential=0.4,       # Some sequential reasoning
        tool_intensive=0.7,   # High tool usage
        complexity=0.7,       # High complexity
    )
    
    web_capabilities = AgentCapabilities(
        baseline_accuracy=0.30,  # 30% single-agent accuracy
        token_budget=3000,       # Moderate token budget
        model_capability=0.7,    # Good capability model
    )
    
    result = selector.explain_selection(web_task, web_capabilities)
    print(f"\nRecommended Architecture: {result['selected_architecture'].upper()}")
    print(f"\nScores:")
    for arch, score in sorted(result['scores'].items(), key=lambda x: -x[1]):
        print(f"  {arch:15s}: {score:.3f}")
    
    print(f"\nReasoning:")
    for reason in result['reasoning']:
        print(f"  - {reason}")
    
    # Example 3: Sequential Reasoning Task
    print("\n" + "=" * 80)
    print("Example 3: Sequential Reasoning Task")
    print("=" * 80)
    
    sequential_task = TaskCharacteristics(
        parallelizable=0.1,   # Very low parallelizability
        dynamic=0.2,          # Low dynamic adaptation
        sequential=0.9,       # High sequential reasoning
        tool_intensive=0.3,   # Low tool usage
        complexity=0.5,       # Moderate complexity
    )
    
    sequential_capabilities = AgentCapabilities(
        baseline_accuracy=0.40,  # 40% single-agent accuracy
        token_budget=2000,       # Limited token budget
        model_capability=0.75,   # Good capability model
    )
    
    result = selector.explain_selection(sequential_task, sequential_capabilities)
    print(f"\nRecommended Architecture: {result['selected_architecture'].upper()}")
    print(f"\nScores:")
    for arch, score in sorted(result['scores'].items(), key=lambda x: -x[1]):
        print(f"  {arch:15s}: {score:.3f}")
    
    print(f"\nReasoning:")
    for reason in result['reasoning']:
        print(f"  - {reason}")
    
    # Example 4: High Capability Saturation
    print("\n" + "=" * 80)
    print("Example 4: High Single-Agent Capability (Saturation)")
    print("=" * 80)
    
    simple_task = TaskCharacteristics(
        parallelizable=0.5,   # Moderate parallelizability
        dynamic=0.4,          # Moderate dynamic adaptation
        sequential=0.3,       # Low sequential reasoning
        tool_intensive=0.4,   # Moderate tool usage
        complexity=0.4,       # Moderate complexity
    )
    
    high_capabilities = AgentCapabilities(
        baseline_accuracy=0.60,  # 60% single-agent accuracy (above saturation!)
        token_budget=4000,       # Good token budget
        model_capability=0.9,    # Very high capability model
    )
    
    result = selector.explain_selection(simple_task, high_capabilities)
    print(f"\nRecommended Architecture: {result['selected_architecture'].upper()}")
    print(f"\nScores:")
    for arch, score in sorted(result['scores'].items(), key=lambda x: -x[1]):
        print(f"  {arch:15s}: {score:.3f}")
    
    print(f"\nReasoning:")
    for reason in result['reasoning']:
        print(f"  - {reason}")
    
    # Example 5: Complex Hybrid Task
    print("\n" + "=" * 80)
    print("Example 5: Complex Multi-Faceted Task")
    print("=" * 80)
    
    complex_task = TaskCharacteristics(
        parallelizable=0.6,   # Moderate parallelizability
        dynamic=0.6,          # Moderate dynamic adaptation
        sequential=0.5,       # Moderate sequential reasoning
        tool_intensive=0.6,   # Moderate tool usage
        complexity=0.9,       # Very high complexity
    )
    
    balanced_capabilities = AgentCapabilities(
        baseline_accuracy=0.25,  # 25% single-agent accuracy
        token_budget=6000,       # Large token budget
        model_capability=0.85,   # High capability model
    )
    
    result = selector.explain_selection(complex_task, balanced_capabilities)
    print(f"\nRecommended Architecture: {result['selected_architecture'].upper()}")
    print(f"\nScores:")
    for arch, score in sorted(result['scores'].items(), key=lambda x: -x[1]):
        print(f"  {arch:15s}: {score:.3f}")
    
    print(f"\nReasoning:")
    for reason in result['reasoning']:
        print(f"  - {reason}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
