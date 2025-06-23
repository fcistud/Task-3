"""
Unit tests for the command-line interface of the Stack Overflow Survey Data Analysis Library.
"""

import unittest
import io
import sys
import os
import tempfile
import pandas as pd
from pathlib import Path
from unittest.mock import patch

from so_lib.cli import main

class TestCLI(unittest.TestCase):
    """Test cases for the CLI module"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a minimal test dataset
        self.test_data_dir = Path(__file__).parent / "test_data"
        self.test_data_dir.mkdir(exist_ok=True)
        
        self.test_data_path = self.test_data_dir / "test_so_data.xlsx"
        
        # Create schema data
        schema_data = {
            'column': ['Q1', 'Q2', 'Q3'],
            'question_text': [
                'Test question 1?', 
                'Test multiple-choice question?', 
                'Another test question?'
            ],
            'type': ['SC', 'MC', 'SC']
        }
        
        # Create raw data
        raw_data = {
            'Q1': ['Option A', 'Option B', 'Option A', 'Option C'],
            'Q2': [
                'Option X;Option Y', 
                'Option Z', 
                'Option X', 
                'Option Y;Option Z'
            ],
            'Q3': ['Yes', 'No', 'Yes', 'Yes']
        }
        
        # Create Excel file with both sheets
        with pd.ExcelWriter(self.test_data_path) as writer:
            pd.DataFrame(schema_data).to_excel(writer, sheet_name='schema', index=False)
            pd.DataFrame(raw_data).to_excel(writer, sheet_name='raw data', index=False)
        
        # Override the default data path for testing
        self.original_data_path = os.environ.get('SO_DATA_PATH')
        os.environ['SO_DATA_PATH'] = str(self.test_data_path)
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Restore the original data path
        if self.original_data_path:
            os.environ['SO_DATA_PATH'] = self.original_data_path
        else:
            os.environ.pop('SO_DATA_PATH', None)
        
        # Remove test data file
        if self.test_data_path.exists():
            self.test_data_path.unlink()
        
        # Remove test data directory
        if self.test_data_dir.exists():
            self.test_data_dir.rmdir()

    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('sys.argv', ['so_lib', 'list-questions', '--data-path'])
    def test_list_questions_command(self, mock_stdout, mock_argv):
        """Test the list-questions command"""
        # Add data path to args
        mock_argv.append(str(self.test_data_path))
        
        # Redirect stdout and run the command
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            with patch('sys.argv', mock_argv):
                with self.assertRaises(SystemExit) as cm:
                    main()
                
                # Command should exit with code 0 on success
                if hasattr(cm.exception, 'code'):
                    self.assertEqual(cm.exception.code, 0)
                
                output = mock_stdout.getvalue()
                self.assertIn('Q1', output)
                self.assertIn('Test question 1?', output)
                self.assertIn('Q2', output)
                self.assertIn('Test multiple-choice question?', output)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_search_questions_command(self, mock_stdout):
        """Test the search-questions command"""
        with patch('sys.argv', ['so_lib', 'search-questions', 'multiple', '--data-path', str(self.test_data_path)]):
            try:
                main()
            except SystemExit:
                pass
            
            output = mock_stdout.getvalue()
            self.assertIn('Q2', output)
            self.assertIn('Test multiple-choice question?', output)
            self.assertNotIn('Q1', output)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_search_options_command(self, mock_stdout):
        """Test the search-options command"""
        with patch('sys.argv', ['so_lib', 'search-options', 'Q2', '--data-path', str(self.test_data_path)]):
            try:
                main()
            except SystemExit:
                pass
            
            output = mock_stdout.getvalue()
            self.assertIn('Options for question: Q2', output)
            self.assertIn('Option X', output)
            self.assertIn('Option Y', output)
            self.assertIn('Option Z', output)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_distribution_sc_command(self, mock_stdout):
        """Test the distribution-sc command"""
        with patch('sys.argv', ['so_lib', 'distribution-sc', 'Q1', '--data-path', str(self.test_data_path)]):
            try:
                main()
            except SystemExit:
                pass
            
            output = mock_stdout.getvalue()
            self.assertIn('Distribution for: Q1', output)
            self.assertIn('Test question 1?', output)
            self.assertIn('Option A', output)
            self.assertIn('50.00%', output)  # Option A percentage

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_distribution_mc_command(self, mock_stdout):
        """Test the distribution-mc command"""
        with patch('sys.argv', ['so_lib', 'distribution-mc', 'Q2', '--data-path', str(self.test_data_path)]):
            try:
                main()
            except SystemExit:
                pass
            
            output = mock_stdout.getvalue()
            self.assertIn('Distribution for: Q2', output)
            self.assertIn('Test multiple-choice question?', output)
            self.assertIn('Option X', output)
            self.assertIn('Option Y', output)
            self.assertIn('Option Z', output)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_subset_command(self, mock_stdout):
        """Test the subset command"""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            with patch('sys.argv', [
                'so_lib', 'subset', 'Q1', 'Option A', 
                '--output', temp_path, 
                '--data-path', str(self.test_data_path)
            ]):
                try:
                    main()
                except SystemExit:
                    pass
                
                output = mock_stdout.getvalue()
                self.assertIn('Created subset with 2 respondents', output)
                self.assertIn(f'Subset saved to {temp_path}', output)
                
                # Verify the saved file
                self.assertTrue(os.path.exists(temp_path))
                df = pd.read_csv(temp_path)
                self.assertEqual(len(df), 2)
                self.assertTrue((df['Q1'] == 'Option A').all())
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main()