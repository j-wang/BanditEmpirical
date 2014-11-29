"""
policy.py
James Wang
Nov 29, 2014
"""


class Policy(object):
    """Abstract class for Policy classes"""
    def __init__(self, num_arms, segments=1):
        self.num_arms = num_arms
        self.segments = segments

    def get_arm(self, context, arms, features):
        raise NotImplementedError("This method must be overridden.")

    def pull_arm(self, arm, feedback):
        raise NotImplementedError("This method must be overridden.")
