"""
Stack Overflow Survey Data Analysis Library

This library provides tools for analyzing the Stack Overflow Developer Survey data.
"""

__version__ = '0.1.0'

from .core import (
    load_data,
    list_questions,
    search_questions,
    search_options
)

from .analysis import (
    subset_respondents,
    distribution_sc,
    distribution_mc
)