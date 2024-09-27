import unittest
from unittest import mock
import pandas as pd
from main import compute_dominator_mutants, compute_lowest_layer_mutants, compute_tcap
from MutantNode import MutantNode
import networkx as nx

class TestTCAPMock(unittest.TestCase):

    def setUp(self):
        # Set up mock data for mutants and killmatrix
        self.mutants_df = pd.DataFrame({
            "Mutant": ["m1", "m2", "m3", "m4", "m5", "m6", "m7", "m8", "m9", "m10", "m11", "m12", "m13", "m14"],
            "KilledTests": [set(), {"t2", "t4"}, {"t1"}, {"t2"}, {"t2"}, {"t1"}, {"t2"}, {"t1"}, {"t2"}, set(), {"t1"}, {"t1"}, {"t1"}, {"t2"}]
        })

        self.killmatrix_df = pd.DataFrame({
            "TestID": ["t1", "t1", "t1", "t1", "t1", "t1", "t1", "t1", "t1", "t1", "t1", "t1", "t1", "t1",
                       "t2", "t2", "t2", "t2", "t2", "t2", "t2", "t2", "t2", "t2", "t2", "t2", "t2", "t2",
                       "t3", "t3", "t3", "t3", "t3", "t3", "t3", "t3", "t3", "t3", "t3", "t3", "t3", "t3",
                       "t4", "t4", "t4", "t4", "t4", "t4", "t4", "t4", "t4", "t4", "t4", "t4", "t4", "t4"],
            "Mutant": ["m1", "m2", "m3", "m4", "m5", "m6", "m7", "m8", "m9", "m10", "m11", "m12", "m13", "m14",
                       "m1", "m2", "m3", "m4", "m5", "m6", "m7", "m8", "m9", "m10", "m11", "m12", "m13", "m14",
                       "m1", "m2", "m3", "m4", "m5", "m6", "m7", "m8", "m9", "m10", "m11", "m12", "m13", "m14",
                       "m1", "m2", "m3", "m4", "m5", "m6", "m7", "m8", "m9", "m10", "m11", "m12", "m13", "m14"],
            "Killed": [0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1, 0,
                       0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1,
                       0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
        })

        # Create a basic hierarchy
        self.hierarchy = nx.DiGraph()

        # Short names mapping for the mutants
        self.short_names_to_nodes_mapping = {
            'X00': 'm2-m5', 'X01': 'm3-m6', 'X02': 'm1-m10', 'X03': 'm11-m12', 'X04': 'm8-m13', 'X05': 'm4-m7-m9-m14'
        }


        # Create nodes for each mutant
        self.mutant_nodes = {f"m{i}": MutantNode(f"m{i}") for i in range(1, 15)}
        # Assign test sets to each mutant node using killmatrix_df
        for mutant_name in self.mutant_nodes:
            # Get all tests that killed this mutant
            killing_tests = set(
                self.killmatrix_df[
                    (self.killmatrix_df["Mutant"] == mutant_name) & (self.killmatrix_df["Killed"] == 1)
                    ]["TestID"].unique()
            )
            # Assign the tests to the mutant node
            self.mutant_nodes[mutant_name].add_tests(killing_tests)


        self.merged_nodes = {}

        for key_ in self.short_names_to_nodes_mapping.keys():
            self.merged_nodes[key_] = self.mutant_nodes[self.short_names_to_nodes_mapping[key_].split("-")[0]]
            self.merged_nodes[key_].name = key_




        # Add nodes to the hierarchy graph
        for node in self.merged_nodes.values():
            self.hierarchy.add_node(node)

        # Add edges to simulate parent-child relationships
        # self.hierarchy.add_edge(self.mutant_nodes['m4'], self.mutant_nodes['m2'])
        # self.hierarchy.add_edge(self.mutant_nodes['m6'], self.mutant_nodes['m3'])




    def test_dominator_mutants(self):
        # Modify the mutant nodes to use short names (like X04, X05, etc.) in the mock hierarchy
        mutant_node_mapping = {
            'X04': self.mutant_nodes['m8'],  # m8-m13 group
            'X05': self.mutant_nodes['m4']  # m4-m7-m9-m14 group
        }

        # Set the names for each node
        for short_name, mutant_node in mutant_node_mapping.items():
            mutant_node.name = short_name  # Assign short name to the mock node

        # Create a mock hierarchy based on these short names
        self.hierarchy = nx.DiGraph()
        for node in mutant_node_mapping.values():
            self.hierarchy.add_node(node)

        # Add an edge to simulate parent-child relationships
        self.hierarchy.add_edge(self.mutant_nodes['m4'], self.mutant_nodes['m2'])  # Example edge

        # Compute dominator mutants with updated mock hierarchy
        dominator_mutants_df, dominator_mutant_detecting_tests = compute_dominator_mutants(self.hierarchy,
                                                                                           self.short_names_to_nodes_mapping)

        # Define the expected dominator nodes using short names
        expected_dominators = {"X04", "X05"}  # These are the short names representing dominators

        # Extract the dominator mutants from the DataFrame
        dominator_mutants = set(dominator_mutants_df['Node'].apply(lambda node: node.name))

        # Assert that the expected dominators are in the result
        self.assertTrue(expected_dominators.issubset(dominator_mutants),
                        f"Expected dominators: {expected_dominators}, but got: {dominator_mutants}")

    @mock.patch('main.create_results_directory')
    def test_tcap_scores(self, mock_create_results_directory):
        # Simulate dominator mutants
        dominator_mutants = {'X04', 'X05'}
        dominator_mutant_detecting_tests = {'t1', 't2'}

        # Compute TCAP scores
        print(self.hierarchy, dominator_mutants, dominator_mutant_detecting_tests, self.short_names_to_nodes_mapping)
        tcap_df = compute_tcap(self.hierarchy, dominator_mutants, dominator_mutant_detecting_tests, self.short_names_to_nodes_mapping)

        print(tcap_df)

        # Expected TCAP scores
        expected_tcap = {
            'm2': 0.5, 'm5': 0.5, 'm3': 0.5, 'm6': 0.5,
            'm1': 0.0, 'm10': 0.0, 'm11': 1.0, 'm12': 1.0,
            'm8': 1.0, 'm13': 1.0, 'm4': 1.0, 'm7': 1.0,
            'm9': 1.0, 'm14': 1.0
        }

        for _, row in tcap_df.iterrows():
            mutant = row['Mutant']
            tcap_score = row['TCAP']
            self.assertEqual(expected_tcap[mutant], tcap_score, f"Expected TCAP for {mutant}: {expected_tcap[mutant]}, but got: {tcap_score}")

    @mock.patch('main.create_results_directory')
    def test_lowest_layer_mutants(self, mock_create_results_directory):
        # Modify the mutant nodes to use short names (like X00, X01, etc.)



        # Compute lowest layer mutants
        print(f"{self.hierarchy.nodes}, self.merged_nodes={self.merged_nodes}, self.short_names_to_nodes_mapping={self.short_names_to_nodes_mapping}")
        lowest_layer_df = compute_lowest_layer_mutants(self.hierarchy,
                                                       self.merged_nodes,
                                                       self.short_names_to_nodes_mapping
                                                       )

        # Expected lowest layer mutants (compare actual sets, not their string representations)
        expected_lowest_layer = [{"m6", "m3"}]

        # Check that the lowest layer mutants are correctly grouped
        lowest_layer_mutants = []
        for row in lowest_layer_df['Mutants']:
            # Convert string representation of sets back to actual sets
            lowest_layer_mutants.append(row)  # Evaluating to convert back to set

        # Assert that the expected sets are found in the result
        for expected_set in expected_lowest_layer:
            self.assertIn(expected_set, lowest_layer_mutants,
                          f"Expected lowest layer mutants: {expected_set}, but got: {lowest_layer_mutants}")


if __name__ == '__main__':
    unittest.main()
