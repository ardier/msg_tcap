import unittest
from unittest import mock
import pandas as pd
import os
import tempfile
from main import main
from MutantNode import MutantNode
import networkx as nx

class TestMainWithTCAPData(unittest.TestCase):

    @mock.patch("main.parse_arguments")
    @mock.patch("main.load_cache_if_possible")
    @mock.patch("main.plot_graph")
    @mock.patch("main.create_results_directory")
    def test_main_with_tcap_data(self, mock_create_results_directory, mock_plot_graph, mock_load_cache_if_possible, mock_parse_arguments):
        # Mock the arguments
        mock_parse_arguments.return_value = mock.Mock(
            csv=["test_data/tcap/killmatrix.csv", 1],
            killmatrix=["test_data/tcap/killmatrix.csv", 1, 0, 2],
            output=None,
            tcap=True,
            sanitize=False,
            disable_cache=False,
            results_dir="../results",
            results_prefix="tcap"
        )

        # Mock the sanitized data loading
        mock_load_cache_if_possible.side_effect = [
            pd.DataFrame({
                'mutant': ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9', 'm10', 'm11', 'm12', 'm13', 'm14'],
            }),
            pd.DataFrame({
                'TestID': ['t1', 't1', 't1', 't2', 't2', 't2', 't2', 't2', 't3', 't3', 't4', 't4', 't4'],
                'Mutant': ['m1', 'm3', 'm5', 'm7', 'm9', 'm11', 'm13', 'm2', 'm4', 'm6', 'm8', 'm10', 'm12'],
                'Killed': [0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1]
            })
        ]

        # Create a temporary directory to use as the mock results directory
        with tempfile.TemporaryDirectory() as temp_results_dir:
            mock_create_results_directory.return_value = temp_results_dir

            # Run the main function
            with mock.patch("main.generate_mutation_subsumption_graph") as mock_generate_graph:
                # Mock hierarchy and short names mapping
                mock_hierarchy = nx.DiGraph()

                node1 = MutantNode("X01")
                node2 = MutantNode("X02")
                node3 = MutantNode("X03")
                node4 = MutantNode("X04")

                node1.add_tests({"t1"})
                node2.add_tests({"t2"})
                node3.add_tests({"t3"})
                node4.add_tests({"t4"})

                mock_hierarchy.add_node(node1)
                mock_hierarchy.add_node(node2)
                mock_hierarchy.add_node(node3)
                mock_hierarchy.add_node(node4)

                mock_generate_graph.return_value = (mock_hierarchy, {"X01": node1, "X02": node2, "X03": node3, "X04": node4},
                                                    {"X01": "m1", "X02": "m2", "X03": "m3", "X04": "m4"})

                # Call main to execute the test
                main()

                # Check if the dominator mutants were correctly computed
                self.assertTrue(mock_plot_graph.called)
                mock_generate_graph.assert_called()

                # Verify that the CSV file was written in the mock results directory
                dominator_file_path = os.path.join(temp_results_dir, "tcap_dominator_mutants_tests.csv")
                self.assertTrue(os.path.exists(dominator_file_path))

                # Verify that the lowest layer mutant CSV file is written
                lowest_layer_mutants_file_path = os.path.join(temp_results_dir, "tcap_lowest_layer_mutant_to_unique_tests.csv")
                self.assertTrue(os.path.exists(lowest_layer_mutants_file_path))

    @mock.patch("main.parse_arguments")
    @mock.patch("main.load_cache_if_possible")
    @mock.patch("main.create_results_directory")
    def test_dominator_mutants(self, mock_create_results_directory, mock_load_cache_if_possible, mock_parse_arguments):
        """
        Test dominator mutants computation using the given killmatrix.csv data.
        """
        # Mock the arguments
        mock_parse_arguments.return_value = mock.Mock(
            csv=["test_data/tcap/killmatrix.csv", 1],
            killmatrix=["test_data/tcap/killmatrix.csv", 1, 0, 2],
            output=None,
            tcap=False,
            sanitize=False,
            disable_cache=False,
            results_dir="../results",
            results_prefix="tcap"
        )

        # Mock the sanitized data loading
        mock_load_cache_if_possible.side_effect = [
            pd.DataFrame({
                'mutant': ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9', 'm10', 'm11', 'm12', 'm13', 'm14'],
            }),
            pd.DataFrame({
                'TestID': ['t1', 't1', 't2', 't2', 't3', 't4'],
                'Mutant': ['m1', 'm3', 'm5', 'm7', 'm9', 'm11'],
                'Killed': [0, 1, 1, 0, 1, 0]
            })
        ]

        # Create a temporary directory to use as the mock results directory
        with tempfile.TemporaryDirectory() as temp_results_dir:
            mock_create_results_directory.return_value = temp_results_dir

            # Run the main function
            with mock.patch("main.generate_mutation_subsumption_graph") as mock_generate_graph:
                # Mock hierarchy and short names mapping
                mock_hierarchy = nx.DiGraph()

                node1 = MutantNode("X01")
                node2 = MutantNode("X02")
                node3 = MutantNode("X03")

                node1.add_tests({"t1"})
                node2.add_tests({"t2"})
                node3.add_tests({"t3"})

                mock_hierarchy.add_node(node1)
                mock_hierarchy.add_node(node2)
                mock_hierarchy.add_node(node3)

                mock_generate_graph.return_value = (mock_hierarchy, {"X01": node1, "X02": node2, "X03": node3},
                                                    {"X01": "m1", "X02": "m2", "X03": "m3"})

                # Call main to execute the test
                main()

                # Verify that the CSV file for dominator mutants is written
                dominator_file_path = os.path.join(temp_results_dir, "tcap_dominator_mutants_tests.csv")
                self.assertTrue(os.path.exists(dominator_file_path))

    @mock.patch("main.parse_arguments")
    @mock.patch("main.load_cache_if_possible")
    @mock.patch("main.create_results_directory")
    def test_lowest_layer_mutants(self, mock_create_results_directory, mock_load_cache_if_possible, mock_parse_arguments):
        """
        Test lowest layer mutants computation using the given killmatrix.csv data.
        """
        # Mock the arguments
        mock_parse_arguments.return_value = mock.Mock(
            csv=["test_data/tcap/killmatrix.csv", 1],
            killmatrix=["test_data/tcap/killmatrix.csv", 1, 0, 2],
            output=None,
            tcap=False,
            sanitize=False,
            disable_cache=False,
            results_dir="../results",
            results_prefix="tcap"
        )

        # Mock the sanitized data loading
        mock_load_cache_if_possible.side_effect = [
            pd.DataFrame({
                'mutant': ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9', 'm10', 'm11', 'm12', 'm13', 'm14'],
            }),
            pd.DataFrame({
                'TestID': ['t1', 't1', 't2', 't2', 't3', 't4'],
                'Mutant': ['m1', 'm3', 'm5', 'm7', 'm9', 'm11'],
                'Killed': [0, 1, 1, 0, 1, 0]
            })
        ]

        # Create a temporary directory to use as the mock results directory
        with tempfile.TemporaryDirectory() as temp_results_dir:
            mock_create_results_directory.return_value = temp_results_dir

            # Run the main function
            with mock.patch("main.generate_mutation_subsumption_graph") as mock_generate_graph:
                # Mock hierarchy and short names mapping
                mock_hierarchy = nx.DiGraph()

                node1 = MutantNode("X01")
                node2 = MutantNode("X02")
                node3 = MutantNode("X03")

                node1.add_tests({"t1"})
                node2.add_tests({"t2"})
                node3.add_tests({"t3"})

                mock_hierarchy.add_node(node1)
                mock_hierarchy.add_node(node2)
                mock_hierarchy.add_node(node3)

                mock_generate_graph.return_value = (mock_hierarchy, {"X01": node1, "X02": node2, "X03": node3},
                                                    {"X01": "m1", "X02": "m2", "X03": "m3"})

                # Call main to execute the test
                main()

                # Verify that the CSV file for lowest layer mutants is written
                lowest_layer_mutants_file_path = os.path.join(temp_results_dir, "tcap_lowest_layer_mutant_to_unique_tests.csv")
                self.assertTrue(os.path.exists(lowest_layer_mutants_file_path))

    @mock.patch("main.parse_arguments")
    @mock.patch("main.load_cache_if_possible")
    @mock.patch("main.create_results_directory")

    def test_main_without_tcap_data(self, mock_create_results_directory, mock_load_cache_if_possible, mock_parse_arguments):
        # Mock the arguments
        mock_parse_arguments.return_value = mock.Mock(
            csv=["test_data/tcap/killmatrix.csv", 1],
            killmatrix=["test_data/tcap/killmatrix.csv", 1, 0, 2],
            output=None,
            tcap=False,
            sanitize=False,
            disable_cache=False,
            results_dir="../results",
            results_prefix="tcap"
        )

        # Mock the sanitized data loading
        mock_load_cache_if_possible.side_effect = [
            pd.DataFrame({
                'mutant': ['m1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9', 'm10', 'm11', 'm12', 'm13', 'm14'],
            }),
            pd.DataFrame({
                'TestID': ['t1', 't1', 't1', 't2', 't2', 't2', 't2', 't2', 't3', 't3', 't4', 't4', 't4'],
                'Mutant': ['m1', 'm3', 'm5', 'm7', 'm9', 'm11', 'm13', 'm2', 'm4', 'm6', 'm8', 'm10', 'm12'],
                'Killed': [0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1]
            })
        ]

        # Create a temporary directory to use as the mock results directory
        with tempfile.TemporaryDirectory() as temp_results_dir:
            mock_create_results_directory.return_value = temp_results_dir

            # Run the main function
            with mock.patch("main.generate_mutation_subsumption_graph") as mock_generate_graph:
                # Mock hierarchy and short names mapping
                mock_hierarchy = nx.DiGraph()

                node1 = MutantNode("X01")
                node2 = MutantNode("X02")
                node3 = MutantNode("X03")
                node4 = MutantNode("X04")

                node1.add_tests({"t1"})
                node2.add_tests({"t2"})
                node3.add_tests({"t3"})
                node4.add_tests({"t4"})
                mock_hierarchy.add_node(node1)
                mock_hierarchy.add_node(node2)
                mock_hierarchy.add_node(node3)
                mock_hierarchy.add_node(node4)

                mock_generate_graph.return_value = (mock_hierarchy, {"X01": node1, "X02": node2, "X03": node3, "X04": node4},
                                                    {"X01": "m1", "X02": "m2", "X03": "m3", "X04": "m4"})
                # Call main to execute the test
                main()

                # Check if the dominator mutants were correctly computed
                mock_generate_graph.assert_called()




if __name__ == "__main__":
    unittest.main()
