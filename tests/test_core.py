"""
Unit tests for the core module of the Stack Overflow Survey Data Analysis Library.
"""

import unittest
import os
import pandas as pd
from pathlib import Path

from so_lib.core import load_data, list_questions, search_questions, search_options

class TestCore(unittest.TestCase):
    """Test cases for core.py module"""
    
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
    
    def test_load_data(self):
        """Test that data can be loaded from the test file"""
        data = load_data(self.test_data_path)
        
        self.assertIn('schema', data)
        self.assertIn('raw data', data)
        self.assertEqual(len(data['schema']), 3)
        self.assertEqual(len(data['raw data']), 4)
    
    def test_list_questions(self):
        """Test listing all questions"""
        # Patch the load_data function to use our test data
        def patched_load_data(*args, **kwargs):
            return load_data(self.test_data_path)
        
        original_load_data = load_data
        try:
            from so_lib import core
            core.load_data = patched_load_data
            
            questions = list_questions()
            
            self.assertEqual(len(questions), 3)
            self.assertIn('question_id', questions.columns)
            self.assertIn('question_text', questions.columns)
            self.assertIn('type', questions.columns)
            
            self.assertIn('Q1', questions['question_id'].values)
            self.assertIn('Test question 1?', questions['question_text'].values)
        finally:
            # Restore the original function
            core.load_data = original_load_data
    
    def test_search_questions(self):
        """Test searching for questions"""
        # Patch the load_data function to use our test data
        def patched_load_data(*args, **kwargs):
            return load_data(self.test_data_path)
        
        original_load_data = load_data
        try:
            from so_lib import core
            core.load_data = patched_load_data
            
            # Search by question text
            results = search_questions('multiple')
            self.assertEqual(len(results), 1)
            self.assertEqual(results.iloc[0]['question_id'], 'Q2')
            
            # Search by question ID
            results = search_questions('Q3')
            self.assertEqual(len(results), 1)
            self.assertEqual(results.iloc[0]['question_text'], 'Another test question?')
            
            # Search with no matches
            results = search_questions('nonexistent')
            self.assertEqual(len(results), 0)
        finally:
            # Restore the original function
            core.load_data = original_load_data
    
    def test_search_options(self):
        """Test searching for options of a question"""
        # Patch the load_data function to use our test data
        def patched_load_data(*args, **kwargs):
            return load_data(self.test_data_path)
        
        original_load_data = load_data
        try:
            from so_lib import core
            core.load_data = patched_load_data
            
            # Get options for a single-choice question
            options = search_options('Q1')
            self.assertEqual(options['question_id'], 'Q1')
            self.assertIn('Option A', options['options'])
            self.assertIn('Option B', options['options'])
            self.assertIn('Option C', options['options'])
            
            # Get options for a multiple-choice question
            options = search_options('Q2')
            self.assertEqual(options['question_id'], 'Q2')
            self.assertIn('Option X', options['options'])
            self.assertIn('Option Y', options['options'])
            self.assertIn('Option Z', options['options'])
            
            # Filter options by query
            options = search_options('Q2', 'X')
            self.assertIn('Option X', options['options'])
            self.assertNotIn('Option Z', options['options'])
        finally:
            # Restore the original function
            core.load_data = original_load_data


if __name__ == '__main__':
    unittest.main()