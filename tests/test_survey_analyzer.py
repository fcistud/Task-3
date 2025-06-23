import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import os
from src.survey_analyzer import SurveyAnalyzer


@pytest.fixture
def sample_data():
    data = {
        'ResponseId': [1, 2, 3, 4, 5],
        'Country': ['USA', 'UK', 'Canada', 'USA', 'UK'],
        'Languages': ['Python;JavaScript', 'Python', 'JavaScript;Java', 'Python;Java', 'JavaScript'],
        'YearsCode': [5, 3, 7, 2, 4],
        'EmptyColumn': [np.nan, np.nan, np.nan, np.nan, np.nan]
    }
    return pd.DataFrame(data)


@pytest.fixture
def temp_excel_file(sample_data):
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.xlsx', delete=False) as f:
        sample_data.to_excel(f.name, index=False)
        temp_path = f.name
    
    yield temp_path
    
    os.unlink(temp_path)


@pytest.fixture
def analyzer(temp_excel_file):
    return SurveyAnalyzer(temp_excel_file)


class TestSurveyAnalyzer:
    
    def test_initialization(self, analyzer):
        assert analyzer.df is not None
        assert len(analyzer.df) == 5
        assert len(analyzer.questions) == 4  # Excluding ResponseId only
    
    def test_load_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            SurveyAnalyzer('/nonexistent/path.xlsx')
    
    def test_question_type_detection(self, analyzer):
        assert analyzer.question_types['Country'] == 'SC'
        assert analyzer.question_types['Languages'] == 'MC'
        assert analyzer.question_types['YearsCode'] == 'SC'
        assert analyzer.question_types['EmptyColumn'] == 'empty'
    
    def test_get_survey_structure(self, analyzer):
        structure = analyzer.get_survey_structure()
        
        assert 'Country' in structure
        assert structure['Country']['type'] == 'SC'
        assert structure['Country']['unique_values'] == 3
        assert structure['Country']['response_count'] == 5
        
        assert 'Languages' in structure
        assert structure['Languages']['type'] == 'MC'
        assert structure['Languages']['response_count'] == 5
    
    def test_search_questions(self, analyzer):
        results = analyzer.search_questions('year')
        assert 'YearsCode' in results
        assert len(results) == 1
        
        results = analyzer.search_questions('Country')
        assert 'Country' in results
        
        results = analyzer.search_questions('nonexistent')
        assert len(results) == 0
    
    def test_search_options_single_choice(self, analyzer):
        options = analyzer.search_options('Country', 'U')
        assert 'USA' in options
        assert 'UK' in options
        assert len(options) == 2
    
    def test_search_options_multiple_choice(self, analyzer):
        options = analyzer.search_options('Languages', 'Java')
        assert 'Java' in options
        assert 'JavaScript' in options
        assert len(options) == 2
    
    def test_search_options_invalid_question(self, analyzer):
        with pytest.raises(ValueError):
            analyzer.search_options('InvalidQuestion', 'test')
    
    def test_create_subset_single_choice(self, analyzer):
        subset = analyzer.create_subset('Country', 'USA')
        assert len(subset) == 2
        assert all(subset['Country'] == 'USA')
    
    def test_create_subset_multiple_choice(self, analyzer):
        subset = analyzer.create_subset('Languages', 'Python')
        assert len(subset) == 3
        assert all(subset['Languages'].str.contains('Python'))
    
    def test_create_subset_invalid_question(self, analyzer):
        with pytest.raises(ValueError):
            analyzer.create_subset('InvalidQuestion', 'test')
    
    def test_get_distribution_single_choice(self, analyzer):
        dist = analyzer.get_distribution('Country')
        
        assert 'USA' in dist
        assert 'UK' in dist
        assert 'Canada' in dist
        
        assert dist['USA'] == 40.0  # 2/5
        assert dist['UK'] == 40.0   # 2/5
        assert dist['Canada'] == 20.0  # 1/5
    
    def test_get_distribution_multiple_choice(self, analyzer):
        dist = analyzer.get_distribution('Languages')
        
        assert 'Python' in dist
        assert 'JavaScript' in dist
        assert 'Java' in dist
        
        assert dist['Python'] == 60.0  # 3/5
        assert dist['JavaScript'] == 60.0  # 3/5
        assert dist['Java'] == 40.0  # 2/5
    
    def test_get_distribution_with_subset(self, analyzer):
        subset = analyzer.create_subset('Country', 'USA')
        dist = analyzer.get_distribution('Languages', subset)
        
        assert 'Python' in dist
        assert dist['Python'] == 100.0  # Both USA respondents use Python
    
    def test_get_distribution_empty_column(self, analyzer):
        dist = analyzer.get_distribution('EmptyColumn')
        assert len(dist) == 0
    
    def test_display_distribution(self, analyzer):
        df_dist = analyzer.display_distribution('Country')
        
        assert len(df_dist) == 3
        assert 'Option' in df_dist.columns
        assert 'Percentage' in df_dist.columns
        assert df_dist.iloc[0]['Percentage'] == 40.0
    
    def test_display_distribution_with_limit(self, analyzer):
        df_dist = analyzer.display_distribution('Country', top_n=2)
        
        assert len(df_dist) == 3  # 2 top + 1 "Others"
        assert df_dist.iloc[-1]['Option'] == 'Others'
        assert df_dist.iloc[-1]['Percentage'] == 20.0