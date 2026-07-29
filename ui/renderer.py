# This file is responsible for visuals only (board, tiles, header, menu).
# Team members responsible: João and Praneet

import pygame


BOARD_SIZE = 4

CANVAS_COLOR = (250, 248, 243)
BOARD_COLOR = (145, 128, 112)
EMPTY_TILE_COLOR = (187, 173, 156)
TEXT_DARK = (105, 94, 82)
TEXT_LIGHT = (249, 246, 242)

HEADER_TEXT = (119, 110, 101)
HEADER_BOX = (187, 173, 160)
BUTTON_COLOR = (143, 122, 102)
BUTTON_TEXT = (255, 255, 255)

TILE_COLORS = {
    0: EMPTY_TILE_COLOR,
    2: (238, 228, 218),
    4: (237, 221, 190),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
}
LARGE_TILE_COLOR = (60, 58, 50)

BOARD_SHADOW_COLOR = (75, 55, 40)
FONT_CANDIDATES = ("Clear Sans", "Helvetica Neue", "Avenir Next", "Arial", "DejaVu Sans")


class BoardRenderer:
    # Draws a 4x4 2048 board onto an existing pygame surface.

    # Stores renderer settings and caches loaded fonts.
    def __init__(
        self,
        tile_size=111,
        gap=10,
        margin=10,
        font_size=50,
        font_name=None,
        board_radius=22,
        tile_radius=10,
        scale=2,
    ):
        self.tile_size = tile_size
        self.gap = gap
        self.margin = margin
        self.font_size = font_size
        self.font_name = font_name
        self.board_radius = board_radius
        self.tile_radius = tile_radius
        self.scale = scale
        self._fonts = {}
        self._font_path = None

    # Returns the total board width/height in pixels.
    @property
    def pixel_size(self):
        return (self.margin * 2) + (self.tile_size * BOARD_SIZE) + (self.gap * (BOARD_SIZE - 1))

    # Draws the board and returns the tile rectangles.
    def draw(self, surface, board, top_left=(0, 0)):
        grid = self._grid_from(board)
        self._draw_board_shapes(surface, grid, top_left)

        rects = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                value = int(grid[row][col])
                rect = self._tile_rect(top_left, row, col)
                self._draw_text(surface, rect, value)
                rects.append(rect)

        return rects

    def draw_frame(self, surface, tiles, top_left=(0, 0)):
        self._draw_empty_background(surface, top_left)
        for tile in tiles:
            self._draw_floating_tile(surface, tile, top_left)

    def _draw_empty_background(self, surface, top_left):
        empty_grid = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self._draw_board_shapes(surface, empty_grid, top_left)

    def _draw_floating_tile(self, surface, tile, top_left):
        value = tile["value"]
        if value == 0:
            return

        base_rect = self._tile_rect(top_left, tile["row"], tile["col"])
        scale_factor = tile.get("scale", 1.0)

        if scale_factor != 1.0:
            w = max(1, int(base_rect.width * scale_factor))
            h = max(1, int(base_rect.height * scale_factor))
            rect = pygame.Rect(0, 0, w, h)
            rect.center = base_rect.center
        else:
            rect = base_rect

        color = TILE_COLORS.get(value, LARGE_TILE_COLOR)
        pygame.draw.rect(surface, color, rect, border_radius=self.tile_radius)
        self._draw_text(surface, rect, value)

    # Draws board, shadow, and tile backgrounds on a smooth layer.
    def _draw_board_shapes(self, surface, grid, top_left):
        scale = max(1, int(self.scale))
        shadow_margin = 10
        layer_size = (self.pixel_size + 2 * shadow_margin, self.pixel_size + 2 * shadow_margin)
        layer = pygame.Surface((layer_size[0] * scale, layer_size[1] * scale), pygame.SRCALPHA)
        origin = (shadow_margin, shadow_margin)

        board_rect = self._scale_rect(pygame.Rect(origin[0], origin[1], self.pixel_size, self.pixel_size), scale)
        self._draw_soft_shadow(layer, board_rect, self.board_radius * scale, scale)
        pygame.draw.rect(layer, BOARD_COLOR, board_rect, border_radius=self.board_radius * scale)

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                value = int(grid[row][col])
                rect = self._tile_rect(origin, row, col)
                self._draw_tile_shape(layer, rect, value, scale)

        if scale > 1:
            layer = pygame.transform.smoothscale(layer, layer_size)

        surface.blit(layer, (top_left[0] - shadow_margin, top_left[1] - shadow_margin))

    # Draws a subtle layered shadow behind the board.
    def _draw_soft_shadow(self, surface, rect, radius, scale):
        for offset, alpha in ((7, 18), (5, 24), (3, 32)):
            shadow = rect.move(0, offset * scale)
            color = (*BOARD_SHADOW_COLOR, alpha)
            pygame.draw.rect(surface, color, shadow, border_radius=radius)

    # Draws one rounded tile with the color for its value.
    def _draw_tile_shape(self, surface, rect, value, scale):
        scaled_rect = self._scale_rect(rect, scale)
        color = TILE_COLORS.get(value, LARGE_TILE_COLOR)
        pygame.draw.rect(surface, color, scaled_rect, border_radius=self.tile_radius * scale)

    # Draws the centered number for non-empty tiles.
    def _draw_text(self, surface, rect, value):
        if value == 0:
            return

        text_color = TEXT_DARK if value <= 4 else TEXT_LIGHT
        text = self._font_for(value).render(str(value), True, text_color)
        text_rect = text.get_rect(center=(rect.centerx, rect.centery - 2))
        surface.blit(text, text_rect)

    # Calculates the screen rectangle for one tile position.
    def _tile_rect(self, top_left, row, col):
        x = top_left[0] + self.margin + col * (self.tile_size + self.gap)
        y = top_left[1] + self.margin + row * (self.tile_size + self.gap)
        return pygame.Rect(x, y, self.tile_size, self.tile_size)

    # Multiplies a rectangle by the antialiasing scale.
    def _scale_rect(self, rect, scale):
        return pygame.Rect(rect.x * scale, rect.y * scale, rect.w * scale, rect.h * scale)

    # Chooses and caches a font size that fits the tile value.
    def _font_for(self, value):
        pygame.font.init()
        digits = len(str(value))

        if digits >= 5:
            size = int(self.font_size * 0.58)
        elif digits == 4:
            size = int(self.font_size * 0.70)
        elif digits == 3:
            size = int(self.font_size * 0.82)
        else:
            size = self.font_size

        if size not in self._fonts:
            self._fonts[size] = self._load_font(size)

        return self._fonts[size]

    # Loads the preferred font at the requested size.
    def _load_font(self, size):
        font_path = self._resolved_font_path()
        if font_path:
            font = pygame.font.Font(font_path, size)
        else:
            font = pygame.font.SysFont(None, size, bold=True)
        font.set_bold(True)
        return font

    # Finds the first available font from the preferred list.
    def _resolved_font_path(self):
        if self._font_path is not None:
            return self._font_path

        names = (self.font_name,) if self.font_name else FONT_CANDIDATES
        for name in names:
            path = pygame.font.match_font(name, bold=True)
            if path:
                self._font_path = path
                return self._font_path

        self._font_path = ""
        return None

    # Accepts either a Board object or a raw 4x4 grid.
    def _grid_from(self, board):
        grid = getattr(board, "grid", board)
        shape = getattr(grid, "shape", None)

        if shape is not None:
            if tuple(shape) != (BOARD_SIZE, BOARD_SIZE):
                raise ValueError("BoardRenderer expects a 4x4 grid.")
            return grid

        if len(grid) != BOARD_SIZE or any(len(row) != BOARD_SIZE for row in grid):
            raise ValueError("BoardRenderer expects a 4x4 grid.")

        return grid


