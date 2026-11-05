"""The pygame window: drawing the board and handling clicks and keys."""

from __future__ import annotations

import math

import pygame

from .board import CRYSTAL, EMITTERS, FIXED, WALL, Level, Pos
from .progress import Progress
from .puzzle import Puzzle
from .scoring import MAX_STARS, stars

CELL = 64
HUD = 76
FOOTER = 40
MARGIN = 24
MIN_WIDTH = 760
FPS = 60
HINT_SECONDS = 1.5

BG = (14, 17, 28)
FLOOR = (26, 31, 48)
GRID = (36, 42, 62)
WALL_FILL = (58, 66, 92)
WALL_EDGE = (82, 92, 124)
TEXT = (226, 230, 240)
MUTED = (140, 148, 170)
GOLD = (255, 214, 102)
BEAM = (255, 222, 130)
BEAM_GLOW = (255, 180, 60, 60)
CRYSTAL_OFF = (80, 110, 150)
CRYSTAL_ON = (120, 240, 255)
CRYSTAL_GLOW = (120, 240, 255, 70)
MIRROR = (215, 228, 255)
MIRROR_FIXED = (118, 126, 148)
PIVOT = (70, 110, 200)
HINT = (120, 255, 160)
EMITTER = (255, 165, 60)
STAR_EMPTY = (70, 78, 104)

HELP = "Click a mirror to turn it    Z undo    R restart    H hint    N / P next / previous    Esc quit"


