import os
import unittest
import tempfile
import pandas as pd
from unittest.mock import patch
from main import main
from datetime import datetime
import shutil

class TestTCAPIntegration(unittest.TestCase):

    def setUp(self):
        # Prepare temporary directory and prefix for the test
        self.test_dir = tempfile.mkdtemp()
        self.prefix = "tcap"
        self.csv_path = "../test_data/tcap/killmatrix.csv"  # Assuming test data is stored here
        self.results_dir = self.test_dir  # Override the default results directory

    def tearDown(self):
        # Remove the temporary directory after the test
        shutil.rmtree(self.test_dir)

    @patch('main.create_results_directory')
    def test_tcap_integration(self, mock_create_results_directory):
        # Patch create_results_directory to use the temp directory
        timestamp_dir = os.path.join(self.results_dir, datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        os.makedirs(timestamp_dir, exist_ok=True)
        mock_create_results_directory.return_value = timestamp_dir

        # Integration test that runs the full pipeline
        args = [
            "--csv", self.csv_path, "1",
            "--killmatrix", self.csv_path, "1", "0", "2",
            "--tcap",
            "--results_prefix", self.prefix,
            "--results_dir", self.results_dir
        ]

        # Execute the main function with the given arguments
        with unittest.mock.patch('sys.argv', ['main.py'] + args):
            main()

        # Define expected file paths
        dominator_file = os.path.join(timestamp_dir, f"{self.prefix}_dominator_mutants_tests.csv")
        tcap_scores_file = os.path.join(timestamp_dir, f"{self.prefix}_tcap_scores.csv")
        lowest_layer_file = os.path.join(timestamp_dir, f"{self.prefix}_lowest_layer_mutant_to_unique_tests.csv")

        # Check that the generated files exist
        self.assertTrue(os.path.exists(dominator_file), f"Dominator file does not exist: {dominator_file}")
        self.assertTrue(os.path.exists(tcap_scores_file), f"TCAP scores file does not exist: {tcap_scores_file}")
        self.assertTrue(os.path.exists(lowest_layer_file), f"Lowest layer file does not exist: {lowest_layer_file}")

        # Load and test the content of each file
        self._check_dominator_file(dominator_file)
        self._check_tcap_scores_file(tcap_scores_file)
        self._check_lowest_layer_file(lowest_layer_file)

    def _check_dominator_file(self, filepath):
        # Load the dominator file and verify contents
        dominator_df = pd.read_csv(filepath)
        print(f"Dominator file contents:\n{dominator_df}")

        # Define expected dominator mutants
        expected_dominators = {"m8", "m13", "m4", "m7", "m9", "m14"}

        # Check that the correct dominators are present in the file
        dominator_mutants = set()
        for row in dominator_df['Mutants']:
            dominator_mutants.update(eval(row))  # Convert string representation of set back to set

        self.assertTrue(expected_dominators.issubset(dominator_mutants), f"Expected dominator mutants: {expected_dominators}, but got: {dominator_mutants}")

    def _check_tcap_scores_file(self, filepath):
        # Load the TCAP scores file and verify contents
        tcap_df = pd.read_csv(filepath)
        print(f"TCAP scores file contents:\n{tcap_df}")

        # Expected TCAP scores based on the integration logic
        expected_tcap = {
            'm2': 0.5, 'm5': 0.5, 'm3': 0.5, 'm6': 0.5,
            'm1': 0.0, 'm10': 0.0, 'm11': 1.0, 'm12': 1.0,
            'm8': 1.0, 'm13': 1.0, 'm4': 1.0, 'm7': 1.0,
            'm9': 1.0, 'm14': 1.0
        }

        # Check TCAP scores
        for _, row in tcap_df.iterrows():
            mutant = row['Mutant']
            tcap_score = row['TCAP']
            self.assertEqual(expected_tcap[mutant], tcap_score, f"Expected TCAP for {mutant}: {expected_tcap[mutant]}, but got: {tcap_score}")

    def _check_lowest_layer_file(self, filepath):
        # Load the lowest layer file and verify contents
        lowest_layer_df = pd.read_csv(filepath)
        print(f"Lowest layer file contents:\n{lowest_layer_df}")

        # Expected lowest layer mutants
        expected_lowest_layer = {"{'m6', 'm3'}"}
        expected_lowest_layer_ = {"{'m3', 'm6'}"}

        # Check that the lowest layer mutants are correctly grouped
        lowest_layer_mutants = set()
        for row in lowest_layer_df['Mutants']:
            lowest_layer_mutants.add(row)

        self.assertTrue(expected_lowest_layer.issubset(lowest_layer_mutants) or expected_lowest_layer_.issubset(lowest_layer_mutants), f"Expected lowest layer mutants: {expected_lowest_layer} or {expected_lowest_layer_}, but got: {lowest_layer_mutants}")

if __name__ == '__main__':
    unittest.main()
