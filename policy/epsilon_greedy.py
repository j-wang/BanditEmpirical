"""
epsilon_greedy.py
James Wang
Nov 30, 2014
"""
from policy import Policy
import random


class EpsilonGreedy(Policy):
    """Standard epsilon greedy, linear regret."""
    def __init__(self, arm_list, epsilon=.1):
        super(EpsilonGreedy, self).__init__(arm_list)
        self.name = 'EpsilonGreedy({})'.format(epsilon)
        self.ep = epsilon
        self.arm_rewards = {arm: 0 for arm in arm_list}

    def get_arm(self, arms, context=None, features=None):
        rewards = [(a, r) for a, r in self.arm_rewards.items()
                   if a in arms]
        if random.random() >= self.ep:
            # exploitation step
            return max(rewards,
                       key=lambda x: x[1])[0]
        else:
            # exploration step
            random.choice(arms)

    def pull_arm(self, arm, feedback, context=None, features=None):
        self.arm_rewards[arm] += feedback
