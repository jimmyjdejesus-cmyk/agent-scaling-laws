# Contributing to Agent Scaling Laws

Thank you for your interest in contributing to this project! This document provides guidelines for contributing.

## Quick Links

- **[Development Standards](docs/DEVELOPMENT_STANDARDS.md)** - Comprehensive coding standards and best practices
- **[API Contracts](docs/API_CONTRACTS.md)** - API documentation and contracts
- **[Architecture Guide](docs/ARCHITECTURE.md)** - Technical architecture overview

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/jimmyjdejesus-cmyk/agent-scaling-laws.git
cd agent-scaling-laws
```

2. Install in development mode:
```bash
pip install -e ".[dev]"
```

## Running Tests

Run the test suite:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest tests/ --cov=agent_scaling_laws --cov-report=term
```

## Code Style

This project follows Python best practices. See [Development Standards](docs/DEVELOPMENT_STANDARDS.md) for complete details.

### Quick Reference

- Use Black for code formatting:
```bash
black src/ tests/
```

- Use flake8 for linting:
```bash
flake8 src/ tests/
```

- Use mypy for type checking:
```bash
mypy src/
```

### Key Standards

- Python 3.8+ compatibility
- Type hints on all public APIs
- Google-style docstrings
- 80%+ test coverage
- Follow naming conventions in [Development Standards](docs/DEVELOPMENT_STANDARDS.md)

## Adding New Features

1. Create a new branch for your feature
2. Implement your changes with tests
3. Ensure all tests pass
4. Update documentation as needed
5. Submit a pull request

## Adding Tests

- Place tests in the `tests/` directory
- Mirror the structure of the `src/` directory
- Name test files with `test_` prefix
- Use descriptive test function names

Example:
```python
def test_new_feature():
    """Test description."""
    # Arrange
    # Act
    # Assert
```

## Documentation

All code changes must be properly documented:

- Update README.md for major changes
- Add Google-style docstrings to all public classes and functions
- Include type hints (see [Development Standards](docs/DEVELOPMENT_STANDARDS.md))
- Provide usage examples
- Update [API Contracts](docs/API_CONTRACTS.md) for API changes
- Follow documentation standards in [Development Standards](docs/DEVELOPMENT_STANDARDS.md)

## Submitting Pull Requests

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Update documentation
6. Submit a pull request with a clear description

## Code of Conduct

- Be respectful and constructive
- Focus on the code, not the person
- Welcome newcomers
- Help others learn

## Questions?

Feel free to open an issue for discussion or questions.
