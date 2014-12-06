"""
run_MAB.py
James Wang
Nov 29. 2014
"""
from environment.rejection_MAB import RejectionMABRecordSampling
from policy.UCB import UCB
import sqlite3
import time
import datetime

db = 'data/final_copy.db'

conn = sqlite3.connect(db)
c = conn.cursor()
c.execute('SELECT articleID FROM article')
arms = [arm[0] for arm in c.fetchall()]
policies = [UCB(arms)]

conn.close()

n = 10000

t0 = time.time()
MAB = RejectionMABRecordSampling(db, n, range(2, 7), arms, policies)
MAB.run()
print MAB.total_pulls
t1 = time.time()

MAB.output_accept_reject('data/acceptreject.gz')

the_time = str(datetime.timedelta(seconds=t1-t0))
print('Now: {}'.format(time.time()))
print('Took a total of {}'.format(the_time))
print('Number of pulls required to reach {} was {}'.format(n,
                                                           MAB.total_pulls))
