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
import json
import numpy as np
import ast


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

    while len(hashes) < num_trees:
        tree = generate_random_cotree()
        leaves = sum([tree.out_degree(node) == 0 for node in tree.nodes])
        if min_size <= leaves <= max_size:
            hashed = hash(tree)
        if min_size <= leaves <= max_size:
            if hashed not in hashes:
                hashes.add(hashed)
                trees.append(tree)
    return trees

### reads the file, reads the paths in that file and loads those trees
def get_tree_data_from_file(path: str):
    trees = []
    with open(path, 'r') as f:
        #for loop for file with tqdm
        for line in f.readlines():
            line = line.strip()
            if line == '':
                continue
            tree = nx.read_graphml(line)
            trees.append(tree)
    return trees

def run_single_benchmark(run_func, data, rel, leaves):
    success = True

    start_time = datetime.now()
    try:
        output = run_func(data)
    except:
        success = False

    delta_time = datetime.now() - start_time

    if success:
        symmetric_difference = lib.sym_diff(output, rel, leaves)
    else:
        symmetric_difference = 0.
    return {
        'delta_time': delta_time,
        'symmetric_difference': symmetric_difference,
        'nodes': leaves,
        'rel_size': len(rel[0]) + len(rel[1]) + len(rel['d']),
        'success': success,
    }

def dict_list_to_csv(dict_list: list[dict], file_path: str):
    if not any(dict_list):
        return
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=dict_list[0].keys())

        # Schreiben der Kopfzeile
        writer.writeheader()

        # Schreiben der Daten
        for d in dict_list:
            if set(dict_list[0].keys()) != d.keys():
                raise ValueError(f'dict in list must contain the same keys {dict_list[0].keys()=} != {d.keys()=}')
            writer.writerow(d)

def dump_json(data_dict: dict, file_path: str):
    try:
        with open(file_path, 'w') as f:
            json.dump(convert_tuples_to_strings(data_dict), f)
    except:
        raise ValueError(f'{data_dict=}')
def dump_tree(tree: nx.Graph, file_path: str):
    nx.write_graphml(tree, file_path)
def dump_shit(data_dict: dict, tree: nx.Graph, file_name: str, dir_path='failed_graphs'):
    file_path = os.path.join(dir_path, file_name)
    dump_json(data_dict, file_path+'.json')
    dump_tree(tree, file_path+'.graphml')

def load_json(file_path: str):
    with open(file_path, 'r') as f:
        return restore_tuples(json.load(f))
def load_tree(file_path: str):
    return nx.read_graphml(file_path)
def load_shit(file_name: str, dir_path='failed_graphs'):
    file_path = os.path.join(dir_path, file_name)
    data_dict = load_json(file_path+'.json')
    tree = load_tree(file_path+'.graphml')
    return data_dict, tree

