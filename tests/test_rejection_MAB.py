"""
test_rejection_MAB.py
James Wang
Nov 28, 2014
"""
import unittest
import sqlite3
import numpy as np
from environment.rejection_MAB import RejectionMAB
from policy.UCB import UCB, IndexedUCB, KLUCB
from policy.thompson import Thompson, ContextualThompson
from policy.oblivious import Oblivious
from policy.epsilon_greedy import EpsilonGreedy
from policy.linUCB import LinUCB


class RejectionMABTest(unittest.TestCase):
    def setUp(self):
        db = 'data/tester.db'
        self.conn = sqlite3.connect(db)
        self.c = self.conn.cursor()
        self.c.execute('SELECT articleID FROM article')
        self.n = 10000
        arms = [arm[0] for arm in self.c.fetchall()]
        policies = [UCB(arms), IndexedUCB(arms, range(2, 7)), KLUCB(arms),
                    Thompson(arms), Oblivious(arms), EpsilonGreedy(arms),
                    EpsilonGreedy(arms, .05), LinUCB(arms)]
        self.MAB = RejectionMAB(db, self.n, range(2, 7),
                                arms, policies)

    def tearDown(self):
        self.conn.close()
        del(self.MAB)

    def test_utility(self):
        def allclose(x, y, rtol=1.e-5, atol=1.e-8):
            return np.less_equal(abs(x-y), atol + rtol * abs(y)).all()

        user_feat = {2: np.array([1., 0.59341027, 0.08518741, 0.09934202,
                                  0.21214867, 0.00991163]),
                     3: np.array([1., 0.13210272,  0.71309447, 0.00255777,
                                  0.14336339, 0.00888169]),
                     4: np.array([1., 0.10497026, 0.00166479, 0.77222832,
                                  0.11474214, 0.00639448]),
                     5: np.array([1., 0.11964846, 0.07486103, 0.11676501,
                                  0.6806986, 0.00802689]),
                     6: np.array([1., 0.01935529, 0.00857222, 0.01433817,
                                  0.02326897, 0.93446538])}
        art_109453_feat = np.array([1., 4.21669000e-01, 1.10000000e-05,
                                    1.09020000e-02, 3.09585000e-01,
                                    2.57833000e-01])
        arms = [109498, 109509, 109508, 109473, 109453,
                109503, 109502, 109501, 109492, 109495,
                109494, 109484, 109506, 109514, 109505,
                109515, 109512, 109513, 109511, 109510]

        user_called = self.MAB.user_feat
        article_called = self.MAB.article_feat
        event_2_called = self.MAB.get_event(2)
        pools_called = self.MAB.poolarticles

        features = {i: np.outer(user_called[4], article_called[i])
                    for i in arms}
        features_called = event_2_called['features']
        arms_called = event_2_called['arms']

        del(event_2_called['features'])
        del(event_2_called['arms'])

        event_2 = {'user': 4, 'pulled': 109484, 'reward': 0}

        ctr_109558_2 = 0.02894356005788712
        ctr_109558_2_called = self.MAB.get_ctrs()[2][109558]

        self.assertAlmostEqual(user_feat[3][3], user_called[3][3])
        self.assertTrue(allclose(art_109453_feat, article_called[109453]))
        self.assertEqual(event_2, event_2_called)
        self.assertTrue(allclose(features[109502], features_called[109502]))
        self.assertTrue(allclose(features[109515], features_called[109515]))
        self.assertItemsEqual(arms, arms_called)
        self.assertItemsEqual(arms, pools_called[1])
        self.assertAlmostEqual(ctr_109558_2, ctr_109558_2_called)

        self.MAB.run()
        self.MAB.output_decisions('data/test_results.gz')
        # test that file is actually self.n * num_policies + 1
        print self.MAB.total_pulls
