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
            if i != j and ((i, j) in weights or (j, i) in weights):
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
            if i != j and ((i, j) in weights or (j, i) in weights):
                weight += weights[(i, j)]
    return weight


# weights are saved in the graph as edge attributes
def partition_greedy(graph: networkx.Graph):
    # initialize partitions
    left = []
    right = []
    # initialize scores
    left_score = 0
    right_score = 0

    # add nodes to partitions until no improvement is possible
    while True:
        # initialize best score and best node
        best_score = 0
        best_node = -1
        # iterate over all nodes
        for node in graph.nodes:
            # if the node is not yet in a partition
            if node not in left and node not in right:
                # calculate the score of the node in the left partition
                left.append(node)
                score = score_average(left, right, graph.edges)
                left.remove(node)
                # if the score is better than the current best score, save it
                if score > best_score:
                    best_score = score
                    best_node = node
        # if no improvement is possible, stop
        if best_score <= left_score:
            break
        # otherwise, add the best node to the left partition
        left.append(best_node)
        left_score = best_score

        # initialize best score and best node
        best_score = 0
        best_node = -1
        # iterate over all nodes
        for node in graph.nodes:
            # if the node is not yet in a partition
            if node not in left and node not in right:
                # calculate the score of the node in the right partition
                right.append(node)
                score = score_average(left, right, graph.edges)
                right.remove(node)
                # if the score is better than the current best score, save it
                if score > best_score:
                    best_score = score
                    best_node = node
        # if no improvement is possible, stop
        if best_score <= right_score:
            break
        # otherwise, add the best node to the right partition
        right.append(best_node)
        right_score = best_score

    return left, right
