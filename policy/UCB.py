"""
UCB.py
James Wang
Nov 29, 2014
"""
from policy import Policy
from index import IndexWrapper
import pyBandits.policy.UCB
import pyBandits.policy.klUCB


class UCB(Policy):
    """UCB from Auer 2002, implemented as written in Garvier, Cappe 2002"""
    def __init__(self, arm_list):
        super(UCB, self).__init__(arm_list)
        self.name = 'UCB'
        self.policy = UCBWrapper(arm_list)
        self.policy.startGame()

    def get_arm(self, arms, context=None, features=None):
        return self.policy.choice(arms)

    def pull_arm(self, arm, feedback, context=None, features=None):
        self.policy.getReward(arm, feedback)


class UCBWrapper(IndexWrapper, pyBandits.policy.UCB.UCB):
    """Wraps pyBandits implementation of UCB"""
    def __init__(self, arm_list, amplitude=1., lower=0.):
        self.arm_list = arm_list
        pyBandits.policy.UCB.UCB.__init__(self, len(arm_list),
                                          amplitude, lower)

    def startGame(self):
        self.t = 1
        for arm in self.arm_list:
            self.nbDraws[arm] = 0
            self.cumReward[arm] = 0


class IndexedUCB(Policy):
    """Indexed UCB, as per contextual bandit approach in Woodroofe 1979"""
    def __init__(self, arm_list, context_list):
        super(IndexedUCB, self).__init__(arm_list)
        self.name = 'IndexedUCB'
        self.policies = {i: UCBWrapper(arm_list) for i in context_list}
        for policy in self.policies.values():
            policy.startGame()

    def get_arm(self, arms, context, features=None):
        return self.policies[context].choice(arms)

    def pull_arm(self, arm, feedback, context, features=None):
        self.policies[context].getReward(arm, feedback)


class KLUCB(UCB):
    """KL UCB implementation from Garivier, Cappe 2011"""
    def __init__(self, arm_list):
        super(KLUCB, self).__init__(arm_list)
        self.name = 'KL-UCB'
        self.policy = KLUCBWrapper(arm_list)
        self.policy.startGame()


class KLUCBWrapper(IndexWrapper, pyBandits.policy.klUCB.klUCB):
    def __init__(self, arm_list, amplitude=1., lower=0.):
        self.arm_list = arm_list
        pyBandits.policy.klUCB.klUCB.__init__(self, len(arm_list),
                                              amplitude, lower)

    def startGame(self):
        self.t = 1
        for arm in self.arm_list:
            self.nbDraws[arm] = 0
            self.cumReward[arm] = 0
