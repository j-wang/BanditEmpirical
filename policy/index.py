"""
index.py
James Wang
Nov 29, 2014
"""
import random


class IndexWrapper(object):
    def choice(self, choices):
        index = dict()
        for arm in choices:
            index[arm] = self.computeIndex(arm)
        maxIndex = max(index.values())
        bestArms = [arm for arm in index.keys() if index[arm] == maxIndex]
        return random.choice(bestArms)
