"""
Core functionality for the Stack Overflow Survey Data Analysis Library.

This module provides functions for loading and exploring the survey data.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union

try:
    import pandas as pd
except ImportError:
    print("Error: pandas is required. Install it using 'pip install pandas openpyxl'")
    sys.exit(1)

# Use a default path that can work relatively to the script location
DEFAULT_DATA_PATH = str(Path(__file__).parent.parent / "so_2024_raw.xlsx")

def load_data(file_path: Optional[str] = None) -> Dict[str, pd.DataFrame]:
    """
    Load the Stack Overflow survey data from an Excel file.

    Args:
        file_path: Path to the Excel file. If None, uses default path.

    Returns:
        Dictionary of DataFrames, one per sheet in the Excel file
    
    Raises:
        FileNotFoundError: If the file doesn't exist
        Exception: For other errors during file loading
    """
    # Use the provided path or the default path
    path = file_path or DEFAULT_DATA_PATH
    
    try:
        # Get the Excel file sheet names
        xlsx = pd.ExcelFile(path)
        sheet_names = xlsx.sheet_names

        # Load each sheet into a dictionary of dataframes
        dataframes = {}
        for sheet in sheet_names:
            dataframes[sheet] = pd.read_excel(path, sheet_name=sheet)

        return dataframes
    except FileNotFoundError:
        print(f"Error: File not found at {path}")
        raise
    except Exception as e:
        print(f"Error loading data: {e}")
        raise

def list_questions() -> pd.DataFrame:
    """
    List all questions in the survey with their IDs and text.
    
    Returns:
        DataFrame containing question identifiers and their text
    """
    try:
        data = load_data()
        schema = data['schema']
        
        # Return the column and question_text columns from the schema
        questions = schema[['column', 'question_text', 'type']].copy()
        questions.columns = ['question_id', 'question_text', 'type']
        
        return questions
    except Exception as e:
        print(f"Error listing questions: {e}")
        raise

def search_questions(query: str) -> pd.DataFrame:
    """
    Search for questions containing the specified query string.
    
    Args:
        query: Search string to look for in question text
        
    Returns:
        DataFrame with matching questions
    """
    if not query or not isinstance(query, str):
        raise ValueError("Query must be a non-empty string")
    
    try:
        questions = list_questions()
        
        # Case-insensitive search in question text
        matches = questions[
            questions['question_text'].str.lower().str.contains(query.lower()) |
            questions['question_id'].str.lower().str.contains(query.lower())
        ]
        
        return matches
    except Exception as e:
        print(f"Error searching questions: {e}")
        raise

def search_options(question_id: str, query: str = None) -> Dict[str, List[str]]:
    """
    Get options for a specific question, optionally filtered by a search term.
    
    Args:
        question_id: Question identifier
        query: Optional search string to filter options
        
    Returns:
        Dictionary with question_id and a list of available options
    """
    if not question_id or not isinstance(question_id, str):
        raise ValueError("Question ID must be a non-empty string")
    
    try:
        data = load_data()
        raw_data = data['raw data']
        
        # Check if the question exists
        if question_id not in raw_data.columns:
            raise ValueError(f"Question ID '{question_id}' not found in the dataset")
        
        # Get all unique options for this question
        options = raw_data[question_id].dropna().unique().tolist()
        
        # For multiple-choice questions, split by semicolon and get unique values
        if ';' in str(options):
            all_options = []
            for opt in options:
                if isinstance(opt, str) and ';' in opt:
                    all_options.extend(opt.split(';'))
                else:
                    all_options.append(opt)
            options = list(set(all_options))
        
        # If a query is provided, filter the options
        if query:
            options = [opt for opt in options if query.lower() in str(opt).lower()]
        
        return {
            "question_id": question_id,
            "options": options
        }
    except Exception as e:
        print(f"Error searching options: {e}")
        raise