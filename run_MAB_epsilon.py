"""
run_MAB_epsilon.py
James Wang
Dec 1, 2014
"""
from environment.rejection_MAB import RejectionMAB
from policy.oblivious import Oblivious
from policy.epsilon_greedy import EpsilonGreedy
import sqlite3
import time
import datetime

db = 'data/final_copy.db'

conn = sqlite3.connect(db)
c = conn.cursor()
c.execute('SELECT articleID FROM article')
arms = [arm[0] for arm in c.fetchall()]
policies = [Oblivious(arms),
            EpsilonGreedy(arms),
            EpsilonGreedy(arms, 0.2),
            EpsilonGreedy(arms, 0.05)]

conn.close()

n = 1000000

t0 = time.time()
MAB = RejectionMAB(db, n, range(2, 7), arms, policies)
MAB.run()
MAB.output_decisions('data/results_epsilon.gz')
print MAB.total_pulls
t1 = time.time()

the_time = str(datetime.timedelta(seconds=t1-t0))
print('Now: {}'.format(time.time()))
print('Took a total of {}'.format(the_time))
print('Number of pulls required to reach {} was {}'.format(n,
                                                           MAB.total_pulls))
