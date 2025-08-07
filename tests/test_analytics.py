"""
Test Suite for Analytics Module

Comprehensive testing for the advanced data analytics pipeline.
Demonstrates professional testing practices and quality assurance.

Author: Osman Abdullahi
"""

import unittest
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipe.analytics.statistical_analysis import StatisticalAnalyzer
from pipe.analytics.business_intelligence import BusinessIntelligence
from pipe.ml.customer_segmentation import CustomerSegmentation


class TestStatisticalAnalysis(unittest.TestCase):
    """Test cases for Statistical Analysis module."""
    
    def setUp(self):
        """Set up test data."""
        np.random.seed(42)
        self.test_data = pd.DataFrame({
            'revenue': np.random.lognormal(5, 1, 100),
            'quantity': np.random.poisson(2, 100) + 1,
            'customer_age': np.random.normal(40, 15, 100),
            'customer_segment': np.random.choice(['Premium', 'Standard', 'Basic'], 100)
        })
        self.analyzer = StatisticalAnalyzer(self.test_data)
    
    def test_descriptive_statistics(self):
        """Test descriptive statistics calculation."""
        stats = self.analyzer.descriptive_statistics(['revenue', 'quantity'])
        
        # Check that all required statistics are present
        self.assertIn('revenue', stats)
        self.assertIn('quantity', stats)
        
        # Check required metrics
        required_metrics = ['mean', 'median', 'std', 'min', 'max', 'skewness', 'kurtosis']
        for metric in required_metrics:
            self.assertIn(metric, stats['revenue'])
            self.assertIsInstance(stats['revenue'][metric], (int, float))
    
    def test_correlation_analysis(self):
        """Test correlation analysis."""
        corr_matrix = self.analyzer.correlation_analysis(method='pearson')
        
        # Check matrix properties
        self.assertIsInstance(corr_matrix, pd.DataFrame)
        self.assertEqual(corr_matrix.shape[0], corr_matrix.shape[1])  # Square matrix
        
        # Check diagonal is 1 (correlation with self)
        np.testing.assert_array_almost_equal(np.diag(corr_matrix), 1.0, decimal=10)
    
    def test_hypothesis_testing(self):
        """Test hypothesis testing functionality."""
        result = self.analyzer.hypothesis_testing(
            group_col='customer_segment',
            value_col='revenue',
            test_type='anova'
        )
        
        # Check result structure
        required_keys = ['test_name', 'statistic', 'p_value', 'significant']
        for key in required_keys:
            self.assertIn(key, result)
        
        # Check data types
        self.assertIsInstance(result['statistic'], (int, float))
        self.assertIsInstance(result['p_value'], (int, float))
        self.assertIsInstance(result['significant'], bool)
    
    def test_generate_report(self):
        """Test report generation."""
        # Run some analysis first
        self.analyzer.descriptive_statistics(['revenue'])
        self.analyzer.hypothesis_testing('customer_segment', 'revenue', 'anova')
        
        report = self.analyzer.generate_report()
        
        self.assertIsInstance(report, str)
        self.assertIn('Statistical Analysis Report', report)
        self.assertIn('Dataset Shape', report)


class TestBusinessIntelligence(unittest.TestCase):
    """Test cases for Business Intelligence module."""
    
    def setUp(self):
        """Set up test data."""
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', '2023-12-31', freq='D')
        
        self.test_data = pd.DataFrame({
            'date': np.random.choice(dates, 200),
            'customer_id': [f'CUST_{i%50:03d}' for i in range(200)],
            'revenue': np.random.lognormal(4, 1, 200)
        })
        
        self.bi_analyzer = BusinessIntelligence(self.test_data, date_col='date')
    
    def test_revenue_analytics(self):
        """Test revenue analytics calculation."""
        analytics = self.bi_analyzer.revenue_analytics(revenue_col='revenue', period='monthly')
        
        # Check required keys
        required_keys = ['total_revenue', 'avg_transaction_value', 'total_transactions', 'period_analysis']
        for key in required_keys:
            self.assertIn(key, analytics)
        
        # Check data types and values
        self.assertIsInstance(analytics['total_revenue'], (int, float))
        self.assertGreater(analytics['total_revenue'], 0)
        self.assertIsInstance(analytics['period_analysis'], pd.DataFrame)
    
    def test_customer_analytics(self):
        """Test customer analytics calculation."""
        analytics = self.bi_analyzer.customer_analytics(
            customer_col='customer_id',
            revenue_col='revenue'
        )
        
        # Check required keys
        required_keys = ['total_customers', 'avg_customer_lifetime_value', 'customer_retention_rate']
        for key in required_keys:
            self.assertIn(key, analytics)
        
        # Check logical constraints
        self.assertGreater(analytics['total_customers'], 0)
        self.assertGreaterEqual(analytics['customer_retention_rate'], 0)
        self.assertLessEqual(analytics['customer_retention_rate'], 1)
    
    def test_performance_indicators(self):
        """Test KPI calculation."""
        # Run prerequisite analyses
        self.bi_analyzer.revenue_analytics(revenue_col='revenue')
        self.bi_analyzer.customer_analytics(customer_col='customer_id', revenue_col='revenue')
        
        kpis = self.bi_analyzer.performance_indicators()
        
        self.assertIsInstance(kpis, dict)
        self.assertIn('revenue_kpis', kpis)
        self.assertIn('customer_kpis', kpis)
    
    def test_executive_summary(self):
        """Test executive summary generation."""
        # Run prerequisite analyses
        self.bi_analyzer.revenue_analytics(revenue_col='revenue')
        self.bi_analyzer.customer_analytics(customer_col='customer_id', revenue_col='revenue')
        self.bi_analyzer.performance_indicators()
        
        summary = self.bi_analyzer.generate_executive_summary()
        
        self.assertIsInstance(summary, str)
        self.assertIn('Executive Business Intelligence Summary', summary)
        self.assertIn('Key Performance Indicators', summary)


