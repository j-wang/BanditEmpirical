"""
contextualgaussian.py
James Wang
Nov 29, 2014
"""
import numpy as np
from numpy.random import multivariate_normal
from math import sqrt, log


class ContextualGaussian(object):
    """Gaussian prior for Thompson Sampling (Agrawal 2014)"""
    def __init__(self, dim, R=.5, delta=.05):
        self.t = 1
        self.dim = dim
        self.R = R
        self.delta = delta
        self.d = dim**2
        self.b_bt = np.zeros((self.d, self.d))
        self.I = np.identity(self.d)
        self.b_times_r = np.zeros(self.d)

    def reset(self):
        self.t = 1
        dim = self.dim
        self.d = dim**2
        self.b_bt = np.zeros(self.d)
        self.I = np.identity(self.d)
        self.b_times_r = np.zeros(dim)

    def update(self, obs, context_vect):
        """Updates posterior. Takes reward."""
        self.t += 1
        context_flat = context_vect.flatten()
        context_matrix = np.outer(context_flat,
                                  context_flat)
        self.b_bt += context_matrix
        self.b_times_r += context_flat * obs

    def sample(self):
        v = self.R * sqrt(9 * self.dim * log(self.t/self.delta))
        B = self.I + self.b_bt
        B_inv = np.linalg.inv(B)
        mu_hat = np.dot(B_inv, self.b_times_r)
        return multivariate_normal(mu_hat, v**2 * B_inv)
