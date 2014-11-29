"""
policy.py
James Wang
Nov 29, 2014
"""


class Policy(object):
    """Abstract class for Policy classes"""
    name = 'POLICY'

    def __init__(self, arm_list):
        self.arm_list = arm_list

    def get_arm(self, arms, context=None, features=None):
        raise NotImplementedError("This method must be overridden.")

    def pull_arm(self, arm, feedback, context=None):
        raise NotImplementedError("This method must be overridden.")
