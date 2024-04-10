"""Define what is a game mode."""

from collections.abc import Callable, Iterable
from dataclasses import dataclass

from .game_mode_id import GameModeId
from .player import Player


@dataclass
class GameMode:
    """Properties of a game mode."""

    name: GameModeId

    def __init__(self, name: GameModeId | str) -> None:
        """Construct a GameMode from a name or a GameModeId."""
        self.name: GameModeId
        if isinstance(name, GameModeId):
            self.name = name
        elif isinstance(name, str):
            self.name = GameModeId(name)
        else:
            raise TypeError(f"Expected GameModeId or str, got {type(self.name)}.")


@dataclass
class ScoreMode(GameMode):
    """Simple game mode in which each player has a pre-defined score."""

    def points(self, player: Player) -> float:
        """Return the number of points earned by `player` doing `self.name`."""
        try:
            return player.score_at[self.name].score  # type: ignore
        except KeyError as exc:
            raise ValueError(f"{player.name} can't do {self.name}.") from exc


@dataclass
class SwimLikeRelayMode(GameMode):
    """Define the mode 'swim-like relay'."""

    atomic_modes: list[GameModeId]
    age_chrono_points: Callable[[float, float], float]

    def __init__(
        self,
        name: GameModeId | str,
        atomic_modes: Iterable[GameModeId],
        age_chrono_points: Callable[[float, float], float],
    ) -> None:
        """Initialize a SwimLikeRelayMode from an iterable."""
        super().__init__(name)
        self.atomic_modes = list(atomic_modes)
        self.age_chrono_points = age_chrono_points

    def points(self, player_for: dict[GameModeId, Player]) -> float:
        """
        Return the number of points earned by doing `self.name`.

        `player_for` gives the players doing each game mode.
        """
        total_age: float = sum(player_for[game_id].age for game_id in self.atomic_modes)
        total_chrono: float = sum(
            player_for[game_id].score_at[game_id].chrono  # type: ignore
            for game_id in self.atomic_modes
        )
        return self.age_chrono_points(total_age, total_chrono)
