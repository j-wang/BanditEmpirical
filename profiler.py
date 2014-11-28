"""
profiler.py
James Wang
Nov 27, 2014
"""
import cProfile
import os
from process_to_sqlite import ProcessWebscope


testdb = 'profile.db'
if os.path.isfile(testdb):
    os.remove(testdb)

proc = ProcessWebscope(testdb, log=False)
cProfile.run('proc.process_file("tests/data/fivepercent.gz")',
             'profiler_results')
