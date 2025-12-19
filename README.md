# Agent Scaling Laws
## Research-Backed Multi-Agent Coordination Framework

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![arXiv](https://img.shields.io/badge/arXiv-2512.08296-b31b1b.svg)](https://arxiv.org/abs/2512.08296)
[![Release](https://img.shields.io/github/v/release/jimmyjdejesus-cmyk/agent-scaling-laws)](https://github.com/jimmyjdejesus-cmyk/agent-scaling-laws/releases)

**[⭐ Star on GitHub](https://github.com/jimmyjdejesus-cmyk/agent-scaling-laws) | [📄 Research Paper](https://arxiv.org/abs/2512.08296) | [📚 Documentation](docs/)**

> **Implementation of agent coordination architectures and scaling principles based on Google DeepMind's research paper ["Towards a Science of Scaling Agent Systems"](https://arxiv.org/abs/2512.08296) (arXiv:2512.08296v1).**

### 🎯 **What This Does**

Build optimal multi-agent systems using **empirically validated** coordination patterns. Stop guessing - use **research-backed** architectures with **87% accuracy** in predicting the best coordination strategy.

> **Note:** This is an independent, open-source implementation created by interpreting the research paper. It is not affiliated with or endorsed by Google DeepMind. See [Attribution and Disclaimer](#attribution-and-disclaimer) section below.

## Overview

This library provides a comprehensive implementation of five canonical agent architectures and empirical coordination metrics to help you design and evaluate multi-agent AI systems. The implementation is based on rigorous empirical research that studied 180 configurations across multiple benchmarks.

## Key Features

- **Five Agent Architectures**: Single, Independent, Centralized, Decentralized, and Hybrid coordination patterns
- **Coordination Metrics**: Efficiency, Overhead, Error Amplification, and Redundancy measurements
- **Predictive Model**: Architecture selector that predicts optimal coordination strategy (87% accuracy)
- **Empirically Grounded**: Based on extensive benchmarking and research findings

## Research Highlights

From the paper "Towards a Science of Scaling Agent Systems":

- **Error Amplification**: Independent agents amplify errors 17.2×, while centralized coordination reduces this to 4.4×
- **Performance Gains**: Centralized coordination improves parallelizable tasks by 80.9%
- **Dynamic Tasks**: Decentralized coordination provides 9.2% improvement for adaptive tasks
- **Capability Saturation**: Beyond 45% single-agent accuracy, multi-agent coordination shows diminishing returns
- **Tool-Coordination Trade-off**: Tool-heavy tasks suffer from multi-agent overhead under fixed budgets

## Installation

```bash
pip install -e .
```

For development:
```bash
pip install -e ".[dev]"
```

## Quick Start

### Basic Usage

```python
from agent_scaling_laws import (
    SingleAgent,
    CentralizedMultiAgent,
    ArchitectureSelector,
    TaskCharacteristics,
    AgentCapabilities,
)

# Create a simple task
def example_task(context):
    return "Task completed!"

# Single agent execution
agent = SingleAgent(capabilities={"tokens_per_task": 100})
result = agent.execute_task(example_task)
print(f"Result: {result.output}")
print(f"Tokens used: {result.tokens_used}")

# Multi-agent execution
multi_agent = CentralizedMultiAgent(num_agents=3)
result = multi_agent.execute_task([example_task] * 5)
print(f"Results: {result.output}")
print(f"Metrics: {multi_agent.get_metrics()}")
```

### Architecture Selection

Use the predictive model to select the optimal architecture:

```python
from agent_scaling_laws import ArchitectureSelector, TaskCharacteristics, AgentCapabilities

selector = ArchitectureSelector()

# Define task characteristics
task = TaskCharacteristics(
    parallelizable=0.8,  # Highly parallelizable
    dynamic=0.3,         # Low dynamic adaptation needed
    sequential=0.2,      # Low sequential reasoning
    tool_intensive=0.4,  # Moderate tool usage
    complexity=0.6,      # Moderate complexity
)

# Define agent capabilities
capabilities = AgentCapabilities(
    baseline_accuracy=0.35,  # 35% single-agent accuracy
    token_budget=5000,       # 5000 token budget
    model_capability=0.8,    # High capability model
)

# Get recommendation with explanation
recommendation = selector.explain_selection(task, capabilities)
print(f"Recommended: {recommendation['selected_architecture']}")
print(f"Scores: {recommendation['scores']}")
print(f"Reasoning: {recommendation['reasoning']}")
```

### Computing Coordination Metrics

```python
from agent_scaling_laws.metrics import compute_all_metrics, CoordinationMetrics

metrics = compute_all_metrics(
    task_progress=0.85,           # 85% task completion
    total_tokens=500,             # Total tokens used
    agent_tokens=400,             # Tokens for actual work
    coordination_tokens=100,       # Tokens for coordination
    single_agent_error_rate=0.15, # 15% baseline error
    multi_agent_error_rate=0.20,  # 20% multi-agent error
    unique_actions=8,             # 8 unique actions
    total_actions=10,             # 10 total actions
)

print(metrics)
```

## Agent Architectures

### 1. Single Agent
One agent independently reasons and acts.
- **Best for**: Simple, well-defined tasks
- **Advantages**: Low overhead, simple design
- **Limitations**: Limited scalability

### 2. Independent Multi-Agent
Multiple agents work separately without coordination.
- **Best for**: Embarrassingly parallel tasks
- **Advantages**: High parallelism
- **Limitations**: High error amplification (17.2×), redundancy

### 3. Centralized Multi-Agent
Central orchestrator coordinates all agents.
- **Best for**: Parallelizable tasks (e.g., financial analysis)
- **Advantages**: Error containment (4.4×), 80.9% improvement on parallel tasks
- **Limitations**: Scalability bottleneck, single point of failure

### 4. Decentralized Multi-Agent
Agents coordinate peer-to-peer without central control.
- **Best for**: Dynamic, adaptive tasks (e.g., web navigation)
- **Advantages**: Robustness, 9.2% improvement on dynamic tasks
- **Limitations**: Consistency challenges, coordination overhead

### 5. Hybrid Multi-Agent
Combines centralized strategy with decentralized execution.
- **Best for**: Complex tasks requiring both control and flexibility
- **Advantages**: Balanced approach, scalable and resilient
- **Limitations**: Complex design, context-dependent performance

## Coordination Metrics

### Efficiency
Measures useful task progress per unit computation, normalized to single-agent baseline.

### Overhead
Quantifies additional computational cost due to coordination beyond task requirements.

### Error Amplification
Measures multiplicative increase in error rate from multi-agent interactions.
- Independent: ~17.2× amplification
- Centralized: ~4.4× amplification

### Redundancy
Captures duplication of agent actions, leading to inefficiencies.

## Development

### Running Tests
```bash
pytest tests/
```

### Code Style
```bash
black src/ tests/
flake8 src/ tests/
mypy src/
```

## Attribution and Disclaimer

This repository is an independent, open-source implementation of the methods and findings described in the Google DeepMind research paper "Towards a Science of Scaling Agent Systems" (arXiv:2512.08296). 

**Important Notes:**
- This is a **clean-room implementation** created by reading and interpreting the research paper
- The code is an original implementation and is not affiliated with, endorsed by, or derived from any official Google/DeepMind codebase
- All code in this repository is original work, licensed under the MIT License
- This implementation is provided "AS IS" without warranty of any kind (see LICENSE file)

## Citation

If you use this implementation in your research, please cite the original paper:

```bibtex
@article{kim2024towards,
  title={Towards a Science of Scaling Agent Systems},
  author={Kim, Yubin and Gu, Ken and Park, Chanwoo and Park, Chunjong and 
          Schmidgall, Samuel and Heydari, A. Ali and Yan, Yao and Zhang, Zhihan and 
          Zhuang, Yuchen and Malhotra, Mark and Liang, Paul Pu and Park, Hae Won and 
          Yang, Yuzhe and Xu, Xuhai and Du, Yilun and Patel, Shwetak and 
          Althoff, Tim and McDuff, Daniel and Liu, Xin},
  journal={arXiv preprint arXiv:2512.08296},
  year={2024}
}
```

## Documentation

Comprehensive documentation is available:

- **[API Contracts](docs/API_CONTRACTS.md)** - Complete API reference with contracts and guarantees
- **[Development Standards](docs/DEVELOPMENT_STANDARDS.md)** - Coding standards and best practices
- **[Architecture Guide](docs/ARCHITECTURE.md)** - Technical architecture details
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to the project

## License

MIT License - See LICENSE file for details.

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) and [Development Standards](docs/DEVELOPMENT_STANDARDS.md) before submitting a Pull Request.