"""Star ratings: how close a solve came to par. No pygame in here."""

from __future__ import annotations

MAX_STARS = 3
TWO_STAR_SLACK = 2  # moves over par that still earn two stars


def stars(moves: int | None, par: int | None) -> int:
    """Stars for solving a level in ``moves``: 3 at or under par, 2 within +2, 1 otherwise.

    Returns 0 when the level wasn't solved (``moves`` is None). Levels without a par
    can't be rated, so any solve of one earns a single star.
    """
    if moves is None:
        return 0
    if par is None:
        return 1
    if moves <= par:
        return 3
    if moves <= par + TWO_STAR_SLACK:
        return 2
    return 1


def total_stars(best: dict[str, int], pars: dict[str, int | None]) -> int:
    """Sum of stars across levels, using the best move count saved for each."""
    return sum(stars(best.get(level_id), par) for level_id, par in pars.items())
