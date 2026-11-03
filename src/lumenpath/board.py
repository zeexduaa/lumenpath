"""Level parsing and beam tracing. No pygame in here, so the rules are easy to test."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

Pos = tuple[int, int]
Dir = tuple[int, int]

RIGHT: Dir = (1, 0)
LEFT: Dir = (-1, 0)
UP: Dir = (0, -1)
DOWN: Dir = (0, 1)

EMPTY = "."
WALL = "#"
CRYSTAL = "o"
EMITTERS: dict[str, Dir] = {">": RIGHT, "<": LEFT, "^": UP, "v": DOWN}
ROTATABLE = frozenset({"/", "\\"})
FIXED = {"f": "/", "b": "\\"}  # fixed mirrors the player can't turn
TILES = frozenset({EMPTY, WALL, CRYSTAL, *EMITTERS, *ROTATABLE, *FIXED})


class LevelError(ValueError):
    """Raised when a level file can't be used."""


def reflect(direction: Dir, mirror: str) -> Dir:
    """New direction after bouncing off a ``/`` or ``\\`` mirror (y grows downwards)."""
    dx, dy = direction
    return (-dy, -dx) if mirror == "/" else (dy, dx)


def flip(mirror: str) -> str:
    return "\\" if mirror == "/" else "/"


@dataclass(frozen=True)
class Level:
    id: str
    name: str
    rows: tuple[str, ...]
    par: int | None = None

    @property
    def width(self) -> int:
        return len(self.rows[0])

    @property
    def height(self) -> int:
        return len(self.rows)

    def tile(self, pos: Pos) -> str:
        x, y = pos
        if 0 <= y < self.height and 0 <= x < self.width:
            return self.rows[y][x]
        return WALL

    def positions(self, tiles) -> list[Pos]:
        return [
            (x, y) for y, row in enumerate(self.rows) for x, ch in enumerate(row) if ch in tiles
        ]

    @property
    def emitters(self) -> list[tuple[Pos, Dir]]:
        return [(pos, EMITTERS[self.tile(pos)]) for pos in self.positions(EMITTERS)]

    @property
    def crystals(self) -> frozenset[Pos]:
        return frozenset(self.positions({CRYSTAL}))

    @property
    def mirrors(self) -> dict[Pos, str]:
        """Starting state of the mirrors the player can rotate."""
        return {pos: self.tile(pos) for pos in self.positions(ROTATABLE)}


def parse_level(text: str, level_id: str = "level") -> Level:
    """Read a level file: ``key: value`` header lines, a ``---`` line, then the grid."""
    lines = text.replace("\r\n", "\n").split("\n")
    try:
        split = lines.index("---")
    except ValueError:
        raise LevelError(f"{level_id}: missing '---' line between header and grid") from None

    meta: dict[str, str] = {}
    for number, line in enumerate(lines[:split], 1):
        if not line.strip() or line.lstrip().startswith(";"):
            continue
        key, sep, value = line.partition(":")
        key = key.strip().lower()
        if not sep or key not in ("name", "par"):
            raise LevelError(f"{level_id}:{number}: expected 'name: ...' or 'par: ...'")
        meta[key] = value.strip()

    rows = tuple(line for line in lines[split + 1 :] if line.strip())
    if not rows:
        raise LevelError(f"{level_id}: the grid is empty")
    if len({len(row) for row in rows}) != 1:
        raise LevelError(f"{level_id}: every grid row must be the same width")
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch not in TILES:
                raise LevelError(f"{level_id}: unknown tile {ch!r} at column {x + 1}, row {y + 1}")

    try:
        par = int(meta["par"]) if "par" in meta else None
    except ValueError:
        raise LevelError(f"{level_id}: par must be a whole number") from None

    level = Level(level_id, meta.get("name", level_id), rows, par)
    if not level.emitters:
        raise LevelError(f"{level_id}: needs at least one emitter (> < ^ v)")
    if not level.crystals:
        raise LevelError(f"{level_id}: needs at least one crystal (o)")
    return level


@dataclass(frozen=True)
class TraceResult:
    # One polyline per emitter, as points in cell units (a cell's centre is x + 0.5, y + 0.5).
    beams: tuple[tuple[tuple[float, float], ...], ...]
    lit: frozenset[Pos]


def _centre(pos: Pos) -> tuple[float, float]:
    return (pos[0] + 0.5, pos[1] + 0.5)


def trace(level: Level, mirrors: Mapping[Pos, str]) -> TraceResult:
    """Follow every beam from its emitter until it hits a wall, an emitter or loops."""
    beams = []
    lit: set[Pos] = set()
    for start, direction in level.emitters:
        points = [_centre(start)]
        x, y = start
        seen: set[tuple[int, int, Dir]] = set()
        while True:
            nxt = (x + direction[0], y + direction[1])
            tile = level.tile(nxt)
            if tile == WALL or tile in EMITTERS:
                points.append((x + 0.5 + direction[0] / 2, y + 0.5 + direction[1] / 2))
                break
            x, y = nxt
            if (x, y, direction) in seen:
                points.append(_centre(nxt))
                break
            seen.add((x, y, direction))
            if tile == CRYSTAL:
                lit.add(nxt)
            mirror = mirrors.get(nxt) or FIXED.get(tile)
            if mirror:
                points.append(_centre(nxt))
                direction = reflect(direction, mirror)
        beams.append(tuple(points))
    return TraceResult(tuple(beams), frozenset(lit))
