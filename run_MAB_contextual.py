"""
run_MAB_contextual.py
James Wang
Nov 29. 2014
"""
from environment.rejection_MAB import RejectionMAB
from policy.UCB import IndexedUCB
from policy.thompson import ContextualThompson
from policy.oblivious import Oblivious
import sqlite3
import time
import datetime

db = 'data/final_copy.db'

conn = sqlite3.connect(db)
c = conn.cursor()
c.execute('SELECT articleID FROM article')
arms = [arm[0] for arm in c.fetchall()]
policies = [IndexedUCB(arms, range(2, 7)), ContextualThompson(arms),
            Oblivious(arms)]

conn.close()

n = 1000000

t0 = time.time()
MAB = RejectionMAB(db, n, range(2, 7), arms, policies)
MAB.run()
MAB.output_decisions('data/results_contextual2.gz')
print MAB.total_pulls
t1 = time.time()

the_time = str(datetime.timedelta(seconds=t1-t0))
print('Now: {}'.format(time.time()))
print('Took a total of {}'.format(the_time))
print('Number of pulls required to reach {} was {}'.format(n,
                                                           MAB.total_pulls))
