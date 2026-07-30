import math
from pathlib import Path

import pygame

FONT_DIR = Path(__file__).resolve().parent / "assets" / "fonts"

FALLBACK_FONTS = ("Inter", "Helvetica Neue", "Avenir Next", "Arial", "DejaVu Sans")

WEIGHTS = {
    "regular": "Inter-Regular.ttf",
    "semibold": "Inter-SemiBold.ttf",
    "bold": "Inter-Bold.ttf",
}

CANVAS = (250, 248, 245)
SURFACE = (255, 254, 252)
BOARD = (163, 149, 137)
BOARD_INNER = (196, 184, 172)
EMPTY_TILE = (186, 173, 161)

INK = (74, 67, 60)
INK_SOFT = (129, 118, 107)
INK_FAINT = (168, 158, 148)
ON_DARK = (252, 250, 248)

ACCENT = (214, 116, 64)
ACCENT_DARK = (191, 98, 50)
ACCENT_SOFT = (247, 234, 225)
STAR = (223, 158, 74)

DIVIDER = (228, 220, 212)
SHADOW = (120, 100, 84)

TILE_COLORS = {
    0: EMPTY_TILE,
    2: (238, 230, 221),
    4: (236, 223, 200),
    8: (240, 180, 126),
    16: (240, 152, 104),
    32: (238, 128, 98),
    64: (233, 100, 66),
    128: (234, 202, 120),
    256: (233, 197, 100),
    512: (232, 191, 80),
    1024: (231, 186, 62),
    2048: (229, 180, 44),
}
BIG_TILE = (60, 56, 50)

CANVAS_COLOR = CANVAS

_font_cache = {}


def font(size, weight="regular"):
    key = (size, weight)
    if key in _font_cache:
        return _font_cache[key]

    pygame.font.init()
    path = FONT_DIR / WEIGHTS.get(weight, WEIGHTS["regular"])

    if path.exists():
        loaded = pygame.font.Font(str(path), size)
    else:
        bold = weight in ("semibold", "bold")
        name = ",".join(FALLBACK_FONTS)
        loaded = pygame.font.SysFont(name, size, bold=bold)

    _font_cache[key] = loaded
    return loaded


def rounded_shadow(surface, rect, radius, layers=((8, 14), (5, 20), (2, 26))):
    for offset, alpha in layers:
        pygame.draw.rect(
            surface,
            (*SHADOW, alpha),
            rect.move(0, offset),
            border_radius=radius,
        )


def blit_center(surface, text_surface, center):
    surface.blit(text_surface, text_surface.get_rect(center=center))


def draw_star(surface, center, radius, color, scale=3):
    inner = radius * 0.42
    size = int(radius * 2 * scale) + 4
    layer = pygame.Surface((size, size), pygame.SRCALPHA)
    mid = size / 2

    points = []
    for index in range(10):
        angle = -math.pi / 2 + index * math.pi / 5
        length = (radius if index % 2 == 0 else inner) * scale
        points.append((mid + math.cos(angle) * length, mid + math.sin(angle) * length))

    pygame.draw.polygon(layer, color, points)
    layer = pygame.transform.smoothscale(layer, (size // scale, size // scale))
    surface.blit(layer, layer.get_rect(center=center))


def draw_spinner(surface, center, radius, color, dots=8, scale=3):
    ticks = pygame.time.get_ticks()
    lead = int(ticks / 90) % dots

    size = int((radius + 4) * 2 * scale)
    layer = pygame.Surface((size, size), pygame.SRCALPHA)
    mid = size / 2

    for index in range(dots):
        angle = -math.pi / 2 + index * (2 * math.pi / dots)
        distance = (index - lead) % dots
        alpha = int(235 * (1 - distance / dots) ** 1.6) + 20
        dot_radius = (2.6 - 1.0 * (distance / dots)) * scale
        x = mid + math.cos(angle) * radius * scale
        y = mid + math.sin(angle) * radius * scale
        pygame.draw.circle(layer, (*color, alpha), (x, y), dot_radius)

    layer = pygame.transform.smoothscale(layer, (size // scale, size // scale))
    surface.blit(layer, layer.get_rect(center=center))


def lerp(color_a, color_b, t):
    return tuple(round(a + (b - a) * t) for a, b in zip(color_a, color_b))
