import sys
import os
import typing

sys.path.append('fitch-graph-prak')
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
# sys.path.append('fitch-utils')

import lib
import louvain

def dprint(out: str):
    if False:
        print(out)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from fitch_utils import partitions
from fitch_utils import louvain as our_louvain
from fitch_utils import leiden

from code_utils.log import log

def run_func_gen(partition_func, scoring_func, dist_type):
    def return_func(data):
        weights = data['weights'][dist_type]
        
        dprint('########################')
        test = lib.partition_heuristic_scaffold(
            weights['d'],weights[1],weights[0],data['nodes'],
            partition_func, scoring_func,
            data['rel'], True, True, data['median'], data['reciprocal'])
        return test
    return return_func

def run_alg1(data):
    print(f"{data['rel']=},\n{data['nodes']=},\n{data['order']=}")
    try:
        test = lib.algorithm_one(data['rel'],data['nodes'],data['order'])
    except Exception as e:
        log(f"Exception: {e}, {data['rel']=},\n{data['nodes']=},\n{data['order']=}")
        raise e
    return lib.cotree_to_rel(test)

def run_alg2_uniform(data):
    weights = data['weights']['uniform']
    test = lib.algorithm_two(data['nodes'],weights['d'],weights[1],weights[0])
    return test
def run_alg2_normal(data):
    weights = data['weights']['normal']
    test = lib.algorithm_two(data['nodes'],weights['d'],weights[1],weights[0])
    return test

def run_louvain(data):
    weights = data['weights']['normal']
    partition_func = our_louvain.partition_louvain_normalized
    scoring_func = partitions.score_sum
    
    dprint('########################')
    test = lib.partition_heuristic_scaffold(
        weights['d'],weights[1],weights[0],data['nodes'],
        partition_func, scoring_func,
        data['rel'], True, True, data['median'], data['reciprocal'])
    return test

def run_louvain_standard(data):
    weights = data['weights']['normal']
    partition_func = louvain.louvain_standard
    scoring_func = partitions.score_sum
    
    dprint('########################')
    test = lib.partition_heuristic_scaffold(
        weights['d'],weights[1],weights[0],data['nodes'],
        partition_func, scoring_func,
        data['rel'], True, True, data['median'], data['reciprocal'])
    return test

def run_louvain_custom(data):
    weights = data['weights']['normal']
    partition_func = louvain.louvain_custom
    scoring_func = partitions.score_sum
    
    dprint('########################')
    test = lib.partition_heuristic_scaffold(
        weights['d'],weights[1],weights[0],data['nodes'],
        partition_func, scoring_func,
        data['rel'], True, True, data['median'], data['reciprocal'])
    return test

def run_leiden(data):
    weights = data['weights']['normal']
    partition_func = leiden.partition_leiden_normalized
    scoring_func = partitions.score_sum
    
    dprint('########################')
    test = lib.partition_heuristic_scaffold(
        weights['d'],weights[1],weights[0],data['nodes'],
        partition_func, scoring_func,
        data['rel'], True, True, data['median'], data['reciprocal'])
    return test

def run_greedy_sum(data):
    weights = data['weights']['normal']
    # print(f'{weights=}')
    partition_func = partitions.partition_greedy_sum
    scoring_func = partitions.score_sum
    
    dprint('########################')
    test = lib.partition_heuristic_scaffold(
        weights['d'],weights[1],weights[0],data['nodes'],
        partition_func, scoring_func,
        data['rel'], True, True, data['median'], data['reciprocal'])
    return test

def run_greedy_average(data):
    weights = data['weights']['normal']
    partition_func = partitions.partition_greedy_sum
    scoring_func = partitions.score_average
    
    dprint('########################')
    test = lib.partition_heuristic_scaffold(
        weights['d'],weights[1],weights[0],data['nodes'],
        partition_func, scoring_func,
        data['rel'], True, True, data['median'], data['reciprocal'])
    return test

def run_random_sum(data):
    weights = data['weights']['normal']
    partition_func = partitions.partition_random
    scoring_func = partitions.score_sum
    
    dprint('########################')
    test = lib.partition_heuristic_scaffold(
        weights['d'],weights[1],weights[0],data['nodes'],
        partition_func, scoring_func,
        data['rel'], True, True, data['median'], data['reciprocal'])
    return test

def run_random_average(data):
    weights = data['weights']['normal']
    partition_func = partitions.partition_random
    scoring_func = partitions.score_average
    
    dprint('########################')
    test = lib.partition_heuristic_scaffold(
        weights['d'],weights[1],weights[0],data['nodes'],
        partition_func, scoring_func,
        data['rel'], True, True, data['median'], data['reciprocal'])
    return test
