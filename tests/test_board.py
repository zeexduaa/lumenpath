import pytest

from lumenpath.board import DOWN, LEFT, RIGHT, UP, LevelError, parse_level, reflect, trace


def level(grid: str, header: str = "name: Test"):
    return parse_level(f"{header}\n---\n{grid.strip()}\n", "test")


@pytest.mark.parametrize(
    "direction, mirror, expected",
    [
        (RIGHT, "/", UP),
        (LEFT, "/", DOWN),
        (UP, "/", RIGHT),
        (DOWN, "/", LEFT),
        (RIGHT, "\\", DOWN),
        (LEFT, "\\", UP),
        (UP, "\\", LEFT),
        (DOWN, "\\", RIGHT),
    ],
)
def test_reflect(direction, mirror, expected):
    assert reflect(direction, mirror) == expected


def test_parse_reads_header_and_pieces():
    lv = level(
        """
#####
#>/o#
#.b.#
#####
""",
        "name: Hello\npar: 3\n; a comment",
    )
    assert lv.name == "Hello"
    assert lv.par == 3
    assert (lv.width, lv.height) == (5, 4)
    assert lv.emitters == [((1, 1), RIGHT)]
    assert lv.crystals == {(3, 1)}
    assert lv.mirrors == {(2, 1): "/"}


def test_windows_line_endings_are_fine():
    lv = parse_level("name: X\r\n---\r\n###\r\n#>o\r\n###\r\n", "x")
    assert lv.crystals == {(2, 1)}


@pytest.mark.parametrize(
    "text, message",
    [
        ("name: X\n###\n", "---"),
        ("name: X\n---\n", "empty"),
        ("name: X\n---\n####\n#>o\n", "same width"),
        ("name: X\n---\n#>?o#\n", "unknown tile"),
        ("name: X\n---\n#..o#\n", "emitter"),
        ("name: X\n---\n#>..#\n", "crystal"),
        ("colour: red\n---\n#>o#\n", "expected"),
        ("par: lots\n---\n#>o#\n", "par"),
    ],
)
def test_bad_levels(text, message):
    with pytest.raises(LevelError, match=message):
        parse_level(text, "bad")


def test_beam_lights_crystals_it_passes_through():
    lv = level("#######\n#>o.o.#\n#######")
    result = trace(lv, lv.mirrors)
    assert result.lit == {(2, 1), (4, 1)}
    assert result.beams == (((1.5, 1.5), (6.0, 1.5)),)  # stops at the wall's edge


def test_beam_turns_at_mirrors():
    lv = level("######\n#>.\\.#\n#....#\n#..o.#\n######")
    result = trace(lv, lv.mirrors)
    assert result.lit == {(3, 3)}
    assert result.beams[0] == ((1.5, 1.5), (3.5, 1.5), (3.5, 4.0))


def test_fixed_mirrors_reflect_too():
    lv = level("#####\n#>.b#\n#...#\n#..o#\n#####")
    assert trace(lv, lv.mirrors).lit == {(3, 3)}


def test_beam_is_blocked_by_walls_and_emitters():
    lv = level("#######\n#>.#.o#\n#######")
    assert trace(lv, lv.mirrors).lit == frozenset()
    lv = level("#######\n#>..<o#\n#######")
    assert trace(lv, lv.mirrors).lit == frozenset()


def test_beam_through_a_ring_of_mirrors_ends():
    # Mirrors are reversible, so a beam can't loop forever: it bounces round and leaves.
    lv = level(
        """
#######
#v....#
#\\..\\.#
#.....#
#/../.#
#....o#
#######
"""
    )
    result = trace(lv, lv.mirrors)
    assert result.beams[0][-1] == (1.5, 6.0)
    assert result.lit == frozenset()


def test_beams_leaving_the_grid_stop():
    lv = parse_level("name: X\n---\n>.o.\n", "x")
    assert trace(lv, lv.mirrors).lit == {(2, 0)}
