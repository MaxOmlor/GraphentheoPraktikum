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
np.seterr(all='ignore')
import ast
import warnings
import re
import numpy as np


import preprocess
from algs import Algs
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fitch_utils.random_trees import generate_random_cotree
from fitch_utils.make_partial import make_partial


sys.path.append('fitch-graph-prak')
import lib

sys.path.append('code_utils')
from code_utils.log import log


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
            # print(f'{line=}')
            line = line.strip()
            if line == '':
                continue
            tree = nx.read_graphml(line)
            trees.append(tree)
    return trees

def run_single_benchmark(run_func, data, rel, leaves):
    success = True

    start_time = datetime.now()
    # try:
    output = run_func(data)
    # except Exception as e:
        # success = False

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
            log(f'Dumped {file_path}')
    except Exception as e:
        log(f'Failed to dump {file_path}, {data_dict=}, {e=}')
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
    fitch_graphs = []
    if args.input and not args.load_dump:
        #todo: """temporary workaround"""
        # check if path in args.input exists
        if not os.path.isfile(args.input):
            raise ValueError(f'input path {args.input} does not exist')

        # check if args.input has extension.txt
        if os.path.splitext(args.input)[1].lower() == '.graphml':
            fitch_graphs.append(nx.read_graphml(args.input))
        elif os.path.isfile(args.input):
            fitch_graphs = get_tree_data_from_file(args.input)
            print(f'{len(fitch_graphs)=}')
        else:
            tree_file_list = find_files_with_extension(args.input, '.graphml')
            if not args.quiet:
                bar = tqdm(total=len(tree_file_list), desc='load tree files')
            fitch_graphs = []
            for file in tree_file_list:
                for tree in get_tree_data_from_file(file):
                    fitch_graphs.append(tree)
                if not args.quiet:
                    bar.update(1)
    relations = []

    if len(fitch_graphs)== 0 and not args.load_dump:
        if not args.quiet:
            print('No trees found')
        log('No trees found')
        raise ValueError('No trees found')

    ### get relations (with a tqdm loadbar)
    invalid = 0
    if not args.load_dump:
        if not args.quiet:
            bar = tqdm(total=len(fitch_graphs), desc='load relations')
        # for tree in fitch_graphs:
        #     nodes = sum([tree.out_degree(node) == 0 for node in tree.nodes])

        #     fitch = lib.rel_to_fitch(rel, list(range(nodes)))
        #     if not lib.check_fitch_graph(fitch):
        #         invalid += 1
        #     else:
        #         relations.append(lib.cotree_to_rel(tree))
        #     if not args.quiet:
        #         bar.update(1)
        for fitch in fitch_graphs:
            relations.append(lib.graph_to_rel(fitch))
            if not args.quiet:
                bar.update(1)
        if not args.quiet:
            bar.close()
    print (f'{invalid=} {len(relations)=}')
    
    ### create partials
    partial_values = parse_input_string_to_list(args.partial)
    print(f'{partial_values=}')
    if not args.quiet:
        bar = tqdm(total=len(partial_values)*len(relations), desc='create partials')
    partials = []
    for p in partial_values:
        for rel in relations:
            partials.append(make_partial(rel, p))
            # print(f'{rel=}')
            # print(f'{partials[-1]=}')
            if not args.quiet:
                bar.update(1)
    
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
        for partial, tree in zip(partials, fitch_graphs):
            leaves = len(tree.nodes())
            data = preprocess.preprocess(partial, leaves, (0,1,2),{'present': dists_present, 'nonpresent': dists_nonpresent})
            alg_input_data.append(data)
        
        test_data = list(zip(fitch_graphs, relations, partials, alg_input_data))

    # runinp
    ### run alg1
    results = []
    # for i in range(len(trees)):
    if not args.quiet:
        pbar = tqdm(total=len(fitch_graphs), desc='run benchmarks')
    for i, (tree, rel, partial, data) in enumerate(test_data):
        # print(f'{(tree, rel, partial, data)=}')
        leaves = len(tree.nodes())
        tree_hash = hash(tree)
        if args.alg1:
            result = run_single_benchmark(Algs.run_alg1, data, rel, leaves)
            results.append({**result, 'tree': tree_hash, 'alg': 'Alg1'})
            print('alg1 done')

        if args.alg2:
            result = run_single_benchmark(Algs.run_alg2_uniform, data, rel, leaves)
            results.append({**result, 'tree': tree_hash, 'alg': 'Alg2'})
            print('alg2 done')

        if args.normal:
            result = run_single_benchmark(Algs.run_alg2_normal, data, rel, leaves)
            results.append({**result, 'tree': tree_hash, 'alg': 'Alg2_normal'})
            print('normal done')

        if args.louvain:
            result = run_single_benchmark(Algs.run_louvain, data, rel, leaves)
            results.append({**result, 'tree': tree_hash, 'alg': 'Louvain'})
            print('louvain done')
        
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
            print('leiden done')

        if args.greedy_sum:
            result = run_single_benchmark(Algs.run_greedy_sum, data, rel, leaves)
            results.append({**result, 'tree': tree_hash, 'alg': 'Greedy Sum'})
            print('greedy sum done')

        if args.greedy_average:
            result = run_single_benchmark(Algs.run_greedy_average, data, rel, leaves)
            results.append({**result, 'tree': tree_hash, 'alg': 'Greedy Average'})
            print('greedy average done')

        if args.random_sum:
            result = run_single_benchmark(Algs.run_random_sum, data, rel, leaves)
            results.append({**result, 'tree': tree_hash, 'alg': 'Random Sum'})
            print('random sum')

        if args.random_average:
            result = run_single_benchmark(Algs.run_random_average, data, rel, leaves)
            results.append({**result, 'tree': tree_hash, 'alg': 'Random Average'})
            print('random average')

        if args.louvain_standard:
            result = run_single_benchmark(Algs.run_louvain_standard, data, rel, leaves)
            results.append({**result, 'tree': tree_hash, 'alg': 'Louvain Lib'})
            print('louvain standard done')
        
        if args.louvain_custom:
            result = run_single_benchmark(Algs.run_louvain_custom, data, rel, leaves)
            results.append({**result, 'tree': tree_hash, 'alg': 'Louvain Custom'})
            print('louvain custom done')

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

    print(f'{results=}')
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

