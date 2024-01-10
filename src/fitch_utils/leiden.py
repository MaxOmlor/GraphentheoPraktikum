import networkx
import numpy as np
import copy
import math


def is_iterable(obj):
    try:
        iter(obj)
        return True
    except TypeError:
        return False

def flatten(l: list):
    if is_iterable(l):
        flat_list = []
        for item in l:
            list_item = flatten(item)
            flat_list += list_item

        return flat_list
    else:
        return [l]

def len_flatten(iterable) -> int:
    return len(flatten(iterable))

def collapse_nodes(graph: networkx.Graph, u,v):
    new_node = (u, v)
    new_node = tuple(flatten(new_node))

    result_graph = copy.deepcopy(graph)
    result_graph.add_node(new_node)

    neighbours = set(graph.neighbors(u)) | set(graph.neighbors(v))
    for n in neighbours:
        weight = 0
        if (n, u) in graph.edges and (n, v) in graph.edges:
            weight = graph.edges[(u, n)]['weight'] + graph.edges[(v, n)]['weight']
        elif (n, u) in graph.edges:
            weight = graph.edges[(u, n)]['weight']
        else:
            weight = graph.edges[(v, n)]['weight']

        result_graph.add_edge(new_node, n, weight=weight)

    result_graph.remove_node(u)
    result_graph.remove_node(v)
    return result_graph, new_node

def move_node_to_partition(partitions: list[list], node, partition_index):
    result_partitions = copy.deepcopy(partitions)
    for p in result_partitions:
        if node in p:
            p.remove(node)
    result_partitions[partition_index].append(node)
    result_partitions = [p for p in result_partitions if p]
    return result_partitions

def quality_function(graph: networkx.Graph, partitions: list[list]):
    weight = 0
    for p in partitions:
        # sum weights of all edges in partition
        p_weight = 0
        for u in p:
            for v in p:
                if u == v:
                    continue
                if (u,v) in graph.edges:
                    p_weight += graph.edges[(u,v)]['weight']
        weight += p_weight
    return -weight

def quality_function_2part(graph: networkx.Graph, partitions: list[list]):
    weight = quality_function(graph, partitions)

    distance_2parts = abs(len(partitions)-2)

    max_weight = -min(graph.edges[e]['weight'] for e in graph.edges)*graph.number_of_edges()
    print(f'{weight=}, {max_weight=}, {distance_2parts=} -> {weight - max_weight*distance_2parts}')
    print(f'{partitions=}')
    return weight - max_weight*distance_2parts

def find_best_move(partitions, q_func, v):
    modified_partitions = [move_node_to_partition(partitions, v, i) for i,c in enumerate(partitions)]
    modified_partition_qualities = [q_func(graph,p) for p in modified_partitions]
    
    h_p = q_func(graph,partitions)
    modified_partition_deltas = [q-h_p for q in modified_partition_qualities]
    
    maxid = np.argmax(modified_partition_deltas)

    delta = modified_partition_deltas[maxid]
    best_partition = modified_partitions[maxid]

    return delta, best_partition

def move_nodes_fast(graph: networkx.Graph, partitions: list[list]):
    queue = graph.nodes
    q_func = quality_function_2part
    result_partitions = copy.deepcopy(partitions)

    while any(queue):
        v = queue.pop(0)
        
        delta, best_partition = find_best_move(result_partitions, q_func, v)
        
        if delta > 0:
            result_partitions = best_partition
            # get nodes adjacent to n
            neighbors = [neigh for neigh in set(graph.neighbors(v)) if neigh not in best_partition]
            queue += [n for n in neighbors if n not in queue]
                
    return result_partitions

def aggregate_graph(graph: networkx.Graph, partitions: list[list]) -> networkx.Graph:
    result_graph = graph

    for p in partitions:
        if len(p) <= 1:
            continue
        
        new_node = p[0]
        for n in p[1:]:
            result_graph, new_node = collapse_nodes(result_graph, new_node, n)
    return result_graph

def singleton_partition(graph: networkx.Graph):
    partitions = []
    for n in graph.nodes:
        partitions.append([n])
    return partitions

def partition_leiden_normalized(graph: networkx.Graph):
    # normalize weights, i.e. subtract the average weight from each edge
    mean_weight = np.mean([graph.edges[e]['weight'] for e in graph.edges])
    
    mean_graph = copy.deepcopy(graph)
    
    for e in mean_graph.edges:
        mean_graph.edges[e]['weight'] -= mean_weight
        
    return partition_leiden(mean_graph)

def refine_partition(graph: networkx.Graph, partitions: list[list]):
    refined_partitions = singleton_partition(graph)
    for p in partitions:
        refined_partitions = merge_nodes_subset(graph, refined_partitions, p)
    return refined_partitions

def get_edges(set1, set2):
    if isinstance(set1, int): # wenn node^
        set1 = [set1]
    return [graph.edges[(v,w)]['weight'] for w in set2 for v in set1]

def merge_nodes_subset(graph: networkx.Graph, partitions: list[list], subset):
    connectivness_threshhold = .8
    result_partitions = copy.deepcopy(partitions)

    R = [v for v in subset
         if sum(get_edges(v, subset))
            >= connectivness_threshhold*len_flatten(v) * (len_flatten(subset) - len_flatten(v))]

    for v in R:
        if [v] in partitions:
            T = [c for c in partitions
                 if set(c).issubset(set(subset))
                 and sum(get_edges(c, subset))]
    
    return result_partitions

def partition_leiden(graph: networkx.Graph):
    current_graph = graph # G
    partitions = singleton_partition(current_graph)
    done = False
    while True:
        partitions = move_nodes_fast(current_graph, partitions)
        done = len(partitions) == len(current_graph.nodes)
        if not done:
            partitions = refine_partition(current_graph, partitions)
            current_graph = aggregate_graph(current_graph, partitions)

        if done:
            break
    # return flatten(partitions)
    #remove empty partitions
    return [flatten(p) for p in partitions]

if __name__ == '__main__':
    num_nodes = 4

    graph = networkx.Graph()
    graph.add_nodes_from(range(num_nodes))
    graph.add_edge(0,1, weight=0)
    graph.add_edge(0,2, weight=1)
    graph.add_edge(0,3, weight=1)
    graph.add_edge(1,2, weight=1)
    graph.add_edge(1,3, weight=1)
    graph.add_edge(2,3, weight=1)


    partitions = partition_leiden(graph)

    print(partitions)