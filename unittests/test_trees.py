### create a test for every tree in ./failed_graphs
import unittest
from unittest.mock import patch
from src.fitch_utils.make_partial import make_partial, recreate_symmetry, remove_n_random_items, sort_tuples, random_numbers, count_in_range
from src.fitch_utils.leiden import partition_leiden_normalized
import benchmark.algs.Algs
import networkx

class TestLeiden(unittest.TestCase):
    def test_1(self):
        file = "../failed_grpahs/leiden_fail_1.graphml"
        cograph = networkx.read_graphml(file)
        