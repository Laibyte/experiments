# My Project

A balanced Python template for everyday use, side projects, and experiments.

## Features

- 🚀 Modern Python 3.11+ with Poetry
- 🧪 Testing with pytest and coverage (70% threshold)
- 🔍 Fast linting and formatting with Ruff
- 📝 Type checking with mypy (relaxed mode)
- 🪝 Simple pre-commit hooks
- 🎯 Easy to use, easy to scale

## Quick Start

### Prerequisites

- Python 3.11+
- [Poetry](https://python-poetry.org/docs/#installation)

### Setup

```bash
# Clone and setup
git clone <your-repo-url>
cd my-project

# One-command setup
make setup

# Or manual setup
poetry install
poetry run pre-commit install
```

## Development

### Quick Commands

```bash
make test          # Run tests
make test-cov      # Run tests with coverage report
make lint          # Check code quality
make format        # Format code
make type-check    # Run type checking
make check         # Run all checks
make clean         # Clean up generated files
```

### Detailed Commands

```bash
# Testing
poetry run pytest                    # Run all tests
poetry run pytest tests/test_main.py # Run specific test
poetry run pytest -v                 # Verbose output
poetry run pytest --cov              # With coverage

# Linting and Formatting
poetry run ruff check .              # Check for issues
poetry run ruff check --fix .        # Auto-fix issues
poetry run ruff format .             # Format code

# Type Checking
poetry run mypy src/                 # Check types
```

## Project Structure

```
my-project/
├── src/                    # Source code
│   └── main.py
├── tests/                  # Tests
│   ├── conftest.py
│   └── test_main.py
├── .vscode/                # VSCode settings
├── pyproject.toml          # Project config
├── .pre-commit-config.yaml # Git hooks
├── .gitignore
├── Makefile
└── README.md
```

## Adding Dependencies

```bash
# Add runtime dependency
poetry add requests

# Add dev dependency
poetry add --group dev pytest-asyncio
```

## Code Quality

### Type Hints
Type hints are required for function signatures but relaxed for experiments:

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"
```

### Testing
Maintain at least 70% test coverage:

```bash
poetry run pytest --cov
open htmlcov/index.html  # View coverage report
```

### Pre-commit Hooks
Hooks run automatically on commit:
- Trailing whitespace removal
- File formatting
- Ruff linting and formatting
- mypy type checking

Skip hooks only when necessary:
```bash
git commit --no-verify
```

## IDE Setup

### VSCode/Cursor

Recommended extensions (auto-prompt on open):
- Ruff (charliermarsh.ruff)
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- mypy (ms-python.mypy-type-checker)

Settings are pre-configured in `.vscode/settings.json`:
- Format on save
- Auto-fix on save
- Type checking enabled

## Scaling Up

When your project grows, consider adding:

- **Security scanning**: `poetry add --group dev bandit detect-secrets`
- **Async testing**: `poetry add --group dev pytest-asyncio`
- **Parallel testing**: `poetry add --group dev pytest-xdist`
- **Stricter mypy**: Enable `strict = true` in `pyproject.toml`
- **CI/CD**: Add GitHub Actions workflows
- **More linting rules**: Expand Ruff's `select` list in `pyproject.toml`

## Troubleshooting

**Virtual environment issues:**
```bash
poetry install
poetry shell  # Activate environment
```

**Pre-commit hooks not running:**
```bash
poetry run pre-commit install
```

**Type checking errors:**
```bash
poetry run mypy src/
# Add type: ignore comments for third-party libraries
```

**Coverage too low:**
```bash
poetry run pytest --cov --cov-report=html
open htmlcov/index.html
# Write tests for uncovered code
```

## License

[Your License Here]

## Tips for Everyday Use

- **Quick experiments**: Skip tests initially, add them later
- **Type hints**: Start simple, add more as code stabilizes
- **Coverage**: 70% is a good balance, not too strict
- **Pre-commit**: Let it guide you, don't fight it
- **Ruff**: Trust the auto-fixes, they're fast and safe
