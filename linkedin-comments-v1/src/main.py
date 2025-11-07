"""Main module for my-project."""

from typing import Final

MESSAGE: Final[str] = "Hello, World!"


def greet(name: str) -> str:
    """Greet someone by name.

    Args:
        name: The name to greet

    Returns:
        A greeting message
    """
    return f"Hello, {name}!"


def main() -> None:
    """Run the main program."""
    result = greet("World")
    print(result)  # noqa: T201


if __name__ == "__main__":
    main()
