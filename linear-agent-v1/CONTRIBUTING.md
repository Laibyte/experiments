# Contributing

Thanks for your interest in contributing!

## Quick Start

1. Fork and clone the repository
2. Run `make setup` to install dependencies
3. Create a branch: `git checkout -b feature/your-feature`
4. Make your changes
5. Run checks: `make check`
6. Commit and push
7. Open a Pull Request

## Development Workflow

### Making Changes

1. Write your code with type hints
2. Add tests for new functionality
3. Update documentation if needed

### Running Checks

```bash
make format      # Format code
make type-check  # Check types
make test        # Run tests
make check       # Run all checks
```

### Commit Messages

Use clear, descriptive commit messages:
- `feat: add new feature`
- `fix: resolve bug in X`
- `docs: update README`
- `test: add tests for Y`

### Pull Requests

- Keep PRs focused and small
- Include tests for new features
- Update CHANGELOG.md
- Ensure all checks pass

## Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for public functions
- Keep functions small and focused
- Aim for 70%+ test coverage

## Questions?

Open an issue or start a discussion!
