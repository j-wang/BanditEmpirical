"""
profiler.py
James Wang
Nov 27, 2014
"""
import cProfile
import os
from process_to_sqlite import ProcessWebscope
import sqlite3
from environment.rejection_MAB import RejectionMAB
from policy.UCB import UCB, IndexedUCB, KLUCB
from policy.thompson import Thompson
from policy.oblivious import Oblivious
from policy.glmUCB import GLMUCB


# testdb = 'profile.db'
# if os.path.isfile(testdb):
#     os.remove(testdb)
# proc = ProcessWebscope(testdb, log=False)
# cProfile.run('proc.process_file("tests/data/fivepercent.gz")',
#              'profiler_results')


db = 'full.db'
conn = sqlite3.connect(db)
c = conn.cursor()
c.execute('SELECT articleID FROM article')
arms = [arm[0] for arm in c.fetchall()]
# policies = [UCB(arms), IndexedUCB(arms, range(2, 7)),
#             Thompson(arms), Oblivious(arms)]
policies = [GLMUCB(arms)]

cProfile.run('''MAB = RejectionMAB("{}", 1000,
              range(2, 7), arms, policies); MAB.run()'''.format(db),
             'MAB_profiler_results')
