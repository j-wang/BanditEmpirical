"""
test_process_to_sqlite.py
James Wang
Nov 24, 2014
"""
import unittest
import os
import sqlite3
from process_to_sqlite import UniqueDict, ProcessWebscope


class UniqueDictTest(unittest.TestCase):
    def setUp(self):
        self.fixture = UniqueDict()
        self.fixture[3] = 4

    def tearDown(self):
        del(self.fixture)

    def test_values(self):
        self.assertRaises(ValueError, self.fixture.update, {10: 4})

    def test_keys(self):
        self.assertRaises(KeyError, self.fixture.update, {3: 10})


class FreshDBTest(unittest.TestCase):
    def setUp(self):
        self.dbname = 'test.db'
        if os.path.isfile(self.dbname):
            os.remove(self.dbname)
        self.fixture = ProcessWebscope(self.dbname, log=False)
        self.testfile = 'tests/data/minimal.gz'

    def tearDown(self):
        del(self.fixture)

    def testBasicProcess(self):
        self.fixture.process_file(self.testfile)

        conn = sqlite3.connect(self.dbname)
        c = conn.cursor()
        c.execute('''SELECT COUNT(*) FROM event''')
        count = c.fetchone()[0]
        c.execute('''SELECT COUNT(*) FROM user''')
        user_count = c.fetchone()[0]
        c.execute('''SELECT * from user WHERE feat2=0.121789''')
        user = c.fetchone()
        c.execute('''SELECT COUNT(*) FROM pool''')
        pools = c.fetchone()[0]
        c.execute('''SELECT COUNT(*) from poolarticle''')
        pool_articles = c.fetchone()[0]
        c.execute('''SELECT * from article WHERE articleID=109511''')
        article = c.fetchone()

        self.assertEqual(5, count)
        self.assertEqual(count, user_count)
        self.assertEqual((4, 1, 0.121789, 0.003283,
                          0.628306, 0.246422, 0.000200), user[1:])
        self.assertEqual(3, pools)
        self.assertEqual(20 + 21 + 20, pool_articles)
        self.assertEqual((109511, 0, 1, 0.381149, 0.000129,
                          0.060038, 0.269129, 0.289554), article)
        conn.close()

    def testSkipProcess(self):
        self.fixture.process_file(self.testfile, skip_lines=2)
        conn = sqlite3.connect(self.dbname)
        c = conn.cursor()
        c.execute('''SELECT COUNT(*) FROM event''')
        count = c.fetchone()[0]
        c.execute('''SELECT displayed FROM event WHERE eventID=1''')
        displayed = c.fetchone()[0]

        self.assertEqual(3, count)
        self.assertEqual(109511, displayed)

        conn.close()


class BiggerDBTest(unittest.TestCase):
    def setUp(self):
        if os.path.isfile('testbigger.db'):
            os.remove('testbigger.db')
        self.fixture = ProcessWebscope('testbigger.db', log=False)

    def tearDown(self):
        del(self.fixture)

    def testProcess(self):
        self.fixture.process_file('tests/data/testdata.gz')


if __name__ == '__main__':
    unittest.main()
