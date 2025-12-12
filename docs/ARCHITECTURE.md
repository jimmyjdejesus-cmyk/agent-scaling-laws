# Architecture Documentation

This document describes the internal architecture of the agent-scaling-laws library.

## Package Structure

```
agent-scaling-laws/
├── src/agent_scaling_laws/
│   ├── architectures/      # Agent architecture implementations
│   ├── metrics/            # Coordination metrics
│   ├── models/             # Predictive models
│   └── utils/              # Utility functions
├── tests/                  # Test suite
├── examples/               # Usage examples
└── docs/                   # Documentation
```

## Core Components

### 1. Agent Architectures (`architectures/`)

All architectures implement the paper's five canonical patterns with empirically-grounded coordination strategies.

See README.md for detailed descriptions of each architecture type and their characteristics from the research paper.

## Extension Points

### Adding New Architectures
1. Inherit from `Agent` base class
2. Implement `execute_task()` method
3. Add to architecture selector scoring
4. Write tests

### Adding New Metrics
1. Add calculation function to `coordination_metrics.py`
2. Update `CoordinationMetrics` dataclass if persistent
3. Export from `__init__.py`
4. Write tests

## Performance Considerations

- **ThreadPoolExecutor**: Used for parallel agent execution
- **Message Passing**: In-memory lists for coordination
- **State Management**: Dictionary-based for simplicity
- **Scalability**: Current implementation suitable for 2-20 agents
