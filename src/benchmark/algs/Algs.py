import sys
import os
import typing

sys.path.append('fitch-graph-prak')

import lib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from fitch_utils import partitions
from fitch_utils import louvain
from fitch_utils import leiden

def run_func_gen(partition_func, scoring_func, dist_type):
    def return_func(data):
        weights = data['weights'][dist_type]
        partition_func = partition_func
        scoring_func = scoring_func
        
        test = lib.partition_heuristic_scaffold(
            weights['d'],weights[1],weights[0],data['nodes'],
            partition_func, scoring_func,
            data['rel'])
        return test
    return return_func

def run_alg1(data):
    test = lib.algorithm_one(data['rel'],list(range(data['nodes'])),data['order'])
    return lib.cotree_to_rel(test)

def run_alg2_uniform(data):
    weights = data['weights']['uniform']
    test = lib.algorithm_two(list(range(data['nodes'])),weights['d'],weights[1],weights[0])
    return test
def run_alg2_normal(data):
    weights = data['weights']['normal']
    test = lib.algorithm_two(list(range(data['nodes'])),weights['d'],weights[1],weights[0])
    return test

def run_louvain(data):
    weights = data['weights']
    partition_func = louvain.partition_louvain_normalized
    scoring_func = partitions.score_sum
    
    test = lib.partition_heuristic_scaffold(
        weights['d'],weights[1],weights[0],data['nodes'],
        partition_func, scoring_func,
        data['rel'])
    return test

def run_leiden(data):
    weights = data['weights']['normal']
    partition_func = leiden.partition_leiden_normalized
    scoring_func = partitions.score_sum
    
    test = lib.partition_heuristic_scaffold(
        weights['d'],weights[1],weights[0],data['nodes'],
        partition_func, scoring_func,
        data['rel'])
    return test

def run_greedy_sum(data):
    weights = data['weights']
    partition_func = partitions.partition_greedy_sum
    scoring_func = partitions.score_sum
    
    test = lib.partition_heuristic_scaffold(
        weights['d'],weights[1],weights[0],data['nodes'],
        partition_func, scoring_func,
        data['rel'])
    return test

def run_greedy_average(data):
    weights = data['weights']
    partition_func = partitions.partition_greedy_sum
    scoring_func = partitions.score_average
    
    test = lib.partition_heuristic_scaffold(
        weights['d'],weights[1],weights[0],data['nodes'],
        partition_func, scoring_func,
        data['rel'])
    return test

def run_random_sum(data):
    weights = data['weights']
    partition_func = partitions.partition_random
    scoring_func = partitions.score_sum
    
    test = lib.partition_heuristic_scaffold(
        weights['d'],weights[1],weights[0],data['nodes'],
        partition_func, scoring_func,
        data['rel'])
    return test

def run_random_average(data):
    weights = data['weights']
    partition_func = partitions.partition_random
    scoring_func = partitions.score_average
    
    test = lib.partition_heuristic_scaffold(
        weights['d'],weights[1],weights[0],data['nodes'],
        partition_func, scoring_func,
        data['rel'])
    return test
