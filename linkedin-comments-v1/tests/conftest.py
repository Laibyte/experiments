"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def sample_name() -> str:
    """Provide a sample name for testing."""
    return "Alice"
