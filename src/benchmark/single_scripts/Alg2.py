import sys
import typing
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from fitch_utils import make_partial


import lib

def assign_rel_weights(e_completed, e_complement, rel,weight):
    rel_weights = []
    for e in e_completed:
        if e in rel:
            rel_weights.append((e,weight))
        else:
            rel_weights.append((e,-weight))
    for e in e_complement:
        rel_weights.append((e,0.))
    rel_weights_dict = dict(rel_weights)
    return rel_weights_dict

def assign_all_weights(rel: dict[typing.Any, list[tuple[int, int]]], num_nodes: int, weight: float):
    rel_0 = rel[0]
    rel_1 = rel[1]
    rel_d = rel['d']

    e_completed =rel_0 + rel_1 + make_partial.recreate_symmetry(rel_d)
    e_complement = [(i,j) for i in range(num_nodes) for j in range(num_nodes) if (i,j) not in e_completed and i != j]
    
    return {
        1: assign_rel_weights(e_completed,e_complement,rel_1,weight),
        0: assign_rel_weights(e_completed,e_complement,rel_0,weight),
        'd': assign_rel_weights(e_completed,e_complement,rel_d,weight),
    }

def preprocess(rel: dict[typing.Any, list[tuple[int, int]]], num_nodes: int):
    return {**assign_all_weights(rel,num_nodes,1.), 'nodes': num_nodes}


def run(data):
    test = lib.algorithm_two(list(range(data['nodes'])),data['d'],data[1],data[0])
    # return lib.cotree_to_rel(test)
    return test
