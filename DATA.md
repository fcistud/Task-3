# Stack Overflow 2024 Dataset Documentation

## File Location

The Stack Overflow 2024 raw data is stored in an Excel file located at:

```
/Users/mariamhassan/Downloads/Task 3/so_2024_raw.xlsx
```

## Data Overview

This file contains raw data extracted from Stack Overflow for the year 2024. It includes information about questions, answers, users, and other metrics from the Stack Overflow platform.

## Data Structure

The Excel file likely contains multiple sheets with different aspects of Stack Overflow data. The exact structure can be explored using the `load_data.py` script with the `--info` flag.

## Working with the Data

To load and analyze this data:

1. Ensure you have the required dependencies installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the data loading script:
   ```bash
   python load_data.py --info
   ```

3. For custom analysis, you can import the loader function in your own scripts:
   ```python
   from load_data import load_stackoverflow_data
   
   df = load_stackoverflow_data()
   # Perform your analysis here
   ```

## Data Usage Guidelines

When using this data for analysis or research:

- Cite the source as "Stack Overflow 2024 Dataset"
- Be aware of any potential sampling biases in the data
- Consider privacy implications when publishing results based on this data