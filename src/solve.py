"""Functions that find the best team for a competition in different scenarios."""

import logging
from collections.abc import Iterable

import gurobipy as grb  # type: ignore
from gurobipy import GRB  # pylint: disable=no-name-in-module

from .competition import Competition
from .game_mode import GameModeId
from .player import Player, PlayerId

BIN = GRB.BINARY
logger = logging.getLogger("root")

EPS = 10 ** (-5)


def best_team(
    club: Iterable[Player],
    competition: Competition,
) -> dict[GameModeId, PlayerId]:
    """
    Find a best team among the members of the club with best affectation.

    Maximize the expected point gains.
    """
    players: dict[PlayerId, Player] = {
        full_player.name: full_player for full_player in club
    }
    associations_set: frozenset[tuple[PlayerId, GameModeId]] = frozenset(
        (full_player.name, game_mode_id)
        for full_player in club
        for game_mode_id in full_player.known_modes
        if game_mode_id in competition.atomic_modes_ids
    )
    candidates_for: dict[GameModeId, set[PlayerId]] = {}
    for player, game_mode in associations_set:
        candidates_for.setdefault(game_mode, set())
        candidates_for[game_mode].add(player)
    env = grb.Env(empty=True)  # pylint: disable=no-member
    env.setParam("OutputFlag", 0)
    env.start()
    m = grb.Model(name="OneTeamBuilder", env=env)  # pylint: disable=no-member
    selected = m.addVars(players.keys(), BIN)
    associations = m.addVars(associations_set, BIN)
    m.addConstrs(
        (
            sum(
                associations[player, game_mode, BIN]
                for game_mode in competition.score_mode_ids
                if player in candidates_for[game_mode]
            )
            <= selected[player, BIN]
            for player in players
        )
    )  # player plays at most one score mode if it is chosen.
    m.addConstrs(
        (
            sum(
                associations[player, atomic_mode, BIN]
                for atomic_mode in competition.swim_relay_modes[
                    relay_mode_id
                ].atomic_modes
                if player in candidates_for[atomic_mode]
            )
            <= selected[player, BIN]
            for player in players
            for relay_mode_id in competition.swim_relay_modes
        )
    )  # player plays at most once atomic mode in each swim relay if it is chosen.
    m.addConstrs(
        (
            sum(
                associations[player, game_mode, BIN]
                for player in players
                if player in candidates_for[game_mode]
            )
            == 1
            for game_mode in competition.atomic_modes_ids
        )
    )  # 1 player per game mode
    # No more players than the allowed number :
    m.addConstr(
        sum(selected[player, BIN] for player in players) <= competition.nb_players
    )
    m.setObjective(
        sum(
            (
                players[player].perf_at[game_mode].score  # type: ignore
                * associations[player, game_mode, BIN]
            )
            for player, game_mode in associations_set
            if game_mode in competition.score_mode_ids
        ),
        sense=GRB.MAXIMIZE,
    )  # Manque les relais
    m.optimize()
    return {
        game_mode: player
        for (player, game_mode) in associations_set
        if associations[player, game_mode, BIN].X >= 1 - EPS
    }
