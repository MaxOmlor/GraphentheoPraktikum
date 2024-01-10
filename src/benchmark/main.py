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
from algs import Algs

import preprocess
from algs import Algs
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fitch_utils.random_trees import generate_random_cotree
from fitch_utils.make_partial import make_partial


sys.path.append('fitch-graph-prak')
import lib


import math
def create_tree_data(num_trees: int, min_size: int=0, max_size: int=math.inf):
    trees = []
    hashes = set()

    pbar = tqdm(total=num_trees, desc='create trees  ')
    while len(hashes) < num_trees:
        tree = generate_random_cotree()
        leaves = sum([tree.out_degree(node) == 0 for node in tree.nodes])
        if min_size <= leaves <= max_size:
            hashed = hash(tree)
        if min_size <= leaves <= max_size:
            if hashed not in hashes:
                hashes.add(hashed)
                trees.append(tree)
                pbar.update(1)
    pbar.close()
    return trees

### reads the file, reads the paths in that file and loads those trees
def get_tree_data_from_file(path: str):
    trees = []
    with open(path, 'r') as f:
        #for loop for file with tqdm
        for line in tqdm(f.readlines(), desc='read trees    '):
            line = line.strip()
            if line == '':
                continue
            tree = nx.read_graphml(line)
            trees.append(tree)
    return trees

def run_single_benchmark(run_func, data, rel, leaves):
    start_time = datetime.now()
    output = run_func(data)
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
    cotrees = []
    fitch_graphs = []
    if args.trees:
        cotrees = create_tree_data(args.runs, min_size=args.min, max_size=args.max)
    if args.input:
        fitch_graphs = get_tree_data_from_file(args.input)
    if len(cotrees) + len(fitch_graphs)== 0:
        print('No trees found')
        return
    
    ### get relations (with a tqdm loadbar)
    bar = tqdm(total=len(cotrees) + len(fitch_graphs), desc='load relations')
    relations = []
    for tree in cotrees:
        relations.append(lib.cotree_to_rel(tree))
        bar.update(1)
    for fitch in fitch_graphs:
        relations.append(lib.graph_to_rel(fitch))
        bar.update(1)
    bar.close()
    
    ### create partials
    partials = [make_partial(rel, args.partial) for rel in relations]

    # run
    ### run alg1
    results = []
    # for i in range(len(trees)):
    pbar = tqdm(total=len(cotrees), desc='run benchmarks')
    for tree, rel, partial in zip(cotrees, relations, partials):
        leaves = sum([tree.out_degree(node) == 0 for node in tree.nodes])
        tree_hash = hash(tree)
        data = preprocess.preprocess(partial, leaves, (0,1,2),{'present': (0.8, 1,1), 'nonpresent': (.5,1,1)})
        if args.alg1:
            result = run_single_benchmark(Algs.run_alg1, data, rel, leaves)
            results.append({**result, 'tree': tree_hash, 'alg': 'Alg1'})

        if args.alg2:
            result = run_single_benchmark(Algs.run_alg2, data, rel, leaves)
            results.append({**result, 'tree': tree_hash, 'alg': 'Alg2'})

        if args.normal:
            result = run_single_benchmark(Algs.run, data, rel, leaves)
            results.append({**result, 'tree': tree_hash, 'alg': 'Alg2_normal'})
    
        if args.sat:
            result = lib.check_fitch_graph(lib.rel_to_fitch(partial))
            results.append({'sat': result, 'tree': tree_hash, 'alg': 'SAT'})

        if args.louvain:
            result = run_single_benchmark(Algs.run_louvain, data, rel, leaves)
            results.append({**result, 'tree': tree_hash, 'alg': 'Louvain'})

        if args.greedy_sum:
            result = run_single_benchmark(Algs.run_greedy_sum, data, rel, leaves)
            results.append({**result, 'tree': tree_hash, 'alg': 'Greedy Sum'})

        if args.greedy_average:
            result = run_single_benchmark(Algs.run_greedy_average, data, rel, leaves)
            results.append({**result, 'tree': tree_hash, 'alg': 'Greedy Average'})

        if args.random_sum:
            result = run_single_benchmark(Algs.run_random_sum, data, rel, leaves)
            results.append({**result, 'tree': tree_hash, 'alg': 'Random Sum'})

        if args.random_average:
            result = run_single_benchmark(Algs.run_random_average, data, rel, leaves)
            results.append({**result, 'tree': tree_hash, 'alg': 'Random Average'})
        

        pbar.update(1)
    pbar.close()
    return results

if __name__ == '__main__':
    ### parse arguments
    parser = argparse.ArgumentParser(description='Run Benchmarks.')
    ### Flags for which algorithms to run
    parser.add_argument('--alg1', action='store_true', help='Run algorithm 1')
    parser.add_argument('--alg2', action='store_true', help='Run algorithm 2')
    parser.add_argument('--normal', action='store_true', help='Run normal distribution')
    parser.add_argument('--sat', action='store_true', help='Check satisfiability')
    parser.add_argument('--louvain', action='store_true', help='Run louvain')
    parser.add_argument('--greedy_sum', action='store_true', help='Run greedy sum')
    parser.add_argument('--greedy_average', action='store_true', help='Run greedy average')
    parser.add_argument('--random_sum', action='store_true', help='Run random sum')
    parser.add_argument('--random_average', action='store_true', help='Run random average')

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
    print(f.renderText('Benchmark...'))
    if not any([args.alg1, args.alg2, args.normal, args.sat, args.louvain, args.greedy_sum, args.greedy_average, args.random_sum, args.random_average]):
        print('No algorithms selected')
        sys.exit()
    if not any([args.input, args.trees]):
        print('No input file or tree creation selected')
        sys.exit()
    results = run_benchmark(args)
    dict_list_to_csv(results, args.output)
    