def run_benchmark(args):
    # setup
    ### create trees
    cotrees = []
    fitch_graphs = []
    if args.trees:
        cotrees = create_tree_data(args.runs, min_size=args.min, max_size=args.max)
    if args.input and not args.load_dump:
        #todo: """temporary workaround"""
        cotrees = get_tree_data_from_file(args.input)
    relations = []
        
    if len(cotrees) + len(fitch_graphs)== 0 and not args.load_dump:
        if not args.quiet:
            print('No trees found')
        return

    ### get relations (with a tqdm loadbar)
    if not args.load_dump:
        if not args.quiet:
            bar = tqdm(total=len(cotrees) + len(fitch_graphs), desc='load relations')
        for tree in cotrees:
            relations.append(lib.cotree_to_rel(tree))
            if not args.quiet:
                bar.update(1)
        for fitch in fitch_graphs:
            relations.append(lib.graph_to_rel(fitch))
            if not args.quiet:
                bar.update(1)
        if not args.quiet:
            bar.close()
    
    ### create partials
    partials = [make_partial(rel, args.partial) for rel in relations]
    
    # chick if folder failed_graphs exists
    if not os.path.exists('failed_graphs'):
        os.makedirs('failed_graphs')

    ###ascii art of a chick
    '''''''''
     ( o>
      /) )
      `"`
    '''''''''
    dists_present = get_tuple(args.prob_dist_present)
    dists_nonpresent = get_tuple(args.prob_dist_nonpresent)

    test_data = []
    if args.load_dump:
        # get list of names without extensions
        file_names = {os.path.splitext(file)[0] for file in os.listdir(args.input)}
        for name in file_names:
            if not args.quiet:
                print(f'loading {name}')
            data_dict, tree = load_shit(name, args.input)
            data_dict['data']['rel'] = convert_rel_items_to_tuple(data_dict['data']['rel'])
            test_data.append((tree, convert_rel_items_to_tuple(data_dict['rel']), data_dict['partial'], data_dict['data']))

    else:
        alg_input_data = []
        for partial, tree in zip(partials, cotrees):
            leaves = sum([tree.out_degree(node) == 0 for node in tree.nodes])
            data = preprocess.preprocess(partial, leaves, (0,1,2),{'present': dists_present, 'nonpresent': dists_nonpresent})
            alg_input_data.append(data)
        
        test_data = list(zip(cotrees, relations, partials, alg_input_data))

    # runinp
    ### run alg1
    results = []
    # for i in range(len(trees)):
    if not args.quiet:
        pbar = tqdm(total=len(cotrees), desc='run benchmarks')
    for i, (tree, rel, partial, data) in enumerate(test_data):
        leaves = sum([tree.out_degree(node) == 0 for node in tree.nodes])
        tree_hash = hash(tree)
        if args.alg1:
            result = run_single_benchmark(Algs.run_alg1, data, rel, leaves)
            results.append({**result, 'tree': tree_hash, 'alg': 'Alg1'})

        if args.alg2:
            result = run_single_benchmark(Algs.run_alg2_uniform, data, rel, leaves)
            results.append({**result, 'tree': tree_hash, 'alg': 'Alg2'})

        if args.normal:
            result = run_single_benchmark(Algs.run_alg2_normal, data, rel, leaves)
            results.append({**result, 'tree': tree_hash, 'alg': 'Alg2_normal'})

        if args.louvain:
            result = run_single_benchmark(Algs.run_louvain, data, rel, leaves)
            results.append({**result, 'tree': tree_hash, 'alg': 'Louvain'})
        
        if args.leiden:
            # try:
            result = run_single_benchmark(Algs.run_leiden, data, rel, leaves)
            results.append({**result, 'tree': tree_hash, 'alg': 'Leiden'})
            # ''except:
            #     print(f'Leiden failed')
            #     file_name = f'leiden_fail_{i}'
            #     info_dict = {
            #         'data': data,
            #         'rel': rel,
            #         'partial': partial,
            #     }
            #  ''   dump_shit(info_dict, tree, file_name)

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

        if args.louvain_standard:
            result = run_single_benchmark(Algs.run_louvain_standard, data, rel, leaves)
            results.append({**result, 'tree': tree_hash, 'alg': 'Louvain Lib'})
        
        if args.louvain_custom:
            result = run_single_benchmark(Algs.run_louvain_custom, data, rel, leaves)
            results.append({**result, 'tree': tree_hash, 'alg': 'Louvain Custom'})

        if args.dump:
            file_name = f'tree_{i}'
            info_dict = {
                     'data': data,
                     'rel': rel,
                     'partial': partial,
                 }
            dump_shit(info_dict, tree, file_name,args.dump_dir)

        
        if not args.quiet:
            pbar.update(1)
    if not args.quiet:
        pbar.close()
    return results

def convert_tuples_to_strings(d):
    def recursive_convert(d):
        if isinstance(d, dict):
            for key, value in list(d.items()):
                if isinstance(value, np.ndarray):
                    # !!achtung achtung fehlerverdächtig!!
                    d[key] = value.tolist()[0]  # NumPy-Array in Liste umwandeln
                if isinstance(key, tuple):
                    new_key = f"tuple{key}"
                    d[new_key] = d.pop(key)
                if isinstance(value, (dict, list)):
                    recursive_convert(value)
        elif isinstance(d, list):
            for i, item in enumerate(d):
                if isinstance(item, (dict, list)):
                    recursive_convert(item)

    recursive_convert(d)
    return d

