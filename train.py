#  Runs TD(0) self-play and saves the learned value function.
#
#   python train.py                    # this has 10000 episodes which takes more than 20 mins
#   python train.py --episodes 3000
#   python train.py --episodes 2000 --resume    # continues from an existing checkpoint saved in checkpoints/

import argparse
from pathlib import Path

from agents.n_tuple_network import NTupleNetwork
from training.td_learning import TDTrainer

DEFAULT_CHECKPOINT = "checkpoints/value_function.npz"


def main():
    parser = argparse.ArgumentParser(description="Train the 2048 n-tuple value function.")
    parser.add_argument("--episodes", type=int, default=10000)
    parser.add_argument("--alpha", type=float, default=0.01)
    parser.add_argument("--checkpoint", default=DEFAULT_CHECKPOINT)
    parser.add_argument("--log-every", type=int, default=1000)
    parser.add_argument("--resume", action="store_true", help="load the checkpoint before training")
    args = parser.parse_args()

    path = Path(args.checkpoint)
    if args.resume and path.exists():
        network = NTupleNetwork.load(path)
        print(f"Resumed from {path}")
    else:
        network = NTupleNetwork()
        print("Starting from an untrained network")

    trainer = TDTrainer(
        network=network,
        learning_rate=args.alpha,
        episodes=args.episodes,
        checkpoint_path=args.checkpoint,
        log_every=args.log_every,
    )
    trainer.train()

    trainer.save_checkpoint()
    print(f"Final weights saved to {args.checkpoint}")


if __name__ == "__main__":
    main()