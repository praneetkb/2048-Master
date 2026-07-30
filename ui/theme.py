from pathlib import Path

import pygame

FONT_DIR = Path(__file__).resolve().parent / "assets" / "fonts"

FALLBACK_FONTS = ("Inter", "Helvetica Neue", "Avenir Next", "Arial", "DejaVu Sans")

WEIGHTS = {
    "regular": "Inter-Regular.ttf",
    "medium": "Inter-Medium.ttf",
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

ACCENT = (226, 155, 112)
ACCENT_DARK = (210, 136, 92)
ACCENT_SOFT = (247, 236, 228)

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


def lerp(color_a, color_b, t):
    return tuple(round(a + (b - a) * t) for a, b in zip(color_a, color_b))
