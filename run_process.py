"""
run_process.py
James Wang
Nov 26, 2014
"""
import os
import time
import datetime
from process_to_sqlite import ProcessWebscope

# process all files in the data directory
proc = ProcessWebscope('full.db', log=False)

t0 = time.time()
for file in os.listdir('Webscope/R6/'):
    if file.endswith('.gz'):
        print file
        proc.process_file('Webscope/R6/' + file)
t1 = time.time()

the_time = str(datetime.timedelta(seconds=t1-t0))
print('Processing all files took a total of {}'.format(the_time))
with open('gz_to_database_time.txt', 'w') as f:
    f.write('Total time = {}'.format(the_time))
