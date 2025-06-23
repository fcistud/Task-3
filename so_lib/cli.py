"""
Command-line interface for the Stack Overflow Survey Data Analysis Library.

This module provides a CLI for interacting with the library functions.
"""

import argparse
import sys
import json
from typing import Dict, List, Optional

from .core import load_data, list_questions, search_questions, search_options
from .analysis import subset_respondents, distribution_sc, distribution_mc

def format_questions(questions):
    """Format question data for CLI output"""
    lines = []
    for _, row in questions.iterrows():
        lines.append(f"{row['question_id']} ({row['type']}): {row['question_text']}")
    
    return "\n".join(lines)

def format_options(options_data):
    """Format options data for CLI output"""
    lines = [f"Options for question: {options_data['question_id']}"]
    for option in options_data['options']:
        lines.append(f"- {option}")
    
    return "\n".join(lines)

def format_distribution(dist_data):
    """Format distribution data for CLI output"""
    lines = [
        f"Distribution for: {dist_data['question_id']}",
        f"Question: {dist_data['question_text']}",
        "\nOptions:"
    ]
    
    # Sort by percentage (descending)
    sorted_dist = sorted(
        dist_data['distribution'].items(), 
        key=lambda x: x[1], 
        reverse=True
    )
    
    for option, percentage in sorted_dist:
        lines.append(f"- {option}: {percentage:.2f}%")
    
    return "\n".join(lines)

def parse_args(args=None):
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="Stack Overflow Survey Data Analysis Tool",
        prog="python -m so_lib"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # list-questions command
    list_parser = subparsers.add_parser(
        'list-questions', 
        help='List all survey questions'
    )
    list_parser.add_argument(
        '--data-path', 
        help='Path to the Stack Overflow survey data file'
    )
    
    # search-questions command
    search_q_parser = subparsers.add_parser(
        'search-questions', 
        help='Search for questions by text'
    )
    search_q_parser.add_argument('query', help='Search term')
    search_q_parser.add_argument(
        '--data-path', 
        help='Path to the Stack Overflow survey data file'
    )
    
    # search-options command
    search_o_parser = subparsers.add_parser(
        'search-options', 
        help='List options for a specific question'
    )
    search_o_parser.add_argument('question_id', help='Question identifier')
    search_o_parser.add_argument('--query', help='Filter options by search term')
    search_o_parser.add_argument(
        '--data-path', 
        help='Path to the Stack Overflow survey data file'
    )
    
    # subset command
    subset_parser = subparsers.add_parser(
        'subset', 
        help='Create a subset of respondents based on an answer'
    )
    subset_parser.add_argument('question_id', help='Question identifier')
    subset_parser.add_argument('option', help='Selected option')
    subset_parser.add_argument(
        '--output', 
        help='Output file for the subset data (CSV format)'
    )
    subset_parser.add_argument(
        '--data-path', 
        help='Path to the Stack Overflow survey data file'
    )
    
    # distribution-sc command
    dist_sc_parser = subparsers.add_parser(
        'distribution-sc', 
        help='Calculate distribution for a single-choice question'
    )
    dist_sc_parser.add_argument('question_id', help='Question identifier')
    dist_sc_parser.add_argument(
        '--data-path', 
        help='Path to the Stack Overflow survey data file'
    )
    
    # distribution-mc command
    dist_mc_parser = subparsers.add_parser(
        'distribution-mc', 
        help='Calculate distribution for a multiple-choice question'
    )
    dist_mc_parser.add_argument('question_id', help='Question identifier')
    dist_mc_parser.add_argument(
        '--data-path', 
        help='Path to the Stack Overflow survey data file'
    )
    
    return parser.parse_args(args)

def main(args=None):
    """Main CLI entry point"""
    args = parse_args(args)
    
    if not args.command:
        print("Error: Please specify a command.")
        print("Run 'python -m so_lib --help' for usage information.")
        sys.exit(1)
    
    try:
        # Execute the appropriate command
        if args.command == 'list-questions':
            data_path = args.data_path if hasattr(args, 'data_path') else None
            # Force loading the data with the provided path before calling other functions
            if data_path:
                load_data(data_path)
            questions = list_questions()
            print(format_questions(questions))
            
        elif args.command == 'search-questions':
            data_path = args.data_path if hasattr(args, 'data_path') else None
            if data_path:
                load_data(data_path)
            questions = search_questions(args.query)
            if questions.empty:
                print(f"No questions found matching: {args.query}")
            else:
                print(format_questions(questions))
            
        elif args.command == 'search-options':
            data_path = args.data_path if hasattr(args, 'data_path') else None
            if data_path:
                load_data(data_path)
            options = search_options(args.question_id, args.query)
            print(format_options(options))
            
        elif args.command == 'subset':
            data_path = args.data_path if hasattr(args, 'data_path') else None
            if data_path:
                load_data(data_path)
            subset = subset_respondents(args.question_id, args.option)
            print(f"Created subset with {len(subset)} respondents.")
            
            if args.output:
                subset.to_csv(args.output, index=False)
                print(f"Subset saved to {args.output}")
            
        elif args.command == 'distribution-sc':
            data_path = args.data_path if hasattr(args, 'data_path') else None
            if data_path:
                load_data(data_path)
            dist = distribution_sc(args.question_id)
            print(format_distribution(dist))
            
        elif args.command == 'distribution-mc':
            data_path = args.data_path if hasattr(args, 'data_path') else None
            if data_path:
                load_data(data_path)
            dist = distribution_mc(args.question_id)
            print(format_distribution(dist))
            
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()