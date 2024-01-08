# time
# tree vergleich

import sys
import os
import argparse
import networkx as nx
from datetime import datetime
from tqdm import tqdm
import csv
from pyfiglet import Figlet


from single_scripts import Alg1, Alg2
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fitch_utils.random_trees import generate_random_cotree
from fitch_utils.make_partial import make_partial


sys.path.append('fitch-graph-prak')
import lib


import math
def create_tree_data(num_trees: int, min_size: int=0, max_size: int=math.inf):
    trees = []
    hashes = set()

    while len(hashes) < num_trees:
        tree = generate_random_cotree()
        leaves = sum([tree.out_degree(node) == 0 for node in tree.nodes])
        if min_size <= leaves <= max_size:
            hashed = hash(tree)
            if hashed not in hashes:
                hashes.add(hashed)
                trees.append(tree)
    return trees

### reads the file, reads the paths in that file and loads those trees
def get_tree_data_from_file(path: str):
    trees = []
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if line == '':
                continue
            tree = nx.read_graphml(line)
            trees.append(tree)
    return trees

def run_single_benchmark(run_func, data, rel, leaves):
    start_time = datetime.now()
    output = run_func.run(data)
    delta_time = datetime.now() - start_time

    symmetric_difference = lib.sym_diff(output, rel, leaves)
    return {
        'delta_time': delta_time,
        'symmetric_difference': symmetric_difference,
        'nodes': leaves,
        'rel_size': len(rel[0]) + len(rel[1]) + len(rel['d']),
    }

def dict_list_to_csv(dict_list: list[dict], file_path: str):
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=dict_list[0].keys())

        # Schreiben der Kopfzeile
        writer.writeheader()

        # Schreiben der Daten
        for d in dict_list:
            if set(dict_list[0].keys()) != d.keys():
                raise ValueError(f'dict in list must contain the same keys {dict_list[0].keys()=} != {d.keys()=}')
            writer.writerow(d)

def run_benchmark(args):
    # setup
    ### create trees
    trees = []
    if args.trees:
        trees = create_tree_data(args.runs, min_size=args.min, max_size=args.max)
    if args.input:
        trees = trees + get_tree_data_from_file(args.input)
    if len(trees) == 0:
        print('No trees found')
        return
    
    ### get relations
    relations = [lib.cotree_to_rel(tree) for tree in trees]

    ### create partials
    partials = [make_partial(rel, args.partial) for rel in relations]

    # run
    ### run alg1
    results = []
    # for i in range(len(trees)):
    for tree, rel, partial in tqdm(zip(trees, relations, partials), 'run benchmark'):
        leaves = sum([tree.out_degree(node) == 0 for node in tree.nodes])
        tree_hash = hash(tree)

        if args.alg1:
            ## count tree leaves

            data = Alg1.preprocess(partial, leaves, (0,1,2))
            
            result = run_single_benchmark(Alg1, data, rel, leaves)
            results.append({**result, 'tree': tree_hash, 'alg': 'Alg1'})

        if args.alg2:
            data = Alg2.preprocess(partial, leaves)
            
            result = run_single_benchmark(Alg2, data, rel, leaves)
            results.append({**result, 'tree': tree_hash, 'alg': 'Alg2'})

        if args.normal:
            data = Alg2.preprocess(partial, leaves, 'normal', {'present': (0.8, 1,1), 'nonpresent': (.5,1,1)})
            
            result = run_single_benchmark(Alg2, data, rel, leaves)
            results.append({**result, 'tree': tree_hash, 'alg': 'Alg2_normal'})
    
        if args.sat:
            
            result = lib.check_fitch_graph(tree)
            results.append({'sat': result, 'tree': tree_hash, 'alg': 'SAT'})
    return results

if __name__ == '__main__':
    ### parse arguments
    parser = argparse.ArgumentParser(description='Run Benchmarks.')
    ### Flags for which algorithms to run
    parser.add_argument('--alg1', action='store_true', help='Run algorithm 1')
    parser.add_argument('--alg2', action='store_true', help='Run algorithm 2')
    parser.add_argument('--normal', action='store_true', help='Run normal distribution')
    parser.add_argument('--sat', action='store_true', help='Check satisfiability')

    ### Input file
    parser.add_argument('--input', type=str, help='Input file')

    ### Create trees flag
    parser.add_argument('--trees', action='store_true', help='Create trees')

    ### Min and Max
    parser.add_argument('--min', type=int, default=5, help='Minimum number of leaves')
    parser.add_argument('--max', type=int, default=math.inf, help='Maximum number of leaves')

    ### Output file
    parser.add_argument('--output',default="out.csv" , type=str, help='Output file')

    ### Partial percentage
    parser.add_argument('--partial', type=float,default=.2, help='Percentage of partials')

    ### Number of runs
    parser.add_argument('--runs', type=int, default=1000, help='Number of runs')

    args = parser.parse_args()


    f = Figlet(font='slant')
    print(f.renderText('Benchmark'))
    results = run_benchmark(args)
    dict_list_to_csv(results, args.output)
    