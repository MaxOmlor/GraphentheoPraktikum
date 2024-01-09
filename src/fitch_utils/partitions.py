import networkx
import sys

sys.path.append('fitch-graph-prak')

import lib

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
    # initialize partitions, fill left with all nodes
    left = [n for n in graph.nodes]
    # initialize right with 1 node
    right = [left.pop()]
    # initialize scores
    score = score_function(left, right, graph.edges)


    return left, right
