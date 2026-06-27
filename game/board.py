# This file handles board creation and representation.
# It is responsible for initializing, resetting, and displaying the game board.
# Team member responsible: Zenith
import numpy as np

# Represents the 4x4 game board and the tiles on it.
class Board:

    # Creates a new, empty board: a 4x4 grid of zeros (ints).
    def __init__(self):
        self.grid = np.zeros((4,4), dtype=int)

    # Clears the board back to all zeros (empty), reusing the same grid.
    def reset(self):
        self.grid[:] = 0

    # Prints the board in a readable way for debugging.
    def display_board(self):
        for row in self.grid:
            line = ""
            for value in row:
                if value == 0:
                    cell = " "
                else:
                    cell = str(value)
                line += f"{cell:>6}"
            print(line)

    # Returns a list of (row, col) positions of every empty cell.
    def get_empty_cells(self):
        empty_cells = []
        for row in range(4):
            for col in range(4):
                if self.grid[row][col] == 0:
                    empty_cells.append((row, col))
        return empty_cells

    # Returns True if the board has no empty cells left, False otherwise.
    def is_full(self):
        return len(self.get_empty_cells()) == 0

    # Returns a deep copy of this board (independent grid).
    def copy(self):
        new_board = Board()
        new_board.grid = self.grid.copy()
        return new_board

    # Sets the tile value at (row, col).
    def set_tile(self, row, col, value):
        self.grid[row][col] = value

    # Returns the tile value at (row, col).
    def get_tile(self, row, col):
        return self.grid[row][col]
