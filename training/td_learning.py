# TD Learning trainer for 2048.

# This is responsible for:
# generating self-play games
# choosing moves greedily using the current value function
# calculating TD error
# updating the N-tuple network
# saving checkpoints during training

# The N-tuple network acts as the value function V(s). It estimates how good a board position is.
# Training improves this estimate through experience.

# Team member responsible: Praneet

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from agents.n_tuple_network import NTupleNetwork
from game.game import MOVES, Game
from game.score import points_after_merge


class TDTrainer:
    def __init__(
        self,
        network: NTupleNetwork,
        learning_rate=0.01,
        episodes=10000,  # 10,000 games
        log_every=500,   # print + checkpoint interval
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

        # How often to print progress and save a checkpoint
        self.log_every = log_every

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
            if episode % self.log_every == 0:

                average = float(np.mean(scores[-self.log_every:]))
                best = int(np.max(scores[-self.log_every:]))

                print(
                    f"Episode {episode}, "
                    f"Average Score: {average:.1f}, "
                    f"Best: {best}"
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


    def evaluate_moves(self, state):
        """Greedy one-step lookahead.

        Returns (action, afterstate, reward, reward + V(afterstate)).
        The fourth element is exactly the TD target for the PREVIOUS afterstate,
        which is why the caller can reuse it instead of recomputing.
        """
        best_action = None
        best_afterstate = None
        best_reward = 0.0
        best_value = float("-inf")

        for action, move in MOVES.items():
            afterstate, merged_values, changed = move(state)
            if not changed:
                continue

            reward = points_after_merge(merged_values)
            value = reward + self.network.value(afterstate, validate=False)

            if value > best_value:
                best_action = action
                best_afterstate = afterstate
                best_reward = reward
                best_value = value

        return best_action, best_afterstate, best_reward, best_value

    def play_episode(self):
        """One self-play game with TD(0) updates over afterstates.

        V(afterstate) estimates FUTURE reward only, so the target for afterstate A1 is
        R2 + V(A2), where R2 is the reward of the move taken from the NEXT board.
        The current move's own reward is used for action selection, not for the target.
        """
        game = Game()
        action, afterstate, _reward, _value = self.evaluate_moves(game.board.grid)

        while action is not None:
            game.move(action)

            next_action, next_afterstate, _next_reward, target = self.evaluate_moves(
                game.board.grid
            )
            if next_action is None:  # terminal: no future reward
                target = 0.0

            delta = target - self.network.value(afterstate, validate=False)
            self.network.update(afterstate, self.alpha * delta)

            action, afterstate = next_action, next_afterstate

        return game.score

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