#convert a string like (0.,1.,3.) to a tuple
def get_tuple(input: str):
    # Remove spaces, convert to tuple
    return ast.literal_eval(input.replace(" ", ""))


def restore_tuples(d):
    def recursive_restore(d):
        if isinstance(d, dict):
            for key, value in list(d.items()):
                if isinstance(key, str) and key.startswith('tuple(') and key.endswith(')'):
                    new_key = tuple(map(int, key[6:-1].split(', ')))
                    d[new_key] = d.pop(key)
                    key = new_key

                new_key = convert_to_suitable_type(key)
                d[new_key] = d.pop(key)
                key = new_key

                if isinstance(value, (dict, list)):
                    recursive_restore(value)
        elif isinstance(d, list):
            for i, item in enumerate(d):
                if isinstance(item, (dict, list)):
                    recursive_restore(item)

    restored_dict = d.copy()
    recursive_restore(restored_dict)
    return restored_dict

def convert_rel_items_to_tuple(rel):
    return {key: [tuple(l) for l in value] for key, value in rel.items()}

def convert_to_suitable_type(x):
    if isinstance(x, str):
        try:
            number = int(x)
            return number
        except ValueError:
            pass
    return x

if False:
    # Beispielaufruf
    nested_dict = {
        (1, 2): {'c': 1},
        'd': [{(3,4): 2}, ('f', 'g')],
        'h': ('i', 'j')
    }

    converted_dict = convert_tuples_to_strings(nested_dict)
    print(f'{converted_dict=}')
    restored_dict = restore_tuples(converted_dict)
    print(f'{restored_dict=}')

if __name__ == '__main__':
    ### parse arguments
    parser = argparse.ArgumentParser(description='Run Benchmarks.')
    ### Flags for which algorithms to run
    parser.add_argument('--alg1', action='store_true', help='Run algorithm 1')
    parser.add_argument('--alg2', action='store_true', help='Run algorithm 2')
    parser.add_argument('--normal', action='store_true', help='Run normal distribution')
    parser.add_argument('--louvain', action='store_true', help='Run louvain')
    parser.add_argument('--louvain_standard', action='store_true', help='Run louvain_standard from library')
    parser.add_argument('--louvain_custom', action='store_true', help='Run louvain_custom')
    parser.add_argument('--leiden', action='store_true', help='Run leiden')
    parser.add_argument('--greedy_sum', action='store_true', help='Run greedy sum')
    parser.add_argument('--greedy_average', action='store_true', help='Run greedy average')
    parser.add_argument('--random_sum', action='store_true', help='Run random sum')
    parser.add_argument('--random_average', action='store_true', help='Run random average')
    # Probability distribution
    parser.add_argument('--prob_dist_present', type=str, default='normal', help='Probability distribution')
    parser.add_argument('--prob_dist_nonpresent', type=str, default='normal', help='Probability distribution')
    parser.add_argument('--median', action='store_true', default=False, help='Medial value')
    parser.add_argument('--reciprocal', action='store_true', default=False, help='Reciprocal value')

    parser.add_argument('--load_dump', action='store_true', help='Load debug files.')
    parser.add_argument('--dump_dir', type=str, default='tree_dump', help='Directory to dump debug files to.')
    parser.add_argument('--dump', action='store_true', help='Dump debug files.')

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

    ### quiet
    parser.add_argument('--quiet', action='store_true', help='Quiet mode')

    args = parser.parse_args()

    f = Figlet(font='slant')
    if not args.quiet:
        print(f.renderText('Benchmark...'))
    if not any([args.alg1, args.alg2, args.normal, args.louvain,args.leiden, args.greedy_sum, args.greedy_average, args.random_sum, args.random_average]):
        if not args.quiet:
            print('No algorithms selected')
        sys.exit()
    if not any([args.input, args.trees]):
        if not args.quiet:
            print('No input file or tree creation selected')
        sys.exit()
    results = run_benchmark(args)
    dict_list_to_csv(results, args.output)
    