# Header display above the board - game title, score, best score, and restart button
class HeaderRenderer:

    def __init__(self):
        pygame.font.init()

        self.title_font = pygame.font.SysFont("Arial", 42, bold=True)
        self.label_font = pygame.font.SysFont("Arial", 16, bold=True)
        self.score_font = pygame.font.SysFont("Arial", 22, bold=True)

    def draw(self, surface, score, best_score):

        # Game title 
        title = self.title_font.render("2048 Master", True, HEADER_TEXT)
        surface.blit(title, (20, 20))

        # Score box
        self._draw_score_box(
            surface,
            x=300,
            y=15,
            label="SCORE",
            value=score
        )

        # Best score box 
        self._draw_score_box(
            surface,
            x=410,
            y=15,
            label="BEST",
            value=best_score
        )

        # Restart button 
        restart_rect = pygame.Rect(530, 15, 120, 60)

        pygame.draw.rect(
            surface,
            BUTTON_COLOR,
            restart_rect,
            border_radius=8
        )

        text = self.label_font.render("Restart", True, BUTTON_TEXT)

        text_rect = text.get_rect(center=restart_rect.center)

        surface.blit(text, text_rect)

        # Return rectangle so the game loop can detect mouse clicks later
        return restart_rect
    
    def _draw_score_box(self, surface, x, y, label, value):

        box = pygame.Rect(x, y, 95, 60)

        pygame.draw.rect(
            surface,
            HEADER_BOX,
            box,
            border_radius=8
        )

        label_text = self.label_font.render(label, True, BUTTON_TEXT)

        value_text = self.score_font.render(str(value), True, BUTTON_TEXT)

        surface.blit(
            label_text,
            label_text.get_rect(center=(box.centerx, box.y + 16))
        )

        surface.blit(
            value_text,
            value_text.get_rect(center=(box.centerx, box.y + 42))
        )


