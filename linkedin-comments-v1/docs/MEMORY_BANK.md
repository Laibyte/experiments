# Memory Bank - Architectural Decision Records

This document tracks key architectural decisions and established patterns for the project.

## Purpose

The Memory Bank serves as a living record of:
- Architectural decisions and their rationale
- Established patterns and conventions
- Technology choices and why they were made
- Important lessons learned
- Context for future maintainers and AI assistants

## Format

Each entry should follow this structure:

```
## [Date] - [Decision Title]

**Status**: [Proposed | Accepted | Deprecated | Superseded]

**Context**: What is the issue we're trying to solve?

**Decision**: What did we decide to do?

**Rationale**: Why did we make this decision?

**Consequences**: What are the trade-offs and implications?

**Alternatives Considered**: What other options did we evaluate?
```

---

## Decision Records

### Example Entry (Delete this when you add your first decision)

## 2024-01-15 - Use Poetry for Dependency Management

**Status**: Accepted

**Context**: Need a robust Python dependency management solution for the project template.

**Decision**: Use Poetry exclusively for dependency management.

**Rationale**:
- Modern, deterministic dependency resolution
- Built-in virtual environment management
- Lock file for reproducible builds
- Superior to pip, pip-tools, pipenv in terms of UX and reliability
- Wide adoption in the Python community

**Consequences**:
- Team must install Poetry locally
- All dependencies must be added via `poetry add`
- Cannot use pip directly in production environments
- Simpler dependency management workflow

**Alternatives Considered**:
- pip + requirements.txt: Less reliable, no lock file
- pipenv: Slower, less reliable resolution
- conda: Overkill for pure Python projects

---

## 2025-11-05 - AI-Native Workflow Unification

**Status**: Accepted

**Context**:

The Python template project had fragmented AI assistant configuration, duplicate tooling setup, and incomplete documentation structure. Files were scattered across `.cursor/`, `.github/`, and `.vscode/` with overlapping responsibilities and inconsistent patterns.

**Decision**:

Implemented a comprehensive unification of the AI-native workflow across 6 phases:

1. **Core Documentation Structure**
   - Created `.cursor/rules/shared-rules.mdc` as single source of truth for AI agent rules
   - Both Cursor (AGENTS.md) and GitHub Copilot (copilot-instructions.md) now reference shared rules
   - Populated all documentation files in `docs/` with structured content
   - Created `.cursorignore` to exclude build artifacts and caches

2. **Cursor IDE Integration**
   - Consolidated `.cursor/rules/*.mdc` files by concern (core, types, testing, async, security)
   - Updated commit command to align with Conventional Commits
   - Simplified `.cursor/hooks.json` to avoid duplication with pre-commit
   - Updated hook scripts to check pre-commit instead of running linters directly
   - Enhanced `python-standard.mdc` with comprehensive project-specific guidance

3. **GitHub Ecosystem**
   - Consolidated multiple CI workflow files into single `python-ci.yml` using modern tools (Ruff, not Black/isort)
   - Created proper `dependabot.yml` for automated dependency updates
   - Removed experimental/duplicate workflows (auto-docs, auto-fix, auto-pr, code-review, deploy-cf-worker)
   - Created `.github/workflows/README.md` documenting all workflows
   - Enhanced PR template with comprehensive quality gates checklist

4. **VSCode/Cursor Environment Setup**
   - Created `.cursor/hooks/setup-extensions.sh` for auto-installing extensions
   - Integrated extension setup into main setup script
   - Enhanced `.vscode/settings.json` with Python-specific settings, ErrorLens, BetterComments, spell checking
   - Added PYTHONPATH configuration for all terminal environments

5. **Documentation Completion**
   - Created `docs/ARCHITECTURE.mermaid` with visual project structure diagram
   - Established `docs/CHANGELOG.md` structure with Keep a Changelog format
   - Created `docs/PROJECT_SPEC.md` template guide
   - Updated main `README.md` with comprehensive setup, contributing guidelines, and troubleshooting
   - Documented all tooling, workflows, and AI integration points

6. **Cleanup and Testing**
   - Reviewed and incorporated patterns from example cursor rules
   - Deleted `example/` folder after extraction
   - Documented this architectural decision for future reference

**Rationale**:

- **Single Source of Truth**: Eliminates duplication between Cursor and GitHub Copilot configs
- **Modern Tooling**: Uses Ruff exclusively (replaces Black, isort, flake8) for 10-100x speedup
- **Pre-commit Integration**: Hooks handle all quality checks; Cursor hooks don't duplicate logic
- **Developer Experience**: One-command setup script installs everything needed
- **AI-First**: Optimized for working with Cursor AI and GitHub Copilot from day one
- **Comprehensive Docs**: Clear architecture, technical stack, and contribution guidelines
- **Maintainability**: Well-organized structure makes future updates straightforward

**Consequences**:

Positive:
- Developers can set up project in one command: `bash .cursor/hooks/setup.sh`
- AI assistants have clear, consistent rules across all tools
- No duplication between pre-commit hooks and Cursor hooks
- Modern CI/CD pipeline with GitHub Actions
- Comprehensive documentation structure ready for any project
- Clear contributing guidelines and quality standards
- Extensions install automatically

Trade-offs:
- Slightly more initial setup complexity (but automated)
- Requires Poetry (can't use pip directly)
- Opinionated tool choices (Ruff, mypy, pytest)
- Must maintain consistency between docs when updating
- Setup script requires bash (Windows users need WSL/Git Bash)

**Alternatives Considered**:

1. **Keep separate configs for each AI tool**
   - Rejected: Creates maintenance burden and inconsistency

2. **Use Black + isort + flake8 instead of Ruff**
   - Rejected: Ruff is 10-100x faster and replaces all three

3. **Manual extension installation**
   - Rejected: Automated setup provides better developer experience

4. **Cursor hooks run linters directly**
   - Rejected: Duplicates pre-commit logic; pre-commit is the single authority

5. **Keep all experimental GitHub workflows**
   - Rejected: Clutters the template; users can add what they need

**Impact**:

- All future Python projects using this template will have:
  - Consistent AI assistant behavior
  - Automated quality enforcement
  - Modern, fast tooling
  - Comprehensive documentation
  - One-command setup
- Template is now production-ready for AI-native development workflows
- Provides clear patterns for other language templates

---

<!-- Add your decisions below this line -->
