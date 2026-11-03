"""The state of one level being played: mirror positions, moves and undo."""

from __future__ import annotations

from .board import Level, Pos, TraceResult, flip, trace
from .solver import solve


class Puzzle:
    def __init__(self, level: Level) -> None:
        self.level = level
        self.reset()

    def reset(self) -> None:
        self.mirrors = dict(self.level.mirrors)
        self.history: list[Pos] = []
        self.result: TraceResult = trace(self.level, self.mirrors)

    @property
    def moves(self) -> int:
        return len(self.history)

    @property
    def solved(self) -> bool:
        return self.level.crystals <= self.result.lit

    def rotate(self, pos: Pos) -> bool:
        """Turn the mirror at ``pos``. Returns False if there's no rotatable mirror there."""
        if pos not in self.mirrors or self.solved:
            return False
        self.mirrors[pos] = flip(self.mirrors[pos])
        self.history.append(pos)
        self.result = trace(self.level, self.mirrors)
        return True

    def undo(self) -> bool:
        if not self.history or self.solved:
            return False
        pos = self.history.pop()
        self.mirrors[pos] = flip(self.mirrors[pos])
        self.result = trace(self.level, self.mirrors)
        return True

    def hint(self) -> Pos | None:
        """A mirror worth turning from the current layout, or None if solved/unsolvable."""
        if self.solved:
            return None
        answer = solve(self.level, self.mirrors)
        return min(answer) if answer else None
