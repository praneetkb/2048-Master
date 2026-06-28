import numpy as np


def empty_cells(grid):
    empty_cells = []
    for row in range(4):
        for col in range(4):
            if grid[row][col] == 0:
                empty_cells.append((row, col))
    return empty_cells


def chance_node(depth,grid):
    
    cells = empty_cells(grid)
    if depth == 0 or not cells:
        return heuristic(grid)

      
    total = 0.0
    for (r, c) in cells:
        for value, prob in ((2, 0.9), (4, 0.1)):
            child = grid.copy()
            child[r][c] = value
            p = prob / len(cells)
            total += p * max_node(child, depth - 1)
    return total