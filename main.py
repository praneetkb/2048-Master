# Main program entry point.
# Runs one game as an MDP rollout: observe state, pick action, apply, repeat.
# Team member responsible: João

from game.game import Game
from agents.expectimax_agent import ExpectimaxAgent

def main():

    game = Game()
    agent = ExpectimaxAgent(depth=3)

    # Play until no move can change the board.
    while not game.is_game_over():

        # Snapshot of the raw grid before the move (agents operate on the numpy
        # grid, not the Board object — movement.py expects grid.shape etc.).
        # copy() keeps it independent of the live board.
        state = game.board.grid.copy()
        score_before = game.score

        action = agent.choose_action(state)

        # move() returns False if the move was illegal (board/score unchanged).
        changed = game.move(action)
        if not changed:
            print(f"Illegal move chosen by agent: {action}")
            break

        # Reward = points gained from this move's merges.
        reward = game.score - score_before

        print(f"action={action}, reward={reward}, score={game.score}")
        game.board.display_board()

    print("Game over!")

if __name__ == "__main__":
    main()
