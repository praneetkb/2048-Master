# This file handles tile movement and merge logic.
# It is responsible for moving tiles in all four directions and applying merge rules.
# Team member responsible: Praneet

import numpy as np

# Helper: Slides all non-zero tiles to the left without merging them
# row: An array representing a row of tiles
def slide_row_left(row):

    # Keep only non-zero tiles
    non_zero_tiles = row[row != 0]

    # Create a new empty row
    new_row = np.zeros(len(row), dtype=int)

    # Place all non-zero tiles at the beginning of the row
    new_row[:len(non_zero_tiles)] = non_zero_tiles

    return new_row


# Helper: Merges tiles in a row from left to right
# Only merges tiles of the same value and ensures that each tile can only merge once per move
def merge_row_left(row):

    merged_values = [] # Values created from merges (used for overall game score)
    changed = False # Flag to indicate if any merges happened

    new_row = row.copy()

    i = 0

    while i < len(new_row) - 1: 

        # If two adjacent tiles are non-zero and equal, merge them
        if new_row[i] != 0 and new_row[i] == new_row[i + 1]:

            new_row[i] = new_row[i] * 2
            new_row[i + 1] = 0

            # Store merged value
            merged_values.append(new_row[i])

            changed = True

            # Skip next tile (to prevent double merging)
            i += 2
        else:
            i += 1

    return new_row, merged_values, changed


# Performs a full LEFT move on a single row (slide + merge + slide)
def move_row_left(row):

    # Step 1: slide
    slid_row = slide_row_left(row)

    # Step 2: merge
    merged_row, merged_values, merged_changed = merge_row_left(slid_row)

    # Step 3: slide again (to remove gaps after merge)
    final_row = slide_row_left(merged_row)

    # Check if any changes occurred (either from sliding or merging)
    changed = not np.array_equal(row, final_row) or merged_changed

    return final_row, merged_values, changed


# Performs a full LEFT move on the entire board
# It applies row-based movement to every row
def move_left(board):

    new_board = np.zeros_like(board)
    all_merged_values = []
    changed = False

    for i in range(board.shape[0]):
        new_row, merged_values, row_changed = move_row_left(board[i])

        new_board[i] = new_row
        all_merged_values.extend(merged_values)

        if row_changed:
            changed = True

    return new_board, all_merged_values, changed


# Reusing LEFT movement logic for other movements: RIGHT, UP, DOWN
# This maintains consistency, avoids code duplication and easier to debug later

# Performs a full RIGHT move on the entire board
def move_right(board): 
    
    # Step 1: reverse each row
    reversed_board = np.array([row[::-1] for row in board])

    # Step 2: apply left move logic on reversed board
    moved_board, merged_values, changed = move_left(reversed_board)

    # Step 3: reverse back
    final_board = np.array([row[::-1] for row in moved_board])

    return final_board, merged_values, changed


# Performs a full UP move on the entire board
def move_up(board):

    # Step 1: transpose 
    transposed_board = board.T

    # Step 2: apply left move on transposed board
    moved_board, merged_values, changed = move_left(transposed_board)

    # Step 3: transpose back to original 
    final_board = moved_board.T

    return final_board, merged_values, changed


# Performs a full DOWN move on the entire board
# This mirrors move_up but uses RIGHT movement instead of LEFT
def move_down(board):

    # Step 1: transpose board
    transposed_board = board.T

    # Step 2: apply right move logic on transposed board
    moved_board, merged_values, changed = move_right(transposed_board)

    # Step 3: transpose back
    final_board = moved_board.T

    return final_board, merged_values, changed