class TestCustomerSegmentation(unittest.TestCase):
    """Test cases for Customer Segmentation module."""
    
    def setUp(self):
        """Set up test data."""
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', '2023-12-31', freq='D')
        
        self.test_data = pd.DataFrame({
            'customer_id': [f'CUST_{i%30:03d}' for i in range(150)],
            'date': np.random.choice(dates, 150),
            'revenue': np.random.lognormal(4, 1, 150)
        })
        
        self.segmentation = CustomerSegmentation(self.test_data)
    
    def test_calculate_rfm(self):
        """Test RFM calculation."""
        rfm_data = self.segmentation.calculate_rfm(
            customer_col='customer_id',
            date_col='date',
            revenue_col='revenue'
        )
        
        # Check structure
        self.assertIsInstance(rfm_data, pd.DataFrame)
        required_columns = ['customer_id', 'recency', 'frequency', 'monetary', 'rfm_score']
        for col in required_columns:
            self.assertIn(col, rfm_data.columns)
        
        # Check data quality
        self.assertGreater(len(rfm_data), 0)
        self.assertTrue(all(rfm_data['frequency'] > 0))
        self.assertTrue(all(rfm_data['monetary'] > 0))
    
    def test_create_customer_segments(self):
        """Test customer segmentation."""
        # First calculate RFM
        self.segmentation.calculate_rfm(
            customer_col='customer_id',
            date_col='date',
            revenue_col='revenue'
        )
        
        # Create segments
        segments = self.segmentation.create_customer_segments(method='rfm_rules')
        
        self.assertIsInstance(segments, pd.DataFrame)
        self.assertIn('segment', segments.columns)
        self.assertGreater(segments['segment'].nunique(), 1)
    
    def test_analyze_segments(self):
        """Test segment analysis."""
        # Setup segmentation
        self.segmentation.calculate_rfm(
            customer_col='customer_id',
            date_col='date',
            revenue_col='revenue'
        )
        self.segmentation.create_customer_segments(method='rfm_rules')
        
        analysis = self.segmentation.analyze_segments()
        
        # Check structure
        required_keys = ['segment_summary', 'segment_sizes', 'total_customers', 'total_revenue']
        for key in required_keys:
            self.assertIn(key, analysis)
        
        # Check data quality
        self.assertGreater(analysis['total_customers'], 0)
        self.assertGreater(analysis['total_revenue'], 0)
    
    def test_generate_recommendations(self):
        """Test recommendation generation."""
        # Setup segmentation
        self.segmentation.calculate_rfm(
            customer_col='customer_id',
            date_col='date',
            revenue_col='revenue'
        )
        self.segmentation.create_customer_segments(method='rfm_rules')
        
        recommendations = self.segmentation.generate_recommendations()
        
        self.assertIsInstance(recommendations, dict)
        
        # Check recommendation structure
        for segment, rec in recommendations.items():
            self.assertIn('strategy', rec)
            self.assertIn('actions', rec)
            self.assertIn('priority', rec)
            self.assertIsInstance(rec['actions'], list)


class TestDataQuality(unittest.TestCase):
    """Test data quality and validation."""
    
    def test_data_completeness(self):
        """Test data completeness checks."""
        # Create data with missing values
        data = pd.DataFrame({
            'col1': [1, 2, None, 4, 5],
            'col2': [1, None, 3, 4, None],
            'col3': [1, 2, 3, 4, 5]
        })
        
        completeness = (1 - data.isnull().sum().sum() / (data.shape[0] * data.shape[1])) * 100
        
        self.assertIsInstance(completeness, (int, float))
        self.assertGreaterEqual(completeness, 0)
        self.assertLessEqual(completeness, 100)
    
    def test_data_types(self):
        """Test data type validation."""
        data = pd.DataFrame({
            'numeric_col': [1, 2, 3, 4, 5],
            'string_col': ['a', 'b', 'c', 'd', 'e'],
            'date_col': pd.date_range('2023-01-01', periods=5)
        })
        
        # Check numeric column
        self.assertTrue(pd.api.types.is_numeric_dtype(data['numeric_col']))
        
        # Check string column
        self.assertTrue(pd.api.types.is_object_dtype(data['string_col']))
        
        # Check date column
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(data['date_col']))


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestStatisticalAnalysis))
    test_suite.addTest(unittest.makeSuite(TestBusinessIntelligence))
    test_suite.addTest(unittest.makeSuite(TestCustomerSegmentation))
    test_suite.addTest(unittest.makeSuite(TestDataQuality))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}")
