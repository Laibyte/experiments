"""Shared pytest fixtures."""

import pytest


@pytest.fixture
def sample_numbers() -> tuple[int, int]:
    """Provide sample numbers for testing.
    Returns:
        Tuple of (10, 5)
    """
    return (10, 5)


@pytest.fixture
def sample_name() -> str:
    """Provide sample name for testing.
    Returns:
        Sample name string
    """
    return "Test User"
