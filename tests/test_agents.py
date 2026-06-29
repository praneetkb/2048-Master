from game.game import Game
from agents.random_agent import RandomAgent
from agents.expectimax_agent import ExpectimaxAgent


def play_game(agent, max_steps=1000):
    game = Game()

    steps = 0

    while not game.is_game_over() and steps < max_steps:

        board = game.board.grid

        action = agent.choose_action(board)

        if action is None:
            break

        game.move(action)

        steps += 1

    return game.score, game.board.grid.max()


def run_multiple(agent, games=10):
    scores = []
    max_tiles = []

    for _ in range(games):
        score, max_tile = play_game(agent)

        scores.append(score)
        max_tiles.append(max_tile)

    print(f"\n{agent.__class__.__name__}")
    print("Avg Score:", sum(scores) / len(scores))
    print("Avg Max Tile:", sum(max_tiles) / len(max_tiles))


if __name__ == "__main__":

    random_agent = RandomAgent()
    expectimax_agent = ExpectimaxAgent(depth=2)

    run_multiple(random_agent, games=10)
    run_multiple(expectimax_agent, games=10)