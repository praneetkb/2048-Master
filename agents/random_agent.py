# Implements random agent for 2048
# Picks random action without considering board state

import random

ACTIONS = ["left", "right", "up", "down"]

class RandomAgent:
    
    def choose_action(self, state):
        return random.choice(ACTIONS)