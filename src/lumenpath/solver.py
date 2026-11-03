"""Brute-force solver, used for hints and to check that every bundled level can be solved."""

from __future__ import annotations

from collections.abc import Mapping
from itertools import combinations

from .board import Level, Pos, flip, trace


def solve(level: Level, mirrors: Mapping[Pos, str] | None = None) -> frozenset[Pos] | None:
    """The smallest set of mirrors to turn (from ``mirrors``, default the level's start)
    so that every crystal is lit. ``None`` if there is no solution.

    Tries every subset, smallest first: fine for the handful of mirrors a level has.
    """
    start = dict(level.mirrors if mirrors is None else mirrors)
    positions = sorted(start)
    for count in range(len(positions) + 1):
        for combo in combinations(positions, count):
            layout = dict(start)
            for pos in combo:
                layout[pos] = flip(layout[pos])
            if level.crystals <= trace(level, layout).lit:
                return frozenset(combo)
    return None
