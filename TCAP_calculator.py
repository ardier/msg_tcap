import pandas as pd


def compute_tcap(dmsg, dominator_mutants, dominator_mutant_detecting_tests, short_names_to_nodes_mapping):
    """
    Computes the TCAP (Test Coverage Adequacy Percentage) score for each mutant in a Directed Mutation Subsumption Graph (DMSG).

    The TCAP score for a mutant is computed based on the proportion of tests detecting the mutant that also detect
    dominator mutants. Dominator mutants automatically receive a TCAP score of 1.0, as they represent nodes with
    no parents in the hierarchy. Non-dominator mutants get a fractional TCAP score based on how many of their detecting
    tests overlap with the set of tests that detect dominator mutants.

    Args:
        dmsg: The directed mutation subsumption graph (DMSG) where mutants are represented as nodes.
        dominator_mutants (set): A set of dominator mutants (mutants that have no parents in the graph).
        dominator_mutant_detecting_tests (set): The set of tests that detect dominator mutants.
        short_names_to_nodes_mapping (dict): A mapping from short mutant names to their corresponding nodes in the graph.

    Returns:
        pd.DataFrame: A DataFrame containing the TCAP scores for each mutant, with columns "Mutant" and "TCAP".
    """

    print("Computing TCAP...")

    # Dictionary to store TCAP scores for each node in the DMSG
    tcap_scores = {}

    # Iterate over each mutant node in the DMSG
    for mutant_node in dmsg.nodes:
        # If the mutant is a dominator mutant, assign a TCAP of 1.0
        if mutant_node in dominator_mutants:
            tcap_scores[mutant_node] = 1.0
        else:
            # If the mutant has associated tests, compute the TCAP score as the ratio of tests detecting dominator mutants
            if len(mutant_node.tests) > 0:
                tcap = len(mutant_node.tests.intersection(dominator_mutant_detecting_tests)) / len(mutant_node.tests)
            else:
                tcap = 0  # If no tests detect the mutant, the TCAP is 0
            tcap_scores[mutant_node] = tcap

    print(f"TCAP scores for each mutant node: {tcap_scores}")

    # Break down the TCAP scores for each mutant by splitting the short names
    tcap_scores_per_mutant = {mutant: tcap for node, tcap in tcap_scores.items()
                              for mutant in short_names_to_nodes_mapping[node.name].split("-")}


    # Create a DataFrame from the TCAP scores
    tcap_scores_df = pd.DataFrame(tcap_scores_per_mutant.items(), columns=["Mutant", "TCAP"])
    print(f"TCAP scores for each mutant: {tcap_scores_df}")


    return tcap_scores_df
