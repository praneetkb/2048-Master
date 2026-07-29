# Main program entry point.
# Runs one game as an MDP rollout: observe state, pick action, apply, repeat.
# Team member responsible: João

import pygame

from ui.game_loop import get_agent, run_game_loop, run_comparison
from ui.menu import run_menu

WINDOW_WIDTH = 700
WINDOW_HEIGHT = 700

def main():
    pygame.init()

    screen = pygame.display.set_mode(
        (WINDOW_WIDTH, WINDOW_HEIGHT)
    )

    pygame.display.set_caption("2048 Master")

    while True:
        choice = run_menu(screen)

        if choice is None:
            break

        if choice == "compare":
            if not run_comparison(screen):
                break
            continue

        agent = get_agent(choice)

        if agent is None:
            continue

        if not run_game_loop(screen, agent):
            break

    pygame.quit()


if __name__ == "__main__":
    main()


# from agents.expectimax_rl_agent import HeuristicExpectimaxAgent
# from game.game import Game


# def main():

#     game = Game()
#     agent = HeuristicExpectimaxAgent(depth=3)

#     # Play until no move can change the board.
#     while not game.is_game_over():

#         # Snapshot of the raw grid before the move (agents operate on the numpy
#         # grid, not the Board object — movement.py expects grid.shape etc.).
#         # copy() keeps it independent of the live board.
#         state = game.board.grid.copy()
#         score_before = game.score

#         action = agent.choose_action(state)

#         # move() returns False if the move was illegal (board/score unchanged).
#         changed = game.move(action)
#         if not changed:
#             print(f"Illegal move chosen by agent: {action}")
#             break

#         # Reward = points gained from this move's merges.
#         reward = game.score - score_before

#         print(f"action={action}, reward={reward}, score={game.score}")
#         game.board.display_board()

#     print("Game over!")

# if __name__ == "__main__":
#     main()
