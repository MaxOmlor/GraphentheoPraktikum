import sys
import os
import typing

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from fitch_utils import weights


def preprocess(rel: dict[typing.Any, list[tuple[int, int]]], num_nodes: int, order: tuple[int], w_type='uniform', dist_data=None, median: bool = False, reciprocal: bool = False):
    dist_types = ['uniform', 'normal']

    return {
        'rel':rel,
        # 'nodes': list(range(num_nodes)),
        'nodes': list(range(num_nodes)),
        'order': order,
        'weights': {
            dist_type: weights.assign_all_weights(rel,num_nodes,dist_type,dist_data) for dist_type in dist_types
        },
        'median': median,
        'reciprocal': reciprocal
    }
