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
from src.fitch_utils import random_trees
import warnings
warnings.filterwarnings("ignore")


def build_command(algorithm_parameters, runs_parameters, nodes, percentages, dists_present, dists_nonpresent, median, reciprocal):
    command = "python3 ./src/benchmark/main.py" + algorithm_parameters + runs_parameters
    command += " --quiet"
    command += " --partial=" + str(percentages)
    command += " --prob_dist_present=\"" + str(dists_present) + "\""
    command += " --prob_dist_nonpresent=\"" + str(dists_nonpresent) + "\""
    command += " --input=\"./data_gen/trees/" + str(nodes) + ".txt\""
    if median:
        command += " --median"
    if reciprocal:
        command += " --reciprocal"
    # build output file name
    output_file = "./data_gen/out/res"
    output_file += "_n" + str(nodes)
    # remove . from percentages
    output_file += "_p" + str(percentages).replace(".", "")
    output_file += "_dp" + str(dists_present).replace(".", "").replace(",", "_")
    output_file += "_dnp" + str(dists_nonpresent).replace(".", "").replace(",", "_")
    if median:
        output_file += "_m"
    if reciprocal:
        output_file += "_r"
    output_file += ".csv"

    command += " --output=\"" + output_file + "\""

    #check existence of output file in ./data_gen/out/
    if os.path.isfile(output_file):
        return None


    #run command and wait for it to finish    
    return command

def run_command(command):
    #call subprocess quiet
    subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    

#load .tests.json
with open('./data_gen/tests.json') as f:
    tests = json.load(f)

if __name__ == "__main__":

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

    for percent in percentages:
        for dist_p in dists_present:
            for dist_np in dists_nonpresent:
                for med in median:
                    for rep in reciprocal:
                        for n in nodes:
                            command = build_command(algorithm_parameters, runs_parameters, n, percent, dist_p, dist_np, med, rep)
                            if command is not None:
                                command_queue.append(build_command(algorithm_parameters, runs_parameters, n, percent, dist_p, dist_np, med, rep))

    count = len(percentages) * len(dists_present) * len(dists_nonpresent) * len(median) * len(reciprocal) * len(nodes)
    print("Total number of tests: " + str(count))
    print("Number of tests to run: " + str(len(command_queue)))

    ### I want to let a number of tests run in parallel

    # number of tests to run in parallel
    parallel = 10
    # number of tests to run in total
    total = len(command_queue)


    count = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(count)
    for _ in tqdm.tqdm(pool.imap_unordered(run_command, command_queue), total=len(command_queue)):
        pass