class Game:
    def __init__(self, levels: list[Level], progress: Progress, start: int = 0,
                 unlock_all: bool = False) -> None:
        self.levels = levels
        self.progress = progress
        self.unlock_all = unlock_all
        cols = max(level.width for level in levels)
        self.board_rows = max(level.height for level in levels)
        self.size = (
            max(cols * CELL + 2 * MARGIN, MIN_WIDTH),
            HUD + self.board_rows * CELL + MARGIN + FOOTER,
        )
        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption("Lumenpath")
        self.font = pygame.font.Font(None, 34)
        self.small = pygame.font.Font(None, 24)
        self.big = pygame.font.Font(None, 64)
        self.overlay = pygame.Surface(self.size, pygame.SRCALPHA)
        self.load(start)

    # ----- state -------------------------------------------------------------------------

    @property
    def level(self) -> Level:
        return self.puzzle.level

    def load(self, index: int) -> None:
        self.index = index
        self.puzzle = Puzzle(self.levels[index])
        self.hint_pos: Pos | None = None
        self.hint_until = 0.0
        self.recorded = False
        self.new_best = False

    def unlocked(self, index: int) -> bool:
        return self.unlock_all or index == 0 or self.progress.solved(self.levels[index - 1].id)

    def go(self, index: int) -> bool:
        if 0 <= index < len(self.levels) and self.unlocked(index):
            self.load(index)
            return True
        return False

    def origin(self) -> tuple[int, int]:
        x = (self.size[0] - self.level.width * CELL) // 2
        y = HUD + (self.board_rows - self.level.height) * CELL // 2
        return x, y

    def to_px(self, x: float, y: float) -> tuple[int, int]:
        ox, oy = self.origin()
        return round(ox + x * CELL), round(oy + y * CELL)

    def cell_at(self, pixel: tuple[int, int]) -> Pos | None:
        ox, oy = self.origin()
        x, y = (pixel[0] - ox) // CELL, (pixel[1] - oy) // CELL
        if 0 <= x < self.level.width and 0 <= y < self.level.height:
            return (x, y)
        return None

    def after_move(self) -> None:
        self.hint_pos = None
        if self.puzzle.solved and not self.recorded:
            self.recorded = True
            self.new_best = self.progress.record(self.level.id, self.puzzle.moves)
            try:
                self.progress.save()
            except OSError:
                pass  # progress is a nice-to-have; never crash the game over it

    # ----- input -------------------------------------------------------------------------

    def handle(self, event: pygame.event.Event) -> bool:
        """Process one event. Returns False when the game should close."""
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 3):
            cell = self.cell_at(event.pos)
            if cell is not None and self.puzzle.rotate(cell):
                self.after_move()
        elif event.type == pygame.KEYDOWN:
            return self.key(event.key)
        return True

    def key(self, key: int) -> bool:
        if key == pygame.K_ESCAPE:
            return False
        if key in (pygame.K_z, pygame.K_u, pygame.K_BACKSPACE):
            self.puzzle.undo()
            self.hint_pos = None
        elif key == pygame.K_r:
            self.load(self.index)
        elif key == pygame.K_h:
            self.hint_pos = self.puzzle.hint()
            self.hint_until = pygame.time.get_ticks() / 1000 + HINT_SECONDS
        elif key in (pygame.K_n, pygame.K_RIGHT) or (key == pygame.K_RETURN and self.puzzle.solved):
            self.go(self.index + 1)
        elif key in (pygame.K_p, pygame.K_LEFT):
            self.go(self.index - 1)
        return True

    # ----- drawing -----------------------------------------------------------------------

    def text(self, font, message: str, colour, pos, anchor: str = "topleft") -> None:
        surface = font.render(message, True, colour)
        rect = surface.get_rect(**{anchor: pos})
        self.screen.blit(surface, rect)

    def draw(self) -> None:
        self.screen.fill(BG)
        self.overlay.fill((0, 0, 0, 0))
        self.draw_hud()
        self.draw_tiles()
        self.draw_beams()
        self.draw_pieces()
        self.screen.blit(self.overlay, (0, 0))
        if self.hint_pos and pygame.time.get_ticks() / 1000 < self.hint_until:
            x, y = self.to_px(*self.hint_pos)
            pygame.draw.rect(self.screen, HINT, (x + 2, y + 2, CELL - 4, CELL - 4), 3, border_radius=8)
        self.text(self.small, HELP, MUTED, (self.size[0] // 2, self.size[1] - FOOTER // 2), "center")
        if self.puzzle.solved:
            self.draw_solved()

    def draw_hud(self) -> None:
        title = f"{self.index + 1}/{len(self.levels)}   {self.level.name}"
        self.text(self.font, title, TEXT, (MARGIN, HUD // 2), "midleft")
        best = self.progress.best.get(self.level.id)
        stats = f"Moves {self.puzzle.moves}    Par {self.level.par or '-'}    Best {best or '-'}"
        right = self.size[0] - MARGIN
        if best is not None:
            earned = stars(best, self.level.par)
            self.draw_stars(earned, (right - 36, HUD // 2), radius=9)
            right -= 84
        self.text(self.font, stats, MUTED, (right, HUD // 2), "midright")

    def draw_stars(self, earned: int, centre: tuple[int, int], radius: int) -> None:
        """A row of MAX_STARS stars centred on ``centre``, the first ``earned`` filled in."""
        gap = radius * 2 + radius // 2
        first_x = centre[0] - gap * (MAX_STARS - 1) // 2
        for i in range(MAX_STARS):
            points = star_points((first_x + i * gap, centre[1]), radius)
            if i < earned:
                pygame.draw.polygon(self.screen, GOLD, points)
            else:
                pygame.draw.polygon(self.screen, STAR_EMPTY, points, 2)

    def draw_tiles(self) -> None:
        for y, row in enumerate(self.level.rows):
            for x, tile in enumerate(row):
                px, py = self.to_px(x, y)
                rect = pygame.Rect(px, py, CELL, CELL)
                if tile == WALL:
                    pygame.draw.rect(self.screen, WALL_FILL, rect)
                    pygame.draw.rect(self.screen, WALL_EDGE, rect.inflate(-6, -6), 2, border_radius=4)
                else:
                    pygame.draw.rect(self.screen, FLOOR, rect)
                    pygame.draw.rect(self.screen, GRID, rect, 1)

    def draw_beams(self) -> None:
        for beam in self.puzzle.result.beams:
            points = [self.to_px(x, y) for x, y in beam]
            if len(points) > 1:
                pygame.draw.lines(self.overlay, BEAM_GLOW, False, points, 14)
                pygame.draw.lines(self.screen, BEAM, False, points, 4)

    def draw_pieces(self) -> None:
        lit = self.puzzle.result.lit
        for x, y in self.level.crystals:
            cx, cy = self.to_px(x + 0.5, y + 0.5)
            r = CELL * 0.3
            diamond = [(cx, cy - r), (cx + r * 0.75, cy), (cx, cy + r), (cx - r * 0.75, cy)]
            if (x, y) in lit:
                pygame.draw.circle(self.overlay, CRYSTAL_GLOW, (cx, cy), CELL * 0.45)
                pygame.draw.polygon(self.screen, CRYSTAL_ON, diamond)
            else:
                pygame.draw.polygon(self.screen, CRYSTAL_OFF, diamond, 3)

        mirrors = [(pos, kind, True) for pos, kind in self.puzzle.mirrors.items()]
        mirrors += [(pos, FIXED[self.level.tile(pos)], False) for pos in self.level.positions(FIXED)]
        for (x, y), kind, movable in mirrors:
            px, py = self.to_px(x, y)
            pad = 10
            if kind == "/":
                a, b = (px + pad, py + CELL - pad), (px + CELL - pad, py + pad)
            else:
                a, b = (px + pad, py + pad), (px + CELL - pad, py + CELL - pad)
            if movable:
                pygame.draw.circle(self.screen, PIVOT, (px + CELL // 2, py + CELL // 2), 9)
            pygame.draw.line(self.screen, MIRROR if movable else MIRROR_FIXED, a, b, 7)
            if not movable:
                for end in (a, b):
                    pygame.draw.circle(self.screen, WALL_EDGE, end, 5)

        for (x, y), (dx, dy) in self.level.emitters:
            cx, cy = self.to_px(x + 0.5, y + 0.5)
            pygame.draw.circle(self.screen, EMITTER, (cx, cy), CELL * 0.3)
            tip = (cx + dx * CELL * 0.42, cy + dy * CELL * 0.42)
            side = (-dy * CELL * 0.16, dx * CELL * 0.16)
            base = (cx + dx * CELL * 0.18, cy + dy * CELL * 0.18)
            pygame.draw.polygon(
                self.screen, GOLD,
                [tip, (base[0] + side[0], base[1] + side[1]), (base[0] - side[0], base[1] - side[1])],
            )

    def draw_solved(self) -> None:
        w, h = 460, 230
        panel = pygame.Rect((self.size[0] - w) // 2, HUD + (self.board_rows * CELL - h) // 2, w, h)
        shade = pygame.Surface(panel.size, pygame.SRCALPHA)
        shade.fill((10, 12, 20, 225))
        self.screen.blit(shade, panel)
        pygame.draw.rect(self.screen, GOLD, panel, 2, border_radius=12)
        cx = panel.centerx
        self.text(self.big, "Solved!", GOLD, (cx, panel.top + 46), "center")
        par = f" (par {self.level.par})" if self.level.par else ""
        line = f"{self.puzzle.moves} moves{par}" + ("   New best!" if self.new_best else "")
        self.text(self.font, line, TEXT, (cx, panel.top + 104), "center")
        self.draw_stars(stars(self.puzzle.moves, self.level.par), (cx, panel.top + 148), radius=16)
        last = self.index == len(self.levels) - 1
        prompt = "You've lit every crystal. Thanks for playing!" if last else "Press Enter for the next level"
        self.text(self.small, prompt, MUTED, (cx, panel.top + 196), "center")

    def run(self) -> None:
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if not self.handle(event):
                    running = False
            self.draw()
            pygame.display.flip()
            clock.tick(FPS)


def star_points(centre: tuple[int, int], radius: float) -> list[tuple[float, float]]:
    """The ten corners of a five-pointed star, point up."""
    cx, cy = centre
    points = []
    for i in range(10):
        r = radius if i % 2 == 0 else radius * 0.45
        angle = math.pi / 2 + i * math.pi / 5
        points.append((cx + r * math.cos(angle), cy - r * math.sin(angle)))
    return points
