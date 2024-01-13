import networkx
import sys

sys.path.append('fitch-graph-prak')

import lib
from fitch_utils.weights import assign_all_weights
import random


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

def partition_random(graph: networkx.Graph):
    partitions = ([], [])
    # num_nodes = graph.number_of_nodes()
    for n in graph.nodes:
        ran = random.randint(0, 1)
        partitions[ran].append(n)

    if not any(partitions[0]):
        index = random.randint(0, len(partitions[1])-1)
        partitions[0].append(partitions[1].pop(index))
    if not any(partitions[1]):
        index = random.randint(0, len(partitions[0])-1)
        partitions[1].append(partitions[0].pop(index))
    return partitions

def partition_right_solo(graph: networkx.Graph):
    left = [n for n in graph.nodes]
    # initialize right with 1 node
    right = [left.pop()]
    return left, right

def partition_left_solo(graph: networkx.Graph):
    left = [n for n in graph.nodes]
    # initialize right with 1 node
    right = [left.pop(0)]
    return left, right





if __name__ == '__main__':
    num_nodes = 10
    rel = {0:[], 1:[], 'd':[]}
    weights = assign_all_weights(rel, num_nodes, 'normal')
    
    # result_sum = lib.partition_heuristic_scaffold(weights['d'], weights[1], weights[0], list(range(num_nodes)),partition_greedy_sum,score_sum)
    # print(f'{result_sum=}')
    # result_average = lib.partition_heuristic_scaffold(weights['d'], weights[1], weights[0], list(range(num_nodes)),partition_random,score_average)
    # difference = lib.sym_diff(result_sum, result_average, num_nodes)
    # print(f'{result_sum=}')
    # print(f'{result_average=}')
    # print(f'{difference=}')

    result_right = lib.partition_heuristic_scaffold(weights['d'], weights[1], weights[0], list(range(num_nodes)),partition_right_solo,score_sum)
    print(f'{result_right=}')
    result_left = lib.partition_heuristic_scaffold(weights['d'], weights[1], weights[0], list(range(num_nodes)),partition_left_solo,score_sum)
    print(f'{result_right=}')
    print(f'{result_left=}')
    difference = lib.sym_diff(result_right, result_left, num_nodes)
    print(f'{difference=}')