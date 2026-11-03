"""Loading the levels that ship with the game, or a folder of your own."""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path

from .board import Level, LevelError, parse_level


def load_levels(folder: Path | None = None) -> list[Level]:
    """All ``*.txt`` levels in ``folder`` (default: the bundled ones), sorted by file name."""
    source = Path(folder) if folder is not None else files("lumenpath").joinpath("levels")
    entries = sorted((e for e in source.iterdir() if e.name.endswith(".txt")), key=lambda e: e.name)
    levels = [parse_level(e.read_text(encoding="utf-8"), e.name[: -len(".txt")]) for e in entries]
    if not levels:
        raise LevelError(f"no level files (*.txt) found in {source}")
    return levels
