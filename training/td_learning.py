"""
TD Learning trainer for 2048.

Responsible for:
- generating self-play games
- choosing moves greedily using the current value function
- calculating TD error
- updating the N-tuple network
- saving checkpoints during training

The N-tuple network acts as the value function V(s).
It estimates how good a board position is.
Training improves this estimate through experience.
"""

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from agents.n_tuple_network import NTupleNetwork
from game.game import MOVES, Game


class TDTrainer:
    def __init__(
        self,
        network: NTupleNetwork,
        learning_rate=0.01,
        episodes=10000,  # 10,000 games
        checkpoint_path="checkpoints/value_function.npz",
        log_path="training_logs/training_scores.csv",
    ):

        # The N-tuple network stores our learned value function
        # Initially all table values are 0, meaning the agent has no knowledge
        self.network = network

        # Alpha controls how much each experience changes the value function
        # Higher alpha = faster learning but more unstable updates
        # Lower alpha = slower but more stable learning
        self.alpha = learning_rate

        # Number of self-play games used for training
        self.episodes = episodes

        # Location where learned weights are saved
        self.checkpoint_path = checkpoint_path

        # Location to save training progress
        self.log_path = log_path

        # Stores episode numbers and average scores
        self.training_history: list[tuple[int, float]] = []

    def train(self):

        scores = []

        # Agent is trained by playing many games against itself
        # Each completed game provides experience used to improve V(s)
        for episode in range(1, self.episodes + 1):
            # Final score is stored only for monitoring training progress
            # The score itself is not used to update the network
            score = self.play_episode()

            scores.append(score)

            # After every 1000 episodes: calculate average score, save progress and create checkpoint
            if episode > 0 and episode % 1000 == 0:

                average = np.mean(scores[-1000:])

                print(
                    f"Episode {episode}, "
                    f"Average Score: {average:.2f}"
                )

                # Save values for graph
                self.training_history.append(
                    (episode, average)
                )

                self.save_checkpoint()

        # Save training data
        self.save_training_log()

        # Generate graph
        self.plot_training_progress()


    def play_episode(self):

        # Start a new 2048 game
        # The agent will repeatedly observe, choose actions, receive rewards, and update its value function
        game = Game()

        while not game.is_game_over():
            # Current board before taking an action
            # This represents the current state s
            state = game.board.grid.copy()

            # Select the action with the highest estimated future value
            # This returns the move chosen (left, right, up or down) and the board after movement but before random tile spawn (afterstate)
            action, afterstate = self.choose_action(state)

            if action is None:
                break

            # Store score before move so we can calculate reward
            old_score = game.score

            # Apply the chosen move
            # The environment performs the movement, calculates merge score, and spawns a random tile
            game.move(action)

            # Reward is the immediate score gained from this move
            # Example: merging two 4 tiles into an 8 gives reward = 8
            reward = game.score - old_score

            # This is the new state after the random tile spawns
            next_state = game.board.grid.copy()

            # Find the best possible future afterstate from the new board. This estimates V(s_next)
            next_value = self.best_afterstate_value(next_state)

            # Current estimate of how good the previous afterstate was
            current_value = self.network.value(afterstate)

            # TD error delta tells us how wrong our prediction was
            # If reward + future value > current value, then the board was better than expected, increase its value
            # If reward + future value < current value, then the board was worse than expected, decrease its value.
            delta = reward + next_value - current_value

            # Update the N-tuple lookup tables
            # The network moves its prediction slightly toward the target: new value = old value + alpha * delta
            self.network.update(afterstate, self.alpha * delta)

        return game.score

    def choose_action(self, state):

        best_action = None
        best_value = float("-inf")
        best_afterstate = None

        # During training we do not use deep Expectimax search
        # Instead, the agent performs a fast greedy one-step search using the current value function.
        for action, move in MOVES.items():
            afterstate, _merged, changed = move(state)

            if not changed:
                continue

            value = self.network.value(afterstate)

            # Keep the move with the highest predicted value
            if value > best_value:
                best_value = value
                best_action = action
                best_afterstate = afterstate

        return best_action, best_afterstate

    def best_afterstate_value(self, state):

        # Find the move that currently looks best from this state and return its predicted value
        _, afterstate = self.choose_action(state)

        # No possible moves means terminal state
        if afterstate is None:
            return 0

        return self.network.value(afterstate)

    def save_checkpoint(self):

        # Create checkpoint directory if it does not exist
        path = Path(self.checkpoint_path)

        path.parent.mkdir(parents=True, exist_ok=True)

        # Save current N-tuple lookup table values
        # This also allows training to continue later without restarting
        self.network.save(path)

    def save_training_log(self):

        path = Path(self.log_path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True
        )


        with open(path, "w", newline="") as file:

            writer = csv.writer(file)

            writer.writerow(
                [
                    "Episode",
                    "Average Score"
                ]
            )


            writer.writerows(
                self.training_history
            )


        print(
            f"Training log saved to {path}"
        )



    def plot_training_progress(self):

        episodes = [
            item[0]
            for item in self.training_history
        ]

        averages = [
            item[1]
            for item in self.training_history
        ]


        plt.figure(figsize=(8,5))

        plt.plot(
            episodes,
            averages,
            marker="o"
        )


        plt.xlabel(
            "Training Episodes"
        )

        plt.ylabel(
            "Average Score"
        )

        plt.title(
            "TD Learning Training Progress"
        )


        plt.grid(True)


        plt.savefig(
            "training_logs/training_progress.png"
        )


        plt.show()
