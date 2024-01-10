from fitch_utils import weights
from fitch_utils import louvain

import sys
sys.path.append('fitch-graph-prak')
import lib


def preprocess(rel: dict[typing.Any, list[tuple[int, int]]], num_nodes: int, w_type='uniform', dist_data=None):
    return {**weights.assign_all_weights(rel,num_nodes,w_type,dist_data), 'nodes': num_nodes}


def run(data):
    test = lib.partition_heuristic_scaffold()
    return test
