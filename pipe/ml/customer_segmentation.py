"""
Customer Segmentation Module

Advanced customer segmentation using RFM analysis, clustering algorithms,
and behavioral analytics for targeted marketing and customer insights.

Author: Osman Abdullahi
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Tuple
import warnings

warnings.filterwarnings('ignore')


class CustomerSegmentation:
    """
    Professional customer segmentation toolkit using advanced analytics.
    
    Features:
    - RFM (Recency, Frequency, Monetary) analysis
    - K-means clustering
    - Customer lifetime value calculation
    - Behavioral segmentation
    - Actionable business insights
    """
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize Customer Segmentation analyzer.
        
        Args:
            data (pd.DataFrame): Customer transaction data
        """
        self.data = data.copy()
        self.rfm_data = None
        self.segments = None
        self.model = None
        self.scaler = StandardScaler()
        
    def calculate_rfm(self, 
                     customer_col: str = 'customer_id',
                     date_col: str = 'date',
                     revenue_col: str = 'revenue',
                     reference_date: Optional[str] = None) -> pd.DataFrame:
        """
        Calculate RFM (Recency, Frequency, Monetary) metrics.
        
        Args:
            customer_col: Customer identifier column
            date_col: Transaction date column
            revenue_col: Revenue/monetary value column
            reference_date: Reference date for recency calculation
            
        Returns:
            pd.DataFrame: RFM metrics for each customer
        """
        # Ensure date column is datetime
        self.data[date_col] = pd.to_datetime(self.data[date_col])
        
        # Set reference date
        if reference_date is None:
            reference_date = self.data[date_col].max()
        else:
            reference_date = pd.to_datetime(reference_date)
            
        # Calculate RFM metrics
        rfm = self.data.groupby(customer_col).agg({
            date_col: lambda x: (reference_date - x.max()).days,  # Recency
            revenue_col: ['count', 'sum']  # Frequency and Monetary
        }).reset_index()
        
        # Flatten column names
        rfm.columns = [customer_col, 'recency', 'frequency', 'monetary']
        
        # Calculate RFM scores (1-5 scale)
        rfm['recency_score'] = pd.qcut(rfm['recency'], 5, labels=[5,4,3,2,1]).astype(int)
        rfm['frequency_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1,2,3,4,5]).astype(int)
        rfm['monetary_score'] = pd.qcut(rfm['monetary'].rank(method='first'), 5, labels=[1,2,3,4,5]).astype(int)
        
        # Create RFM segment
        rfm['rfm_segment'] = (rfm['recency_score'].astype(str) + 
                             rfm['frequency_score'].astype(str) + 
                             rfm['monetary_score'].astype(str))
        
        # Calculate overall RFM score
        rfm['rfm_score'] = rfm['recency_score'] + rfm['frequency_score'] + rfm['monetary_score']
        
        self.rfm_data = rfm
        return rfm
    
    def create_customer_segments(self, method: str = 'rfm_rules') -> pd.DataFrame:
        """
        Create customer segments using various methods.
        
        Args:
            method: Segmentation method ('rfm_rules', 'kmeans', 'dbscan')
            
        Returns:
            pd.DataFrame: Customer data with segment labels
        """
        if self.rfm_data is None:
            raise ValueError("RFM data not calculated. Run calculate_rfm() first.")
            
        rfm = self.rfm_data.copy()
        
        if method == 'rfm_rules':
            # Rule-based segmentation
            def segment_customers(row):
                if row['rfm_score'] >= 12:
                    return 'Champions'
                elif row['rfm_score'] >= 10:
                    return 'Loyal Customers'
                elif row['rfm_score'] >= 8:
                    return 'Potential Loyalists'
                elif row['rfm_score'] >= 6:
                    return 'At Risk'
                elif row['rfm_score'] >= 4:
                    return 'Cannot Lose Them'
                else:
                    return 'Lost Customers'
                    
            rfm['segment'] = rfm.apply(segment_customers, axis=1)
            
        elif method == 'kmeans':
            # K-means clustering
            features = ['recency', 'frequency', 'monetary']
            X = self.scaler.fit_transform(rfm[features])
            
            # Find optimal number of clusters
            silhouette_scores = []
            K_range = range(2, 8)
            
            for k in K_range:
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                cluster_labels = kmeans.fit_predict(X)
                silhouette_avg = silhouette_score(X, cluster_labels)
                silhouette_scores.append(silhouette_avg)
            
            # Use optimal number of clusters
            optimal_k = K_range[np.argmax(silhouette_scores)]
            
            self.model = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
            rfm['segment'] = self.model.fit_predict(X)
            
            # Create meaningful segment names
            segment_names = {
                0: 'High Value',
                1: 'Medium Value', 
                2: 'Low Value',
                3: 'New Customers',
                4: 'At Risk',
                5: 'Lost Customers'
            }
            
            rfm['segment'] = rfm['segment'].map(lambda x: segment_names.get(x, f'Segment_{x}'))
            
        elif method == 'dbscan':
            # DBSCAN clustering
            features = ['recency', 'frequency', 'monetary']
            X = self.scaler.fit_transform(rfm[features])
            
            self.model = DBSCAN(eps=0.5, min_samples=5)
            rfm['segment'] = self.model.fit_predict(X)
            
            # Handle noise points
            rfm['segment'] = rfm['segment'].map(lambda x: 'Outliers' if x == -1 else f'Cluster_{x}')
            
        else:
            raise ValueError("Method must be 'rfm_rules', 'kmeans', or 'dbscan'")
            
        self.segments = rfm
        return rfm
    
    def analyze_segments(self) -> Dict:
        """
        Analyze customer segments and provide business insights.
        
        Returns:
            Dict: Comprehensive segment analysis
        """
        if self.segments is None:
            raise ValueError("Segments not created. Run create_customer_segments() first.")
            
        analysis = {}
        
        # Segment summary statistics
        segment_summary = self.segments.groupby('segment').agg({
            'recency': ['mean', 'median'],
            'frequency': ['mean', 'median'],
            'monetary': ['mean', 'median', 'sum'],
            'rfm_score': 'mean'
        }).round(2)
        
        # Segment sizes
        segment_sizes = self.segments['segment'].value_counts()
        segment_percentages = (segment_sizes / len(self.segments) * 100).round(2)
        
        # Revenue contribution by segment
        revenue_by_segment = self.segments.groupby('segment')['monetary'].sum().sort_values(ascending=False)
        revenue_percentage = (revenue_by_segment / revenue_by_segment.sum() * 100).round(2)
        
        analysis = {
            'segment_summary': segment_summary,
            'segment_sizes': segment_sizes,
            'segment_percentages': segment_percentages,
            'revenue_by_segment': revenue_by_segment,
            'revenue_percentage': revenue_percentage,
            'total_customers': len(self.segments),
            'total_revenue': self.segments['monetary'].sum()
        }
        
        return analysis
    
    def generate_recommendations(self) -> Dict:
        """
        Generate actionable business recommendations for each segment.
        
        Returns:
            Dict: Marketing and business recommendations
        """
        if self.segments is None:
            raise ValueError("Segments not created. Run create_customer_segments() first.")
            
        recommendations = {}
        
        # Analyze each segment
        for segment in self.segments['segment'].unique():
            segment_data = self.segments[self.segments['segment'] == segment]
            
            avg_recency = segment_data['recency'].mean()
            avg_frequency = segment_data['frequency'].mean()
            avg_monetary = segment_data['monetary'].mean()
            
            # Generate recommendations based on segment characteristics
            if 'Champions' in segment or 'High Value' in segment:
                recommendations[segment] = {
                    'strategy': 'Reward and Retain',
                    'actions': [
                        'Offer exclusive products and early access',
                        'Implement VIP customer service',
                        'Request referrals and testimonials',
                        'Upsell premium products'
                    ],
                    'priority': 'High'
                }
            elif 'Loyal' in segment or 'Medium Value' in segment:
                recommendations[segment] = {
                    'strategy': 'Nurture and Grow',
                    'actions': [
                        'Offer loyalty programs',
                        'Cross-sell complementary products',
                        'Provide personalized recommendations',
                        'Engage through targeted content'
                    ],
                    'priority': 'Medium'
                }
            elif 'At Risk' in segment:
                recommendations[segment] = {
                    'strategy': 'Win Back',
                    'actions': [
                        'Send personalized win-back campaigns',
                        'Offer special discounts or incentives',
                        'Conduct satisfaction surveys',
                        'Provide exceptional customer service'
                    ],
                    'priority': 'High'
                }
            elif 'Lost' in segment or 'Low Value' in segment:
                recommendations[segment] = {
                    'strategy': 'Reactivate or Let Go',
                    'actions': [
                        'Send final win-back offer',
                        'Conduct exit interviews',
                        'Remove from expensive marketing channels',
                        'Focus resources on higher-value segments'
                    ],
                    'priority': 'Low'
                }
            else:
                recommendations[segment] = {
                    'strategy': 'Analyze and Engage',
                    'actions': [
                        'Conduct deeper analysis of segment behavior',
                        'Test different engagement strategies',
                        'Monitor segment evolution',
                        'Customize communication approach'
                    ],
                    'priority': 'Medium'
                }
                
        return recommendations
    
    def visualize_segments(self, save_path: Optional[str] = None) -> None:
        """
        Create visualizations for customer segments.
        
        Args:
            save_path: Path to save the visualization
        """
        if self.segments is None:
            raise ValueError("Segments not created. Run create_customer_segments() first.")
            
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Segment distribution
        self.segments['segment'].value_counts().plot(kind='bar', ax=axes[0,0])
        axes[0,0].set_title('Customer Segment Distribution')
        axes[0,0].set_xlabel('Segment')
        axes[0,0].set_ylabel('Number of Customers')
        
        # RFM scatter plot
        scatter = axes[0,1].scatter(self.segments['frequency'], self.segments['monetary'], 
                                  c=self.segments['recency'], alpha=0.6, cmap='viridis')
        axes[0,1].set_xlabel('Frequency')
        axes[0,1].set_ylabel('Monetary')
        axes[0,1].set_title('RFM Analysis (Color = Recency)')
        plt.colorbar(scatter, ax=axes[0,1])
        
        # Revenue by segment
        revenue_by_segment = self.segments.groupby('segment')['monetary'].sum()
        revenue_by_segment.plot(kind='pie', ax=axes[1,0], autopct='%1.1f%%')
        axes[1,0].set_title('Revenue Distribution by Segment')
        
        # Segment characteristics heatmap
        segment_chars = self.segments.groupby('segment')[['recency', 'frequency', 'monetary']].mean()
        sns.heatmap(segment_chars.T, annot=True, cmap='YlOrRd', ax=axes[1,1])
        axes[1,1].set_title('Segment Characteristics Heatmap')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
