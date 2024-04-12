"""Define a class Competition providing useful Generators."""

from collections.abc import Iterable
from io import IOBase

from .game_mode import GameMode, GameModeId, ScoreMode, SwimLikeRelayMode


class Competition:
    """A class defining some useful generators."""

    def __init__(self, game_modes: Iterable[GameMode], nb_players: int) -> None:
        """Initialize the competition with a set of game modes."""
        self.nb_players: int = nb_players
        self.game_modes: dict[GameModeId, GameMode] = {
            game_mode.name: game_mode for game_mode in game_modes
        }
        self.score_mode_ids: frozenset[GameModeId] = frozenset(
            name
            for name, mode in self.game_modes.items()
            if isinstance(mode, ScoreMode)
        )
        self.swim_relay_modes: dict[GameModeId, SwimLikeRelayMode] = {
            name: mode
            for name, mode in self.game_modes.items()
            if isinstance(mode, SwimLikeRelayMode)
        }
        self.atomic_modes_ids: frozenset[GameModeId] = self.score_mode_ids | frozenset(
            sub_mode
            for mode in self.swim_relay_modes.values()
            for sub_mode in mode.atomic_modes
        )

    @classmethod
    def from_json(cls, fd: IOBase) -> "Competition":
        """Transform a json into a Competition."""
        raise NotImplementedError

    def __str__(self) -> str:
        """Return a string representation."""
        raise NotImplementedError
