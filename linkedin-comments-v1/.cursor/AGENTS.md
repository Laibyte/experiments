# Cursor AI Agent Configuration

This file configures AI agent behavior for Cursor IDE.

## Shared Rules

All core rules for AI agents are defined in `.cursor/rules/shared-rules.mdc`.

This includes:
- Persona and communication style
- Core directives and workflow
- Package management requirements
- Commit message format
- Code generation standards
- Error handling principles
- Allowed terminal commands

## Project-Specific Rules

Additional project-specific rules are organized in `.cursor/rules/`:
- `python-standard.mdc` - Project structure and documentation standards
- `python-core.mdc` - Python best practices
- `python-types.mdc` - Type hints and type checking
- `python-testing.mdc` - Testing guidelines
- `python-async.mdc` - Async programming patterns
- `python-security.mdc` - Security requirements
- `conventional-commits.mdc` - Commit message format enforcement
- `bash.mdc` - Bash scripting guidelines

## Commands

Custom commands are available in `.cursor/commands/`:
- `commit.md` - Guided commit workflow with conventional commits

## Hooks

Cursor hooks are configured in `.cursor/hooks.json` and scripts in `.cursor/hooks/`:
- Pre-prompt logging
- Shell execution checks
- File edit validation
- Final checks on stop

See `.cursor/hooks.json` for hook configuration.
