# This file is responsible for visuals only (board/grid and tiles).
# Team member responsible: João

import pygame


BOARD_SIZE = 4

CANVAS_COLOR = (250, 248, 243)
BOARD_COLOR = (145, 128, 112)
EMPTY_TILE_COLOR = (187, 173, 156)
TEXT_DARK = (105, 94, 82)
TEXT_LIGHT = (249, 246, 242)

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
