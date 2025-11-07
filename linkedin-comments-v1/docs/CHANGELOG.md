# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project template setup
- Poetry dependency management
- Ruff for linting and formatting
- mypy for type checking
- pytest for testing with coverage
- Pre-commit hooks for quality enforcement
- GitHub Actions CI/CD pipeline
- Comprehensive documentation structure
- AI-native development workflow (Cursor/Copilot integration)
- VSCode/Cursor IDE configuration

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- Bandit security scanning enabled
- detect-secrets credential scanning enabled

---

## Guidelines for Updating This File

### When to Update

Update this file when:
- Releasing a new version
- Adding new features
- Fixing bugs
- Making breaking changes
- Removing features
- Updating dependencies (major versions)
- Addressing security vulnerabilities

### Version Format

Use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes (e.g., 1.0.0 → 2.0.0)
- **MINOR**: New features, backwards compatible (e.g., 1.0.0 → 1.1.0)
- **PATCH**: Bug fixes, backwards compatible (e.g., 1.0.0 → 1.0.1)

### Categories

Use these standard categories:

- **Added**: New features
- **Changed**: Changes to existing functionality
- **Deprecated**: Features that will be removed in future versions
- **Removed**: Features that have been removed
- **Fixed**: Bug fixes
- **Security**: Security fixes or improvements

### Entry Format

Each entry should:
- Start with a verb (Add, Fix, Update, Remove, etc.)
- Be clear and concise
- Reference issue/PR numbers when applicable
- Be user-focused (not implementation details)

**Example**:
```markdown
## [1.2.0] - 2024-03-15

### Added
- User authentication endpoint (#42)
- Password reset functionality (#45)

### Fixed
- Memory leak in background worker (#48)
- Incorrect pagination on user list (#50)

### Security
- Updated dependencies to fix CVE-2024-1234 (#52)
```

### Unreleased Section

- Keep an `[Unreleased]` section at the top
- Add entries here as changes are made
- Move to versioned section when releasing

### Links

At the bottom of the file, add version comparison links:

```markdown
[Unreleased]: https://github.com/username/repo/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/username/repo/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/username/repo/releases/tag/v1.1.0
```

### Best Practices

1. **Write for users**, not developers
2. **Be specific** - "Fixed login bug" → "Fixed session timeout causing unexpected logouts"
3. **Group related changes** - Don't list every file changed
4. **Keep it updated** - Update as you go, not at release time
5. **Link to issues/PRs** - Helps with context
6. **Note breaking changes** - Call them out clearly

---

## Example Full Entry

```markdown
## [1.0.0] - 2024-01-15

### Added
- REST API for user management (#10)
- JWT authentication (#12)
- Rate limiting on API endpoints (#15)
- Comprehensive API documentation (#18)

### Changed
- Migrated from Flask to FastAPI for better async support (#20)
- Updated Python requirement to 3.11+ (#22)

### Deprecated
- Legacy `/api/v1/` endpoints (use `/api/v2/`) (#25)

### Removed
- Support for Python 3.9 and 3.10 (#22)

### Fixed
- Race condition in concurrent user creation (#28)
- Memory leak in WebSocket connections (#30)

### Security
- Updated dependencies to address CVE-2024-1234 (#35)
- Added input validation to prevent SQL injection (#38)

[1.0.0]: https://github.com/username/repo/releases/tag/v1.0.0
```
