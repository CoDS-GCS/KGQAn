import unittest
from kgqan.nlp import utils


class TestNlpUtils(unittest.TestCase):
    def test_remove_duplicates(self):
        lst = [1, 2, 3]
        self.assertEqual(lst, utils.remove_duplicates(lst))

        lst = []
        self.assertEqual(lst, utils.remove_duplicates(lst))

        lst = [1, 2, 2, 4]
        self.assertEqual([1,2,4], utils.remove_duplicates(lst))


if __name__ == '__main__':
    unittest.main()


