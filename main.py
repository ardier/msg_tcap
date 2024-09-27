import argparse
from copy import copy
from os import path, makedirs
from datetime import datetime
import pandas as pd

from TCAP_calculator import compute_tcap
from parser import generate_mutation_subsumption_graph
from plot import plot_graph


def parse_arguments():
    """
    Parse command-line arguments for the script.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Generate a mutation subsumption graph")
    parser.add_argument("--csv", help="CSV file with mutants", nargs=2, required=True)
    parser.add_argument("--killmatrix", help="CSV file with the kill matrix", nargs=4, required=True)
    parser.add_argument("--output", help="Output file for the graph")
    parser.add_argument("--tcap", help="Calculate the T-cap", action="store_true")
    parser.add_argument("--sanitize", help="Use sanitize", action="store_true")
    parser.add_argument("--disable_cache", help="Disable cache and force sanitization", action="store_true")
    parser.add_argument("--results_dir", help="Directory to store the results", required=False)
    parser.add_argument("--results_prefix", help="Prefix for the result files", required=False)
    return parser.parse_args()


def cache_exists(file_path):
    """
    Check if the cached sanitized file exists.

    Args:
        file_path (str): Path to the cached file.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    return path.exists(file_path)






def load_cache_if_possible(file_path, cache_path, disable_cache):

    if not disable_cache and cache_exists(cache_path):
        # Load from cache
        return pd.read_csv(cache_path)
    else:
        # Sanitize and cache
        return sanitize_data(file_path, cache_path)


def compute_dominator_mutants(hierarchy, short_names_to_nodes_mapping):
    """
    Compute and return the dominator mutants (mutants without parents).

    Args:
        hierarchy: The graph hierarchy.
        short_names_to_nodes_mapping (dict): Mapping from short names to nodes.

    Returns:
        pd.DataFrame: A DataFrame containing dominator mutants and their detecting tests.
    """
    dominator_mutants = [node for node in hierarchy.nodes() if hierarchy.in_degree(node) == 0 and len(node.tests) > 0]
    dominator_mutants_df = pd.DataFrame(columns=["Node", "Mutants", "Tests"])
    dominator_mutant_detecting_tests = set()

    for mutant in dominator_mutants:
        dominator_mutants_df.loc[len(dominator_mutants_df)] = {
            "Node": mutant,
            "Mutants": set(short_names_to_nodes_mapping[mutant.name].split("-")),
            "Tests": mutant.tests
        }
        dominator_mutant_detecting_tests = dominator_mutant_detecting_tests.union(mutant.tests)

    return dominator_mutants_df, dominator_mutant_detecting_tests


def compute_lowest_layer_mutants(hierarchy, merged_nodes, short_names_to_nodes_mapping):
    """
    Compute and return the lowest layer mutants that are not equivalent.

    Args:
        hierarchy: The graph hierarchy.
        merged_nodes (dict): Merged nodes data.
        short_names_to_nodes_mapping (dict): Mapping from short names to nodes.

    Returns:
        pd.DataFrame: A DataFrame containing the lowest layer mutants and their unique tests.
    """
    equivalent_mutants = [node for node in hierarchy.nodes() if len(merged_nodes[str(node)].tests) == 0]
    lowest_layer_mutants = [node for node in hierarchy.nodes() if
                            hierarchy.out_degree(node) == 0 and node not in equivalent_mutants]

    lowest_layer_mutant_to_unique_tests_df = pd.DataFrame(columns=["Node", "Mutants", "Unique Tests", "Tests"])

    for mutant in lowest_layer_mutants:
        tests = copy(mutant.tests)
        parents = hierarchy.predecessors(mutant)
        for parent in parents:
            tests = tests - parent.tests
        mutant.unique_tests = mutant.tests if len(tests) == 0 else tests

        lowest_layer_mutant_to_unique_tests_df.loc[len(lowest_layer_mutant_to_unique_tests_df)] = {
            "Node": mutant,
            "Mutants": set(short_names_to_nodes_mapping[mutant.name].split("-")),
            "Unique Tests": mutant.unique_tests,
            "Tests": mutant.tests
        }

    return lowest_layer_mutant_to_unique_tests_df


def create_results_directory(results_dir="results"):
    """
    Creates a directory for the current run based on the timestamp (year, month, day, hour, minute, second).

    Returns:
        str: The path to the created directory.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    results_dir = path.join(results_dir, timestamp)
    makedirs(results_dir, exist_ok=True)
    return results_dir


def main():
    args = parse_arguments()

    # Create the results directory based on the current timestamp
    results_dir = create_results_directory(args.results_dir)

    #
    cache_dir = path.join("cache")
    makedirs(cache_dir, exist_ok=True)

    # Define cache paths for CSV and killmatrix
    csv_cache_path = path.join(cache_dir, f"{path.basename(args.csv[0])}_sanitized.csv")
    killmatrix_cache_path = path.join(cache_dir, f"{path.basename(args.killmatrix[0])}_sanitized.csv")

    # Load or sanitize the files
    csv_df = load_cache_if_possible(args.csv[0], csv_cache_path, args.disable_cache)
    kill_matrix_df = load_cache_if_possible(args.killmatrix[0], killmatrix_cache_path, args.disable_cache)

    # Generate the mutation subsumption graph
    hierarchy, merged_nodes, short_names_to_nodes_mapping = generate_mutation_subsumption_graph(
        csv_df, int(args.csv[1]), kill_matrix_df, int(args.killmatrix[1]), int(args.killmatrix[2]),
        int(args.killmatrix[3])
    )

    print(f"short_names_to_nodes_mapping: {short_names_to_nodes_mapping}")

    # Output the graph if specified
    plot_graph(hierarchy, results_dir, args.results_prefix)

    # Compute and save dominator mutants
    dominator_mutants_df, dominator_mutant_detecting_tests = compute_dominator_mutants(hierarchy,
                                                                                       short_names_to_nodes_mapping)

    print(f"Dominator mutants: {dominator_mutants_df}")

    dominator_mutants_df.to_csv(path.join(results_dir, f"{args.results_prefix}_dominator_mutants_tests.csv"),
                                index=False)

    # Compute and save lowest layer mutants
    lowest_layer_mutant_to_unique_tests_df = compute_lowest_layer_mutants(hierarchy, merged_nodes,
                                                                          short_names_to_nodes_mapping)
    lowest_layer_mutant_to_unique_tests_df.to_csv(
        path.join(results_dir, f"{args.results_prefix}_lowest_layer_mutant_to_unique_tests.csv"), index=False)

    # Calculate the T-cap if requested
    if args.tcap:
        tcap_scores_df = compute_tcap(hierarchy, dominator_mutants_df["Node"],
                                      dominator_mutant_detecting_tests,
                                      short_names_to_nodes_mapping)
        tcap_scores_df.to_csv(path.join(results_dir, f"{args.results_prefix}_tcap_scores.csv"), index=False)

def sanitize_data(csv_file, cache_path):
    # if the entry for a cell is empty, replace it with 0
    df = pd.read_csv(csv_file)
    df.fillna(0, inplace=True)
    # create a new csv file with the sanitized data with sanitized+time appended to the filename
    df.to_csv(cache_path, index=False)
    return df

if __name__ == "__main__":
    main()
