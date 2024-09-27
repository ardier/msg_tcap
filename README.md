# Mutation Subsumption Graph Generator and TCAP Calculator

This project provides a tool to generate Mutation Subsumption Graphs (MSG) from mutation testing data and calculate the Test Coverage Adequacy Percentage (TCAP) for mutants. It includes functionalities to parse mutant and kill matrix data, create a subsumption hierarchy, compute TCAP scores, and visualize the MSG.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Command-Line Arguments](#command-line-arguments)
  - [Input File Formats](#input-file-formats)
  - [Examples](#examples)
- [Output](#output)
- [Citation](#citation)
- [License](#license)

## Introduction

Mutation testing is a method of software testing where mutants (modified versions of a program) are created to check the effectiveness of test cases. A Mutation Subsumption Graph (MSG) represents the subsumption relationships among mutants based on the tests that detect them.

This tool automates the generation of MSGs and calculates the TCAP, helping developers and testers understand the hierarchical relationships between mutants and the adequacy of their test suites.

## Features

- **Parsing Mutant and Kill Matrix Data**: Reads mutants and their kill status from CSV files.
- **Creating Mutant Nodes**: Represents mutants as nodes with associated killing tests.
- **Merging Indistinguishable Mutants**: Merges mutants that are indistinguishable based on their killing tests.
- **Building Subsumption Hierarchy**: Constructs a hierarchy showing subsumption relationships among mutants.
- **Computing TCAP Scores**: Calculates the Test Coverage Adequacy Percentage for each mutant.
- **Graph Visualization**: Generates and saves a visual representation of the MSG.
- **Caching and Sanitization**: Supports caching of sanitized data to improve performance.

## Requirements

- Python 3.6 or higher
- Required Python packages:
  - `argparse`
  - `pandas`
  - `networkx`
  - `matplotlib`
  - `tqdm`
- Graphviz (for graph layout in visualization)

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/ardier/mutation-subsumption-graph.git
   cd mutation-subsumption-graph
    ```
2. **Install Required Packages**:

   ```bash
   pip install -r requirements.txt
   ```
*Note: Ensure that Graphviz is installed on your system. You can download it from [Graphviz's official website](https://graphviz.org/).*

   
## Usage
Run the main.py script with the required arguments to generate the MSG and compute TCAP scores.
Command-Line Arguments
```bash
python main.py --csv MUTANTS_FILE MUTANT_COLUMN_INDEX
               --killmatrix KILL_MATRIX_FILE MUTANT_COLUMN_INDEX TEST_COLUMN_INDEX KILL_STATUS_COLUMN_INDEX
               [--output OUTPUT_FILE]
               [--tcap]
               [--sanitize]
               [--disable_cache]
               [--results_dir RESULTS_DIRECTORY]
               [--results_prefix RESULTS_PREFIX]
```
* **csv**: Path to the CSV file containing mutants and the index of the mutant ID column.
* **killmatrix**: Path to the CSV file containing the kill matrix and the indices of the mutant ID column, test ID column, and kill status column.
* **output**: (Optional) Path to the output file for the MSG graph image.
* **tcap**: (Optional) Flag to calculate the TCAP scores.
* **sanitize**: (Optional) Flag to sanitize the input data.
* **disable_cache**: (Optional) Flag to disable caching and force data sanitization.
* **results_dir**: (Optional) Directory to store the results (default is results).
* **results_prefix**: (Optional) Prefix for the result files.

## Input File Formats

### Mutants CSV File
A CSV file containing at least one column with mutant identifiers.

Example:
```
mutant_id
1
2
3
4
```
_Note you can just use the mutant_id column name of the kill matrix file for the mutants file._

### Kill Matrix CSV File
A CSV file containing the kill matrix with the following columns:
- **Mutant ID**: Identifier for each mutant.
- **Test ID**: Identifier for each test case.
- **Kill Status**: Binary value indicating whether the test case kills the mutant (1 for killed, 0 for not killed).
- **Other columns**: Additional columns are ignored.
- The first row should contain the column headers.

Example:
```
mutant_id,test_id,kill_status
1,1,1
1,2,0
1,3,1
2,1,0
2,2,1
2,3,0
```

## Examples
#### Generating MSG and Calculating TCAP
```bash
python main.py --csv mutants.csv 0 \
               --killmatrix killmatrix.csv 0 1 2 \
               --tcap \
               --results_prefix my_project
```
               
- Parses `mutants.csv` (mutant IDs in column index 0).
- Parses `killmatrix.csv` (mutant IDs in column 0, test IDs in column 1, kill status in column 2).
- Calculates the TCAP scores.
- Saves results with the prefix my_project in the results directory.

#### Specifying a Custom Results Directory
```bash 
python main.py --csv mutants.csv 0 \
               --killmatrix killmatrix.csv 0 1 2 \
               --tcap \
               --results_dir my_results \
               --results_prefix my_project
```

- Saves results in the `my_results` directory with the prefix my_project.
- The output file will be saved as `my_results/my_project_graph.png`.
- The results file will be saved as `my_results/my_project_results.csv`.
- The cache file will be saved as `my_results/my_project_cache.csv`.
- The sanitized data file will be saved as `my_results/my_project_sanitized.csv`.

## Citation
If you use this tool in your research, please cite the following paper and this repository:
```bibtex

@inproceedings{KaufmanICSE2022,
  title = {Prioritizing Mutants to Guide Mutation Testing},
  author = {
    Samuel J. Kaufman and
    Ryan Featherman and
    Justin Alvin and
    Bob Kurtz and
    Paul Ammann and
    Ren{\'e} Just
  },
  booktitle = {
    Proceedings of the
    International Conference on Software Engineering (ICSE)
  },
  month = {May},
  year = {2022},
  doi = {10.1145/3510003.3510187}
}
```
```bibtex
@misc{mutation-subsumption-graph,
  author = {Madadi, Ardi},
  title = {Mutation Subsumption Graph Generator and TCAP Calculator},
  year = {2024},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/ardier/mutation-subsumption-graph}}
}
```


