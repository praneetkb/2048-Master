# 2048 Reinforcement Learning Agent

## Overview

This project implements an autonomous AI agent that learns to play 2048 through reinforcement learning. The core approach combines Expectimax search with a learned N-tuple network value function, trained via Temporal Difference (TD) learning through self-play. Two baseline agents are included for comparison: a Random Agent and a traditional heuristic-based Expectimax Agent.

The agent takes the current $4 \times 4$ game board as input and outputs one of four possible actions: **up**, **down**, **left**, or **right**, with the goal of maximizing the final score and tile value achieved.

## Features
- Playable 2048 game with a Pygame user interface
- Multiple AI agents:
  - Random Agent (baseline)
  - Expectimax Agent (heuristic-based baseline)
  - Expectimax + Reinforcement Learning Agent
- N-tuple network value function
- TD learning through self-play
- Training checkpoints
- Performance evaluation and comparison between agents


## AI Approach

The reinforcement learning agent learns by repeatedly playing games against itself. The learning pipeline consists of:

1. **N-tuple Network**: estimates the value of a given board state
2. **Temporal Difference (TD) Learning**: updates board values based on observed transitions
3. **Self-Play**: generates training experience without human data
4. **Expectimax Search**: uses the learned value function to make final move decisions