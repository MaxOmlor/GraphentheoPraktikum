# This file will load .tests.json 
# and run all combinations of input parameters
# it will build the arguments for .main.py and run it
#
import json
import os
import sys
import subprocess
import time
import multiprocessing
import tqdm
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from src.fitch_utils import random_trees
import warnings
warnings.filterwarnings("ignore")


def build_command(input_dir, output_dir, algorithm_parameters, runs_parameters, nodes, percentages, dists_present, dists_nonpresent, median, reciprocal, partition=None):
    path = '''"c:/Users/Max/Documents/Studium/Leipzig/M 5. Semester/graphentheo/praktikum/GraphentheoPraktikum/venv/Scripts/python.exe" ./src/benchmark/main.py'''
    command = path + algorithm_parameters + runs_parameters
    # command = "python3 ./src/benchmark/main.py" + algorithm_parameters + runs_parameters
    # command += " --quiet"
    command += " --partial=\"" + str(percentages) + "\""
    command += " --prob_dist_present=\"" + str(dists_present) + "\""
    command += " --prob_dist_nonpresent=\"" + str(dists_nonpresent) + "\""
    
    # diese zeile ändern und graph-prak-GFH/testset einfügen
    # command += " --input=\"./data_gen/trees/" + str(nodes) + ".txt\""
    # if input dir is a file
    # print(f'{input_dir=}')
    if os.path.isfile(input_dir):
        command += f" --input=\"{input_dir}\""
    else:
        input_path = os.path.join(input_dir, str(nodes) + ".txt")
        command += f" --input=\"{input_path}\""
    # command += " --input=\"../../data_gen/trees/" + str(nodes) + ".txt\""

    if partition is not None:
        command += f" --partition=\"{str(partition)}\""

    # if median:
    #     command += " --median"
    # if reciprocal:
    #     command += " --reciprocal"


    # build output file name
    # neuen out ordner definieren
    output_file = os.path.join(output_dir, "res")
    #check if out dir exists
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    # output_file = "../../data_gen/out/res"
    if os.path.isdir(input_dir):
        output_file += "_n" + str(nodes)
    # remove . from percentages
    output_file += "_p" + str(percentages).replace(".", "")
    output_file += "_dp" + str(dists_present).replace(".", "").replace(",", "_")
    output_file += "_dnp" + str(dists_nonpresent).replace(".", "").replace(",", "_")
    # if median:
        # output_file += "_m"
    # if reciprocal:
        # output_file += "_r"
    if partition is not None:
        output_file += "_part" + str(partition[0]) + "-" + str(partition[1])
    output_file += ".csv"

    command += " --output=\"" + output_file + "\""

    #check existence of output file in ./data_gen/out/
    if os.path.isfile(output_file):
        return None


    #run command and wait for it to finish    
    return command

def run_command(command):
    # print(f'{command=}')
    #call subprocess quiet
    subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # subprocess.call(command, shell=True, stdout=subprocess.DEVNULL)
                    
def partition_list(input_list, n):
    if n <= 0:
        raise ValueError("Die Anzahl der Partitionen (n) muss größer als 0 sein.")
    
    list_length = len(input_list)
    partition_sizes = [list_length // n]*n
    remainder = list_length % n
    for i in range(remainder):
        partition_sizes[i] += 1

    partitions = []

    for i in range(n):
        start_index = sum(size for size in partition_sizes[:i])
        end_index = sum(size for size in partition_sizes[:i+1])
        partitions.append((start_index, end_index))

    return partitions


#load .tests.json
with open('./data_gen/tests.json') as f:
    tests = json.load(f)

if __name__ == "__main__":

    test_to_run = ['gen_data', 'gfh_data'][1]

    if test_to_run == 'gen_data':
        ## generate tree data
        print("Generating tree data")
        for size in tests['Nodes']:
            random_trees.create_testset(tests["Runs"], "./data_gen/trees",True, False, size, False)

    #multiprocessing.freeze_support()
    algorithm_parameters = ""
    alg_list = tests['Algs']

    for alg in alg_list:
        algorithm_parameters += " --" + alg

    runs_parameters = " --runs=" + str(tests['Runs'])
    nodes = tests['Nodes']

    percentages = tests['Percentages']
    dists_present = tests['Distributions']['present']
    dists_nonpresent = tests['Distributions']['nonpresent']
    median = tests['Median']
    reciprocal = tests['Reciprocal']

    command_queue = []
    input_dir, output_dir = None, None
    if test_to_run == 'gen_data':
        # gen data test
        input_dir = './data_gen/trees'
        output_dir = './data_gen/out'

        for percent in percentages:
            for dist_p in dists_present:
                for dist_np in dists_nonpresent:
                    for med in median:
                        for rep in reciprocal:
                            for n in nodes:
                                command = build_command(input_dir, output_dir, algorithm_parameters, runs_parameters, n, percent, dist_p, dist_np, med, rep)
                                if command is not None:
                                    command_queue.append(command)

    if test_to_run == 'gfh_data':
        # gfh data test
        input_dir = './graph-prak-GFH/testset.txt'
        output_dir = './data_gen/out_gfh'

        # get number of lines in input file
        num_graphs = None
        with open(input_dir) as f:
            lines = f.readlines()
            num_graphs = len(lines)
        
        num_partitions = 35

        for dist_np in dists_nonpresent:
            for med in median:
                for rep in reciprocal:
                    for partition in partition_list(list(range(num_graphs)), num_partitions):
                        for dist_p in dists_present:
                            for percent in percentages:
                                command = build_command(input_dir, output_dir, algorithm_parameters, runs_parameters, None, percent, dist_p, dist_np, med, rep, partition)
                                if command is not None:
                                    command_queue.append(command)

    print(f'{command_queue[0]=}')

    count = len(percentages) * len(dists_present) * len(dists_nonpresent) * len(median) * len(reciprocal) * (len(nodes) if test_to_run == 'gen_data' else 1) * (num_partitions if test_to_run == 'gfh_data' else 1)
    # count = len(command_queue)
    print("Total number of tests: " + str(count))
    print("Number of tests to run: " + str(len(command_queue)))

    ### I want to let a number of tests run in parallel

    # number of tests to run in parallel
    parallel = 10
    # number of tests to run in total
    total = len(command_queue)

    count = multiprocessing.cpu_count() - 1
    # count = 1
    pool = multiprocessing.Pool(count)
    for _ in tqdm.tqdm(pool.imap_unordered(run_command, command_queue), total=len(command_queue)):
        pass

