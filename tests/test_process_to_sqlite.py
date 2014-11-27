"""
test_process_to_sqlite.py
James Wang
Nov 24, 2014
"""
import unittest
import os
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
        if os.path.isfile('test.db'):
            os.remove('test.db')
        self.fixture = ProcessWebscope('test.db', log=False)

    def tearDown(self):
        del(self.fixture)

    def testProcess(self):
        self.fixture.process_file('tests/data/minimal.gz')
        # Manual inspection looks good--add automated tests

        # test if user features are captured correctly
        # test if article features are captured correctly
        # test if event is captured correctly
        # test if user cluster is truly max feature
        # test minimal case of only a few pools, and if captured correctly


class BiggerDBTest(unittest.TestCase):
    def setUp(self):
        if os.path.isfile('testbig.db'):
            os.remove('testbig.db')
        self.fixture = ProcessWebscope('testbig.db', log=False)

    def tearDown(self):
        del(self.fixture)

    def testProcess(self):
        self.fixture.process_file('tests/data/testdata.gz')


if __name__ == '__main__':
    unittest.main()
