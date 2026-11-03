"""Drive the real game window headlessly (SDL's dummy video driver)."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402
import pytest  # noqa: E402

from lumenpath.app import main  # noqa: E402
from lumenpath.game import CELL, Game  # noqa: E402
from lumenpath.levels import load_levels  # noqa: E402
from lumenpath.progress import Progress  # noqa: E402
from lumenpath.solver import solve  # noqa: E402

LEVELS = load_levels()


@pytest.fixture
def game(tmp_path):
    pygame.init()
    yield Game(LEVELS, Progress(tmp_path / "progress.json"))
    pygame.quit()


def click(game, pos):
    px, py = game.to_px(pos[0] + 0.5, pos[1] + 0.5)
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(px, py))
    return game.handle(event)


def press(game, key):
    return game.handle(pygame.event.Event(pygame.KEYDOWN, key=key))


def test_clicking_mirrors_solves_and_saves(game, tmp_path):
    for pos in solve(game.level):
        click(game, pos)
    assert game.puzzle.solved
    assert game.new_best
    assert Progress.load(tmp_path / "progress.json").best == {LEVELS[0].id: LEVELS[0].par}
    game.draw()  # the solved screen renders


def test_next_level_is_locked_until_solved(game):
    press(game, pygame.K_n)
    assert game.index == 0
    for pos in solve(game.level):
        click(game, pos)
    press(game, pygame.K_RETURN)
    assert game.index == 1
    press(game, pygame.K_p)
    assert game.index == 0


def test_keys_undo_restart_and_hint(game):
    game.load(1)  # needs two moves, so one click doesn't finish it
    mirror = min(game.level.mirrors)
    click(game, mirror)
    assert game.puzzle.moves == 1
    press(game, pygame.K_z)
    assert game.puzzle.moves == 0
    assert game.puzzle.mirrors[mirror] == game.level.mirrors[mirror]
    press(game, pygame.K_h)
    assert game.hint_pos in game.level.mirrors
    game.draw()
    press(game, pygame.K_r)
    assert game.hint_pos is None


def test_clicks_outside_the_board_are_ignored(game):
    assert game.handle(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(1, 1)))
    assert game.puzzle.moves == 0


def test_every_level_fits_and_draws(game):
    w, h = game.size
    for index in range(len(LEVELS)):
        game.load(index)
        ox, oy = game.origin()
        assert ox >= 0 and ox + game.level.width * CELL <= w
        assert oy >= 0 and oy + game.level.height * CELL <= h
        game.draw()


def test_escape_and_close_quit(game):
    assert not press(game, pygame.K_ESCAPE)
    assert not game.handle(pygame.event.Event(pygame.QUIT))


def test_cli_version(capsys):
    with pytest.raises(SystemExit):
        main(["--version"])
    assert "lumenpath" in capsys.readouterr().out


def test_cli_rejects_bad_level_folder(tmp_path, capsys):
    assert main(["--levels", str(tmp_path)]) == 1
    assert "no level files" in capsys.readouterr().err


def test_cli_rejects_out_of_range_level(capsys):
    assert main(["--level", "999"]) == 2