def find_files_with_extension(directory, extension):
    matching_files = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(f'.{extension}'):
                matching_files.append(os.path.join(root, file))

    return matching_files

import re
import numpy as np

def parse_input_string_to_list(input_str):
    '''
    # Beispiele
    input_str1 = '0.2'
    input_str2 = '.5'
    input_str3 = '0.002'
    input_str4 = '[1, 2, 3]'
    input_str5 = '[0:1:0.1]'
    input_str6 = '[0:1:.1]'
    input_str7 = '[0:100:20]'
    input_str8 = '.'

    print(parse_input_string_to_list(input_str1))  # Ausgabe: [0.2]
    print(parse_input_string_to_list(input_str2))  # Ausgabe: [0.5]
    print(parse_input_string_to_list(input_str3))  # Ausgabe: [0.002]
    print(parse_input_string_to_list(input_str4))  # Ausgabe: [1.0, 2.0, 3.0]
    print(parse_input_string_to_list(input_str5))  # Ausgabe: [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    print(parse_input_string_to_list(input_str6))  # Ausgabe: [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    print(parse_input_string_to_list(input_str7))  # Ausgabe: [0.0, 20.0, 40.0, 60.0, 80.0]
    print(parse_input_string_to_list(input_str8))  # raises ValueError
    '''
    
    # Option 1: Eine einzelne Zahl
    if re.match(r'^(?:\d+(\.\d*)?|\.\d+)$', input_str):
        return [float(input_str)]

    # Option 2: Eine Liste von Zahlen
    if re.match(r'^\[.*\]$', input_str):
        input_str = input_str[1:-1]  # Klammern entfernen
        numbers = re.findall(r'[-+]?\d*\.\d+|\d+', input_str)
        return [float(num) for num in numbers]

    # Option 3: Ein Slicing-Ausdruck
    if re.match(r'^\[[-+]?\d*\.\d+|\d+:[-+]?\d*\.\d+|\d+:([-+]?\d*\.\d+|\d+)?:[-+]?\d*\.\d+|\d+\]$', input_str):
        input_str = input_str[1:-1]  # Klammern entfernen
        parts = input_str.split(':')
        start = float(parts[0])
        stop = float(parts[1])
        step = float(parts[2]) if len(parts) == 3 else 1.0
        return list(np.arange(start, stop, step))

    # Wenn der Eingabestring kein derartiges Format hat, gib eine leere Liste zurück
    raise ValueError('Invalid input string: ' + input_str)



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
    warnings.filterwarnings('ignore')
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
    parser.add_argument('--prob_dist_present', type=str, default='(1,0.1,1)', help='Probability distribution for present edges')
    parser.add_argument('--prob_dist_nonpresent', type=str, default='(0.5,0.1,1)', help='Probability distribution for nonpresent edges')
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
    parser.add_argument('--min', type=int, default=5, help='Minimum number of leaves [if tree flag is set]')
    parser.add_argument('--max', type=int, default=math.inf, help='Maximum number of leaves [if tree flag is set]')

    ### Output file
    parser.add_argument('--output',default=None , type=str, help='Output file')

    ### Partial percentage
    parser.add_argument('--partial', type=str,default='.2', help='Percentage of partials. possible input formats: 0.2, [0.1, 0.2, 0.3], [0:1:0.1]. note for slicing the end num is excluded')

    ### Number of runs
    parser.add_argument('--runs', type=int, default=1000, help='Number of runs [if tree flag is set]')

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
    print(f'{results=}')

    if args.output:
        dict_list_to_csv(results, args.output)
    else:
        used_algs = []
        if args.alg1:
            used_algs.append('Alg1')
        if args.alg2:
            used_algs.append('Alg2')
        if args.normal:
            used_algs.append('Normal')
        if args.louvain:
            used_algs.append('Luvain')
        if args.leiden:
            used_algs.append('Leiden')
        if args.greedy_sum:
            used_algs.append('GreedySum')
        if args.greedy_average:
            used_algs.append('GreedyAverage')
        if args.random_sum:
            used_algs.append('RandomSum')
        if args.random_average:
            used_algs.append('RandomAverage')
        used_algs_str = '_'.join(used_algs)

        output_file = "out_"
        output_file += f'input={os.path.basename(args.input).split(".")[0]}'
        output_file += used_algs_str
        output_file += f'partial={args.partial}'
        output_file += ".csv"

        dict_list_to_csv(results, output_file)
    