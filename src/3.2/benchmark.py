import networkx as nx
import os
import sys
import random
import typing

import random_trees
import make_partial

sys.path.append('fitch-graph-prak')

from lib import algorithm_two



def assign_edge_weights(rel: list[tuple[int, int]],num_nodes: int, weight: float):
    ret = []
    for i in range(num_nodes):
        for j in range(num_nodes):
            if (i==j):
                if((i,j) in rel):
                    ret.append((i,j,weight))
                else:
                    ret.append((i,j,0.))
    return ret
    

def assign_all_weights(rel: dict[typing.Any, list[tuple[int, int]]],num_nodes: int, weight: float):
    rel_0 = rel[0]
    rel_1 = rel[1]
    rel_d = rel['d']

    rel_0_weights = assign_edge_weights(rel_0,num_nodes,weight)
    rel_1_weights = assign_edge_weights(rel_1,num_nodes,weight)
    rel_d_weights = assign_edge_weights(rel_d,num_nodes,weight)

    return {
        0: rel_0_weights,
        1: rel_1_weights,
        'd': rel_d_weights,
    }

if __name__ == "__main__":
    tree = random_trees.generate_random_cotree(10)
    num_leaves = len([node for node in tree.nodes if tree.out_degree(node) == 0])
    partial = make_partial.make_partial(graph_to_rel(tree),0.2)
    weights = assign_all_weights(partial,10,1.)

    test = algorithm_two(weights['d'],weights[1],weights[0],num_leaves)