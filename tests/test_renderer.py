import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import numpy as np
import pygame

from game.board import Board
from ui.renderer import BOARD_COLOR, BoardRenderer


class TestBoardRenderer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_draw_accepts_board_object_and_returns_one_rect_per_cell(self):
        board = Board()
        board.set_tile(0, 0, 2)
        board.set_tile(3, 3, 2048)

        renderer = BoardRenderer(tile_size=40, gap=5, margin=10, font_size=18)
        surface = pygame.Surface((renderer.pixel_size, renderer.pixel_size))

        rects = renderer.draw(surface, board)

        self.assertEqual(len(rects), 16)
        self.assertEqual(rects[0].size, (40, 40))
        self.assertEqual(rects[-1].size, (40, 40))
        self.assertNotEqual(surface.get_at(rects[0].center), surface.get_at(rects[1].center))

    def test_draw_accepts_raw_grid_without_mutating_it(self):
        grid = np.array([
            [0, 2, 4, 8],
            [16, 32, 64, 128],
            [256, 512, 1024, 2048],
            [0, 0, 0, 0],
        ])
        original = grid.copy()

        renderer = BoardRenderer(tile_size=30, gap=4, margin=8, font_size=14)
        surface = pygame.Surface((renderer.pixel_size, renderer.pixel_size))

        renderer.draw(surface, grid, top_left=(0, 0))

        np.testing.assert_array_equal(grid, original)

    def test_gaps_under_filled_tiles_match_board_background(self):
        grid = np.array([
            [8, 2, 0, 4],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ])

        renderer = BoardRenderer(tile_size=40, gap=5, margin=10, font_size=18)
        surface = pygame.Surface((renderer.pixel_size, renderer.pixel_size))

        rects = renderer.draw(surface, grid)
        gap_pixel = surface.get_at((rects[0].centerx, rects[0].bottom + 1))

        self.assertEqual(gap_pixel[:3], BOARD_COLOR)


if __name__ == "__main__":
    unittest.main()
