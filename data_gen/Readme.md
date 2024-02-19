# Graph Theory Benchmarking Tool

This tool is designed for running a series of benchmark tests on graph-theoretical algorithms. It automates the process of generating data, setting up test parameters, and executing the tests across multiple configurations. The tool supports parallel execution to speed up the benchmarking process.

## Features

- **Data Generation**: Automatically generates tree data for testing.
- **Flexible Test Configurations**: Allows specifying various algorithm parameters, input data characteristics, and execution options.
- **Parallel Execution**: Utilizes multiprocessing to run multiple tests in parallel, improving the efficiency of the benchmarking process.
- **Customizable Input and Output**: Supports defining custom input directories for test data and output directories for results.

## Configuration

Before running the tool, configure your tests in the `./data_gen/tests.json` file. This JSON file should specify:

- `Nodes`: A list of node counts for generating test data.
- `Algs`: The algorithms to test, specified as command-line flags.
- `Runs`: The number of runs for each test configuration.
- `Percentages`, `Distributions`: Parameters for controlling the characteristics of the generated test data.
- `Median`, `Reciprocal`: Boolean flags for additional test options.

## Usage

To run the tool, navigate to the project directory and execute the main script:

```sh
python generate_data.py
```

The tool will load configurations from `./data_gen/tests.json`, generate necessary data (if the `gen_data` test is selected), and run the specified algorithms with the configured parameters. Results will be saved in the specified output directory.

## Parallel Execution

The tool is set up to run tests in parallel to utilize available CPU resources efficiently. You can adjust the number of parallel processes by modifying the `parallel` variable in the script.

## Output

Results are saved in CSV format in the specified output directory. Each file contains the outcomes of the tests according to the configured parameters.