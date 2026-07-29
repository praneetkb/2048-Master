"""Generates the agent comparison table for the Milestone 2 report.

Produces the Accomplishment 3 proof: random vs heuristic Expectimax vs
Expectimax + RL, over the same number of games, with the same trained network.

Usage:
    PYTHONPATH=. python scripts/evaluate_agents.py
    PYTHONPATH=. python scripts/evaluate_agents.py --games 30 --depth 2
"""

import argparse
import json
import statistics
import time
from pathlib import Path

from agents.random_agent import RandomAgent
from agents.expectimax_rl_agent import ExpectimaxAgent
from game.game import Game
from training.checkpoints import load_value_function


def play_game(agent):
    game = Game()
    moves = 0

    while not game.is_game_over():
        action = agent.choose_action(game.board.grid.copy())
        if action is None:
            break
        game.move(action)
        moves += 1

    return int(game.score), int(game.board.grid.max()), moves


def benchmark(label, agent_factory, games):
    scores = []
    tiles = []
    total_moves = 0

    start = time.time()
    for index in range(games):
        score, tile, moves = play_game(agent_factory())
        scores.append(score)
        tiles.append(tile)
        total_moves += moves
        print(f"  {label} game {index + 1}/{games}: score={score} max_tile={tile}", flush=True)
    elapsed = time.time() - start

    # Win rate = fraction of games that reached the 2048 tile, the standard
    # success criterion for this game.
    wins = sum(1 for tile in tiles if tile >= 2048)

    return {
        "agent": label,
        "games": games,
        "avg_score": round(statistics.mean(scores), 1),
        "best_score": max(scores),
        "median_score": round(statistics.median(scores), 1),
        "highest_tile": max(tiles),
        "reached_2048": f"{wins}/{games}",
        "ms_per_move": round(elapsed / max(total_moves, 1) * 1000, 1),
        "scores": scores,
        "tiles": tiles,
    }


def as_markdown(rows):
    header = "| Agent | Games | Avg Score | Median | Best Score | Highest Tile | Reached 2048 | ms/move |"
    divider = "|---|---|---|---|---|---|---|---|"
    lines = [header, divider]
    for row in rows:
        lines.append(
            f"| {row['agent']} | {row['games']} | {row['avg_score']} | {row['median_score']} "
            f"| {row['best_score']} | {row['highest_tile']} | {row['reached_2048']} | {row['ms_per_move']} |"
        )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Compare the three agents for the report.")
    parser.add_argument("--games", type=int, default=20)
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--checkpoint", default="checkpoints/value_function.npz")
    parser.add_argument("--out", default="training_logs/agent_comparison.json")
    args = parser.parse_args()

    network = load_value_function(args.checkpoint)

    rows = [
        benchmark("Random", RandomAgent, args.games),
        benchmark(
            f"Expectimax (heuristic, depth {args.depth})",
            lambda: ExpectimaxAgent(depth=args.depth),
            args.games,
        ),
    ]

    if network is None:
        print(
            "\nNo trained checkpoint, so the RL row is omitted. "
            "Run 'python train.py' first to include it."
        )
    else:
        rows.append(
            benchmark(
                f"Expectimax + RL (depth {args.depth})",
                lambda: ExpectimaxAgent(depth=args.depth, network=network),
                args.games,
            )
        )

    table = as_markdown(rows)
    print("\n" + table)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, indent=2))
    print(f"\nRaw results saved to {out}")

    markdown_out = out.with_suffix(".md")
    markdown_out.write_text(table + "\n")
    print(f"Table saved to {markdown_out}")


if __name__ == "__main__":
    main()
