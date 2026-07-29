# Shared checkpoint loading for the trained value function.
# Team member responsible: João

# The UI and the comparison screen both need the SAME trained network, otherwise
# the numbers we show don't correspond to the training graph in the report. This
# module is the single place that knows where the checkpoint lives and what to do
# when it isn't there.

from pathlib import Path

from agents.n_tuple_network import NTupleNetwork

DEFAULT_CHECKPOINT = Path("checkpoints/value_function.npz")


def load_value_function(path=DEFAULT_CHECKPOINT):
    """Return the trained NTupleNetwork, or None when no checkpoint exists.

    Returning None is not a failure: an ExpectimaxAgent built with network=None
    falls back to the heuristic evaluation, so the UI still runs on a fresh clone
    before anyone has trained. The printed warning exists so nobody mistakes an
    untrained run for a trained one when reading numbers off the screen.
    """
    checkpoint = Path(path)

    if not checkpoint.exists():
        print(
            f"No checkpoint at {checkpoint}. Falling back to the heuristic evaluation. "
            "Run 'python train.py' first if you want the RL agent."
        )
        return None

    network = NTupleNetwork.load(checkpoint)
    print(f"Loaded trained value function from {checkpoint}")
    return network


def is_trained(path=DEFAULT_CHECKPOINT):
    """True when a checkpoint exists, without loading the 4 MB of tables."""
    return Path(path).exists()
