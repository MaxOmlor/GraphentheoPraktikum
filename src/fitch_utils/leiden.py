import networkx
import random

# def create_singleton_partition(graph: networkx.Graph):
#     partitions = []
#     for n in graph.nodes:
#         partitions.append([n])
#     return partitions

# def move_nodes_fast(graph: networkx.Graph, partitions):
#     queue = [for n in graph.nodes]
#     random.shuffle(queue)

#     while len(queue) > 0:
#         node = queue.pop()
#         partition_max = find_max_partition(graph, partitions, node)
#         if quality_function(graph, partitions)

#     return partitions



# def partition_leiden(graph: networkx.Graph):
#     partition =  create_singleton_partition(graph)

    
#     partition = move_nodes_fast(graph, partition)
    

graph = networkx.Graph()
graph.add_node(1)
graph.add_node(2)

graph.add_edge(1,2, weight=1)

print(graph.edges[(2,1)]['weight'])
print((2,1) in graph.edges)