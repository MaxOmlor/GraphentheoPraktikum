import networkx as nx
import os
import sys
import random
import typing


import random_trees
import make_partial

sys.path.append('fitch-graph-prak')

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

def assign_all_weights(rel: dict[typing.Any, list[tuple[int, int]]],num_nodes: int, weight: float):
    rel_0 = rel[0]
    rel_1 = rel[1]
    rel_d = rel['d']

    e_completed =rel_0 + rel_1 + make_partial.recreate_symmetry(rel_d)
    e_complement = [(i,j) for i in range(num_nodes) for j in range(num_nodes) if (i,j) not in e_completed and i != j]
    
    return {
        1: assign_rel_weights(e_completed,e_complement,rel_1,weight),
        0: assign_rel_weights(e_completed,e_complement,rel_0,weight),
        'd': assign_rel_weights(e_completed,e_complement,rel_d,weight),
    }, e_completed, e_complement


    




if __name__ == "__main__":
    while True:
        tree = random_trees.generate_random_cotree(3)
        num_leaves = len([node for node in tree.nodes if tree.out_degree(node) == 0])
        tree_rel = lib.cotree_to_rel(tree)
        partial = make_partial.make_partial(tree_rel,0.2)
        weights, e_completed, e_complement = assign_all_weights(partial,num_leaves,1.)
        try:
            test = lib.algorithm_two(list(range(num_leaves)),weights['d'],weights[1],weights[0])
        except Exception as e:
            print(tree.nodes.data())
            print(e)
            print(f'{partial=}')
            print()
            print(f'{tree_rel=}')
            print()
            print(f'{weights=}')
            print()
            print(f'{e_completed=}')
            print()
            print(f'{e_complement=}')
            break