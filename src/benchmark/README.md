# README for Tree Comparison Benchmark Tool

## Overview

This tool is designed to benchmark different algorithms on tree data structures, focusing on the comparison and analysis of various tree algorithms. It allows users to load trees from files, generate random trees, or use predefined trees and run a suite of algorithms to evaluate their performance based on specific metrics. The tool is capable of handling large datasets and provides functionalities to output the results in a structured format.

## Features

- **Multiple Algorithms**: Support for various algorithms, including custom implementations and standard algorithms like Louvain and Leiden for community detection.
- **Tree Generation**: Ability to generate random trees based on specified criteria.
- **Partial Tree Analysis**: Support for creating partial trees to simulate incomplete or uncertain data.
- **Benchmarking**: Functionality to benchmark algorithm performance on the datasets, capturing metrics such as execution time and accuracy.
- **Data Handling**: Includes utilities for reading and writing trees and results in different formats (e.g., GraphML, JSON, CSV).
- **Extensibility**: Easy to extend with new algorithms or data preprocessing methods.

## Usage

The tool is executed through a command-line interface (CLI). Here's a basic outline of how to use it:

```sh
python main.py [options]
```

### Options

This section elaborates on all available options for configuring the Tree Comparison Benchmark Tool. These options allow users to customize the benchmarking process extensively, including selecting algorithms, configuring input and output, and defining tree generation parameters.

#### Algorithm Selection Flags

- `--alg1`: Run algorithm 1.
- `--alg2`: Run algorithm 2.
- `--normal`: Run the algorithm with a normal distribution.
- `--louvain`: Execute the Louvain algorithm.
- `--louvain_standard`: Use the standard Louvain algorithm from the library.
- `--louvain_custom`: Execute a custom implementation of the Louvain algorithm.
- `--leiden`: Execute the Leiden algorithm.
- `--greedy_sum`: Run the greedy sum algorithm.
- `--greedy_average`: Run the greedy average algorithm.
- `--random_sum`: Execute the random sum algorithm.
- `--random_average`: Execute the random average algorithm.

#### Probability Distribution Configuration

- `--prob_dist_present`: Define the probability distribution for present edges (default: `(1,0.1,1)`).
- `--prob_dist_nonpresent`: Define the probability distribution for nonpresent edges (default: `(0.5,0.1,1)`).

#### Advanced Algorithm Settings

- `--median`: Use the medial value in calculations.
- `--reciprocal`: Use the reciprocal value in calculations.

#### Data Management

- `--load_dump`: Load previously dumped debug files for analysis.
- `--dump_dir`: Specify the directory to dump debug files to (default: `tree_dump`).
- `--dump`: Enable dumping of debug files during the benchmarking process.

#### Input and Output Configuration

- `--input`: Path to the input file containing tree data.
- `--output`: Path where the benchmark results will be saved.

#### Tree Generation and Partitioning

- `--trees`: Flag to generate random trees based on provided criteria.
- `--min`: Minimum number of leaves in generated trees (default: `5`).
- `--max`: Maximum number of leaves in generated trees (default: `math.inf`).
- `--partition`: Partition the input file by specifying a start and an end id, e.g., `(0,1000)`.

#### Partial Information Handling

- `--partial`: Specify the percentage of partial information in the trees. Accepts single values or ranges, e.g., `0.2`, `[0.1, 0.2, 0.3]`, `[0:1:0.1]`.

#### Benchmark Configuration

- `--runs`: Number of runs to perform during the benchmarking process (default: `1000`).
- `--quiet`: Run in quiet mode, suppressing progress bars and detailed logs.

### Usage Example

To run the benchmark with algorithm 1 on an input file, generating partial trees with 20% missing information and saving the results to a specific output file:

```sh
python main.py --alg1 --input mytrees.graphml --output benchmark_results.csv --partial .2
```

This command configures the benchmark tool to evaluate algorithm 1's performance on the dataset provided in `mytrees.graphml`, focusing on scenarios with 20% partial information and outputting the results to `benchmark_results.csv`.

## Output

The tool outputs a CSV file with the benchmark results, including metrics like execution time and accuracy for each algorithm run. The output file structure depends on the specific algorithms selected and the configurations used.