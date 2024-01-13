import networkx
import numpy as np
import copy
import math
import random


def dprint(out: str):
    if True:
        print(out)


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

def move_node_to_partition(partitions: list[list], node, partition):
    print('#'*20)
    print("move_node_to_partition:")
    print(f'{partitions=}')
    print(f'{node=}')
    print(f'{partition=}')
    if partition not in partitions:
        raise ValueError(f'partition must be in partitions! {partition=} not in {partitions=}')
    
    partition_index = partitions.index(partition)

    result_partitions = copy.deepcopy(partitions)
    
    # remove node from old partition
    for p in result_partitions:
        if node in p:
            p.remove(node)

    # add node to a certain partition
    result_partitions[partition_index].append(node)

    # remove empty comunities
    result_partitions = [p for p in result_partitions if p]
    
    print(f'{result_partitions=}')
    print('#'*20)
    return result_partitions

def quality_function(graph: networkx.Graph, partitions: list[list]) -> float:
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

def quality_function_2part(graph: networkx.Graph, partitions: list[list]) -> float:
    weight = quality_function(graph, partitions)

    distance_2parts = abs(len(partitions)-2)

    max_weight = -min(graph.edges[e]['weight'] for e in graph.edges)*graph.number_of_edges()
    #dprint(f'{graph.number_of_edges()=}, {weight=}, {max_weight=}, {distance_2parts=} -> {weight - max_weight*distance_2parts}')
    #dprint(f'{partitions=}')
    return weight - max_weight*distance_2parts

def modified_partition_delta(aggregate_graph: networkx.Graph,original_graph: networkx.Graph, v, subset, h_p, q_func,partitions):
    p = move_node_to_partition(partitions, v, subset)
    p_flattend = [flatten(c) for c in p]
    q = q_func(original_graph,p_flattend)
    #dprint(f'{q=} {h_p=} {q-h_p=}')
    return q-h_p

def find_best_move(graph: networkx.Graph,partitions, q_func, v):
    h_p = q_func(graph,partitions)
    modified_partitions = [move_node_to_partition(partitions, v, c) for c in partitions]
    modified_partition_qualities = [q_func(graph,p) for p in modified_partitions]
    
    modified_partition_deltas = [q-h_p for q in modified_partition_qualities]
    # modified_partition_deltas = [modified_partition_delta(graph, v, c, h_p, q_func) for c in partitions]
    
    maxid = np.argmax(modified_partition_deltas)

    delta = modified_partition_deltas[maxid]
    best_partition = modified_partitions[maxid]

    return delta, best_partition

def move_nodes_fast(graph: networkx.Graph, partitions: list[list], q_func):
    print('#'*20)
    print("move_nodes_fast")
    queue = [n for n in graph.nodes]
    print(f'{queue=}')
    result_partitions = copy.deepcopy(partitions)

    while any(queue):
        v = queue.pop(0)
        
        delta, best_partition = find_best_move(graph,result_partitions, q_func, v)
        
        if delta > 0:
            if(len(best_partition) > len(result_partitions)):
                ###dprint all graph nodes
                raise ValueError(f'best_partition should be smaller than result_partitions! {best_partition=} not in {result_partitions=}')
            result_partitions = best_partition
            # get nodes adjacent to n
            neighbors = [neigh for neigh in set(graph.neighbors(v)) if neigh not in best_partition]
            queue += [n for n in neighbors if n not in queue]
            print(f'{queue=}')
                
    print('#'*20)
    return result_partitions

def create_aggregate_graph(graph: networkx.Graph, partitions: list[list]) -> networkx.Graph:
    dprint("create_aggregate_graph:")
    result_graph = graph

    for p in partitions:
        if len(p) <= 1:
            continue
        
        new_node = p[0]
        for n in p[1:]:
            result_graph, new_node = collapse_nodes(result_graph, new_node, n)
    dprint(f'{result_graph.nodes=}')
    return result_graph

def singleton_partition(graph: networkx.Graph):
    partitions = []
    for n in graph.nodes:
        partitions.append([n])
    return partitions

def partition_leiden_normalized(graph: networkx.Graph):
    #dprint("partition_leiden_normalized")
             # normalize weights, i.e. subtract the average weight from each edge
    mean_weight = np.mean([graph.edges[e]['weight'] for e in graph.edges])
    
    mean_graph = copy.deepcopy(graph)
    
    for e in mean_graph.edges:
        mean_graph.edges[e]['weight'] -= mean_weight
        #dprint(f'{mean_graph.edges[e]=}')
        
    return partition_leiden(mean_graph)

