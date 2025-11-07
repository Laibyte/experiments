.PHONY: help setup install test test-cov lint format type-check check clean

help:
	@echo "Available commands:"
	@echo "  make setup       - Complete project setup"
	@echo "  make install     - Install dependencies"
	@echo "  make test        - Run tests"
	@echo "  make test-cov    - Run tests with coverage report"
	@echo "  make lint        - Check code quality"
	@echo "  make format      - Format code"
	@echo "  make type-check  - Run type checking"
	@echo "  make check       - Run all checks"
	@echo "  make clean       - Clean up generated files"

setup:
	@echo "🚀 Setting up project..."
	poetry install
	poetry run pre-commit install
	@echo "✅ Setup complete!"

install:
	poetry install

test:
	poetry run pytest

test-cov:
	poetry run pytest --cov --cov-report=html
	@echo "📊 Coverage report: htmlcov/index.html"

lint:
	poetry run ruff check .

format:
	poetry run ruff format .
	poetry run ruff check --fix .

type-check:
	poetry run mypy src/

check: format type-check test
	@echo "✅ All checks passed!"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ dist/ build/
	@echo "✅ Cleaned up!"