# Draws the start menu where the user selects which agent to run
class MenuRenderer:

    OPTIONS = (
        "Random Agent",
        "Expectimax (Heuristic)",
        "Expectimax + TD Learning",
    )

    BUTTON_WIDTH = 420
    BUTTON_HEIGHT = 78
    BUTTON_GAP = 20
    FIRST_BUTTON_Y = 240

    def __init__(self):
        pygame.font.init()

        self.title_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.subtitle_font = pygame.font.SysFont("Arial", 18)
        self.option_font = pygame.font.SysFont("Arial", 23, bold=True)
        self.badge_font = pygame.font.SysFont("Arial", 22, bold=True)
        self.hint_font = pygame.font.SysFont("Arial", 15)

    def draw(self, surface, hovered_index=None):
        surface.fill(CANVAS_COLOR)
        width = surface.get_width()

        title = self.title_font.render("2048 Master", True, HEADER_TEXT)
        surface.blit(title, title.get_rect(center=(width // 2, 100)))

        subtitle = self.subtitle_font.render(
            "Watch an AI agent play", True, TEXT_DARK
        )
        surface.blit(subtitle, subtitle.get_rect(center=(width // 2, 150)))

        rects = []
        for index, label in enumerate(self.OPTIONS):
            rect = pygame.Rect(0, 0, self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
            rect.centerx = width // 2
            rect.y = self.FIRST_BUTTON_Y + index * (self.BUTTON_HEIGHT + self.BUTTON_GAP)
            rects.append(rect)

            self._draw_button(
                surface,
                rect,
                number=index + 1,
                label=label,
                hovered=(index == hovered_index),
            )

        hint_y = self.FIRST_BUTTON_Y + len(self.OPTIONS) * (self.BUTTON_HEIGHT + self.BUTTON_GAP) + 6
        keys = ", ".join(str(index + 1) for index in range(len(self.OPTIONS)))
        hint = self.hint_font.render(f"Click an option, or press {keys}", True, HEADER_TEXT)
        surface.blit(hint, hint.get_rect(center=(width // 2, hint_y)))

        return rects

    def _draw_button(self, surface, rect, number, label, hovered):
        if hovered:
            fill, text_color = BUTTON_COLOR, BUTTON_TEXT
        else:
            fill, text_color = HEADER_BOX, BUTTON_TEXT

        pygame.draw.rect(surface, fill, rect, border_radius=14)

        badge_rect = pygame.Rect(0, 0, 44, 44)
        badge_rect.center = (rect.left + 44, rect.centery)
        pygame.draw.rect(surface, CANVAS_COLOR, badge_rect, border_radius=10)
        badge = self.badge_font.render(str(number), True, TEXT_DARK)
        surface.blit(badge, badge.get_rect(center=badge_rect.center))

        label_surf = self.option_font.render(label, True, text_color)
        surface.blit(label_surf, label_surf.get_rect(midleft=(rect.left + 82, rect.centery)))