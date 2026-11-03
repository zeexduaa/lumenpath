"""Remembering which levels you've solved and your best move counts."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def default_path() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
    return base / "lumenpath" / "progress.json"


class Progress:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path
        self.best: dict[str, int] = {}

    @classmethod
    def load(cls, path: Path) -> Progress:
        """Read saved progress. A missing or damaged file just means a fresh start."""
        progress = cls(path)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            best = data.get("best", {})
            progress.best = {str(k): int(v) for k, v in best.items() if int(v) > 0}
        except (OSError, ValueError, TypeError, AttributeError):
            pass
        return progress

    def save(self) -> None:
        if self.path is None:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps({"version": 1, "best": self.best}, indent=2), encoding="utf-8")
        tmp.replace(self.path)

    def solved(self, level_id: str) -> bool:
        return level_id in self.best

    def record(self, level_id: str, moves: int) -> bool:
        """Store a finished level. Returns True if it's a new best."""
        if level_id in self.best and self.best[level_id] <= moves:
            return False
        self.best[level_id] = moves
        return True

    def first_unsolved(self, level_ids: list[str]) -> int:
        """Index of the first level not solved yet (the last level if all are)."""
        for index, level_id in enumerate(level_ids):
            if not self.solved(level_id):
                return index
        return len(level_ids) - 1
