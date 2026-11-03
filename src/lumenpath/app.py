"""Command-line entry point: ``lumenpath`` or ``python -m lumenpath``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .board import LevelError
from .levels import load_levels
from .progress import Progress, default_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="lumenpath",
        description="A puzzle game about bending light: turn the mirrors until every crystal glows.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--level", type=int, metavar="N", help="start at level N (if unlocked)")
    parser.add_argument(
        "--levels", type=Path, metavar="FOLDER",
        help="play the *.txt levels in FOLDER instead of the built-in ones (all unlocked, not saved)",
    )
    parser.add_argument("--reset-progress", action="store_true", help="forget solved levels")
    args = parser.parse_args(argv)

    try:
        levels = load_levels(args.levels)
    except (LevelError, OSError) as exc:
        print(f"lumenpath: {exc}", file=sys.stderr)
        return 1

    custom = args.levels is not None
    if custom:
        progress = Progress(None)
    elif args.reset_progress:
        progress = Progress(default_path())
        progress.save()
    else:
        progress = Progress.load(default_path())

    start = progress.first_unsolved([level.id for level in levels])
    if args.level is not None:
        if not 1 <= args.level <= len(levels):
            print(f"lumenpath: there are {len(levels)} levels", file=sys.stderr)
            return 2
        start = args.level - 1

    import pygame  # imported late so --help and --version work without a display

    from .game import Game

    pygame.init()
    try:
        game = Game(levels, progress, unlock_all=custom)
        if not game.go(start):
            print(f"lumenpath: level {args.level} is locked; solve the ones before it first",
                  file=sys.stderr)
            return 2
        game.run()
    finally:
        pygame.quit()
    return 0
