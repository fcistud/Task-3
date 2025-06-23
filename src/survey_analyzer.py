import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Set
from pathlib import Path
import warnings

warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')


class SurveyAnalyzer:
    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        self.df = None
        self.questions = {}
        self.question_types = {}
        self._load_data()
        self._analyze_structure()
    
    def _load_data(self):
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data file not found: {self.data_path}")
        
        self.df = pd.read_excel(self.data_path, engine='openpyxl')
        print(f"Loaded survey data: {len(self.df)} responses, {len(self.df.columns)} columns")
    
    def _analyze_structure(self):
        for col in self.df.columns:
            if col == 'ResponseId':
                continue
            
            unique_vals = self.df[col].dropna().unique()
            
            if len(unique_vals) == 0:
                self.question_types[col] = 'empty'
            elif ';' in str(self.df[col].dropna().iloc[0] if len(self.df[col].dropna()) > 0 else ''):
                self.question_types[col] = 'MC'
            else:
                self.question_types[col] = 'SC'
            
            self.questions[col] = {
                'type': self.question_types[col],
                'unique_values': len(unique_vals),
                'response_count': self.df[col].notna().sum()
            }
    
    def get_survey_structure(self) -> Dict[str, Dict]:
        return self.questions
    
    def display_survey_structure(self, limit: Optional[int] = None):
        structure = []
        for i, (q, info) in enumerate(self.questions.items()):
            if limit and i >= limit:
                break
            structure.append({
                'Question': q[:80] + '...' if len(q) > 80 else q,
                'Type': info['type'],
                'Unique Values': info['unique_values'],
                'Responses': info['response_count']
            })
        
        return pd.DataFrame(structure)
    
    def search_questions(self, keyword: str) -> List[str]:
        keyword_lower = keyword.lower()
        matching_questions = []
        
        for q in self.questions.keys():
            if keyword_lower in q.lower():
                matching_questions.append(q)
        
        return matching_questions
    
    def search_options(self, question: str, keyword: str) -> List[str]:
        if question not in self.df.columns:
            raise ValueError(f"Question '{question}' not found in survey")
        
        keyword_lower = keyword.lower()
        matching_options = []
        
        if self.question_types.get(question) == 'MC':
            all_options = set()
            for val in self.df[question].dropna():
                options = str(val).split(';')
                all_options.update(opt.strip() for opt in options)
            
            for opt in all_options:
                if keyword_lower in opt.lower():
                    matching_options.append(opt)
        else:
            unique_vals = self.df[question].dropna().unique()
            for val in unique_vals:
                if keyword_lower in str(val).lower():
                    matching_options.append(str(val))
        
        return sorted(matching_options)
    
    def create_subset(self, question: str, option: str) -> pd.DataFrame:
        if question not in self.df.columns:
            raise ValueError(f"Question '{question}' not found in survey")
        
        if self.question_types.get(question) == 'MC':
            mask = self.df[question].notna() & self.df[question].str.contains(option, case=False, na=False)
        else:
            mask = self.df[question] == option
        
        subset = self.df[mask].copy()
        return subset
    
    def get_distribution(self, question: str, subset_df: Optional[pd.DataFrame] = None) -> Dict[str, float]:
        df = subset_df if subset_df is not None else self.df
        
        if question not in df.columns:
            raise ValueError(f"Question '{question}' not found in data")
        
        total_responses = df[question].notna().sum()
        
        if total_responses == 0:
            return {}
        
        if self.question_types.get(question) == 'MC':
            option_counts = {}
            for val in df[question].dropna():
                options = str(val).split(';')
                for opt in options:
                    opt = opt.strip()
                    option_counts[opt] = option_counts.get(opt, 0) + 1
            
            distribution = {opt: (count / total_responses) * 100 
                          for opt, count in option_counts.items()}
        else:
            value_counts = df[question].value_counts()
            distribution = {str(val): (count / total_responses) * 100 
                          for val, count in value_counts.items()}
        
        return dict(sorted(distribution.items(), key=lambda x: x[1], reverse=True))
    
    def display_distribution(self, question: str, subset_df: Optional[pd.DataFrame] = None, 
                           top_n: Optional[int] = 10) -> pd.DataFrame:
        distribution = self.get_distribution(question, subset_df)
        
        if not distribution:
            return pd.DataFrame({'Option': ['No responses'], 'Percentage': [0]})
        
        items = list(distribution.items())[:top_n] if top_n else distribution.items()
        
        df_dist = pd.DataFrame(items, columns=['Option', 'Percentage'])
        df_dist['Percentage'] = df_dist['Percentage'].round(2)
        
        if top_n and len(distribution) > top_n:
            other_pct = sum(v for k, v in list(distribution.items())[top_n:])
            df_dist = pd.concat([df_dist, pd.DataFrame({'Option': ['Others'], 'Percentage': [round(other_pct, 2)]})], 
                               ignore_index=True)
        
        return df_dist