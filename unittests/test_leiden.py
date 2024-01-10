import unittest
from src.fitch_utils import flatten, len_flatten

class TestLeiden(unittest.TestCase):
    def test_flatten(self):
        self.assertEqual(flatten([1, 2, [3, 4], [[5, 6], 7]]), [1, 2, 3, 4, 5, 6, 7])
        self.assertEqual(flatten([1, 2, 3]), [1, 2, 3])
        self.assertEqual(flatten([]), [])
        self.assertEqual(flatten([[], []]), [])

    def test_len_flatten(self):
        self.assertEqual(len_flatten([1, 2, [3, 4], [[5, 6], 7]]), 7)
        self.assertEqual(len_flatten([1, 2, 3]), 3)
        self.assertEqual(len_flatten([]), 0)
        self.assertEqual(len_flatten([[], []]), 0)

if __name__ == '__main__':
    unittest.main()