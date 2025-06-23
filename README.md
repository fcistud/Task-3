# Stack Overflow Survey Data Analysis Library

A Python library for analyzing Stack Overflow Developer Survey data with command-line interface (CLI) support.

## Features

- Load and explore Stack Overflow survey data from Excel files
- List and search survey questions
- Get details about question options
- Create respondent subsets based on answers
- Calculate distribution of answers for single-choice (SC) and multiple-choice (MC) questions
- Command-line interface for all features

## Prerequisites

- Python 3.6 or higher
- Dependencies: pandas, openpyxl (see requirements.txt)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/so-survey-analysis.git
   cd so-survey-analysis
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### REPL (Python Interactive Mode)

```python
from so_lib import load_data, list_questions, search_questions, subset_respondents, distribution_sc

# Load the data
data = load_data('path/to/so_2024_raw.xlsx')

# List all questions
questions = list_questions()
print(questions)

# Search for questions about coding
coding_questions = search_questions('coding')
print(coding_questions)

# Get distribution for a single-choice question
main_branch_dist = distribution_sc('MainBranch')
print(main_branch_dist)

# Create a subset of professional developers
pro_devs = subset_respondents('MainBranch', 'I am a developer by profession')
```

### Command-Line Interface (CLI)

The library provides a CLI for easy access to all functionality:

```bash
# List all survey questions
python -m so_lib list-questions

# Search for questions containing a specific term
python -m so_lib search-questions "coding"

# List options for a specific question
python -m so_lib search-options MainBranch

# Get distribution for a single-choice question
python -m so_lib distribution-sc MainBranch

# Get distribution for a multiple-choice question
python -m so_lib distribution-mc LearnCode

# Create a subset of respondents based on an answer
python -m so_lib subset MainBranch "I am a developer by profession" --output devs.csv

# Specify a custom data file path
python -m so_lib list-questions --data-path /path/to/custom/so_data.xlsx
```

Use the `--help` flag to see all available commands and options:

```bash
python -m so_lib --help
```

## Running Tests

Run the test suite using pytest:

```bash
# Run all tests
pytest

# Run tests with detailed output
pytest -v

# Run specific test file
pytest tests/test_core.py
```

## Project Structure

- `so_lib/` - Main package
  - `core.py` - Core functionality (loading data, listing questions)
  - `analysis.py` - Analysis functionality (subsetting, distributions)
  - `cli.py` - Command-line interface
- `tests/` - Unit tests
- `README.md` - Documentation
- `requirements.txt` - Dependencies