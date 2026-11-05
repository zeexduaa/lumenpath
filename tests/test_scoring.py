import pytest

from lumenpath.levels import load_levels
from lumenpath.scoring import MAX_STARS, stars, total_stars


@pytest.mark.parametrize(
    "moves, par, expected",
    [
        (None, 3, 0),  # not solved
        (2, 3, 3),  # under par (shouldn't happen, but never punish it)
        (3, 3, 3),
        (4, 3, 2),
        (5, 3, 2),
        (6, 3, 1),
        (40, 3, 1),
        (7, None, 1),  # no par: any solve is one star
    ],
)
def test_stars(moves, par, expected):
    assert stars(moves, par) == expected


def test_total_stars_counts_only_solved_levels():
    pars = {"01": 1, "02": 4, "03": 2}
    assert total_stars({}, pars) == 0
    assert total_stars({"01": 1, "02": 6}, pars) == 3 + 2
    assert total_stars({"01": 1, "02": 4, "03": 2}, pars) == 3 * MAX_STARS


def test_every_bundled_level_can_earn_three_stars():
    # The solver checks each par is the true minimum, so par is always reachable.
    for level in load_levels():
        assert level.par is not None, level.id
        assert stars(level.par, level.par) == MAX_STARS
