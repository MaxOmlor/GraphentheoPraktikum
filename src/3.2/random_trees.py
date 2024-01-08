import networkx as nx
import os
import sys
import random
import typing
import hashlib
import argparse
import make_partial

sys.path.append('fitch-graph-prak')

import lib


# relabel leaves of a tree with integers from 0 to n-1 to fulfill the requirements of cograph_to_rel
def relabel_leaves(tree: nx.DiGraph):
    count = 0
    for node in tree.nodes:
        if tree.out_degree(node) == 0:
            tree.nodes[node]["symbol"] = count
            count += 1
    return tree

# Implementation of probabilistic binary tree automata to generate random trees.
# The automaton is defined by a list of states, a list of alphabet symbols, a list of transitions, and an initial state.
# Each transition is a tuple of the form (state, symbol, left_child_state, right_child_state, weight).
# Left and right child states can also be symbols from the alphabet.
# Weights do not need to be normalized, but should be positive.
# Labels will be saved to the 'symbol' attribute of the nodes.
class TreeAutomaton:
    def __init__(self, states: list[str], alphabet: list[str],transitions: list[tuple[str,str, str, str,float]], initial_state: [str]):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.initial_state = initial_state

        self.current_nodes = 0

    def get_transitions(self, state: str):
        return [t for t in self.transitions if t[0] == state]
    
    #add a node to the tree, and increment the current node counter
    def add_node(self, state: str):
        self.tree.add_node(self.current_nodes, symbol=state)
        self.current_nodes += 1

    def generate_tree_rec(self, node: int):
        #get current state
        state = self.tree.nodes[node]['symbol']
        #get possible transitions
        transitions = self.get_transitions(state)
        #if no transitions are possible, return
        if len(transitions) == 0:
            return
        #pick random transition
        transition = random.choices(transitions, weights=[t[4] for t in transitions])[0]
        
        #relabel current node
        self.tree.nodes[node]["symbol"] = transition[1]
        #add children
        self.add_node(transition[2])
        self.add_node(transition[3])
        left_node_id = self.current_nodes-2
        right_node_id = self.current_nodes-1
        self.tree.add_edge(node, left_node_id)
        self.tree.add_edge(node, right_node_id)
        self.generate_tree_rec(left_node_id)
        self.generate_tree_rec(right_node_id)

    def generate_tree(self):
        self.tree = nx.DiGraph()
        self.add_node(self.initial_state)
        self.generate_tree_rec(0)
        self.current_nodes = 0
        return self.tree


# Sets up transitions of a probabilistic tree automaton that generates a random fitch_cograph and return said tree
def generate_fitch_cotree(w_2_terminals = 4., w_1_terminal = 2., w_0_terminals = 1., factor_e0 = .1, factor_e1 = 2.):
    states = ['E01D', 'E0', 'E0D']
    alphabet = ["", "e", "b", "u"]
    transitions = [
        ("E01D", "e", "E0", "E0", w_0_terminals * factor_e0),
        ("E01D", "e", "", "", w_2_terminals * factor_e0),
        ("E01D", "e", "E0", "", w_1_terminal * factor_e0),
        ("E01D", "e", "", "E0", w_1_terminal * factor_e0),
        ("E01D", "b", "E01D", "E01D", w_0_terminals * factor_e1),
        ("E01D", "b", "", "E01D", w_1_terminal * factor_e1),
        ("E01D", "b", "E01D", "", w_1_terminal * factor_e1),
        ("E01D", "b", "", "", w_2_terminals * factor_e1),
        ("E01D", "u", "E0D", "E01D", w_0_terminals),
        ("E01D", "u", "E0D", "", w_1_terminal),
        ("E01D", "u", "", "E01D", w_1_terminal),
        ("E01D", "u", "", "", w_2_terminals),   
        ("E0", "e", "", "", w_2_terminals * factor_e0),
        ("E0", "e", "E0", "", w_1_terminal * factor_e0),
        ("E0", "e", "", "E0", w_1_terminal * factor_e0),
        ("E0", "e", "E0", "E0", w_0_terminals * factor_e0),
        ("E0D", "e", "", "", w_2_terminals* factor_e0),
        ("E0D", "e", "E0", "", w_1_terminal * factor_e0),
        ("E0D", "e", "", "E0", w_1_terminal * factor_e0),  
        ("E0D", "e", "E0", "E0", w_0_terminals * factor_e0),
        ("E0D", "u", "", "", w_2_terminals),
        ("E0D", "u", "E0D", "", w_1_terminal),
        ("E0D", "u", "", "E0D", w_1_terminal),
        ("E0D", "u", "E0D", "E0D", w_0_terminals),
    ]
    initial_state = "E01D"
    A = TreeAutomaton(states, alphabet, transitions, initial_state)
    tree = A.generate_tree()
    relabel_leaves(tree)
    return tree

