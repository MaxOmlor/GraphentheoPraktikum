import networkx as nx
import os
import sys
import random
import typing

sys.path.append('fitch-graph-prak')

from lib import graph_to_rel

def run_benchmark(partial: dict[typing.Any, list[tuple[int, int]]],)