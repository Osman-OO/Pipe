"""
Business Intelligence Module

Advanced business analytics and KPI calculation for executive reporting
and strategic decision making.

Author: Osman Abdullahi
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta


class BusinessIntelligence:
    """
    Business Intelligence and KPI Analytics toolkit.
    
    Provides comprehensive business metrics calculation and analysis:
    - Revenue analytics
    - Customer metrics
    - Performance indicators
    - Growth analysis
    - Profitability metrics
    """
    
    def __init__(self, data: pd.DataFrame, date_col: str = 'date'):
        """
        Initialize Business Intelligence analyzer.
        
        Args:
            data (pd.DataFrame): Business data
            date_col (str): Name of the date column
        """
        self.data = data.copy()
        self.date_col = date_col
        
        # Ensure date column is datetime
        if date_col in self.data.columns:
            self.data[date_col] = pd.to_datetime(self.data[date_col])
            
        self.kpis = {}
        
    def revenue_analytics(self, 
                         revenue_col: str = 'revenue',
                         period: str = 'monthly') -> Dict:
        """
        Calculate comprehensive revenue analytics.
        
        Args:
            revenue_col: Column containing revenue data
            period: Aggregation period ('daily', 'weekly', 'monthly', 'quarterly')
            
        Returns:
            Dict: Revenue analytics results
        """
        if self.date_col not in self.data.columns or revenue_col not in self.data.columns:
            raise ValueError(f"Required columns {self.date_col} or {revenue_col} not found")
            
        # Set up period grouping
        if period == 'daily':
            self.data['period'] = self.data[self.date_col].dt.date
        elif period == 'weekly':
            self.data['period'] = self.data[self.date_col].dt.to_period('W')
        elif period == 'monthly':
            self.data['period'] = self.data[self.date_col].dt.to_period('M')
        elif period == 'quarterly':
            self.data['period'] = self.data[self.date_col].dt.to_period('Q')
        else:
            raise ValueError("Period must be 'daily', 'weekly', 'monthly', or 'quarterly'")
            
        # Calculate revenue metrics
        revenue_by_period = self.data.groupby('period')[revenue_col].agg([
            'sum', 'mean', 'count', 'std'
        ]).reset_index()
        
        revenue_by_period.columns = ['period', 'total_revenue', 'avg_revenue', 'transactions', 'revenue_std']
        
        # Calculate growth rates
        revenue_by_period['revenue_growth'] = revenue_by_period['total_revenue'].pct_change()
        revenue_by_period['transaction_growth'] = revenue_by_period['transactions'].pct_change()
        
        # Overall metrics
        total_revenue = self.data[revenue_col].sum()
        avg_transaction_value = self.data[revenue_col].mean()
        total_transactions = len(self.data)
        
        # Revenue concentration (top 20% of transactions)
        top_20_pct = self.data[revenue_col].quantile(0.8)
        revenue_concentration = self.data[self.data[revenue_col] >= top_20_pct][revenue_col].sum() / total_revenue
        
        analytics = {
            'period_analysis': revenue_by_period,
            'total_revenue': total_revenue,
            'avg_transaction_value': avg_transaction_value,
            'total_transactions': total_transactions,
            'revenue_concentration_top20': revenue_concentration,
            'revenue_volatility': revenue_by_period['total_revenue'].std(),
            'growth_rate_avg': revenue_by_period['revenue_growth'].mean(),
            'period': period
        }
        
        self.kpis['revenue_analytics'] = analytics
        return analytics
    
    def customer_analytics(self, 
                          customer_col: str = 'customer_id',
                          revenue_col: str = 'revenue') -> Dict:
        """
        Calculate customer-centric business metrics.
        
        Args:
            customer_col: Column containing customer identifiers
            revenue_col: Column containing revenue data
            
        Returns:
            Dict: Customer analytics results
        """
        if customer_col not in self.data.columns:
            raise ValueError(f"Customer column {customer_col} not found")
            
        # Customer metrics
        customer_metrics = self.data.groupby(customer_col).agg({
            revenue_col: ['sum', 'count', 'mean'],
            self.date_col: ['min', 'max']
        }).reset_index()
        
        # Flatten column names
        customer_metrics.columns = [
            customer_col, 'total_revenue', 'transaction_count', 
            'avg_transaction_value', 'first_purchase', 'last_purchase'
        ]
        
        # Calculate customer lifetime value metrics
        customer_metrics['customer_lifetime_days'] = (
            customer_metrics['last_purchase'] - customer_metrics['first_purchase']
        ).dt.days
        
        # Customer segmentation based on RFM-like analysis
        customer_metrics['recency'] = (
            self.data[self.date_col].max() - customer_metrics['last_purchase']
        ).dt.days
        
        customer_metrics['frequency'] = customer_metrics['transaction_count']
        customer_metrics['monetary'] = customer_metrics['total_revenue']
        
        # Calculate percentiles for segmentation
        customer_metrics['recency_score'] = pd.qcut(
            customer_metrics['recency'], 5, labels=[5,4,3,2,1]
        ).astype(int)
        customer_metrics['frequency_score'] = pd.qcut(
            customer_metrics['frequency'].rank(method='first'), 5, labels=[1,2,3,4,5]
        ).astype(int)
        customer_metrics['monetary_score'] = pd.qcut(
            customer_metrics['monetary'].rank(method='first'), 5, labels=[1,2,3,4,5]
        ).astype(int)
        
        # Overall customer analytics
        total_customers = customer_metrics[customer_col].nunique()
        avg_customer_value = customer_metrics['total_revenue'].mean()
        avg_transactions_per_customer = customer_metrics['transaction_count'].mean()
        customer_retention_rate = len(customer_metrics[customer_metrics['transaction_count'] > 1]) / total_customers
        
        analytics = {
            'customer_details': customer_metrics,
            'total_customers': total_customers,
            'avg_customer_lifetime_value': avg_customer_value,
            'avg_transactions_per_customer': avg_transactions_per_customer,
            'customer_retention_rate': customer_retention_rate,
            'top_customers': customer_metrics.nlargest(10, 'total_revenue'),
            'customer_distribution': {
                'high_value': len(customer_metrics[customer_metrics['monetary_score'] >= 4]),
                'medium_value': len(customer_metrics[customer_metrics['monetary_score'] == 3]),
                'low_value': len(customer_metrics[customer_metrics['monetary_score'] <= 2])
            }
        }
        
        self.kpis['customer_analytics'] = analytics
        return analytics
    
    def performance_indicators(self) -> Dict:
        """
        Calculate key performance indicators (KPIs).
        
        Returns:
            Dict: Comprehensive KPI dashboard
        """
        kpis = {}
        
        # Revenue KPIs
        if 'revenue_analytics' in self.kpis:
            rev_analytics = self.kpis['revenue_analytics']
            kpis['revenue_kpis'] = {
                'total_revenue': rev_analytics['total_revenue'],
                'avg_transaction_value': rev_analytics['avg_transaction_value'],
                'revenue_growth_rate': rev_analytics['growth_rate_avg'],
                'revenue_volatility': rev_analytics['revenue_volatility']
            }
        
        # Customer KPIs
        if 'customer_analytics' in self.kpis:
            cust_analytics = self.kpis['customer_analytics']
            kpis['customer_kpis'] = {
                'total_customers': cust_analytics['total_customers'],
                'avg_customer_ltv': cust_analytics['avg_customer_lifetime_value'],
                'customer_retention_rate': cust_analytics['customer_retention_rate'],
                'avg_transactions_per_customer': cust_analytics['avg_transactions_per_customer']
            }
        
        # Operational KPIs
        if self.date_col in self.data.columns:
            date_range = self.data[self.date_col].max() - self.data[self.date_col].min()
            kpis['operational_kpis'] = {
                'data_period_days': date_range.days,
                'daily_transaction_rate': len(self.data) / max(date_range.days, 1),
                'data_completeness': (1 - self.data.isnull().sum().sum() / (self.data.shape[0] * self.data.shape[1])) * 100
            }
        
        self.kpis['performance_indicators'] = kpis
        return kpis
    
    def generate_executive_summary(self) -> str:
        """
        Generate executive summary report.
        
        Returns:
            str: Executive summary in markdown format
        """
        summary = "# Executive Business Intelligence Summary\n\n"
        summary += f"**Report Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        summary += f"**Data Period**: {self.data[self.date_col].min().strftime('%Y-%m-%d')} to {self.data[self.date_col].max().strftime('%Y-%m-%d')}\n\n"
        
        if 'performance_indicators' in self.kpis:
            kpis = self.kpis['performance_indicators']
            
            summary += "## Key Performance Indicators\n\n"
            
            if 'revenue_kpis' in kpis:
                rev_kpis = kpis['revenue_kpis']
                summary += "### Revenue Performance\n"
                summary += f"- **Total Revenue**: ${rev_kpis['total_revenue']:,.2f}\n"
                summary += f"- **Average Transaction Value**: ${rev_kpis['avg_transaction_value']:,.2f}\n"
                summary += f"- **Revenue Growth Rate**: {rev_kpis['revenue_growth_rate']*100:.2f}%\n\n"
            
            if 'customer_kpis' in kpis:
                cust_kpis = kpis['customer_kpis']
                summary += "### Customer Metrics\n"
                summary += f"- **Total Customers**: {cust_kpis['total_customers']:,}\n"
                summary += f"- **Average Customer LTV**: ${cust_kpis['avg_customer_ltv']:,.2f}\n"
                summary += f"- **Customer Retention Rate**: {cust_kpis['customer_retention_rate']*100:.2f}%\n\n"
        
        summary += "## Strategic Recommendations\n\n"
        
        # Add recommendations based on analysis
        if 'customer_analytics' in self.kpis:
            retention_rate = self.kpis['customer_analytics']['customer_retention_rate']
            if retention_rate < 0.5:
                summary += "- **Priority**: Improve customer retention through loyalty programs\n"
            if retention_rate > 0.8:
                summary += "- **Opportunity**: Leverage high retention for referral programs\n"
        
        if 'revenue_analytics' in self.kpis:
            growth_rate = self.kpis['revenue_analytics']['growth_rate_avg']
            if growth_rate > 0.1:
                summary += "- **Strength**: Strong revenue growth momentum\n"
            elif growth_rate < 0:
                summary += "- **Alert**: Revenue decline requires immediate attention\n"
        
        return summary
