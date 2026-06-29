# This file connects the overall game logic and initializes the game.
# It manages game state and connects the board, movement, spawning, and scoring components.
# Team member responsible: Ryan


from game.movement import move_left, move_right, move_up, move_down
from game.score import points_after_merge

from game.board import Board

from game.spawn import spawn_tile

MOVES = {

    "left": move_left, "right": move_right, "up": move_up, "down": move_down,

}


class Game:

    def __init__(self, size=4):
        self.board = Board()
        self.score = 0
        
        # This spawns 2 random tiles
        spawn_tile(self.board)
        spawn_tile(self.board)
 
        
    def move(self, direction):
        new_grid, merged_values, changed = MOVES[direction](self.board.grid)
        if changed:
            self.board.grid = new_grid
            self.score += points_after_merge(merged_values)
            spawn_tile(self.board)
        return changed


    def is_game_over(self):
        # Game over when no moves can change board
        for move in MOVES.values():
            _, _, changed = move(self.board.grid)
            if changed:
                return False
        return True
