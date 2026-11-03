"""Every bundled level must load, be solvable, not start solved, and have the right par."""

import pytest

from lumenpath.board import LevelError, trace
from lumenpath.levels import load_levels
from lumenpath.solver import solve

LEVELS = load_levels()


def test_there_are_levels_with_unique_ids():
    assert len(LEVELS) >= 10
    assert len({level.id for level in LEVELS}) == len(LEVELS)


@pytest.mark.parametrize("level", LEVELS, ids=lambda level: level.id)
def test_level_is_a_fair_puzzle(level):
    assert not level.crystals <= trace(level, level.mirrors).lit, "already solved at the start"
    answer = solve(level)
    assert answer is not None, "no solution"
    assert level.par == len(answer), f"par should be {len(answer)}"


def test_load_custom_folder(tmp_path):
    (tmp_path / "b.txt").write_text("name: B\n---\n#>o#\n", encoding="utf-8")
    (tmp_path / "a.txt").write_text("name: A\n---\n#>o#\n", encoding="utf-8")
    (tmp_path / "notes.md").write_text("ignored", encoding="utf-8")
    assert [level.name for level in load_levels(tmp_path)] == ["A", "B"]


def test_empty_custom_folder(tmp_path):
    with pytest.raises(LevelError, match="no level files"):
        load_levels(tmp_path)
