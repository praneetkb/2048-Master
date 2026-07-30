# Expectimax search agent for 2048.
# Player picks the best move (max node).
# The environment spawns a random tile, 2 (90%) or 4 (10%), on an empty cell (chance node).

# Class Architecture:
# choose_action() --> max_node() --> chance_node() --> evaluate()
# max_node() adds the merge reward earned by each move, then recurses into chance_node().
# evaluate() scores a leaf. With no network it uses a hand-written heuristic; with a
# trained NTupleNetwork it returns the learned afterstate value V(s').
# Every leaf reached by this search is an AFTERSTATE (chance_node returns before spawning),
# which matches what TDTrainer learns.

# There is ONE search here, with two evaluation functions. network=None is the
# heuristic baseline from Milestone 1; network=<trained NTupleNetwork> is the RL
# agent. Both are needed for the report comparison, so they share the code path
# and differ only in evaluate().

import numpy as np

from agents.agent import Agent
from game.game import MOVES
from game.score import points_after_merge


class ExpectimaxAgent(Agent):

    def __init__(self, depth=2, network=None):
        # network: a trained NTupleNetwork, or None to use the hand-written heuristic.

        self.depth = depth
        self.network = network

    # Start the Expectimax search and return the best move
    def choose_action(self, state):
        depth = self._adaptive_depth(state)
        best_action, _ = self.max_node(state, depth)
        return best_action

    def _adaptive_depth(self, state):
        empty = len(empty_cells(state))
        if empty <= 2:
            return self.depth + 1
        return self.depth

    # Returns (best_action, best_value) over all legal moves.
    # Value of a move = immediate merge reward + expected value of the afterstate.
    # The reward term is required: the learned V estimates FUTURE reward only.
    def max_node(self, state, depth):
        if depth <= 0:
            return None, self.evaluate(state)

        best_action = None
        best_value = float("-inf")

        for action, move in MOVES.items():
            new_grid, merged_values, changed = move(state)
            if not changed:  # illegal move, skip
                continue
            value = points_after_merge(merged_values) + self.chance_node(new_grid, depth - 1)
            if value > best_value:
                best_value = value
                best_action = action

        if best_action is None:  # terminal board: no future reward available
            return None, 0.0

        return best_action, best_value

    # Expands random tile spawns and returns the expected value.
    # Returns BEFORE spawning when depth is exhausted, so leaves are afterstates.
    def chance_node(self, state, depth):
        cells = empty_cells(state)

        if depth <= 0 or not cells:
            return self.evaluate(state)

        total = 0.0
        for (row, col) in cells:
            for value, probability in ((2, 0.9), (4, 0.1)):
                child = state.copy()
                child[row, col] = value
                spawn_probability = probability / len(cells)
                _, child_value = self.max_node(child, depth)
                total += spawn_probability * child_value

        return total

    #  Learned value function or the previous heuristic can be used.
    def evaluate(self, state):
        if self.network is not None:
            return self.network.value(state, validate=False)
        empty = len(empty_cells(state))
        max_tile = np.max(state)
        return (100 * empty) + max_tile


# Both earlier names stay valid so in-flight imports keep working.
HeuristicExpectimaxAgent = ExpectimaxAgent
ExpectimaxRLAgent = ExpectimaxAgent


# Helper function to get all empty cells in the grid
def empty_cells(grid):
    empty_cells = []
    for row in range(4):
        for col in range(4):
            if grid[row][col] == 0:
                empty_cells.append((row, col))
    return empty_cells