from setuptools import setup, find_packages

setup(
    name="so-survey-analyzer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.0.3",
        "openpyxl>=3.1.2",
        "click>=8.1.7",
        "tabulate>=0.9.0",
    ],
    entry_points={
        'console_scripts': [
            'so-survey=src.cli:main',
        ],
    },
    python_requires=">=3.8",
)