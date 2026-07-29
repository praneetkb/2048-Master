import statistics

from game.game import Game
from agents.random_agent import RandomAgent
from agents.expectimax_rl_agent import ExpectimaxAgent
from training.checkpoints import load_value_function


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
    # The trained network is loaded ONCE and shared by every game the RL agent
    # plays, so the RL row reflects the same weights as the training graph.
    network = load_value_function()

    results = {
        "Random": benchmark(RandomAgent),
        "Expectimax": benchmark(
            lambda: ExpectimaxAgent(depth=2)
        ),
    }

    # Without a checkpoint the RL agent would be identical to the heuristic row,
    # which would be misleading in a comparison table, so it is omitted instead.
    if network is not None:
        results["Expectimax + RL"] = benchmark(
            lambda: ExpectimaxAgent(depth=2, network=network)
        )

    return results
