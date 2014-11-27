"""
test_process_to_sqlite.py
James Wang
Nov 24, 2014
"""
import unittest
from process_to_sqlite import UniqueDict


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
        pass

    def tearDown(self):
        pass

    def testProcess(self):
        pass

if __name__ == '__main__':
    unittest.main()
