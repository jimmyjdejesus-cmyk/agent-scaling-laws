# Development Standards

This document defines coding standards, conventions, and best practices for the agent-scaling-laws project.

## Table of Contents

1. [Python Version and Dependencies](#python-version-and-dependencies)
2. [Code Style and Formatting](#code-style-and-formatting)
3. [Naming Conventions](#naming-conventions)
4. [Type Hints and Documentation](#type-hints-and-documentation)
5. [Testing Standards](#testing-standards)
6. [Error Handling](#error-handling)
7. [Performance Guidelines](#performance-guidelines)
8. [Security Standards](#security-standards)
9. [Git Workflow](#git-workflow)
10. [Code Review Process](#code-review-process)

---

## Python Version and Dependencies

### Supported Versions

- **Minimum**: Python 3.8
- **Tested**: Python 3.8, 3.9, 3.10, 3.11, 3.12
- **Recommended**: Python 3.11+

### Dependency Management

**Production Dependencies** (keep minimal):
```
numpy>=1.20.0
scipy>=1.7.0
```

**Development Dependencies**:
```
pytest>=7.0.0
pytest-cov>=3.0.0
black>=22.0.0
flake8>=4.0.0
mypy>=0.950
```

### Adding Dependencies

1. **MUST** check GitHub Advisory Database before adding
2. **MUST** use version constraints (e.g., `>=1.0.0,<2.0.0`)
3. **MUST** justify new dependencies in PR description
4. **SHOULD** prefer stdlib over third-party when possible
5. **SHOULD** prefer well-maintained, popular packages

---

## Code Style and Formatting

### Black (Code Formatter)

**All code MUST be formatted with Black**:

```bash
black src/ tests/ examples/
```

**Configuration** (in `pyproject.toml` if needed):
```toml
[tool.black]
line-length = 100
target-version = ['py38']
```

### Flake8 (Linter)

**All code MUST pass flake8**:

```bash
flake8 src/ tests/ examples/
```

**Allowed exceptions**:
- E501: Line too long (Black handles this)
- W503: Line break before binary operator (Black style)

### Import Organization

**Order** (enforced by isort if used):
1. Standard library imports
2. Third-party imports
3. Local application imports

**Example**:
```python
# Standard library
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

# Third-party
import numpy as np

# Local
from agent_scaling_laws.architectures.base import Agent
from agent_scaling_laws.metrics import calculate_efficiency
```

---

## Naming Conventions

### General Rules

- **MUST** use descriptive, meaningful names
- **MUST NOT** use single-letter names except in:
  - Loop iterators: `i`, `j`, `k`
  - Coordinates: `x`, `y`, `z`
  - Generic type parameters: `T`, `K`, `V`

### Python Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Modules | lowercase_with_underscores | `coordination_metrics.py` |
| Packages | lowercase | `architectures/` |
| Classes | CapitalizedWords | `SingleAgent`, `TaskResult` |
| Functions | lowercase_with_underscores | `calculate_efficiency()` |
| Methods | lowercase_with_underscores | `execute_task()` |
| Constants | UPPERCASE_WITH_UNDERSCORES | `DEFAULT_TOKEN_BUDGET` |
| Variables | lowercase_with_underscores | `task_progress` |
| Private | _leading_underscore | `_calculate_score()` |

### Domain-Specific Naming

**Agent-related**:
- Agent classes: `*Agent` suffix (e.g., `SingleAgent`)
- Architecture types: lowercase string literals (`"single"`, `"centralized"`)
- Agent IDs: descriptive strings (`"single_agent"`, `"centralized_system"`)

**Metrics-related**:
- Metric functions: `calculate_*` prefix
- Metric classes: `*Metrics` suffix
- Metric values: noun forms (`efficiency`, `overhead`)

**Task-related**:
- Task objects: `task`, `subtask`, `team_task`
- Results: `result`, `task_result`, `team_result`
- Context: `context`, `task_context`, `peer_context`

---

## Type Hints and Documentation

### Type Hints

**MUST** use type hints for all public APIs:

```python
def calculate_efficiency(
    task_progress: float,
    tokens_used: int,
    baseline_tokens: int = 100
) -> float:
    """Calculate efficiency metric."""
    ...
```

**Type hint standards**:
- Use `Optional[T]` for nullable types
- Use `Union[T1, T2]` for multiple types (sparingly)
- Use `List[T]`, `Dict[K, V]` for Python 3.8 compatibility (not `list[T]`)
- Use `Any` only when truly necessary
- Use `Literal` for string enums

**Complex types**:
```python
from typing import List, Dict, Optional, Literal, Union

ArchitectureType = Literal["single", "independent", "centralized", "decentralized", "hybrid"]

def select_architecture(
    task: TaskCharacteristics,
    capabilities: AgentCapabilities
) -> ArchitectureType:
    ...
```

### Docstrings

**MUST** document all public classes, functions, and methods using Google-style docstrings:

```python
def execute_task(self, task: Any, context: Optional[Dict[str, Any]] = None) -> TaskResult:
    """
    Execute a task and return the result.
    
    Args:
        task: The task to execute (callable or data)
        context: Optional context information for task execution
        
    Returns:
        TaskResult containing the execution outcome with success status,
        output, tokens used, and optional error message
        
    Raises:
        ValueError: If task format is invalid (future enhancement)
        
    Example:
        >>> agent = SingleAgent()
        >>> result = agent.execute_task(lambda ctx: "Hello")
        >>> print(result.output)
        Hello
    """
    ...
```

**Docstring sections** (in order):
1. Brief description (one line)
2. Extended description (optional, detailed explanation)
3. `Args:` - Parameter descriptions
4. `Returns:` - Return value description
5. `Raises:` - Exceptions that may be raised
6. `Example:` - Usage examples (optional but encouraged)
7. `Note:` - Additional notes (optional)

### Module Docstrings

**MUST** include module-level docstring:

```python
"""
Coordination metrics for agent systems.

This module implements the four core coordination metrics from the paper
"Towards a Science of Scaling Agent Systems": Efficiency, Overhead,
Error Amplification, and Redundancy.
"""
```

---

## Testing Standards

### Test Structure

**Location**: Mirror source structure in `tests/`

```
src/agent_scaling_laws/
  architectures/
    base.py
  metrics/
    coordination_metrics.py

tests/
  architectures/
    test_base.py
  metrics/
    test_coordination_metrics.py
```

### Test Naming

**Files**: `test_*.py`
**Functions**: `test_*` prefix with descriptive names

```python
def test_single_agent_execute_callable()
def test_calculate_efficiency_with_zero_tokens()
def test_selector_parallelizable_task()
```

### Test Organization

**Use AAA pattern** (Arrange, Act, Assert):

```python
def test_calculate_efficiency():
    """Test efficiency calculation with normal values."""
    # Arrange
    task_progress = 0.8
    tokens_used = 400
    baseline_tokens = 500
    
    # Act
    efficiency = calculate_efficiency(task_progress, tokens_used, baseline_tokens)
    
    # Assert
    assert efficiency == pytest.approx(1.0)
```

### Test Coverage Requirements

- **Minimum**: 80% line coverage
- **Target**: 90%+ line coverage
- **Critical paths**: 100% coverage

**Check coverage**:
```bash
pytest tests/ --cov=agent_scaling_laws --cov-report=term --cov-report=html
```

### Test Categories

**Unit Tests** (fast, isolated):
- Test individual functions/methods
- Mock external dependencies
- Should run in < 1 second total

**Integration Tests** (slower, connected):
- Test multiple components together
- May use real dependencies
- Mark with `@pytest.mark.integration`

**Edge Cases** (required):
- Null/None inputs
- Empty collections
- Boundary values (0, -1, MAX_INT)
- Invalid inputs

### Assertions

**Use pytest assertions**:
```python
# Good
assert result.success is True
assert len(results) == 3
assert value == pytest.approx(1.234, rel=0.01)

# Avoid
self.assertTrue(result.success)  # unittest style
```

### Fixtures

**Use pytest fixtures for reusable test data**:

```python
@pytest.fixture
def sample_agent():
    """Provide a configured agent for tests."""
    return SingleAgent(capabilities={"tokens_per_task": 100})

def test_agent_execution(sample_agent):
    result = sample_agent.execute_task(lambda ctx: "test")
    assert result.success
```

---

## Error Handling

### Philosophy

- **Fail gracefully**: Agents should return `TaskResult(success=False)` rather than raising
- **Be explicit**: Error messages should be clear and actionable
- **Don't hide**: Log unexpected errors but handle them

### Error Messages

**Good error messages**:
```python
# Specific and actionable
raise ValueError(
    f"num_agents must be >= 1, got {num_agents}"
)

# Include context
return TaskResult(
    success=False,
    error=f"Task execution failed: {str(e)}. Task type: {type(task).__name__}"
)
```

**Bad error messages**:
```python
# Too vague
raise ValueError("Invalid input")

# No context
return TaskResult(success=False, error="Error")
```

### Exception Handling

**Catch specific exceptions**:
```python
# Good
try:
    result = task(context)
except (TypeError, ValueError) as e:
    return TaskResult(success=False, error=f"Task error: {e}")

# Avoid bare except
try:
    result = task(context)
except:  # Too broad
    pass
```

### Validation

**Validate inputs early**:
```python
def __init__(self, num_agents: int = 3):
    if num_agents < 1:
        raise ValueError(f"num_agents must be >= 1, got {num_agents}")
    self.num_agents = num_agents
```

---

## Performance Guidelines

### Algorithmic Complexity

**Document time complexity** for non-trivial operations:

```python
def execute_task(self, task, context=None) -> TaskResult:
    """
    Execute task with decentralized coordination.
    
    Time Complexity: O(n² * r) where n=num_agents, r=coordination_rounds
    Space Complexity: O(n * m) where m=messages per agent
    """
    ...
```

### Memory Management

**Clear large data structures**:
```python
def reset_metrics(self):
    """Reset metrics and clear message history to free memory."""
    self.tokens_used = 0
    self.message_history.clear()  # Explicit clear
```

**Avoid unnecessary copies**:
```python
# Good: iterate directly
for agent in self.agents:
    agent.execute_task(task)

# Avoid: unnecessary list copy
for agent in list(self.agents):  # Creates copy
    agent.execute_task(task)
```

### Concurrency

**Use ThreadPoolExecutor for I/O-bound parallelism**:
```python
with ThreadPoolExecutor(max_workers=self.num_agents) as executor:
    futures = {executor.submit(agent.execute_task, task): agent
               for agent in self.agents}
```

**Note**: Current implementation not thread-safe for shared state

---

## Security Standards

### Input Validation

**Sanitize user inputs**:
```python
def execute_task(self, task, context=None):
    # Validate task type
    if not callable(task) and not isinstance(task, (list, tuple, str, dict)):
        raise TypeError(f"Unsupported task type: {type(task)}")
    
    # Validate context
    if context is not None and not isinstance(context, dict):
        raise TypeError("context must be a dictionary")
```

### Secrets Management

**NEVER hardcode secrets**:
```python
# Bad
API_KEY = "sk-1234567890abcdef"

# Good
import os
API_KEY = os.environ.get("API_KEY")
```

### Dependencies

**Always check for known vulnerabilities**:
```bash
# Before adding new dependency
pip install safety
safety check --json
```

### Code Scanning

**Run CodeQL before merging**:
- Automated via GitHub Actions
- Fix all high-severity issues
- Document false positives

---

## Git Workflow

### Branch Naming

**Format**: `<type>/<short-description>`

**Types**:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions/changes
- `chore/` - Maintenance tasks

**Examples**:
- `feature/add-adaptive-architecture`
- `fix/metrics-calculation-overflow`
- `docs/api-contracts`

### Commit Messages

**Format**:
```
<type>: <subject>

<body>

<footer>
```

**Types**: feat, fix, docs, style, refactor, test, chore

**Example**:
```
feat: Add dynamic architecture adaptation

Implement runtime architecture switching based on performance metrics.
Agents can now adapt their coordination strategy based on observed
efficiency and error rates.

Closes #42
```

**Rules**:
- Subject line: 50 characters max
- Body: Wrap at 72 characters
- Use imperative mood ("Add feature" not "Added feature")
- Reference issues/PRs in footer

### Pull Requests

**PR Title**: Clear, descriptive, follows commit message format

**PR Description** MUST include:
1. **What**: Summary of changes
2. **Why**: Motivation and context
3. **How**: Technical approach (if non-obvious)
4. **Testing**: How changes were tested
5. **Checklist**: Completed items

**Template**:
```markdown
## Summary
Brief description of changes

## Motivation
Why this change is needed

## Changes
- Change 1
- Change 2

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] No new security issues
```

---

## Code Review Process

### Review Checklist

**For Reviewers**:

- [ ] Code follows style guidelines (Black, flake8, mypy)
- [ ] Type hints present and correct
- [ ] Docstrings present and complete
- [ ] Tests added for new functionality
- [ ] Tests pass and coverage maintained
- [ ] No security vulnerabilities introduced
- [ ] Performance impact acceptable
- [ ] Documentation updated
- [ ] API contracts maintained (no breaking changes)
- [ ] Error handling appropriate

### Review Guidelines

**As a Reviewer**:
1. Review within 1-2 business days
2. Be constructive and respectful
3. Focus on code quality, not personal style preferences
4. Suggest specific improvements
5. Approve when ready, request changes if needed

**As an Author**:
1. Respond to all review comments
2. Make requested changes or explain why not
3. Re-request review after changes
4. Keep PRs small and focused

### Approval Requirements

- **Minimum**: 1 approval from maintainer
- **Security changes**: 2 approvals
- **Breaking changes**: Discussion + 2 approvals

---

## Documentation Standards

### README.md

**MUST include**:
1. Project description
2. Installation instructions
3. Quick start / usage examples
4. Link to full documentation
5. Contributing guidelines
6. License information

### Code Comments

**When to comment**:
- Explaining "why", not "what"
- Complex algorithms
- Non-obvious behavior
- Workarounds or hacks (with TODO)

**When NOT to comment**:
- Obvious code
- Repeating function name
- Out-of-date comments (remove instead)

**Example**:
```python
# Good: Explains reasoning
# Use centralized coordination for parallelizable tasks
# because it provides 80.9% improvement (from paper)
if task.parallelizable > 0.7:
    return "centralized"

# Bad: States the obvious
# Check if parallelizable is greater than 0.7
if task.parallelizable > 0.7:
    return "centralized"
```

### API Documentation

**MUST document**:
- All public classes and functions
- Parameters and return values
- Exceptions raised
- Usage examples

**Hosted documentation** (future):
- Sphinx-generated docs
- Read the Docs hosting
- API reference + tutorials

---

## Continuous Integration

### GitHub Actions

**Required checks**:
1. **Tests**: All tests must pass
2. **Linting**: flake8 must pass
3. **Type checking**: mypy must pass (future)
4. **Security**: CodeQL must pass
5. **Coverage**: Must maintain >= 80%

**Matrix testing**:
- Python 3.8, 3.9, 3.10, 3.11, 3.12
- Ubuntu (primary), Windows, macOS (optional)

### Pre-commit Hooks (Recommended)

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.0.0
    hooks:
      - id: black
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

Install:
```bash
pip install pre-commit
pre-commit install
```

---

## Release Process

### Versioning

**Follow Semantic Versioning**:
- `MAJOR.MINOR.PATCH`
- Increment MAJOR for breaking changes
- Increment MINOR for new features
- Increment PATCH for bug fixes

### Release Checklist

1. [ ] Update version in `setup.py` and `__init__.py`
2. [ ] Update CHANGELOG.md
3. [ ] Run full test suite
4. [ ] Update documentation
5. [ ] Create git tag: `git tag -a v1.0.0 -m "Release 1.0.0"`
6. [ ] Push tag: `git push origin v1.0.0`
7. [ ] Create GitHub release with notes
8. [ ] Build and upload to PyPI (when ready)

### CHANGELOG.md

**Format**:
```markdown
# Changelog

## [1.1.0] - 2024-01-15

### Added
- New feature X
- Support for Y

### Changed
- Improved performance of Z

### Fixed
- Bug in A calculation

### Deprecated
- Feature B (will be removed in 2.0.0)

## [1.0.0] - 2024-01-01

Initial release
```

---

## Maintenance Guidelines

### Issue Triage

**Labels**:
- `bug` - Something isn't working
- `enhancement` - New feature request
- `documentation` - Documentation improvements
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed

**Priority**:
- `P0` - Critical (security, data loss)
- `P1` - High (broken functionality)
- `P2` - Medium (degraded experience)
- `P3` - Low (nice to have)

### Deprecation Process

1. Mark feature with `@deprecated` decorator
2. Add deprecation warning
3. Update documentation
4. Wait at least one minor version
5. Remove in next major version

---

## References

- [PEP 8](https://peps.python.org/pep-0008/) - Python Style Guide
- [PEP 257](https://peps.python.org/pep-0257/) - Docstring Conventions
- [PEP 484](https://peps.python.org/pep-0484/) - Type Hints
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)

---

**Last Updated**: December 2024  
**Version**: 1.0.0
