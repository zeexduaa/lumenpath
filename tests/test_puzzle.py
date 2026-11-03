from lumenpath.board import parse_level
from lumenpath.puzzle import Puzzle
from lumenpath.solver import solve

# Needs both mirrors turned: (4, 1) to send the beam down, (4, 4) to send it left.
TWO_TURNS = parse_level(
    "name: Two Turns\npar: 2\n---\n"
    "########\n#>../..#\n#......#\n#......#\n#.o.\\..#\n########\n",
    "two-turns",
)


def test_rotate_and_solve():
    puzzle = Puzzle(TWO_TURNS)
    assert not puzzle.solved
    assert puzzle.rotate((4, 1))
    assert not puzzle.solved
    assert puzzle.rotate((4, 4))
    assert puzzle.solved
    assert puzzle.moves == 2


def test_only_mirrors_rotate():
    puzzle = Puzzle(TWO_TURNS)
    assert not puzzle.rotate((2, 2))
    assert not puzzle.rotate((0, 0))
    assert puzzle.moves == 0


def test_no_moves_after_solving():
    puzzle = Puzzle(TWO_TURNS)
    puzzle.rotate((4, 1))
    puzzle.rotate((4, 4))
    assert not puzzle.rotate((4, 1))
    assert not puzzle.undo()


def test_undo_and_reset():
    puzzle = Puzzle(TWO_TURNS)
    puzzle.rotate((4, 1))
    puzzle.rotate((4, 1))
    assert puzzle.undo()
    assert puzzle.mirrors[(4, 1)] == "\\"
    assert puzzle.moves == 1
    puzzle.reset()
    assert puzzle.mirrors == TWO_TURNS.mirrors
    assert puzzle.moves == 0
    assert not puzzle.undo()


def test_hint_points_at_a_mirror_that_helps():
    puzzle = Puzzle(TWO_TURNS)
    first = puzzle.hint()
    assert first in {(4, 1), (4, 4)}
    puzzle.rotate(first)
    second = puzzle.hint()
    assert second in {(4, 1), (4, 4)} - {first}
    puzzle.rotate(second)
    assert puzzle.solved
    assert puzzle.hint() is None


def test_solver_starts_from_any_layout():
    assert solve(TWO_TURNS, {(4, 1): "\\", (4, 4): "\\"}) == {(4, 4)}
    assert solve(TWO_TURNS, {(4, 1): "\\", (4, 4): "/"}) == frozenset()


def test_unsolvable_level():
    level = parse_level("name: X\n---\n#####\n#>/.#\n#.#o#\n#####\n", "x")
    assert solve(level) is None
    assert Puzzle(level).hint() is None
