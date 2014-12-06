"""
oblivious.py
James Wang
Nov 29, 2014
"""
from policy import Policy
import random


class Oblivious(Policy):
    """Picks arms entirely at random."""
    def __init__(self, arm_list):
        self.name = 'Random'

    def get_arm(self, arms, context=None, features=None):
        return random.choice(arms)

    def pull_arm(self, arm, feedback, context=None, features=None):
        pass
