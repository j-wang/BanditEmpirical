"""
run_MAB_glmucb.py
James Wang
Dec 1, 2014
"""
from environment.rejection_MAB import RejectionMAB
from policy.glmUCB import GLMUCB
from policy.oblivious import Oblivious
import sqlite3
import time
import datetime

db = 'data/final.db'

conn = sqlite3.connect(db)
c = conn.cursor()
c.execute('SELECT articleID FROM article')
arms = [arm[0] for arm in c.fetchall()]
policies = [GLMUCB(arms), Oblivious(arms)]

conn.close()

n = 10000

t0 = time.time()
MAB = RejectionMAB(db, n, range(2, 7), arms, policies)
MAB.run()
MAB.output_decisions('data/results_glmucb2.gz')
print MAB.total_pulls
t1 = time.time()

the_time = str(datetime.timedelta(seconds=t1-t0))
print('Now: {}'.format(time.time()))
print('Took a total of {}'.format(the_time))
print('Number of pulls required to reach {} was {}'.format(n,
                                                           MAB.total_pulls))
