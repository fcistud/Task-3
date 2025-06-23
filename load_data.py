#!/usr/bin/env python3
"""
Stack Overflow 2024 Data Loader

This script loads the Stack Overflow 2024 raw data from an Excel file
and provides functionality to display basic information about the dataset.
"""

import argparse
import sys
try:
    import pandas as pd
except ImportError:
    print("Error: pandas is required. Install it using 'pip install pandas openpyxl'")
    sys.exit(1)

# Path to the Stack Overflow 2024 raw data file
DATA_FILE_PATH = "/Users/mariamhassan/Downloads/Task 3/so_2024_raw.xlsx"


def load_stackoverflow_data(file_path=DATA_FILE_PATH):
    """
    Load the Stack Overflow 2024 data from Excel file.

    Args:
        file_path (str): Path to the Excel file

    Returns:
        dict: Dictionary of DataFrames, one per sheet in the Excel file
    """
    try:
        # Get the Excel file sheet names
        xlsx = pd.ExcelFile(file_path)
        sheet_names = xlsx.sheet_names

        # Load each sheet into a dictionary of dataframes
        dataframes = {}
        for sheet in sheet_names:
            dataframes[sheet] = pd.read_excel(file_path, sheet_name=sheet)

        return dataframes
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        print("Please ensure the file path is correct in the script.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)


def display_info(dataframes):
    """
    Display information about the loaded dataframes.

    Args:
        dataframes (dict): Dictionary of DataFrames
    """
    print("\nStack Overflow 2024 Dataset Information:")
    print("=" * 50)

    if not dataframes:
        print("No data loaded.")
        return

    print(f"Number of sheets: {len(dataframes)}")
    print("\nSheet details:")

    for sheet_name, df in dataframes.items():
        print(f"\n- Sheet: {sheet_name}")
        print(f"  Dimensions: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"  Column names: {', '.join(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}")
        print(f"  Memory usage: {df.memory_usage(deep=True).sum() / (1024**2):.2f} MB")


def main():
    """Main function to parse arguments and execute the script."""
    parser = argparse.ArgumentParser(description="Load and analyze Stack Overflow 2024 data")
    parser.add_argument("--info", action="store_true", help="Display information about the dataset")
    parser.add_argument("--path", type=str, default=DATA_FILE_PATH,
                        help="Path to the Excel file (default is the path in documentation)")
    args = parser.parse_args()

    print(f"Loading Stack Overflow 2024 data from: {args.path}")
    dataframes = load_stackoverflow_data(args.path)

    # Always show basic success message
    sheet_count = len(dataframes)
    total_rows = sum(df.shape[0] for df in dataframes.values())
    print(f"Successfully loaded {sheet_count} sheets with a total of {total_rows} rows")

    # Show detailed info if requested
    if args.info:
        display_info(dataframes)

    return dataframes


if __name__ == "__main__":
    main()
