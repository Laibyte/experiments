"""Tests for the main module."""

import time

import pytest
from src.main import MESSAGE, greet


def test_greet() -> None:
    """Test the greet function."""
    assert greet("Alice") == "Hello, Alice!"
    assert greet("Bob") == "Hello, Bob!"


def test_message_constant() -> None:
    """Test that MESSAGE is set correctly."""
    assert MESSAGE == "Hello, World!"


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("Alice", "Hello, Alice!"),
        ("Bob", "Hello, Bob!"),
        ("", "Hello, !"),
    ],
)
def test_greet_parametrized(name: str, expected: str) -> None:
    """Test greet with multiple inputs."""
    assert greet(name) == expected


@pytest.mark.slow
def test_slow_operation() -> None:
    """Test a slow operation (skipped in fast test runs)."""
    # This test will be skipped during pre-commit

    time.sleep(0.1)
    assert True
