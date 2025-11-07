.PHONY: help new-project

help:
	@echo "Available commands:"
	@echo "  make new-project name=<directory-name>  - Copy python-template to a new directory"

new-project:
	@if [ -z "$(name)" ]; then \
		echo "❌ Error: name parameter is required"; \
		echo "Usage: make new-project name=<directory-name>"; \
		exit 1; \
	fi
	@if [ -d "$(name)" ]; then \
		echo "❌ Error: Directory '$(name)' already exists"; \
		exit 1; \
	fi
	@echo "📦 Copying python-template to $(name)..."
	@rsync -av --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' \
		--exclude='.pytest_cache' --exclude='.mypy_cache' --exclude='.ruff_cache' \
		--exclude='.venv' --exclude='venv' --exclude='htmlcov' --exclude='dist' \
		--exclude='build' --exclude='*.egg-info' --exclude='.DS_Store' \
		python-template/ $(name)/
	@echo "✅ Project '$(name)' created successfully!"

