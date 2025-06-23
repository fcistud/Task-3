"""
Unit tests for the analysis module of the Stack Overflow Survey Data Analysis Library.
"""

import unittest
import os
import pandas as pd
from pathlib import Path

from so_lib.analysis import subset_respondents, distribution_sc, distribution_mc

class TestAnalysis(unittest.TestCase):
    """Test cases for analysis.py module"""
    
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
    
    def test_subset_respondents_sc(self):
        """Test subsetting respondents for a single-choice question"""
        # Patch the load_data function to use our test data
        def patched_load_data(*args, **kwargs):
            return {
                'schema': pd.DataFrame({
                    'column': ['Q1', 'Q2', 'Q3'],
                    'question_text': [
                        'Test question 1?', 
                        'Test multiple-choice question?', 
                        'Another test question?'
                    ],
                    'type': ['SC', 'MC', 'SC']
                }),
                'raw data': pd.DataFrame({
                    'Q1': ['Option A', 'Option B', 'Option A', 'Option C'],
                    'Q2': [
                        'Option X;Option Y', 
                        'Option Z', 
                        'Option X', 
                        'Option Y;Option Z'
                    ],
                    'Q3': ['Yes', 'No', 'Yes', 'Yes']
                })
            }
        
        original_load_data = None
        try:
            from so_lib import analysis
            original_load_data = analysis.load_data
            analysis.load_data = patched_load_data
            
            # Subset for Q1 with Option A
            subset = subset_respondents('Q1', 'Option A')
            self.assertEqual(len(subset), 2)
            self.assertTrue((subset['Q1'] == 'Option A').all())
            
            # Subset for Q3 with Yes
            subset = subset_respondents('Q3', 'Yes')
            self.assertEqual(len(subset), 3)
            self.assertTrue((subset['Q3'] == 'Yes').all())
        finally:
            # Restore the original function
            if original_load_data:
                analysis.load_data = original_load_data
    
    def test_subset_respondents_mc(self):
        """Test subsetting respondents for a multiple-choice question"""
        # Patch the load_data function to use our test data
        def patched_load_data(*args, **kwargs):
            return {
                'schema': pd.DataFrame({
                    'column': ['Q1', 'Q2', 'Q3'],
                    'question_text': [
                        'Test question 1?', 
                        'Test multiple-choice question?', 
                        'Another test question?'
                    ],
                    'type': ['SC', 'MC', 'SC']
                }),
                'raw data': pd.DataFrame({
                    'Q1': ['Option A', 'Option B', 'Option A', 'Option C'],
                    'Q2': [
                        'Option X;Option Y', 
                        'Option Z', 
                        'Option X', 
                        'Option Y;Option Z'
                    ],
                    'Q3': ['Yes', 'No', 'Yes', 'Yes']
                })
            }
        
        original_load_data = None
        try:
            from so_lib import analysis
            original_load_data = analysis.load_data
            analysis.load_data = patched_load_data
            
            # Subset for Q2 with Option X
            subset = subset_respondents('Q2', 'Option X')
            self.assertEqual(len(subset), 2)
            self.assertTrue(subset['Q2'].str.contains('Option X').all())
            
            # Subset for Q2 with Option Y
            subset = subset_respondents('Q2', 'Option Y')
            self.assertEqual(len(subset), 2)
            self.assertTrue(subset['Q2'].str.contains('Option Y').all())
        finally:
            # Restore the original function
            if original_load_data:
                analysis.load_data = original_load_data
    
    def test_distribution_sc(self):
        """Test distribution calculation for single-choice questions"""
        # Patch the load_data function to use our test data
        def patched_load_data(*args, **kwargs):
            return {
                'schema': pd.DataFrame({
                    'column': ['Q1', 'Q2', 'Q3'],
                    'question_text': [
                        'Test question 1?', 
                        'Test multiple-choice question?', 
                        'Another test question?'
                    ],
                    'type': ['SC', 'MC', 'SC']
                }),
                'raw data': pd.DataFrame({
                    'Q1': ['Option A', 'Option B', 'Option A', 'Option C'],
                    'Q2': [
                        'Option X;Option Y', 
                        'Option Z', 
                        'Option X', 
                        'Option Y;Option Z'
                    ],
                    'Q3': ['Yes', 'No', 'Yes', 'Yes']
                })
            }
        
        original_load_data = None
        try:
            from so_lib import analysis
            original_load_data = analysis.load_data
            analysis.load_data = patched_load_data
            
            # Distribution for Q1
            dist = distribution_sc('Q1')
            self.assertEqual(dist['question_id'], 'Q1')
            self.assertEqual(dist['question_text'], 'Test question 1?')
            self.assertIn('distribution', dist)
            
            # Check percentages
            self.assertEqual(dist['distribution']['Option A'], 50.0)  # 2/4 = 50%
            self.assertEqual(dist['distribution']['Option B'], 25.0)  # 1/4 = 25%
            self.assertEqual(dist['distribution']['Option C'], 25.0)  # 1/4 = 25%
            
            # Distribution for Q3
            dist = distribution_sc('Q3')
            self.assertEqual(dist['distribution']['Yes'], 75.0)  # 3/4 = 75%
            self.assertEqual(dist['distribution']['No'], 25.0)   # 1/4 = 25%
        finally:
            # Restore the original function
            if original_load_data:
                analysis.load_data = original_load_data
    
    def test_distribution_mc(self):
        """Test distribution calculation for multiple-choice questions"""
        # Patch the load_data function to use our test data
        def patched_load_data(*args, **kwargs):
            return {
                'schema': pd.DataFrame({
                    'column': ['Q1', 'Q2', 'Q3'],
                    'question_text': [
                        'Test question 1?', 
                        'Test multiple-choice question?', 
                        'Another test question?'
                    ],
                    'type': ['SC', 'MC', 'SC']
                }),
                'raw data': pd.DataFrame({
                    'Q1': ['Option A', 'Option B', 'Option A', 'Option C'],
                    'Q2': [
                        'Option X;Option Y', 
                        'Option Z', 
                        'Option X', 
                        'Option Y;Option Z'
                    ],
                    'Q3': ['Yes', 'No', 'Yes', 'Yes']
                })
            }
        
        original_load_data = None
        try:
            from so_lib import analysis
            original_load_data = analysis.load_data
            analysis.load_data = patched_load_data
            
            # Distribution for Q2
            dist = distribution_mc('Q2')
            self.assertEqual(dist['question_id'], 'Q2')
            self.assertEqual(dist['question_text'], 'Test multiple-choice question?')
            self.assertIn('distribution', dist)
            
            # Check percentages (out of 4 total respondents)
            self.assertEqual(dist['distribution']['Option X'], 50.0)  # 2/4 = 50%
            self.assertEqual(dist['distribution']['Option Y'], 50.0)  # 2/4 = 50%
            self.assertEqual(dist['distribution']['Option Z'], 50.0)  # 2/4 = 50%
        finally:
            # Restore the original function
            if original_load_data:
                analysis.load_data = original_load_data


if __name__ == '__main__':
    unittest.main()