# API Contracts

This document defines the public API contracts for the agent-scaling-laws library. All public APIs are guaranteed to maintain backward compatibility within major versions.

## Version

Current API Version: **1.0.0** (Following Semantic Versioning)

---

## Core Data Structures

### TaskResult

**Module**: `agent_scaling_laws.architectures.base`

Result object returned by agent task execution.

```python
@dataclass
class TaskResult:
    success: bool              # Whether the task completed successfully
    output: Any                # Task output (any type)
    tokens_used: int = 0       # Number of tokens consumed
    error: Optional[str] = None  # Error message if task failed
    metadata: Dict[str, Any] = {}  # Additional metadata
```

**Contract**:
- `success` MUST be a boolean indicating task completion status
- `output` MUST contain the task result when `success=True`
- `tokens_used` MUST be a non-negative integer
- `error` SHOULD be None when `success=True`
- `metadata` MAY contain architecture-specific information

### Message

**Module**: `agent_scaling_laws.architectures.base`

Message object for inter-agent communication.

```python
@dataclass
class Message:
    sender_id: str             # ID of the sending agent
    content: Any               # Message content (any type)
    message_type: str = "default"  # Type of message
    metadata: Dict[str, Any] = {}  # Additional metadata
```

**Contract**:
- `sender_id` MUST be a non-empty string
- `content` MAY be any type
- `message_type` SHOULD describe the message purpose
- Messages are immutable after creation

---

## Agent Interface

### Agent (Abstract Base Class)

**Module**: `agent_scaling_laws.architectures.base`

All agent architectures implement this interface.

#### Constructor

```python
def __init__(self, agent_id: str, capabilities: Optional[Dict[str, Any]] = None)
```

**Parameters**:
- `agent_id`: Unique identifier (MUST be unique within a system)
- `capabilities`: Optional configuration dictionary

**Supported capability keys**:
- `tokens_per_task`: int (default: 100)
- `coordination_tokens_per_task`: int (default: 10)
- `communication_tokens_per_message`: int (default: 5)
- `coordination_rounds`: int (default: 2, for decentralized)
- `strategy_tokens`: int (default: 20, for hybrid)
- `aggregation_tokens`: int (default: 15, for hybrid)
- `team_comm_tokens`: int (default: 3, for hybrid)

#### execute_task

```python
def execute_task(self, task: Any, context: Optional[Dict[str, Any]] = None) -> TaskResult
```

**Parameters**:
- `task`: The task to execute (callable or data)
  - If callable: `task(context: Dict) -> Any`
  - If list/tuple: distributed across agents (architecture-dependent)
  - Otherwise: passed directly to agent
- `context`: Optional execution context dictionary

**Returns**: `TaskResult` object

**Behavior**:
- MUST return a valid `TaskResult`
- MUST handle exceptions gracefully (return `TaskResult` with `success=False`)
- MUST update internal metrics (`tokens_used`, `tasks_completed`, `errors_count`)
- MAY modify `context` but SHOULD NOT mutate input `task`

#### get_metrics

```python
def get_metrics(self) -> Dict[str, Any]
```

**Returns**: Dictionary with current metrics

**Required keys**:
- `agent_id`: str
- `tokens_used`: int
- `tasks_completed`: int
- `errors_count`: int
- `messages_sent`: int
- `messages_received`: int

**Architecture-specific keys** (optional):
- `agents`: List[Dict] (multi-agent architectures)
- `coordination_overhead`: int
- `communication_overhead`: int
- `messages_exchanged`: int

#### reset_metrics

```python
def reset_metrics(self) -> None
```

**Effect**: Resets all metrics to initial state (0 values, empty lists)

---

## Agent Architectures

### SingleAgent

**Module**: `agent_scaling_laws.architectures.single_agent`

**Constructor**:
```python
SingleAgent(agent_id: str = "single_agent", capabilities: Optional[Dict[str, Any]] = None)
```

**Behavior**:
- Executes tasks independently
- No coordination overhead
- Best for simple, well-defined tasks

**Task Execution**:
- Callable tasks: executed with context
- Data tasks: returned directly

### IndependentMultiAgent

**Module**: `agent_scaling_laws.architectures.independent`

**Constructor**:
```python
IndependentMultiAgent(
    agent_id: str = "independent_system",
    num_agents: int = 3,
    capabilities: Optional[Dict[str, Any]] = None
)
```

