"""Define a class representing a player."""

from collections.abc import KeysView
from dataclasses import dataclass

from .game_mode_id import GameModeId


@dataclass(frozen=True)
class PlayerId:
    """Player represented by its name + an optional distinctive sign."""

    fst_name: str
    last_name: str | None = None
    distinction: str | None = None

    def __str__(self) -> str:
        """Return a natural string representation."""
        if self.distinction is None:
            return f"{self.fst_name} {self.last_name or ''}"
        return f"{self.fst_name} {self.last_name or ''} ({self.distinction})"


@dataclass(frozen=True)
class Perf:
    """Class representing the performance of a player at some game mode."""


@dataclass(frozen=True)
class Score(Perf):
    """Class representing the performance of a player as a simple score."""

    score: float


@dataclass(frozen=True)
class Chrono(Perf):
    """Class representing the performance at a relay like in a swimming competition."""

    chrono: float


class Player:
    """Represents a player."""

    def __init__(
        self,
        player_id: PlayerId,
        scores: dict[GameModeId, Perf] | None = None,
        age: float | None = None,  # On code galamment ici
    ) -> None:
        """Initialize the name and scores of the player."""
        self.perf_at: dict[GameModeId, Perf]
        if scores is None:
            self.perf_at = {}
        else:
            self.perf_at = dict(scores)
        self.name = player_id
        self.__age = age

    @classmethod
    def from_name(
        cls, player_name: str, scores: dict[GameModeId, Perf] | None = None
    ) -> "Player":
        """Construct a player using only a name instead of a full identifier."""
        return Player(player_id=PlayerId(fst_name=player_name), scores=scores)

    @property
    def known_modes(self) -> KeysView[GameModeId]:
        """Iterator over the modes known by self."""
        return self.perf_at.keys()

    @property
    def age(self) -> float:
        """Return the age if it was given at the initialization."""
        if self.__age is None:
            raise AttributeError(f"The age of {str(self.name)} was not given.")
        return self.__age
