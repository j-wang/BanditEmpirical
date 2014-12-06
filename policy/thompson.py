"""
thompson.py
James Wang
Nov 29, 2014
"""
from policy import Policy
from index import IndexWrapper
import pyBandits.policy.Thompson
from pyBandits.posterior.Beta import Beta
from posterior.contextualgaussian import ContextualGaussian
import numpy as np


class Thompson(Policy):
    """Thompson sampling (Thompson, 1933)"""
    def __init__(self, arm_list):
        super(Thompson, self).__init__(arm_list)
        self.name = 'Thompson'
        self.policy = ThompsonWrapper(arm_list)
        self.policy.startGame()

    def get_arm(self, arms, context, features):
        return self.policy.choice(arms)

    def pull_arm(self, arm, feedback, context, features=None):
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


class ContextualThompson(IndexWrapper):
    def __init__(self, arm_list, dim=6, posterior=ContextualGaussian):
        self.name = 'ContextualThompson'
        self.arm_list = arm_list
        self.posterior = posterior(dim)

    def get_arm(self, arms, context, features):
        arm_vals = dict()
        mu_tilde = self.posterior.sample()
        for arm in arms:
            arm_vals[arm] = np.inner(features[arm].flatten(), mu_tilde)
        return max([(a, r) for a, r in arm_vals.items()],
                   key=lambda x: x[1])[0]

    def pull_arm(self, arm, feedback, context, features):
        self.posterior.update(feedback, features[arm])
