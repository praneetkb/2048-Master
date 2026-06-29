# This file defines the base Agent interface. 
# Every agent (Random, Expectimax, and RL) should inherit from this class and implement choose_action()

class Agent:
    def choose_action(self, state):
        raise NotImplementedError("choose_action() must be implemented by subclass.")