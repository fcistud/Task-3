# Stack Overflow Survey Data Analyzer

A Python library and CLI tool for analyzing Stack Overflow Developer Survey data. This tool provides functionality to explore survey structure, search questions and options, create respondent subsets, and analyze answer distributions.

## Features

- **Survey Structure Display**: View all survey questions with their types (Single Choice/Multiple Choice)
- **Search Functionality**: Search for specific questions or answer options
- **Subset Creation**: Filter respondents based on specific question-answer combinations
- **Distribution Analysis**: Calculate and display answer distributions for both SC and MC questions
- **CLI Interface**: Command-line interface with both individual commands and interactive REPL mode
- **Unit Tests**: Comprehensive test coverage for core functionality

## Installation

1. Clone or download this repository
2. Navigate to the project directory:
   ```bash
   cd so-survey-analyzer
   ```
3. Install the package and dependencies:
   ```bash
   pip install -e .
   ```

## Setup

1. Ensure you have the Stack Overflow survey data file (`so_2024_raw.xlsx`) in the `data/` directory
2. The file structure should be:
   ```
   so-survey-analyzer/
   ├── data/
   │   └── so_2024_raw.xlsx
   ├── src/
   ├── tests/
   └── README.md
   ```

## Usage

### CLI Commands

After installation, you can use the `so-survey` command:

#### Display Survey Structure
```bash
# Show first 20 questions
so-survey structure

# Show first 50 questions
so-survey structure --limit 50
```

#### Search Questions
```bash
# Search for questions containing "python"
so-survey search python

# Search for questions containing "experience"
so-survey search experience
```

#### Search Answer Options
```bash
# Search for options containing "Java" in the "Languages" question
so-survey search java --in-options --question Languages
```

#### Create Respondent Subsets
```bash
# Create a subset of respondents from USA
so-survey subset Country USA

# Create and save a subset for future analysis
so-survey subset Country USA --save
```

#### Display Answer Distributions
```bash
# Show distribution for a question (top 10 options)
so-survey distribution Languages

# Show top 20 options
so-survey distribution Languages --top 20

# Show distribution using saved subset
so-survey distribution Languages --subset
```

### Interactive REPL Mode

Start the interactive mode:
```bash
so-survey repl
```

Available REPL commands:
- `help` - Show available commands
- `structure [limit]` - Display survey structure
- `search <keyword>` - Search questions
- `search-options <question> <keyword>` - Search options in a question
- `subset <question> <option>` - Create and save subset
- `dist <question> [top_n]` - Show distribution
- `dist-subset <question> [top_n]` - Show distribution for saved subset
- `clear-subset` - Clear saved subset
- `exit` - Exit REPL

Example REPL session:
```
survey> structure 10
survey> search developer
survey> subset Country USA
survey> dist Languages 15
survey> dist-subset YearsCode
survey> exit
```

## Running Tests

Run the unit tests with coverage:
```bash
pytest
```

Run tests with verbose output:
```bash
pytest -v
```

## Library Usage

You can also use the library programmatically:

```python
from src.survey_analyzer import SurveyAnalyzer

# Initialize analyzer
analyzer = SurveyAnalyzer('data/so_2024_raw.xlsx')

# Get survey structure
structure = analyzer.get_survey_structure()

# Search questions
python_questions = analyzer.search_questions('python')

# Create subset
usa_respondents = analyzer.create_subset('Country', 'USA')

# Get distribution
lang_dist = analyzer.get_distribution('Languages')

# Get distribution for subset
usa_lang_dist = analyzer.get_distribution('Languages', usa_respondents)
```

## Question Types

The analyzer automatically detects two types of questions:
- **SC (Single Choice)**: Questions where respondents select one option
- **MC (Multiple Choice)**: Questions where respondents can select multiple options (detected by semicolon-separated values)

## Requirements

- Python 3.8+
- pandas >= 2.0.3
- openpyxl >= 3.1.2
- click >= 8.1.7
- tabulate >= 0.9.0
- pytest >= 7.4.3 (for testing)
- pytest-cov >= 4.1.0 (for test coverage)