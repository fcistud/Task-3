"""
Analysis functionality for the Stack Overflow Survey Data Analysis Library.

This module provides functions for analyzing the survey data.
"""

from typing import Dict, List, Union
import pandas as pd
from .core import load_data, list_questions

def subset_respondents(question_id: str, option: str) -> pd.DataFrame:
    """
    Create a subset of respondents based on their answer to a specific question.

    Args:
        question_id: Question identifier
        option: Selected option value

    Returns:
        DataFrame containing only respondents who selected the specified option

    Raises:
        ValueError: If question_id or option is invalid
    """
    if not question_id or not isinstance(question_id, str):
        raise ValueError("Question ID must be a non-empty string")

    if not option or not isinstance(option, str):
        raise ValueError("Option must be a non-empty string")

    try:
        data = load_data()
        raw_data = data['raw data']
        schema = data['schema']

        # Check if the question exists
        if question_id not in raw_data.columns:
            raise ValueError(f"Question ID '{question_id}' not found in the dataset")

        # Get the question type (SC - single choice, MC - multiple choice)
        question_type = schema.loc[schema['column'] == question_id, 'type'].iloc[0]

        if question_type == 'SC':
            # For single-choice questions, do an exact match
            subset = raw_data[raw_data[question_id] == option]
        else:
            # For multiple-choice questions, check if the option is in the string
            subset = raw_data[raw_data[question_id].str.contains(option, na=False)]

        return subset
    except Exception as e:
        print(f"Error creating subset: {e}")
        raise

def distribution_sc(question_id: str) -> Dict[str, Union[str, Dict[str, float]]]:
    """
    Calculate the distribution of answers for a single-choice question.

    Args:
        question_id: Question identifier

    Returns:
        Dictionary with question information and distribution of answers

    Raises:
        ValueError: If question_id is invalid or not a single-choice question
    """
    if not question_id or not isinstance(question_id, str):
        raise ValueError("Question ID must be a non-empty string")

    try:
        data = load_data()
        raw_data = data['raw data']
        schema = data['schema']

        # Check if the question exists
        if question_id not in raw_data.columns:
            raise ValueError(f"Question ID '{question_id}' not found in the dataset")

        # Get the question type and verify it's a single-choice question
        question_type = schema.loc[schema['column'] == question_id, 'type'].iloc[0]

        if question_type != 'SC':
            raise ValueError(f"Question '{question_id}' is not a single-choice question")

        # Calculate the distribution
        total_responses = len(raw_data[~raw_data[question_id].isna()])
        value_counts = raw_data[question_id].value_counts()

        distribution = {
            option: count / total_responses * 100
            for option, count in value_counts.items()
        }

        # Get the question text
        question_text = schema.loc[schema['column'] == question_id, 'question_text'].iloc[0]

        return {
            "question_id": question_id,
            "question_text": question_text,
            "distribution": distribution
        }
    except Exception as e:
        print(f"Error calculating distribution: {e}")
        raise

def distribution_mc(question_id: str) -> Dict[str, Union[str, Dict[str, float]]]:
    """
    Calculate the distribution of answers for a multiple-choice question.

    Args:
        question_id: Question identifier

    Returns:
        Dictionary with question information and distribution of answers

    Raises:
        ValueError: If question_id is invalid or not a multiple-choice question
    """
    if not question_id or not isinstance(question_id, str):
        raise ValueError("Question ID must be a non-empty string")

    try:
        data = load_data()
        raw_data = data['raw data']
        schema = data['schema']

        # Check if the question exists
        if question_id not in raw_data.columns:
            raise ValueError(f"Question ID '{question_id}' not found in the dataset")

        # Get the question type and verify it's a multiple-choice question
        question_type = schema.loc[schema['column'] == question_id, 'type'].iloc[0]

        if question_type != 'MC':
            raise ValueError(f"Question '{question_id}' is not a multiple-choice question")

        # For multiple-choice questions, we need to count each option separately
        options_count = {}
        total_respondents = len(raw_data)

        # Filter out NaN values
        non_null_data = raw_data[~raw_data[question_id].isna()]

        # Process each respondent's answer
        for answer in non_null_data[question_id]:
            if isinstance(answer, str):
                options = answer.split(';')
                for option in options:
                    if option in options_count:
                        options_count[option] += 1
                    else:
                        options_count[option] = 1

        # Calculate percentages based on total respondents
        distribution = {
            option: count / total_respondents * 100
            for option, count in options_count.items()
        }

        # Get the question text
        question_text = schema.loc[schema['column'] == question_id, 'question_text'].iloc[0]

        return {
            "question_id": question_id,
            "question_text": question_text,
            "distribution": distribution
        }
    except Exception as e:
        print(f"Error calculating distribution: {e}")
        raise