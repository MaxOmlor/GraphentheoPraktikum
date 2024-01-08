import sys
import typing
import os
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from fitch_utils import make_partial


import lib

def assign_rel_weights(e_completed, e_complement, rel, weight):
    rel_weights = []
    for e in e_completed:
        if e in rel:
            rel_weights.append((e, weight))
        else:
            rel_weights.append((e, -weight))
    for e in e_complement:
        rel_weights.append((e, 0.))
    rel_weights_dict = dict(rel_weights)
    return rel_weights_dict

def assign_rel_weights_dist(num_nodes: int, rel: list[tuple[int, int]], dist_0, param_0,dist_1, param_1):
    all_edges = [(i,j) for i in range(num_nodes) for j in range(num_nodes) if i != j]
    rel_complement = [e for e in all_edges if e not in rel]

    rel_weights = {
        **lib.generate_weights(rel, dist_0, param_0),
        **lib.generate_weights(rel_complement, dist_1, param_1)
    }

    rel_weights_dict = dict(rel_weights)
    return rel_weights_dict

def assign_all_weights(rel: dict[typing.Any, list[tuple[int, int]]], num_nodes: int, w_type: str, dist_data: dict):
    rel_0 = rel[0]
    rel_1 = rel[1]
    rel_d = rel['d']

    if 'uniform':
        weight = 1

        e_completed =rel_0 + rel_1 + make_partial.recreate_symmetry(rel_d)
        e_complement = [(i,j) for i in range(num_nodes) for j in range(num_nodes) if (i,j) not in e_completed and i != j]
        
        return {
            1: assign_rel_weights(e_completed,e_complement,rel_1,weight),
            0: assign_rel_weights(e_completed,e_complement,rel_0,weight),
            'd': assign_rel_weights(e_completed,e_complement,rel_d,weight),
        }
    
    if 'normal':
        dist_0 = np.random.normal
        param_0 = dist_data['present']
        dist_1 = np.random.normal
        param_1 = dist_data['nonpresent']

        return {
            1: assign_rel_weights_dist(num_nodes, rel_1, dist_0, param_0, dist_1, param_1),
            0: assign_rel_weights_dist(num_nodes, rel_0, dist_0, param_0, dist_1, param_1),
            'd': assign_rel_weights_dist(num_nodes, rel_d, dist_0, param_0, dist_1, param_1),
        }

    raise ValueError(f'w_type must be uniform or normal not {w_type}')

def preprocess(rel: dict[typing.Any, list[tuple[int, int]]], num_nodes: int, w_type='uniform', dist_data=None):
    return {**assign_all_weights(rel,num_nodes,w_type,dist_data), 'nodes': num_nodes}


def run(data):
    test = lib.algorithm_two(list(range(data['nodes'])),data['d'],data[1],data[0])
    return test
