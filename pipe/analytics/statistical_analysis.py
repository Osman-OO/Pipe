"""
Statistical Analysis Module

Comprehensive statistical analysis capabilities including descriptive statistics,
hypothesis testing, correlation analysis, and regression modeling.

Author: Osman Abdullahi
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import pearsonr, spearmanr, kendalltau
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional, Union
import warnings

warnings.filterwarnings('ignore')


class StatisticalAnalyzer:
    """
    Professional statistical analysis toolkit for data analytics projects.
    
    Provides comprehensive statistical analysis capabilities including:
    - Descriptive statistics
    - Hypothesis testing
    - Correlation analysis
    - Regression modeling
    - Distribution analysis
    """
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize the Statistical Analyzer.
        
        Args:
            data (pd.DataFrame): Input dataset for analysis
        """
        self.data = data.copy()
        self.results = {}
        
    def descriptive_statistics(self, columns: Optional[List[str]] = None) -> Dict:
        """
        Generate comprehensive descriptive statistics.
        
        Args:
            columns: List of columns to analyze. If None, analyzes all numeric columns.
            
        Returns:
            Dict: Comprehensive descriptive statistics
        """
        if columns is None:
            columns = self.data.select_dtypes(include=[np.number]).columns.tolist()
            
        stats_dict = {}
        
        for col in columns:
            if col in self.data.columns:
                series = self.data[col].dropna()
                
                stats_dict[col] = {
                    'count': len(series),
                    'mean': series.mean(),
                    'median': series.median(),
                    'mode': series.mode().iloc[0] if not series.mode().empty else np.nan,
                    'std': series.std(),
                    'variance': series.var(),
                    'min': series.min(),
                    'max': series.max(),
                    'range': series.max() - series.min(),
                    'q1': series.quantile(0.25),
                    'q3': series.quantile(0.75),
                    'iqr': series.quantile(0.75) - series.quantile(0.25),
                    'skewness': stats.skew(series),
                    'kurtosis': stats.kurtosis(series),
                    'cv': series.std() / series.mean() if series.mean() != 0 else np.nan
                }
                
        self.results['descriptive_stats'] = stats_dict
        return stats_dict
    
    def correlation_analysis(self, method: str = 'pearson') -> pd.DataFrame:
        """
        Perform correlation analysis between numeric variables.
        
        Args:
            method: Correlation method ('pearson', 'spearman', 'kendall')
            
        Returns:
            pd.DataFrame: Correlation matrix
        """
        numeric_data = self.data.select_dtypes(include=[np.number])
        
        if method == 'pearson':
            corr_matrix = numeric_data.corr(method='pearson')
        elif method == 'spearman':
            corr_matrix = numeric_data.corr(method='spearman')
        elif method == 'kendall':
            corr_matrix = numeric_data.corr(method='kendall')
        else:
            raise ValueError("Method must be 'pearson', 'spearman', or 'kendall'")
            
        self.results[f'{method}_correlation'] = corr_matrix
        return corr_matrix
    
    def hypothesis_testing(self, 
                          group_col: str, 
                          value_col: str, 
                          test_type: str = 'ttest') -> Dict:
        """
        Perform hypothesis testing between groups.
        
        Args:
            group_col: Column containing group labels
            value_col: Column containing values to test
            test_type: Type of test ('ttest', 'mannwhitney', 'anova', 'kruskal')
            
        Returns:
            Dict: Test results including statistic and p-value
        """
        groups = [group[value_col].dropna() for name, group in self.data.groupby(group_col)]
        
        if test_type == 'ttest' and len(groups) == 2:
            statistic, p_value = stats.ttest_ind(groups[0], groups[1])
            test_name = "Independent t-test"
            
        elif test_type == 'mannwhitney' and len(groups) == 2:
            statistic, p_value = stats.mannwhitneyu(groups[0], groups[1])
            test_name = "Mann-Whitney U test"
            
        elif test_type == 'anova':
            statistic, p_value = stats.f_oneway(*groups)
            test_name = "One-way ANOVA"
            
        elif test_type == 'kruskal':
            statistic, p_value = stats.kruskal(*groups)
            test_name = "Kruskal-Wallis test"
            
        else:
            raise ValueError("Invalid test type or number of groups")
            
        result = {
            'test_name': test_name,
            'statistic': statistic,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'groups': len(groups),
            'group_sizes': [len(group) for group in groups]
        }
        
        self.results['hypothesis_test'] = result
        return result
    
    def regression_analysis(self, 
                           target: str, 
                           features: List[str], 
                           model_type: str = 'linear') -> Dict:
        """
        Perform regression analysis.
        
        Args:
            target: Target variable column name
            features: List of feature column names
            model_type: Type of regression ('linear', 'polynomial')
            
        Returns:
            Dict: Regression results
        """
        from sklearn.linear_model import LinearRegression
        from sklearn.preprocessing import PolynomialFeatures
        from sklearn.metrics import r2_score, mean_squared_error
        
        # Prepare data
        X = self.data[features].dropna()
        y = self.data.loc[X.index, target]
        
        if model_type == 'linear':
            model = LinearRegression()
            X_processed = X
        elif model_type == 'polynomial':
            poly_features = PolynomialFeatures(degree=2)
            X_processed = poly_features.fit_transform(X)
            model = LinearRegression()
        else:
            raise ValueError("Model type must be 'linear' or 'polynomial'")
            
        # Fit model
        model.fit(X_processed, y)
        y_pred = model.predict(X_processed)
        
        # Calculate metrics
        r2 = r2_score(y, y_pred)
        mse = mean_squared_error(y, y_pred)
        rmse = np.sqrt(mse)
        
        result = {
            'model_type': model_type,
            'r2_score': r2,
            'mse': mse,
            'rmse': rmse,
            'coefficients': model.coef_.tolist() if hasattr(model, 'coef_') else None,
            'intercept': model.intercept_ if hasattr(model, 'intercept_') else None,
            'features': features,
            'n_samples': len(X)
        }
        
        self.results['regression'] = result
        return result
    
    def generate_report(self) -> str:
        """
        Generate a comprehensive statistical analysis report.
        
        Returns:
            str: Formatted analysis report
        """
        report = "# Statistical Analysis Report\n\n"
        report += f"**Dataset Shape**: {self.data.shape}\n"
        report += f"**Analysis Date**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        if 'descriptive_stats' in self.results:
            report += "## Descriptive Statistics\n\n"
            for col, stats in self.results['descriptive_stats'].items():
                report += f"### {col}\n"
                report += f"- Mean: {stats['mean']:.4f}\n"
                report += f"- Median: {stats['median']:.4f}\n"
                report += f"- Standard Deviation: {stats['std']:.4f}\n"
                report += f"- Skewness: {stats['skewness']:.4f}\n\n"
                
        if 'hypothesis_test' in self.results:
            test = self.results['hypothesis_test']
            report += "## Hypothesis Testing\n\n"
            report += f"- Test: {test['test_name']}\n"
            report += f"- Statistic: {test['statistic']:.4f}\n"
            report += f"- P-value: {test['p_value']:.4f}\n"
            report += f"- Significant: {test['significant']}\n\n"
            
        return report
