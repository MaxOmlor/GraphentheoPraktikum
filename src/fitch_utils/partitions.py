import networkx
import sys

sys.path.append('fitch-graph-prak')

import lib
from weights import assign_all_weights


# scoring functions get a list of lists (node partitions) and weighted edges
def score_average(left: list[int], right: list[int], weights: dict[tuple[int, int], float]):
    # calculate the weight of the edges between the partitions
    count = 0
    weight = 0
    for i in left:
        for j in right:
            if i != j and ((i, j) in weights):
                weight += weights[(i, j)]
                count += 1
    if count == 0:
        return 0
    return weight / count


def score_sum(left: list[int], right: list[int], weights: dict[tuple[int, int], float]):
    # calculate the weight of the edges between the partitions
    weight = 0
    for i in left:
        for j in right:
            if i != j and ((i, j) in weights):
                weight += weights[(i, j)]
    return weight

def partition_greedy_average(graph: networkx.Graph):
    return partition_greedy(graph, score_average)

def partition_greedy_sum(graph: networkx.Graph):
    return partition_greedy(graph, score_sum)

# weights are saved in the graph as edge attributes
def partition_greedy(graph: networkx.Graph, score_function):
    # create a dict with edges and weights
    weights = {}
    for e in graph.edges:
        weights[e] = graph.edges[e]['weight']
    # initialize partitions, fill left with all nodes
    left = [n for n in graph.nodes]
    # initialize right with 1 node
    right = [left.pop()]
    # initialize scores
    score = score_function(left, right, weights)
    
    while True:
        for n in left:
            left_temp = left.copy()
            left_temp.remove(n)
            right_temp = right.copy()
            right_temp.append(n)
            score_temp = score_function(left_temp, right_temp, weights)
            if score_temp > score:
                left = left_temp
                right = right_temp
                score = score_temp
                break
        else:
            break

    return left, right


if __name__ == '__main__':
    num_nodes = 8
    rel = {0:[], 1:[], 'd':[]}
    weights = assign_all_weights(rel, num_nodes, 'normal')
    print(f'{weights=}')
    result = lib.partition_heuristic_scaffold(weights['d'], weights[1], weights[0], list(range(num_nodes)),partition_greedy_sum,score_sum)
    print(f'{result=}')