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


def benchmark(agent_factory, on_game=None):
    scores = []
    max_tiles = []

    for i in range(NUM_GAMES):
        result = play_game(agent_factory())
        scores.append(result["score"])
        max_tiles.append(result["max_tile"])
        if on_game is not None:
            on_game(i + 1, NUM_GAMES)

    return {
        "Runs": NUM_GAMES,
        "Average Score": round(statistics.mean(scores), 1),
        "Best Score": max(scores),
        "Highest Tile": max(max_tiles),
    }


def compare_agents(on_result=None, on_progress=None):
    # The trained network is loaded ONCE and shared by every game the RL agent
    # plays, so the RL row reflects the same weights as the training graph.
    network = load_value_function()

    agents = [
        ("Random", RandomAgent),
        ("Expectimax", lambda: ExpectimaxAgent(depth=2)),
    ]

    # Without a checkpoint the RL agent would be identical to the heuristic row,
    # which would be misleading in a comparison table, so it is omitted instead.
    if network is not None:
        agents.append(
            ("Expectimax + RL", lambda: ExpectimaxAgent(depth=2, network=network))
        )

    results = {}
    for name, factory in agents:
        def report(done, total, name=name):
            if on_progress is not None:
                on_progress(name, done, total)

        if on_progress is not None:
            on_progress(name, 0, NUM_GAMES)

        results[name] = benchmark(factory, on_game=report)

        if on_result is not None:
            on_result(name, results[name])

    return results
