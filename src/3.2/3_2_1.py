import networkx as nx
import os
import sys
import random
import typing

sys.path.append('fitch-graph-prak')

from lib import graph_to_rel

def create_partial(rel: dict[typing.Any, list[tuple[int, int]]], percent: float, remove_all_directed: bool = False):
    # get subset counts
    rel1_count = len(rel[1])
    rel0_count = len(rel[0])
    reld_count = len(rel['d'])

    total_count = sum([rel1_count, rel0_count, reld_count])

    # if all directed edges should be removed, remove them, and adjust the remaining percent to be removed.
    if(remove_all_directed):
        percent = max(percent - reld_count/total_count,0.)
        print(f'{percent=}')
        # generate random numbers only in the range of the remaining edges
        remove_in_range = total_count - reld_count 
    else:
        # or remove the percent of all edges
        remove_in_range = total_count

    sample_count = round(total_count*percent)

    random_nums = random_numbers(sample_count, remove_in_range)


    rel1_ran_count = count_in_range(random_nums, 0, rel1_count)
    rel0_ran_count = count_in_range(random_nums, rel1_count, rel1_count+rel0_count)
    reld_ran_count = count_in_range(random_nums, rel1_count+rel0_count, total_count)

    rel1_partial = recreate_symmetry(remove_n_random_items(sort_tuples(rel[1]), round(rel1_ran_count/2)))
    rel0_partial = recreate_symmetry(remove_n_random_items(sort_tuples(rel[0]), round(rel0_ran_count/2)))

    if(remove_all_directed):
        reld_partial = []
    else:
        reld_partial = remove_n_random_items(rel['d'], reld_ran_count)

    return {
        1: rel1_partial,
        0: rel0_partial,
        'd': reld_partial,
    }

def recreate_symmetry(l: list[tuple[int, int]]):
    result_list = l.copy()
    for t in l:
        result_list.append((t[1], t[0]))
    return result_list

def remove_n_random_items(l: list, n: int):
    result_list = l.copy()
    for i in range(n):
        ran_index = random.randint(0, len(result_list)-1)
        result_list.pop(ran_index)

    return result_list

def sort_tuples(tuples: list[tuple[int, int]]):
    return [t for t in tuples if t[0] > t[1]]


# generate n unique random numbers between 1 and m
def random_numbers(n: int, m: int):
    if n > m:
        raise ValueError('n must be smaller than m')
    random_numbers = []
    while len(random_numbers) < n:
        r = random.randint(0, m)
        if r not in random_numbers:
            random_numbers.append(r)
    return random_numbers

# get how many numbers in a list are in a range
def count_in_range(nums: list[int], start: int, end: int):
    count = 0
    for num in nums:
        if start <= num < end:
            count += 1
    return count

# get relation size
def get_rel_size(rel: dict[typing.Any, list[tuple[int, int]]]):
    return sum([len(rel[1]), len(rel[0]), len(rel['d'])])


if __name__ == '__main__':
    # graph_path = 'graph-prak-GFH/graph-prak-GFH/n10/D0.25_L0.5_H1.0/D0.25_L0.5_H1.0_n10_0/dFitch.graphml'
    graph_path = 'graph-prak-GFH/graph-prak-GFH/n30/D0.3_L0.3_H0.9/D0.3_L0.3_H0.9_n30_0/dFitch.graphml'

    nx_graph = nx.read_graphml(graph_path)
    print('graph loaded')

    rel = graph_to_rel(nx_graph)

    partial_rel = create_partial(rel, .2)

    relative_size = get_rel_size(partial_rel)/get_rel_size(rel)
    print(f'{relative_size=}')