**Parameters**:
- `num_agents`: Number of independent agents (MUST be >= 1)

**Behavior**:
- Agents work in parallel using ThreadPoolExecutor
- No coordination or communication
- Returns first successful result or aggregates failures
- High error amplification risk (17.2× from paper)

**Task Execution**:
- All agents execute the same task
- Results aggregated using first-success strategy

### CentralizedMultiAgent

**Module**: `agent_scaling_laws.architectures.centralized`

**Constructor**:
```python
CentralizedMultiAgent(
    agent_id: str = "centralized_system",
    num_agents: int = 3,
    capabilities: Optional[Dict[str, Any]] = None
)
```

**Parameters**:
- `num_agents`: Number of worker agents (MUST be >= 1)

**Behavior**:
- Central coordinator decomposes and assigns tasks
- Maintains global state across execution
- Error containment (4.4× amplification from paper)
- 80.9% improvement for parallelizable tasks

**Task Execution**:
- List/tuple tasks: distributed across agents round-robin
- Single task: assigned to first agent
- Coordinator adds overhead tokens

### DecentralizedMultiAgent

**Module**: `agent_scaling_laws.architectures.decentralized`

**Constructor**:
```python
DecentralizedMultiAgent(
    agent_id: str = "decentralized_system",
    num_agents: int = 3,
    capabilities: Optional[Dict[str, Any]] = None
)
```

**Parameters**:
- `num_agents`: Number of peer agents (MUST be >= 1)

**Behavior**:
- Peer-to-peer communication via message broadcasting
- Multiple coordination rounds (default: 2)
- Consensus-based result aggregation
- 9.2% improvement for dynamic tasks

**Task Execution**:
- Agents communicate between rounds
- Latest successful result used as consensus

### HybridMultiAgent

**Module**: `agent_scaling_laws.architectures.hybrid`

**Constructor**:
```python
HybridMultiAgent(
    agent_id: str = "hybrid_system",
    num_agents: int = 6,
    team_size: int = 2,
    capabilities: Optional[Dict[str, Any]] = None
)
```

**Parameters**:
- `num_agents`: Total number of worker agents (MUST be >= 1)
- `team_size`: Size of each team (MUST be >= 1)

**Behavior**:
- Centralized strategic decomposition
- Decentralized team execution
- Balances control and flexibility
- `num_teams = num_agents // team_size`

**Task Execution**:
- List tasks: distributed across teams
- Teams coordinate internally via peer communication
- Results aggregated centrally

---

## Coordination Metrics

### CoordinationMetrics

**Module**: `agent_scaling_laws.metrics.coordination_metrics`

```python
@dataclass
class CoordinationMetrics:
    efficiency: float           # Task progress per computation unit
    overhead: float            # Coordination cost ratio (0.0-1.0)
    error_amplification: float # Error propagation multiplier (>= 1.0)
    redundancy: float          # Duplicate action ratio (0.0-1.0)
```

### Metric Calculations

#### calculate_efficiency

```python
def calculate_efficiency(
    task_progress: float,      # 0.0 to 1.0
    tokens_used: int,          # Total tokens consumed
    baseline_tokens: int = 100 # Single-agent baseline
) -> float
```

**Returns**: Efficiency score (higher is better)

**Formula**: `efficiency = task_progress / (tokens_used / baseline_tokens)`

**Contract**:
- `task_progress` MUST be in range [0.0, 1.0]
- `tokens_used` MUST be non-negative
- Returns 0.0 if `tokens_used == 0`

#### calculate_overhead

```python
def calculate_overhead(
    total_tokens: int,         # Total system tokens
    agent_tokens: int,         # Tokens for actual work
    coordination_tokens: int   # Tokens for coordination
) -> float
```

**Returns**: Overhead ratio in range [0.0, 1.0]

**Formula**: `overhead = coordination_tokens / total_tokens`

**Contract**:
- All parameters MUST be non-negative
- `coordination_tokens + agent_tokens` SHOULD equal `total_tokens`
- Returns 0.0 if `total_tokens == 0`

#### calculate_error_amplification

```python
def calculate_error_amplification(
    single_agent_error_rate: float,  # Baseline error rate (0.0-1.0)
    multi_agent_error_rate: float    # Multi-agent error rate (0.0-1.0)
) -> float
```

