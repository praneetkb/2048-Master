# This file is responsible for visuals only (board, tiles, header, menu).
# Team members responsible: João and Praneet

import pygame

from ui.theme import (
    ACCENT,
    ACCENT_DARK,
    ACCENT_SOFT,
    BIG_TILE,
    BOARD,
    CANVAS,
    CANVAS_COLOR,
    DIVIDER,
    EMPTY_TILE,
    INK,
    INK_FAINT,
    INK_SOFT,
    ON_DARK,
    STAR,
    SURFACE,
    TILE_COLORS,
    blit_center,
    draw_spinner,
    draw_star,
    font,
    lerp,
    rounded_shadow,
)

BOARD_SIZE = 4

TEXT_DARK = INK
TEXT_LIGHT = ON_DARK
HEADER_TEXT = INK_SOFT
BOARD_COLOR = BOARD
EMPTY_TILE_COLOR = EMPTY_TILE


class BoardRenderer:
    # Draws a 4x4 2048 board onto an existing pygame surface.

    # Stores renderer settings and caches loaded fonts.
    def __init__(
        self,
        tile_size=111,
        gap=12,
        margin=12,
        font_size=48,
        board_radius=16,
        tile_radius=8,
        scale=2,
    ):
        self.tile_size = tile_size
        self.gap = gap
        self.margin = margin
        self.font_size = font_size
        self.board_radius = board_radius
        self.tile_radius = tile_radius
        self.scale = scale

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

        color = TILE_COLORS.get(value, BIG_TILE)
        pygame.draw.rect(surface, color, rect, border_radius=self.tile_radius)
        self._draw_text(surface, rect, value)

    # Draws board, shadow, and tile backgrounds on a smooth layer.
    def _draw_board_shapes(self, surface, grid, top_left):
        scale = max(1, int(self.scale))
        pad = 14
        layer_size = (self.pixel_size + 2 * pad, self.pixel_size + 2 * pad)
        layer = pygame.Surface((layer_size[0] * scale, layer_size[1] * scale), pygame.SRCALPHA)
        origin = (pad, pad)

        board_rect = self._scale_rect(
            pygame.Rect(origin[0], origin[1], self.pixel_size, self.pixel_size), scale
        )
        rounded_shadow(
            layer,
            board_rect,
            self.board_radius * scale,
            layers=((10 * scale, 16), (6 * scale, 22), (3 * scale, 28)),
        )
        pygame.draw.rect(layer, BOARD, board_rect, border_radius=self.board_radius * scale)

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                value = int(grid[row][col])
                rect = self._scale_rect(self._tile_rect(origin, row, col), scale)
                color = TILE_COLORS.get(value, BIG_TILE)
                pygame.draw.rect(layer, color, rect, border_radius=self.tile_radius * scale)

        if scale > 1:
            layer = pygame.transform.smoothscale(layer, layer_size)

        surface.blit(layer, (top_left[0] - pad, top_left[1] - pad))

    # Draws the centered number for non-empty tiles.
    def _draw_text(self, surface, rect, value):
        if value == 0:
            return

        color = INK if value <= 4 else ON_DARK
        text = self._font_for(value).render(str(value), True, color)
        surface.blit(text, text.get_rect(center=(rect.centerx, rect.centery - 1)))

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
        digits = len(str(value))
        if digits >= 5:
            size = int(self.font_size * 0.56)
        elif digits == 4:
            size = int(self.font_size * 0.68)
        elif digits == 3:
            size = int(self.font_size * 0.80)
        else:
            size = self.font_size
        return font(size, "bold")

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

    HEIGHT = 84
    BOX_WIDTH = 104
    BOX_HEIGHT = 58
    BUTTON_WIDTH = 96

    def __init__(self, agent_label=None):
        self.agent_label = agent_label

    def draw(self, surface, score, best_score, left=24, top=22, right_margin=24):
        right = surface.get_width() - right_margin

        if self.agent_label:
            tag = font(13, "semibold").render(self.agent_label.upper(), True, ACCENT_DARK)
            tag_rect = tag.get_rect()
            pill = pygame.Rect(0, 0, tag_rect.width + 20, tag_rect.height + 10)
            pill.midleft = (left, top + self.BOX_HEIGHT // 2)
            pygame.draw.rect(surface, ACCENT_SOFT, pill, border_radius=pill.height // 2)
            blit_center(surface, tag, pill.center)

        # Restart button
        restart = pygame.Rect(0, 0, self.BUTTON_WIDTH, self.BOX_HEIGHT)
        restart.topright = (right, top)
        pygame.draw.rect(surface, ACCENT, restart, border_radius=10)
        blit_center(
            surface,
            font(14, "semibold").render("Restart", True, ON_DARK),
            restart.center,
        )

        # Best score box
        best_box = pygame.Rect(0, 0, self.BOX_WIDTH, self.BOX_HEIGHT)
        best_box.topright = (restart.left - 10, top)
        self._score_box(surface, best_box, "BEST", best_score)

        # Score box
        score_box = pygame.Rect(0, 0, self.BOX_WIDTH, self.BOX_HEIGHT)
        score_box.topright = (best_box.left - 10, top)
        self._score_box(surface, score_box, "SCORE", score)

        # Return rectangle so the game loop can detect mouse clicks later
        return restart

    def _score_box(self, surface, box, label, value):
        pygame.draw.rect(surface, SURFACE, box, border_radius=10)
        pygame.draw.rect(surface, DIVIDER, box, width=1, border_radius=10)

        blit_center(
            surface,
            font(11, "semibold").render(label, True, INK_FAINT),
            (box.centerx, box.y + 17),
        )
        blit_center(
            surface,
            font(21, "bold").render(f"{value:,}", True, INK),
            (box.centerx, box.y + 39),
        )


# Draws the start menu where the user selects which agent to run
class MenuRenderer:

    OPTIONS = (
        ("Random Agent", "Picks a legal move at random"),
        ("Expectimax", "Hand-written heuristic evaluation"),
        ("Expectimax + TD Learning", "Learned N-tuple value function"),
        ("Compare Performance", "Benchmark all three agents"),
    )

    PRIMARY = 2

    BUTTON_WIDTH = 440
    BUTTON_HEIGHT = 72
    BUTTON_GAP = 12
    TOP = 208

    def draw(self, surface, hovered_index=None):
        surface.fill(CANVAS)
        width = surface.get_width()
        center_x = width // 2

        title = font(46, "bold").render("2048", True, INK)
        surface.blit(title, title.get_rect(center=(center_x, 96)))

        subtitle = font(16, "regular").render(
            "Watch an agent play", True, INK_SOFT
        )
        surface.blit(subtitle, subtitle.get_rect(center=(center_x, 134)))

        rects = []
        for index, (label, description) in enumerate(self.OPTIONS):
            rect = pygame.Rect(0, 0, self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
            rect.centerx = center_x
            rect.y = self.TOP + index * (self.BUTTON_HEIGHT + self.BUTTON_GAP)
            rects.append(rect)
            self._draw_button(
                surface,
                rect,
                number=index + 1,
                label=label,
                description=description,
                primary=(index == self.PRIMARY),
                hovered=(index == hovered_index),
            )

        hint_y = rects[-1].bottom + 30
        keys = ", ".join(str(i + 1) for i in range(len(self.OPTIONS)))
        hint = font(13, "regular").render(f"Click, or press {keys}", True, INK_FAINT)
        surface.blit(hint, hint.get_rect(center=(center_x, hint_y)))

        return rects

    def _draw_button(self, surface, rect, number, label, description, primary, hovered):
        if hovered:
            fill = ACCENT
            label_color = ON_DARK
            desc_color = lerp(ACCENT, ON_DARK, 0.78)
            badge_fill, badge_text = lerp(ACCENT, ON_DARK, 0.24), ON_DARK
            border = None
        else:
            fill = SURFACE
            label_color = INK
            desc_color = INK_SOFT
            badge_fill, badge_text = lerp(CANVAS, INK_FAINT, 0.22), INK_SOFT
            border = DIVIDER

        pygame.draw.rect(surface, fill, rect, border_radius=12)
        if border:
            pygame.draw.rect(surface, border, rect, width=1, border_radius=12)

        badge = pygame.Rect(0, 0, 30, 30)
        badge.center = (rect.left + 34, rect.centery)
        pygame.draw.rect(surface, badge_fill, badge, border_radius=8)
        blit_center(
            surface,
            font(14, "semibold").render(str(number), True, badge_text),
            badge.center,
        )

        text_x = rect.left + 62
        label_surf = font(17, "semibold").render(label, True, label_color)
        desc_surf = font(12, "regular").render(description, True, desc_color)

        label_rect = label_surf.get_rect(midleft=(text_x, rect.centery - 10))
        surface.blit(label_surf, label_rect)
        surface.blit(desc_surf, desc_surf.get_rect(midleft=(text_x, rect.centery + 12)))

        if primary:
            star_color = ON_DARK if hovered else STAR
            draw_star(surface, (label_rect.right + 15, label_rect.centery), 7, star_color)


class ComparisonRenderer:

    COLUMNS = (
        ("Agent", "name", 0.30, "left"),
        ("Runs", "Runs", 0.13, "right"),
        ("Avg Score", "Average Score", 0.19, "right"),
        ("Best Score", "Best Score", 0.19, "right"),
        ("Best Tile", "Highest Tile", 0.19, "right"),
    )

    AGENT_ORDER = ("Random", "Expectimax", "Expectimax + RL")

    def draw(self, screen, results, running=False, progress=None):
        screen.fill(CANVAS)
        width = screen.get_width()
        margin = 34
        table_width = width - 2 * margin

        title = font(28, "bold").render("Agent Comparison", True, INK)
        screen.blit(title, (margin, 40))

        if running:
            draw_spinner(
                screen,
                (margin + title.get_width() + 26, 40 + title.get_height() // 2),
                9,
                ACCENT,
            )

        if running and progress and progress.get("name"):
            played = progress.get("played", 0)
            total = progress.get("total", 0)
            note = f"Playing {progress['name']}, game {played} of {total}"
        elif running:
            note = "Starting benchmark..."
        else:
            note = "Average over the same number of games for each agent"
        screen.blit(font(13, "regular").render(note, True, INK_SOFT), (margin, 78))

        edges = []
        cursor = margin
        for _, _, fraction, _ in self.COLUMNS:
            span = table_width * fraction
            edges.append((cursor, span))
            cursor += span

        header_y = 128
        for (label, _, _, align), (x, span) in zip(self.COLUMNS, edges):
            surf = font(12, "semibold").render(label.upper(), True, INK_FAINT)
            rect = surf.get_rect()
            if align == "right":
                rect.midright = (x + span - 10, header_y)
            else:
                rect.midleft = (x, header_y)
            screen.blit(surf, rect)

        pygame.draw.line(
            screen, DIVIDER, (margin, header_y + 18), (margin + table_width, header_y + 18)
        )

        rows = list(results.items())

        # Show every agent up front, so the table has a visible shape from the
        # first frame and finished agents appear as soon as they are done.
        pending = [name for name in self.AGENT_ORDER if name not in results]
        if not running:
            pending = []

        best_name = (
            max(results, key=lambda name: results[name]["Average Score"])
            if results
            else None
        )

        row_height = 54
        y = header_y + 18

        for name, stats in rows:
            self._row(screen, name, stats, margin, table_width, edges, y, row_height,
                      is_best=(name == best_name and not running))
            y += row_height
            pygame.draw.line(screen, DIVIDER, (margin, y), (margin + table_width, y))

        for name in pending:
            active = bool(progress) and progress.get("name") == name
            self._pending_row(screen, name, margin, table_width, edges, y, row_height,
                              active=active, progress=progress if active else None)
            y += row_height
            if name != pending[-1]:
                pygame.draw.line(screen, DIVIDER, (margin, y), (margin + table_width, y))

        self._footer(screen, width)

    def _row(self, screen, name, stats, margin, table_width, edges, y, row_height, is_best):
        row = pygame.Rect(margin - 10, y, table_width + 20, row_height)

        if is_best:
            pygame.draw.rect(screen, ACCENT_SOFT, row, border_radius=8)

        values = {"name": name, **stats}
        for (_, key, _, align), (x, span) in zip(self.COLUMNS, edges):
            raw = values.get(key, "")
            text = f"{raw:,}" if isinstance(raw, (int, float)) else str(raw)
            weight = "semibold" if is_best else "regular"
            color = INK if is_best else INK_SOFT
            surf = font(15, weight).render(text, True, color)
            rect = surf.get_rect()
            if align == "right":
                rect.midright = (x + span - 10, row.centery)
            else:
                rect.midleft = (x, row.centery)
            screen.blit(surf, rect)

    def _pending_row(self, screen, name, margin, table_width, edges, y, row_height,
                     active, progress):
        row = pygame.Rect(margin - 10, y, table_width + 20, row_height)
        name_x, _ = edges[0]

        color = INK_SOFT if active else INK_FAINT
        weight = "semibold" if active else "regular"
        surf = font(15, weight).render(name, True, color)
        screen.blit(surf, surf.get_rect(midleft=(name_x, row.centery)))

        if active and progress:
            played = progress.get("played", 0)
            total = progress.get("total", 1)
            status = f"game {played} of {total}"
        else:
            status = "waiting"

        status_surf = font(13, "regular").render(status, True, INK_FAINT)
        second_x, second_span = edges[1]
        screen.blit(status_surf, status_surf.get_rect(midleft=(second_x, row.centery)))

        if active and progress:
            total = max(1, progress.get("total", 1))
            fraction = progress.get("played", 0) / total
            bar_x, bar_span = edges[2]
            bar_width = table_width - (bar_x - margin) - 10
            track = pygame.Rect(bar_x, row.centery - 3, bar_width, 6)
            pygame.draw.rect(screen, DIVIDER, track, border_radius=3)
            if fraction > 0:
                fill = pygame.Rect(track.x, track.y, int(track.width * fraction), track.height)
                pygame.draw.rect(screen, ACCENT, fill, border_radius=3)

    def _footer(self, screen, width):
        hint = font(13, "regular").render("Press Esc to return to the menu", True, INK_FAINT)
        screen.blit(hint, hint.get_rect(center=(width // 2, screen.get_height() - 38)))
