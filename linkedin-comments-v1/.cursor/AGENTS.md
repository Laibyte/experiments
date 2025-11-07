---
description: AI coding assistant rules for everyday Python development
alwaysApply: true
---

# AI Assistant Guidelines

## Role
You are a helpful Python coding assistant focused on writing clean, maintainable code.

## Communication Style
- Be concise and helpful
- Explain your reasoning when making significant decisions
- Suggest improvements when you see opportunities

## Code Standards

### Python Best Practices
- Use type hints for function signatures
- Write clear docstrings for public functions
- Follow PEP 8 style guide
- Prefer f-strings for formatting
- Keep functions small and focused

### Testing
- Write tests for new functionality
- Aim for 70%+ coverage
- Use descriptive test names
- Test edge cases

### Dependencies
- Use Poetry for package management: `poetry add <package>`
- Add dev dependencies: `poetry add --group dev <package>`
- Keep dependencies minimal

## Workflow
1. Understand the requirements
2. Write clean, tested code
3. Run quality checks: `make check`
4. Commit with clear messages

## Quality Checks
Before committing:
```bash
make format      # Format code
make type-check  # Check types
make test        # Run tests
```

## Common Commands
- `make test` - Run tests
- `make format` - Format code
- `make check` - Run all checks
- `poetry add <pkg>` - Add dependency
