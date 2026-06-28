# Expectimax search agent for 2048.
# Player picks the best move (max node); the environment spawns a random
# tile, 2 (90%) or 4 (10%), on an empty cell (chance node).

import numpy as np

from game.movement import move_left, move_right, move_up, move_down

# action name -> movement fn. Each fn takes a raw 4x4 grid and returns
# (new_grid, merged_values, changed).
MOVES = {
    "left": move_left,
    "right": move_right,
    "up": move_up,
    "down": move_down,
}


class ExpectimaxAgent:

    def __init__(self, depth=3):
        self.depth = depth

    # Returns (best_action, best_value) over all legal moves.
    # Depth is decremented here, on the max->chance step.
    # Base cases (depth exhausted, or no legal move) return (None, evaluate).
    def max_node(self, state, depth):
        if depth == 0:
            return None, self.evaluate(state)

        best_action = None
        best_value = float("-inf")
        any_legal = False

        for action, move in MOVES.items():
            new_grid, _merged_values, changed = move(state)
            if not changed:  # illegal move, skip
                continue
            any_legal = True
            value = self.chance_node(new_grid, depth-1)
            if value > best_value:
                best_value = value
                best_action = action

        if not any_legal:  # terminal board
            return None, self.evaluate(state)

        return best_action, best_value

    # Expected value over all possible spawns. Passes depth through to max_node
    # unchanged (max_node already decremented it).
    def chance_node(self, state, depth):
        raise NotImplementedError

    # Heuristic score for a leaf/terminal board.
    def evaluate(self, state):
        raise NotImplementedError

    # Returns the best action name for the current state.
    def choose_action(self, state):
        raise NotImplementedError
