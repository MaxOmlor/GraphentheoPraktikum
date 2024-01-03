import networkx as nx
import os
import sys

sys.path.append('fitch-graph-prak')

from lib import graph_to_rel

graph_path = 'graph-prak-GFH/graph-prak-GFH/n10/D0.25_L0.5_H1.0/D0.25_L0.5_H1.0_n10_0/dFitch.graphml'

nx_graph = nx.read_graphml(graph_path)
print('graph loaded')

rel = graph_to_rel(nx_graph)
print(f'{rel=}')