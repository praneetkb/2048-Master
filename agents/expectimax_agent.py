# Expectimax search agent for 2048.
# Player picks the best move (max node). 
# The environment spawns a random tile, 2 (90%) or 4 (10%), on an empty cell (chance node).

# Class Architecture: 
# choose_action() --> max_node() --> chance_node() --> evaluate() 
# choose_action() is called by the game to get the next move (it simply starts the expectimax search).
# evaluate() is called when the search reaches a leaf node (depth reached or no moves left). It returns number of empty cells and max tile value.
# Depth is how many moves ahead the agent looks. We set it to 2 for a good balance between performance and speed.


import numpy as np
import random

from agents.agent import Agent
from game.game import MOVES


class ExpectimaxAgent(Agent):

    def __init__(self, depth=2):
        self.depth = depth

    # Start the Expectimax search and return the best move
    def choose_action(self, state):
        best_action, _ = self.max_node(state, self.depth)

        return best_action
    

    # Returns (best_action, best_value) over all legal moves.
    # Depth is decremented here, on the max->chance step.
    # Base cases (depth exhausted, or no legal move) return (None, evaluate).
    def max_node(self, state, depth):
        if depth <= 0:
            return None, self.evaluate(state)
        
        if not any(move(state)[2] for move in MOVES.values()): # No moves left
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
    

    # Simulates all possible random tile spawns and returns the expected value. 
    # Passes depth through to max_node
    # unchanged (max_node already decremented it).
    def chance_node(self, state, depth):

        cells = empty_cells(state)

        # Search stops if maximum depth is reached or no empty cells left
        if depth <= 0 or not cells:
            return self.evaluate(state)
        
        # Randomly sample a subset of empty cells to reduce branching factor and speed up the search
        samples = random.sample(cells, min(10, len(cells)))

        total = 0.0

        # Tries spawning a 2 and a 4 in every empty cell
        for (row, col) in samples:

            for value, probability in ((2, 0.9), (4, 0.1)):

                child = state.copy()
                child[row][col] = value

                # Every empty cell is equally likely
                spawn_probability = probability / len(samples)

                # max_node returns (best_action, best_value)
                _, child_value = self.max_node(child, depth)

                total += spawn_probability * child_value

        return total
    

    # Heuristic evaluation function
    # Boards with more empty cells and larger maximum tile values get a higher score
    def evaluate(self, state):
        empty = len(empty_cells(state))
        max_tile = np.max(state)

        # Giving empty cells more weight encourages the agent to keep space open
        score = (100 * empty) + max_tile

        return score
    

# Helper function to get all empty cells in the grid
def empty_cells(grid):
    empty_cells = []
    for row in range(4):
        for col in range(4):
            if grid[row][col] == 0:
                empty_cells.append((row, col))
    return empty_cells