# Technical Documentation

This document describes the technical stack, tools, and dependencies used in this project.

## Tech Stack

### Language & Runtime
- **Python**: 3.11+
- **Package Manager**: Poetry 1.8.0+

### Core Dependencies
None by default - this is a template. Add your dependencies with:
```bash
poetry add <package-name>
```

### Development Dependencies

#### Testing
- **pytest** (^8.4.2): Testing framework
- **pytest-cov** (^7.0.0): Coverage reporting
- **pytest-asyncio** (^1.2.0): Async test support
- **pytest-xdist** (^3.8.0): Parallel test execution

#### Code Quality
- **ruff** (^0.14.3): Fast Python linter and formatter (replaces black, isort, flake8)
- **mypy** (^1.18.2): Static type checker with strict mode
- **bandit** (^1.8.6): Security vulnerability scanner
- **detect-secrets** (^1.5.0): Credential and secret detection

#### Development Tools
- **pre-commit** (^4.3.0): Git hooks for automated quality checks
- **poethepoet** (^0.37.0): Task runner (npm-style scripts for Python)

## Tool Configurations

All tool configurations are centralized in `pyproject.toml`:

### Ruff
- Line length: 100 characters
- Target: Python 3.11+
- Comprehensive rule set (E, W, F, I, B, C4, UP, ARG, SIM, etc.)
- Auto-fix enabled
- Per-file ignores for tests

### mypy
- Strict mode enabled
- All strict flags enabled (warn_return_any, disallow_untyped_defs, etc.)
- Tests excluded from some strict checks

### pytest
- Minimum coverage: 80%
- Parallel execution with xdist
- Coverage reports: terminal, HTML, XML
- Strict markers and configuration

### Bandit
- Security scanning for common vulnerabilities
- Configured via pyproject.toml
- Excludes test directories

## Development Workflow

### Task Runner (Poe)

Available commands via `poetry run poe <command>`:

```bash
setup          # Complete project setup (install + hooks)
test           # Run tests
test-cov       # Run tests with coverage
lint           # Run linting
lint-fix       # Run linting with auto-fix
format         # Format code
type-check     # Run type checking
pre-commit     # Run pre-commit on all files
security       # Run security checks
all            # Run all checks (lint-fix, format, type-check, test)
clean          # Clean up generated files
```

### Make Commands

Alternative interface via `make <command>`:

```bash
make setup       # Complete project setup
make test        # Run tests
make test-cov    # Run tests with coverage
make lint        # Run linting
make lint-fix    # Run linting with auto-fix
make format      # Format code
make type-check  # Run type checking
make security    # Run security checks
make all         # Run all checks
make clean       # Clean up generated files
```

## Pre-commit Hooks

Hooks automatically run on:
- **On commit**: Fast checks (linting, formatting, type checking, security)
- **On push**: Full test suite
- **On commit-msg**: Conventional commit validation

Hooks include:
- File quality checks (trailing whitespace, EOF, YAML/JSON/TOML validation)
- Ruff linting and formatting
- mypy type checking
- Bandit security scanning
- detect-secrets credential detection
- Poetry lock file validation
- Conventional commit message validation

## IDE Setup

### VSCode/Cursor Extensions

Required extensions (auto-prompt on open):
- `charliermarsh.ruff` - Ruff linter and formatter
- `ms-python.python` - Python language support
- `ms-python.vscode-pylance` - Fast type checking
- `ms-python.mypy-type-checker` - mypy integration
- `tamasfe.even-better-toml` - TOML file support
- `streetsidesoftware.code-spell-checker` - Spell checking
- `usernamehw.errorlens` - Inline error display
- `aaron-bond.better-comments` - Enhanced comments
- `eamodio.gitlens` - Git integration

### VSCode Settings

Key settings configured in `.vscode/settings.json`:
- Python interpreter: `.venv/bin/python`
- Format on save with Ruff
- Auto-fix on save
- Auto-organize imports
- Strict type checking
- Pytest test discovery
- 100-character ruler

## Architecture

### Project Structure

```
python-template/
├── src/                      # Source code
│   └── main.py              # Entry point
├── tests/                    # Tests (mirrors src/)
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures
│   └── test_main.py
├── docs/                     # Documentation
│   ├── ARCHITECTURE.md      # Architecture decisions
│   ├── ARCHITECTURE.mermaid # Architecture diagram
│   ├── CHANGELOG.md         # Change history
│   ├── MEMORY_BANK.md       # ADR and key decisions
│   ├── PROJECT_SPEC.md      # Project specification
│   └── TECHNICAL.md         # This file
├── .cursor/                  # Cursor IDE configuration
│   ├── commands/            # Custom commands
│   ├── hooks/               # Cursor hooks
│   └── rules/               # AI agent rules
├── .github/                  # GitHub configuration
│   ├── prompts/             # AI prompts
│   ├── workflows/           # CI/CD workflows
│   ├── copilot-instructions.md
│   └── PULL_REQUEST_TEMPLATE.md
├── .vscode/                  # VSCode/Cursor settings
│   ├── extensions.json      # Recommended extensions
│   └── settings.json        # Workspace settings
├── pyproject.toml           # Project and tool config
├── poetry.lock              # Locked dependencies
├── Makefile                 # Make commands
├── .pre-commit-config.yaml  # Pre-commit hooks
├── .secrets.baseline        # detect-secrets baseline
├── .cursorignore            # Cursor ignore patterns
├── .gitignore               # Git ignore patterns
└── README.md                # Project README
```

## CI/CD

GitHub Actions workflows (see `.github/workflows/`):
- Continuous Integration: Run tests, linting, type checking
- Dependency updates: Dependabot configuration
- Code review automation (optional)

## Security

### Secret Management
- Never commit secrets or API keys
- Use environment variables for configuration
- detect-secrets scans for accidental commits
- Bandit scans for security vulnerabilities

### Dependency Security
- Dependabot for automated dependency updates
- Regular security audits recommended
- Use `poetry show --outdated` to check for updates

## Performance

### Testing
- Parallel test execution with pytest-xdist (`-n=auto`)
- Coverage collection with branch coverage
- HTML coverage reports in `htmlcov/`

### Linting
- Ruff is significantly faster than traditional tools (10-100x)
- Pre-commit caching speeds up subsequent runs

## Troubleshooting

### Common Issues

**Virtual environment not found**:
```bash
poetry install  # Creates .venv automatically
```

**Pre-commit hooks not running**:
```bash
poetry run poe setup  # Installs hooks
```

**Type checking fails**:
```bash
poetry run mypy src/  # Run mypy directly
```

**Coverage below 80%**:
- Add tests for uncovered code
- Check `htmlcov/index.html` for coverage report

## Additional Resources

- [Poetry Documentation](https://python-poetry.org/docs/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [mypy Documentation](https://mypy.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)
- [pre-commit Documentation](https://pre-commit.com/)