**Returns**: Error amplification factor (>= 1.0)

**Formula**: `amplification = multi_agent_error_rate / single_agent_error_rate`

**Contract**:
- Error rates MUST be in range [0.0, 1.0]
- Returns capped value (20.0) if baseline is 0.0
- Value of 1.0 means no amplification
- Paper values: 17.2× (independent), 4.4× (centralized)

#### calculate_redundancy

```python
def calculate_redundancy(
    unique_actions: int,       # Number of unique actions
    total_actions: int         # Total actions taken
) -> float
```

**Returns**: Redundancy ratio in range [0.0, 1.0]

**Formula**: `redundancy = 1.0 - (unique_actions / total_actions)`

**Contract**:
- Both parameters MUST be non-negative
- `unique_actions` MUST be <= `total_actions`
- Returns 0.0 if `total_actions == 0`

#### compute_all_metrics

```python
def compute_all_metrics(
    task_progress: float,
    total_tokens: int,
    agent_tokens: int,
    coordination_tokens: int,
    single_agent_error_rate: float,
    multi_agent_error_rate: float,
    unique_actions: int,
    total_actions: int,
    baseline_tokens: int = 100
) -> CoordinationMetrics
```

**Returns**: `CoordinationMetrics` object with all metrics computed

---

## Architecture Selector

### TaskCharacteristics

**Module**: `agent_scaling_laws.models.architecture_selector`

```python
@dataclass
class TaskCharacteristics:
    parallelizable: float    # 0.0 to 1.0: degree of parallelizability
    dynamic: float          # 0.0 to 1.0: need for dynamic adaptation
    sequential: float       # 0.0 to 1.0: sequential reasoning requirement
    tool_intensive: float   # 0.0 to 1.0: tool usage intensity
    complexity: float       # 0.0 to 1.0: overall complexity
```

**Contract**:
- All fields MUST be in range [0.0, 1.0]
- Higher values indicate stronger presence of characteristic

### AgentCapabilities

**Module**: `agent_scaling_laws.models.architecture_selector`

```python
@dataclass
class AgentCapabilities:
    baseline_accuracy: float  # 0.0 to 1.0: single-agent accuracy
    token_budget: int        # Available tokens
    model_capability: float  # 0.0 to 1.0: relative LLM capability
```

**Contract**:
- `baseline_accuracy` MUST be in range [0.0, 1.0]
- `token_budget` MUST be positive
- `model_capability` MUST be in range [0.0, 1.0]

### ArchitectureSelector

**Module**: `agent_scaling_laws.models.architecture_selector`

#### select_architecture

```python
def select_architecture(
    self,
    task: TaskCharacteristics,
    capabilities: AgentCapabilities
) -> ArchitectureType  # Literal["single", "independent", "centralized", "decentralized", "hybrid"]
```

**Returns**: Recommended architecture name

**Selection Criteria** (from paper):
- **Capability Saturation**: If `baseline_accuracy > 0.45`, favors single agent
- **Parallelizable Tasks**: `parallelizable > 0.7` → centralized (80.9% gain)
- **Dynamic Tasks**: `dynamic > 0.7` → decentralized (9.2% gain)
- **Sequential Tasks**: `sequential > 0.6` → single (multi-agent degrades 39-70%)
- **Tool-Heavy + Limited Budget**: `tool_intensive > 0.7` AND `token_budget < 5000` → single

**Contract**:
- MUST return one of the five valid architecture types
- Selection MUST be deterministic for same inputs
- Returns highest-scoring architecture

#### predict_all_scores

```python
def predict_all_scores(
    self,
    task: TaskCharacteristics,
    capabilities: AgentCapabilities
) -> Dict[ArchitectureType, float]
```

**Returns**: Dictionary mapping each architecture to its predicted score

**Contract**:
- MUST include all five architectures
- Scores MAY be negative
- Higher scores indicate better fit

#### explain_selection

```python
def explain_selection(
    self,
    task: TaskCharacteristics,
    capabilities: AgentCapabilities
) -> Dict[str, Any]
```

**Returns**: Dictionary with keys:
- `selected_architecture`: str
- `scores`: Dict[str, float]
- `reasoning`: List[str]
- `task_characteristics`: Dict[str, float]
- `agent_capabilities`: Dict[str, Any]

