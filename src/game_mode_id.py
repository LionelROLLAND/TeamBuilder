"""Define a game identifier."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GameModeId:
    """Game mode represented by its name + an optional distinctive sign."""

    name: str
    distinction: str | None = None

    def __str__(self) -> str:
        """Return a natural string representation."""
        if self.distinction is None:
            return self.name
        return f"{self.name} ({self.distinction})"
