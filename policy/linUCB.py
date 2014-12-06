"""
linUCB.py
James Wang
Dec 1, 2014
"""
from policy import Policy
from math import sqrt
import numpy as np


class LinUCB(Policy):
    """
    LinUCB, as per Li, Chu, Langford, Schapire 2012
    """
    def __init__(self, arm_list, dim=6, alpha=.01):
        super(LinUCB, self).__init__(arm_list)
        self.name = 'LinUCB'
        self.t = 1
        self.d = dim**2
        self.A = np.identity(self.d)
        self.b = np.zeros(self.d)
        self.pulls = {a: 0 for a in arm_list}
        self.arm_prop = {}
        self.alpha = alpha

    def get_arm(self, arms, context, features):
        alpha = self.alpha
        beta_hat = np.dot(np.linalg.inv(self.A), self.b)
        ps = {a: 0 for a in arms}

        for arm in arms:
            z = features[arm].flatten()
            x = z

            if self.pulls[arm] == 0:  # initialize
                self.arm_prop[arm] = {'A': np.identity(self.d),
                                      'B': np.zeros((self.d, self.d)),
                                      'b': np.zeros(self.d)}

            a_var = self.arm_prop[arm]

            theta_hat = np.dot(np.linalg.inv(a_var['A']),
                               a_var['b'] -
                               np.dot(a_var['B'], beta_hat))

            A0inv = np.linalg.inv(self.A)
            zTA0inv = np.dot(z, A0inv)
            aInv = np.linalg.inv(a_var['A'])
            xTAinv = np.dot(x, aInv)
            s = (np.dot(zTA0inv, z) -
                 2 * np.dot(np.dot(np.dot(zTA0inv, a_var['B']),
                                   aInv), x) +
                 np.dot(xTAinv, x) +
                 np.dot(np.dot(np.dot(np.dot(np.dot(xTAinv,
                                                    a_var['B']), A0inv),
                                      a_var['B'].T), aInv), x))
            ps[arm] = (np.dot(z, beta_hat) + np.inner(x, theta_hat) +
                       alpha * sqrt(s))

        return max(ps.items(), key=lambda x: x[1])[0]

    def pull_arm(self, arm, feedback, context, features):
        self.pulls[arm] += 1
        z = features[arm].flatten()
        x = z
        r = feedback
        B = self.arm_prop[arm]['B']
        aInv = np.linalg.inv(self.arm_prop[arm]['A'])
        b = self.arm_prop[arm]['b']

        self.A += np.dot(np.dot(B.T, aInv), B)
        self.b += np.dot(np.dot(B.T, aInv), b)
        self.arm_prop[arm]['A'] += np.outer(x, x)
        self.arm_prop[arm]['B'] += np.outer(x, z)
        self.arm_prop[arm]['b'] += r * x

        aInv = np.linalg.inv(self.arm_prop[arm]['A'])
        B = self.arm_prop[arm]['B']
        b = self.arm_prop[arm]['b']

        self.A += np.outer(z, z) - np.dot(np.dot(B.T, aInv), B)
        self.b += r * z - np.dot(np.dot(B.T, aInv), b)

        self.t += 1
