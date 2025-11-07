"""Tests for main module."""

from src.main import greet


def test_greet_with_name() -> None:
    """Test greeting with a specific name."""
    result = greet("Alice")
    assert result == "Hello, Alice!"


def test_greet_with_fixture(sample_name: str) -> None:
    """Test greeting using fixture."""
    result = greet(sample_name)
    assert result == "Hello, Alice!"


def test_greet_empty_string() -> None:
    """Test greeting with empty string."""
    result = greet("")
    assert result == "Hello, !"