def generate_fitch_graph(tree: nx.DiGraph):
    rel = lib.cotree_to_rel(tree)
    #count leaves
    nodes = sum([tree.out_degree(node) == 0 for node in tree.nodes]) 
    fitch = lib.rel_to_fitch(rel, range(nodes))
    return fitch

def generate_random_cotree(min_size: int = 3):
    ### generate random cotree until it has at least min_size leaves
    found = False
    while not found:
        tree = generate_fitch_cotree()
        leaves = sum([tree.out_degree(node) == 0 for node in tree.nodes])
        if leaves >= min_size:
            found = True
    return tree

def generate_random_partial(percent: float, min_size: int = 3, remove_all_directed: bool = False):
    ### generate random cotree
    tree = generate_random_cotree(min_size)
    ###convert to rel
    rel = lib.cotree_to_rel(tree)
    ### generate partial rel
    partial_rel = make_partial.make_partial(rel, percent, remove_all_directed)
    return partial_rel


def create_testset(n: int, path: str, fitch_graphs: bool = True, cotrees: bool = True, min_size: int = 3, verbose: bool = False):
    ### ensure directory exists

    if not os.path.exists(path + "/cotrees"):
        os.makedirs(path + "/cotrees", exist_ok=True)
    if not os.path.exists(path + "/fitch"):
        os.makedirs(path + "/fitch", exist_ok=True)
    
    ### avoid duplicate testcases, small trees have a high probability of being duplicates
    hashes = set()

    ### generate testcases
    attempts = 0
    for i in range(n):
        found_non_duplicate = False
        while not found_non_duplicate:
            attempts += 1
            ### generate random cotree
            tree = generate_fitch_cotree()
            ### check for minimum size
            leaves = sum([tree.out_degree(node) == 0 for node in tree.nodes])
            if leaves < min_size:
                continue
            ### calculate hash
            hashed = hash(tree)
            ### check for duplicates
            if hashed in hashes:
                continue
            found_non_duplicate = True
            ### generate fitch graph
            fitch = generate_fitch_graph(tree)
            hashes.add(hashed)
            ### save cotree
            if cotrees:
                filepath = path + "/cotrees/" + str(i) + ".graphml"
                fullpath = os.path.abspath(filepath)
                nx.write_graphml(tree, fullpath)
                if verbose:
                    print(fullpath)
            ### save fitch graph
            if fitch_graphs:
                filepath = path + "/fitch/" + str(i) + ".graphml"
                fullpath = os.path.abspath(filepath)
                nx.write_graphml(fitch, fullpath)
                if verbose:
                    print(fullpath)

    



if __name__ == "__main__":
    ### parse arguments
    parser = argparse.ArgumentParser(description='Generate random testset.')
    parser.add_argument('n', type=int, help='number of testcases to generate')
    parser.add_argument('path', type=str , help='path to save testset to')
    parser.add_argument('--fitch_graphs', default=True, help='generate fitch graphs')
    parser.add_argument('--cotrees', default=True, help='generate cotrees')
    parser.add_argument('-min_size', type=int, default=3, help='minimum size of generated trees')
    parser.add_argument('-v', '--verbose',default=False, action='store_true', help='verbose output')

    args = parser.parse_args()

    create_testset(args.n, args.path, args.fitch_graphs, args.cotrees, args.min_size, args.verbose)