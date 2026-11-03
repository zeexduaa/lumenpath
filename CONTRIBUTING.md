# Contributing

Thanks for taking a look! Bug reports, ideas and new levels are all welcome.

## Set up

```bash
git clone https://github.com/zeexduaa/lumenpath.git
cd lumenpath
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest
python -m lumenpath
```

The tests open the game window headlessly. If they fail on a machine without a display, set
`SDL_VIDEODRIVER=dummy`.

## Adding a level

1. Copy an existing file in `src/lumenpath/levels/` and give it the next number, e.g. `11-my-level.txt`.
2. Draw the grid (tile legend in the README). Set each turnable mirror to its **starting** position.
3. Try it with `python -m lumenpath --levels src/lumenpath/levels --level 11`.
4. Run `python -m pytest tests/test_levels.py`. It fails if the level can't be solved, starts
   solved, or if `par` is wrong, and tells you the correct par.

Good levels teach one idea, have a short solution, and make you think before you click.

## Guidelines

- Keep the game rules in `board.py` / `puzzle.py` free of pygame so they stay easy to test.
- Add or update tests for behaviour changes, and note them in `CHANGELOG.md` under *Unreleased*.
- Only use art, sounds and fonts you made yourself or that have a compatible free licence (say where they came from).
