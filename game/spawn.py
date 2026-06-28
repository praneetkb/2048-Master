# This file handles random tile generation.
# It is responsible for finding valid empty locations and spawning new tiles on the board at each turn.
# New tiles are generated with a value of either 2 or 4, with a higher probability of spawning a 2.
# Team member responsible: Jayden

import random

def spawn_tile(board):
    empty_cells = board.get_empty_cells()
    if not empty_cells:
        return
    
    row, col = random.choice(empty_cells)
    
    # Spawning probabilities: 2: 0.9, 4: 0.1
    if random.random() < 0.9:
        value = 2
    else:
        value = 4

    board.set_tile(row, col, value)