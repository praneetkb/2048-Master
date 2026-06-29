# Implements random agent for 2048
# It picks the next move randomly, without considering board state

import random

from agents.agent import Agent

ACTIONS = ["left", "right", "up", "down"]

class RandomAgent(Agent):
    
    def choose_action(self, state):
        return random.choice(ACTIONS)