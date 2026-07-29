import statistics

from game.game import Game
from agents.random_agent import RandomAgent
from agents.expectimax_rl_agent import HeuristicExpectimaxAgent


NUM_GAMES = 5

def play_game(agent):
    game = Game()

    while not game.is_game_over():
        action = agent.choose_action(game.board.grid.copy())
        game.move(action)

    return {
        "score": game.score,
        "max_tile": int(game.board.grid.max())
    }


def benchmark(agent_factory):
    scores = []
    max_tiles = []

    for i in range(NUM_GAMES):
        result = play_game(agent_factory())
        scores.append(result["score"])
        max_tiles.append(result["max_tile"])

    return {
        "Runs": NUM_GAMES,
        "Average Score": round(statistics.mean(scores), 1),
        "Best Score": max(scores),
        "Highest Tile": max(max_tiles),
    }


def compare_agents():
    return {
        "Random": benchmark(RandomAgent),
        "Expectimax": benchmark(
            lambda: HeuristicExpectimaxAgent(depth=2)
        ),
        #"RL Agent": benchmark(
        #
        #)
    }