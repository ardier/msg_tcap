# TODO add to requirements.txt
import networkx as nx
import pandas as pd
import tqdm

from MutantNode import MutantNode


def create_nodes_from_csv(mutants_file_df: pd.DataFrame, column_for_mutants: int):
    mutants_file_df = pd.DataFrame(mutants_file_df[mutants_file_df.columns[column_for_mutants]])
    nodes = {}
    unique_mutants = mutants_file_df[mutants_file_df.columns[0]].unique()
    for mutant_id in tqdm.tqdm(unique_mutants, total=len(unique_mutants),
                               desc="Creating Initial Mutant Nodes"):

        if mutant_id not in nodes:
            nodes[mutant_id] = MutantNode(mutant_id)
    return mutants_file_df, nodes




def parse_kill_matrix(kill_matrix_df: pd.DataFrame, column_for_mutants: int, column_for_tests: int, column_for_kill_status: int):

    # Filter the DataFrame to only include rows where kill status is 1
    filtered_df = kill_matrix_df[kill_matrix_df.iloc[:, column_for_kill_status] == 1]

    # Group by mutant and aggregate the tests into a set, then convert to a DataFrame
    grouped_df = filtered_df.groupby(filtered_df.columns[column_for_mutants])[
        filtered_df.columns[column_for_tests]].apply(lambda x: set(x)).reset_index()

    # Rename the columns for clarity
    grouped_df.columns = ['MutantID', 'KilledTests']

    return grouped_df


def merge_indistinguishable_nodes(nodes):
    merged_nodes = {}
    for node in nodes.values():
        # Check if there's already a node in merged_nodes with the same tests
        for merged_node in merged_nodes.values():
            if node.is_indistinguishable(merged_node):
                # remove the merged node from merged_nodes
                del merged_nodes[merged_node.name]

                merged_node.merge_with(node)
                # update the key for the merged node to its new name
                merged_nodes[merged_node.name] = merged_node
                break
        else:
            # If no indistinguishable node is found, add it to merged_nodes
            merged_nodes[node.name] = node
    return merged_nodes


def create_subsumption_hierarchy(kill_matrix, mutants):
    hierarchy = nx.DiGraph()

    # First, add all mutants as nodes to the hierarchy
    mutants_to_connect = []
    for mutant in mutants:
        hierarchy.add_node(mutants[mutant])
        # only add edges between mutants with tests
        if len(mutants[mutant].tests) > 0:
            mutants_to_connect.append(mutant)

    # Then, iterate through each mutant to establish parent-child relationships
    mutants_considered = set()
    mutants_considered.add(mutants_to_connect[0])

    for mutant in mutants_to_connect[1:]:
        mutants_considered.add(mutant)
        mutant_obj = mutants[mutant]
        tests = mutant_obj.tests

        # micro-optimization: only consider mutants that haven't been considered yet
        for the_other_mutant in list(mutants_considered - set(mutant)):
            the_other_mutant_obj = mutants[the_other_mutant]
            the_other_mutant__tests = the_other_mutant_obj.tests

            # avoid self edges (we should also avoid this
            if the_other_mutant == mutant or len(the_other_mutant__tests) == 0:
                continue

            handle_new_node(hierarchy, mutant_obj, tests, the_other_mutant_obj, the_other_mutant__tests)

    return hierarchy


def handle_new_node(hierarchy, mutant_obj, tests, the_other_mutant_obj, the_other_mutant__tests):
    # Check if the mutant's tests are a superset of the potential parent's tests
    if tests.issuperset(the_other_mutant__tests):
        # Check if there is any direct child of the potential parent that should actually be the direct child of this mutant
        add_or_refine_edge(hierarchy, mutant_obj, tests, the_other_mutant_obj, the_other_mutant__tests)


    elif the_other_mutant__tests.issuperset(tests):
        # Check if there is any direct child of the mutant that should actually be the direct child of the potential parent
        add_or_refine_edge(hierarchy, the_other_mutant_obj, the_other_mutant__tests, mutant_obj, tests)


def add_or_refine_edge(hierarchy, mutant_obj, tests, the_other_mutant_obj, the_other_mutant__tests):
    did_we_recursively_add = []

    for potential_child in mutant_obj.parents:
        # avoid self edges
        if potential_child is the_other_mutant_obj or potential_child in the_other_mutant_obj.parents:
            continue

        if potential_child.tests.issuperset(the_other_mutant__tests):
            did_we_recursively_add.append(add_or_refine_edge(hierarchy, potential_child, potential_child.tests, the_other_mutant_obj, tests))


    if not any(did_we_recursively_add):
        hierarchy.add_edge(the_other_mutant_obj, mutant_obj)
        if mutant_obj not in the_other_mutant_obj.children:
            the_other_mutant_obj.add_child(mutant_obj)
        if the_other_mutant_obj not in mutant_obj.parents:
            mutant_obj.add_parent(the_other_mutant_obj)

        return True
    return False



def enumerate_nodes_with_short_names(merged_nodes):
    # give hexadecimal names to the merged nodes that starts with a letter and replace the name of the node with the hexadecimal name
    short_names_to_nodes_mapping = {}
    for i, node in enumerate(merged_nodes):
        hex_name = hex(i)[2:]
        if i < 10:
            hex_name = f"0{hex_name}"
        hex_name = f"X{hex_name}"
        short_names_to_nodes_mapping[hex_name] = node
        merged_nodes[node].name = hex_name
    # update the keys in merged_nodes
    merged_nodes = {node.name: node for node in merged_nodes.values()}
    return merged_nodes, short_names_to_nodes_mapping


def generate_mutation_subsumption_graph(csv_df, column_for_mutants_in_csv,
                                        killmatrix_df, column_for_mutants_in_kill_matrix,
                                        column_for_tests_in_kill_matrix,
                                        column_for_kill_status_in_kill_matrix):
    mutants_file_df, nodes = create_nodes_from_csv(csv_df, column_for_mutants_in_csv)
    kill_matrix = parse_kill_matrix(killmatrix_df, column_for_mutants_in_kill_matrix,
                                    column_for_tests_in_kill_matrix, column_for_kill_status_in_kill_matrix)

    # assign tests to the nodes
    for _, (mutant, tests) in kill_matrix.iterrows():
        nodes[mutant].add_tests(tests)
    merged_nodes = merge_indistinguishable_nodes(nodes)
    merged_nodes, short_names_to_nodes_mapping = enumerate_nodes_with_short_names(merged_nodes)


    # Create a subsumption hierarchy from the kill matrix
    hierarchy = create_subsumption_hierarchy(kill_matrix, merged_nodes)

    return hierarchy, merged_nodes, short_names_to_nodes_mapping