**Contract**:
- `reasoning` MUST contain human-readable explanations
- All keys MUST be present in returned dictionary

---

## Versioning and Compatibility

### Semantic Versioning

This library follows [Semantic Versioning 2.0.0](https://semver.org/):
- **MAJOR**: Incompatible API changes
- **MINOR**: Backward-compatible functionality additions
- **PATCH**: Backward-compatible bug fixes

### Deprecation Policy

1. Deprecated features are marked with `@deprecated` decorator
2. Deprecation warnings are issued for at least one minor version
3. Deprecated features are removed in next major version
4. Alternative APIs are documented in deprecation warnings

### Breaking Changes

Breaking changes will only occur in major version updates and will be documented in:
- CHANGELOG.md
- Migration guides
- API documentation

---

## Error Handling

### Exception Hierarchy

```
Exception
└── AgentScalingLawsError (base exception)
    ├── AgentExecutionError (task execution failures)
    ├── CoordinationError (coordination failures)
    ├── ValidationError (input validation failures)
    └── ConfigurationError (invalid configuration)
```

**Note**: Current implementation returns errors via `TaskResult.error` rather than raising exceptions. Future versions may introduce exception hierarchy.

### Error Contract

- Agent methods SHOULD NOT raise exceptions for task failures
- Task failures MUST be indicated via `TaskResult.success=False`
- Invalid inputs MAY raise `ValueError` or `TypeError`
- Configuration errors MAY raise during initialization

---

## Thread Safety

### Thread-Safe Components

- `SingleAgent`: Thread-safe (no shared state)
- `IndependentMultiAgent`: Uses ThreadPoolExecutor (thread-safe)
- `CentralizedMultiAgent`: Not thread-safe (maintains global state)
- `DecentralizedMultiAgent`: Not thread-safe (shared message list)
- `HybridMultiAgent`: Not thread-safe (shared team state)

### Usage Guidelines

- Create separate agent instances for concurrent execution
- Do not share agent instances across threads
- Metrics may be inaccurate if accessed during execution

---

## Performance Guarantees

### Computational Complexity

- `SingleAgent.execute_task()`: O(1) overhead
- `IndependentMultiAgent.execute_task()`: O(n) where n = num_agents
- `CentralizedMultiAgent.execute_task()`: O(n * m) where n = num_agents, m = subtasks
- `DecentralizedMultiAgent.execute_task()`: O(n² * r) where r = coordination_rounds
- `HybridMultiAgent.execute_task()`: O(t * s) where t = num_teams, s = team_size

### Memory Usage

- Agent instances: O(1) per agent
- Message history: O(m) where m = messages sent/received
- Global state (centralized): O(s) where s = state size

### Recommended Limits

- `num_agents`: 2-20 agents per system
- `coordination_rounds`: 1-5 rounds
- `token_budget`: 100-100,000 tokens
- Message history: Cleared via `reset_metrics()` when needed

---

## Extension Points

### Adding Custom Architectures

1. Inherit from `Agent` base class
2. Implement `execute_task()` method
3. Maintain metric tracking contracts
4. Document architecture-specific behavior

```python
from agent_scaling_laws.architectures.base import Agent, TaskResult

class CustomAgent(Agent):
    def execute_task(self, task, context=None) -> TaskResult:
        # Custom implementation
        self.tokens_used += custom_tokens
        self.tasks_completed += 1
        return TaskResult(success=True, output=result)
```

### Adding Custom Metrics

1. Define calculation function with clear signature
2. Document formula and contracts
3. Add to `coordination_metrics.py`
4. Export from `metrics/__init__.py`

---

## API Stability

### Stable APIs (Guaranteed in v1.x)

- Agent base interface (`execute_task`, `get_metrics`, `reset_metrics`)
- Core data structures (`TaskResult`, `Message`)
- All five architecture constructors and behavior
- Coordination metric calculations
- Architecture selector interface

### Experimental APIs

None currently. Future experimental APIs will be marked with `@experimental` decorator.

---

## Support and Questions

For API questions or clarifications:
1. Check this document first
2. Review inline docstrings in source code
3. Check examples in `examples/` directory
4. Open an issue on GitHub

---

**Last Updated**: December 2024  
**API Version**: 1.0.0  
**Document Version**: 1.0.0
