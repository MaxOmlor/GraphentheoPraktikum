import sys
import typing

sys.path.append('fitch-graph-prak')

import lib

def preprocess(rel: dict[typing.Any, list[tuple[int, int]]], num_nodes: int, order: tuple[int]):
    return {'rel':rel, 'nodes': num_nodes, 'order': order}

def run(data):
    test = lib.algorithm_one(data['rel'],list(range(data['nodes'])),data['order'])
    return lib.cotree_to_rel(test)