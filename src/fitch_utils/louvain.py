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

def collapse_nodes(graph: networkx.Graph, u,v):
    new_node = (u, v)
    new_node = tuple(flatten(new_node))

    result_graph = copy.deepcopy(graph)
    result_graph.add_node(new_node)

    neighbours = set(graph.neighbors(u)) | set(graph.neighbors(v))
    for n in neighbours:
        weight = 0
        if (n, u) in graph.edges and (n, v) in graph.edges:
            weight = max(graph.edges[(u, n)]['weight'], graph.edges[(v, n)]['weight'])
        elif (n, u) in graph.edges:
            weight = graph.edges[(u, n)]['weight']
        else:
            weight = graph.edges[(v, n)]['weight']

        result_graph.add_edge(new_node, n, weight=weight)

    result_graph.remove_node(u)
    result_graph.remove_node(v)
    return result_graph, new_node

def move_node_to_partition(partitions, node, partition_index):
    result_partitions = copy.deepcopy(partitions)
    for p in result_partitions:
        if node in p:
            p.remove(node)
    result_partitions[partition_index].append(node)
    result_partitions = [p for p in result_partitions if p]
    return result_partitions

def quality_function(graph: networkx.Graph, partitions):
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

def quality_function_2part(graph: networkx.Graph, partitions):
    weight = quality_function(graph, partitions)

    distance_2parts = abs(len(partitions)-2)

    max_weight = -min(graph.edges[e]['weight'] for e in graph.edges)*graph.number_of_edges()
    return weight - max_weight*distance_2parts

def move_nodes(graph: networkx.Graph, partitions):
    q_func = quality_function_2part
    result_partitions = copy.deepcopy(partitions)

    while True:
        h_old = q_func(graph, result_partitions)
        for n in graph.nodes:
            modified_partitions = [move_node_to_partition(result_partitions, n, i) for i,c in enumerate(result_partitions)]
            modified_partition_qualities = [q_func(graph,p) for p in modified_partitions]
            
            h_p = q_func(graph,result_partitions)
            modified_partition_deltas = [q-h_p for q in modified_partition_qualities]
            
            maxid = np.argmax(modified_partition_deltas)
            
            if modified_partition_deltas[maxid] > 0:
                result_partitions = modified_partitions[maxid]

        h_new = q_func(graph, result_partitions)
        if not h_new > h_old:
            break

    return result_partitions

def aggregate_graph(graph: networkx.Graph, partitions):
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

def partition_louvain_normalized(graph: networkx.Graph):
    # normalize weights, i.e. subtract the average weight from each edge
    mean_weight = np.mean([graph.edges[e]['weight'] for e in graph.edges])
    
    mean_graph = copy.deepcopy(graph)
    
    for e in mean_graph.edges:
        mean_graph.edges[e]['weight'] -= mean_weight
        
    return partition_louvain(mean_graph)

def partition_louvain(graph: networkx.Graph):
    current_graph = graph # G
    partitions = singleton_partition(current_graph)
    done = False
    while True:
        partitions = move_nodes(current_graph, partitions)
        done = len(partitions) == len(current_graph.nodes)
        if not done:
            current_graph = aggregate_graph(current_graph, partitions)
            partitions = singleton_partition(current_graph)

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


    partitions = partition_louvain_normalized(graph)

    (partitions)