def refine_partition(aggregate_graph: networkx.Graph,original_graph: networkx.Graph, partitions: list[list], q_func):
    refined_partitions = singleton_partition(aggregate_graph)
    for p in partitions:
        refined_partitions = merge_nodes_subset(aggregate_graph,original_graph, refined_partitions, p, q_func)
    return refined_partitions

def get_edges_weights(graph: networkx.Graph,set1, set2):
    if isinstance(set1, int): # wenn node
        set1 = [set1]
    #dprint(f'{set1=}, {set2=}')
    flat_set1 = flatten(set1)
    flat_set2 = flatten(set2)
    #dprint(f'{flat_set1=}, {flat_set2=}')
    #dprint(f'{graph.nodes=}')
    return [graph.edges[(v,w)]['weight'] for w in flatten(set2) for v in flatten(set1) if w != v]

def is_well_connected(graph: networkx.Graph,set1, set2) -> bool:
    connectivness_threshhold = 0
    # return sum(get_edges_weights(set1, set2)) >= connectivness_threshhold*len_flatten(set1) * (len_flatten(set2) - len_flatten(set1))
    #dprint(f'{set1=}, {set2=}')
    ret_sum = sum(get_edges_weights(graph,set1, set2))
    #dprint(f'{ret_sum=}')
    return ret_sum <= connectivness_threshhold

def get_prop(aggregate_graph: networkx.Graph,original_graph: networkx.Graph, v, subset, h_p, q_func, degree_of_randomness, partitions):
    part_delta = modified_partition_delta(aggregate_graph,original_graph, v, subset, h_p, q_func,partitions)
    #dprint(f'{part_delta=}')

    if part_delta >= 0:
        #dprint(f'{degree_of_randomness=}')
        ####todo: Fix this
        try:
            #dprint(f'{math.exp((1/degree_of_randomness) * part_delta)=}')
            return math.exp((1/degree_of_randomness) * part_delta)
        except:
            # return largest float possible
            return 10e200
    else:
        return 0

def get_props(aggregate_graph: networkx.Graph,original_graph: networkx.Graph, partitions, v, T, q_func):
    degree_of_randomness = 0.01
    partitions_flat = [flatten(p) for p in partitions]
    h_p = q_func(original_graph,partitions_flat)

    props = [get_prop(aggregate_graph,original_graph, v, c, h_p, q_func, degree_of_randomness,partitions) for c in T]
    return props

def merge_nodes_subset(aggregate_graph: networkx.Graph,original_graph: networkx.Graph, partitions: list[list], subset, q_func):
    ####
    dprint("#################################################")
    dprint("merge_nodes_subset:")
    result_partitions = copy.deepcopy(partitions)
    dprint(f'{subset=}')

    R = [v for v in subset if is_well_connected(original_graph,v, subset)]

    dprint(f'{R=}')

    for v in R:
        if [v] in result_partitions:
            T = [c for c in result_partitions if is_well_connected(original_graph,v, subset)]
            props = get_props(aggregate_graph, original_graph, result_partitions, v, T, q_func)
            random.seed(42) #for reproducability of results. If you find this in the final version, please remove it.
            partition = random.choices(T, props, k=1)[0]
            dprint(f'  {partition=}')
            dprint(f'  {v=}')
            dprint(f'  {result_partitions=}')
            dprint(f'  {props=}')
            if not v in partition:
                partition.append(v)
                result_partitions.remove([v])
    dprint(f'{result_partitions=}')
    dprint("#################################################")
    return result_partitions

def partition_leiden(graph: networkx.Graph):
    q_func = quality_function_2part

    aggregate_graph = graph # G
    original_graph = copy.deepcopy(graph) # G_0
    partitions = singleton_partition(aggregate_graph)
    done = False
    while True:
        partitions = move_nodes_fast(aggregate_graph, partitions, q_func)
        done = len(partitions) == 2#len(aggregate_graph.nodes)# This condition can not be true if we do not merge nodes in the graph.
        ### Possible solution: Keep track of two graphs, one with merged nodes and one without. The one without is used for edge checking
        ### The one with is used for merging nodes.
        if not done:
            partitions = refine_partition(aggregate_graph, original_graph, partitions, q_func)
            aggregate_graph = create_aggregate_graph(aggregate_graph, partitions)


        if done:
            break
    # return flatten(partitions)
    #remove empty partitions
    partition_flat = [flatten(p) for p in partitions]
    dprint(f'{partition_flat=}')
    return partition_flat

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


    partitions = partition_leiden_normalized(graph)

    dprint(partitions)