"""
thompson.py
James Wang
Nov 29, 2014
"""
from policy import Policy
from index import IndexWrapper
import pyBandits.policy.Thompson
from pyBandits.posterior.Beta import Beta


class Thompson(Policy):
    """Thompson sampling (Thompson, 1933)"""
    def __init__(self, arm_list):
        super(Thompson, self).__init__(arm_list)
        self.name = 'Thompson'
        self.policy = ThompsonWrapper(arm_list)
        self.policy.startGame()

    def get_arm(self, arms, context, features):
        return self.policy.choice(arms)

    def pull_arm(self, arm, feedback, context):
        self.policy.getReward(arm, feedback)


class ThompsonWrapper(IndexWrapper, pyBandits.policy.Thompson.Thompson):
    """
    Wraps pyBandits implementation of Thompson Sampling.
    This wrapper defaults to the Beta distribution.
    """
    def __init__(self, arm_list, posterior=Beta):
        self.arm_list = arm_list
        pyBandits.policy.Thompson.Thompson.__init__(self, len(arm_list),
                                                    posterior)
        self.posterior = dict()
        for arm in arm_list:
            self.posterior[arm] = posterior()

    def startGame(self):
        self.t = 1
        for arm in self.arm_list:
            self.posterior[arm].reset()
