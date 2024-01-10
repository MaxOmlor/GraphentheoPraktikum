import unittest
from unittest.mock import patch
from src.fitch_utils.make_partial import make_partial, recreate_symmetry, remove_n_random_items, sort_tuples, random_numbers, count_in_range

class TestPartial(unittest.TestCase):

    def test_create_partial(self):
        rel = {1: [(1, 2), (3, 4)], 0: [(5, 6), (7, 8)], 'd': [(9, 10), (11, 12)]}
        percent = 0.5
        result = make_partial(rel, percent)
        self.assertEqual(len(result[1]), 2)
        self.assertEqual(len(result[0]), 2)
        self.assertEqual(len(result['d']), 1)

    def test_recreate_symmetry(self):
        l = [(1, 2), (3, 4)]
        result = recreate_symmetry(l)
        self.assertEqual(result, [(1, 2), (3, 4), (2, 1), (4, 3), (1, 2), (3, 4)])

    def test_remove_n_random_items(self):
        l = [1, 2, 3, 4, 5]
        n = 2
        result = remove_n_random_items(l, n)
        self.assertEqual(len(result), 3)

    def test_sort_tuples(self):
        tuples = [(1, 2), (3, 2), (4, 5)]
        result = sort_tuples(tuples)
        self.assertEqual(result, [(3, 2)])

    def test_random_numbers(self):
        n = 5
        m = 10
        result = random_numbers(n, m)
        self.assertEqual(len(result), n)
        self.assertTrue(all(i <= m for i in result))
        self.assertEqual(len(set(result)), n)

    def test_count_in_range(self):
        nums = [1, 2, 3, 4, 5]
        start = 2
        end = 4
        result = count_in_range(nums, start, end)
        self.assertEqual(result, 2)

if __name__ == '__main__':
    unittest.main()