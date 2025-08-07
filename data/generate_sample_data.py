"""
Sample Data Generator

Generates realistic sample datasets for demonstrating advanced data analytics capabilities.
Creates datasets for sales, financial, e-commerce, and social media analytics.

Author: Osman Abdullahi
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from typing import Dict, List
import os


class SampleDataGenerator:
    """
    Professional sample data generator for analytics demonstrations.
    """
    
    def __init__(self, seed: int = 42):
        """Initialize with random seed for reproducibility."""
        np.random.seed(seed)
        random.seed(seed)
        
    def generate_sales_data(self, n_customers: int = 1000, n_transactions: int = 5000) -> pd.DataFrame:
        """
        Generate realistic sales transaction data.
        
        Args:
            n_customers: Number of unique customers
            n_transactions: Number of transactions
            
        Returns:
            pd.DataFrame: Sales transaction data
        """
        # Customer demographics
        customers = []
        for i in range(n_customers):
            customers.append({
                'customer_id': f'CUST_{i+1:04d}',
                'age': np.random.normal(40, 15),
                'gender': np.random.choice(['M', 'F'], p=[0.48, 0.52]),
                'city': np.random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'], 
                                       p=[0.3, 0.25, 0.2, 0.15, 0.1]),
                'customer_segment': np.random.choice(['Premium', 'Standard', 'Basic'], p=[0.2, 0.5, 0.3])
            })
        
        customer_df = pd.DataFrame(customers)
        
        # Generate transactions
        transactions = []
        start_date = datetime(2022, 1, 1)
        end_date = datetime(2024, 12, 31)
        
        products = [
            {'product_id': 'PROD_001', 'product_name': 'Laptop Pro', 'category': 'Electronics', 'base_price': 1200},
            {'product_id': 'PROD_002', 'product_name': 'Smartphone X', 'category': 'Electronics', 'base_price': 800},
            {'product_id': 'PROD_003', 'product_name': 'Wireless Headphones', 'category': 'Electronics', 'base_price': 200},
            {'product_id': 'PROD_004', 'product_name': 'Coffee Maker', 'category': 'Appliances', 'base_price': 150},
            {'product_id': 'PROD_005', 'product_name': 'Running Shoes', 'category': 'Sports', 'base_price': 120},
            {'product_id': 'PROD_006', 'product_name': 'Office Chair', 'category': 'Furniture', 'base_price': 300},
            {'product_id': 'PROD_007', 'product_name': 'Tablet', 'category': 'Electronics', 'base_price': 400},
            {'product_id': 'PROD_008', 'product_name': 'Fitness Tracker', 'category': 'Sports', 'base_price': 100}
        ]
        
        for i in range(n_transactions):
            customer = customer_df.sample(1).iloc[0]
            product = random.choice(products)
            
            # Date with seasonal patterns
            transaction_date = start_date + timedelta(days=np.random.randint(0, (end_date - start_date).days))
            
            # Seasonal adjustment
            month = transaction_date.month
            seasonal_multiplier = 1.0
            if month in [11, 12]:  # Holiday season
                seasonal_multiplier = 1.3
            elif month in [6, 7, 8]:  # Summer
                seasonal_multiplier = 1.1
            
            # Customer segment pricing
            segment_multiplier = {'Premium': 1.2, 'Standard': 1.0, 'Basic': 0.8}[customer['customer_segment']]
            
            # Calculate final price with some randomness
            base_price = product['base_price']
            final_price = base_price * seasonal_multiplier * segment_multiplier * np.random.uniform(0.8, 1.2)
            
            # Quantity (most transactions are single items)
            quantity = np.random.choice([1, 2, 3], p=[0.7, 0.2, 0.1])
            
            transactions.append({
                'transaction_id': f'TXN_{i+1:06d}',
                'customer_id': customer['customer_id'],
                'product_id': product['product_id'],
                'product_name': product['product_name'],
                'category': product['category'],
                'date': transaction_date,
                'quantity': quantity,
                'unit_price': final_price,
                'revenue': final_price * quantity,
                'customer_age': customer['age'],
                'customer_gender': customer['gender'],
                'customer_city': customer['city'],
                'customer_segment': customer['customer_segment']
            })
        
        return pd.DataFrame(transactions)
    
    def generate_financial_data(self, n_days: int = 1000) -> pd.DataFrame:
        """
        Generate financial market data for portfolio analysis.
        
        Args:
            n_days: Number of trading days
            
        Returns:
            pd.DataFrame: Financial market data
        """
        start_date = datetime(2022, 1, 1)
        
        # Stock symbols and their characteristics
        stocks = {
            'AAPL': {'initial_price': 150, 'volatility': 0.25, 'drift': 0.08},
            'GOOGL': {'initial_price': 2500, 'volatility': 0.30, 'drift': 0.10},
            'MSFT': {'initial_price': 300, 'volatility': 0.22, 'drift': 0.09},
            'AMZN': {'initial_price': 3200, 'volatility': 0.35, 'drift': 0.12},
            'TSLA': {'initial_price': 800, 'volatility': 0.50, 'drift': 0.15}
        }
        
        financial_data = []
        
        for symbol, params in stocks.items():
            prices = [params['initial_price']]
            
            for day in range(1, n_days):
                # Geometric Brownian Motion for stock prices
                dt = 1/252  # Daily time step
                drift = params['drift']
                volatility = params['volatility']
                
                random_shock = np.random.normal(0, 1)
                price_change = drift * dt + volatility * np.sqrt(dt) * random_shock
                new_price = prices[-1] * np.exp(price_change)
                prices.append(new_price)
                
                # Add market data
                date = start_date + timedelta(days=day)
                volume = np.random.lognormal(15, 0.5)  # Trading volume
                
                financial_data.append({
                    'date': date,
                    'symbol': symbol,
                    'open': prices[-2] * np.random.uniform(0.99, 1.01),
                    'high': new_price * np.random.uniform(1.00, 1.02),
                    'low': new_price * np.random.uniform(0.98, 1.00),
                    'close': new_price,
                    'volume': int(volume),
                    'returns': (new_price - prices[-2]) / prices[-2] if len(prices) > 1 else 0
                })
        
        return pd.DataFrame(financial_data)
    
    def generate_ecommerce_data(self, n_users: int = 2000, n_sessions: int = 10000) -> pd.DataFrame:
        """
        Generate e-commerce user behavior data.
        
        Args:
            n_users: Number of unique users
            n_sessions: Number of user sessions
            
        Returns:
            pd.DataFrame: E-commerce analytics data
        """
        # User acquisition channels
        channels = ['Organic Search', 'Paid Search', 'Social Media', 'Email', 'Direct', 'Referral']
        channel_weights = [0.35, 0.25, 0.15, 0.10, 0.10, 0.05]
        
        # Device types
        devices = ['Desktop', 'Mobile', 'Tablet']
        device_weights = [0.45, 0.45, 0.10]
        
        sessions = []
        
        for i in range(n_sessions):
            user_id = f'USER_{np.random.randint(1, n_users+1):05d}'
            session_date = datetime(2023, 1, 1) + timedelta(days=np.random.randint(0, 365))
            
            # Session characteristics
            channel = np.random.choice(channels, p=channel_weights)
            device = np.random.choice(devices, p=device_weights)
            
            # Behavior metrics
            page_views = np.random.poisson(5) + 1
            session_duration = np.random.exponential(180)  # seconds
            
            # Conversion probability based on channel and device
            base_conversion_rate = 0.02
            channel_multiplier = {
                'Organic Search': 1.2, 'Paid Search': 1.5, 'Social Media': 0.8,
                'Email': 2.0, 'Direct': 1.8, 'Referral': 1.3
            }[channel]
            
            device_multiplier = {'Desktop': 1.2, 'Mobile': 0.9, 'Tablet': 1.0}[device]
            
            conversion_rate = base_conversion_rate * channel_multiplier * device_multiplier
            converted = np.random.random() < conversion_rate
            
            # Revenue if converted
            revenue = 0
            if converted:
                revenue = np.random.lognormal(4, 0.8)  # Log-normal distribution for revenue
            
            sessions.append({
                'session_id': f'SESS_{i+1:07d}',
                'user_id': user_id,
                'date': session_date,
                'channel': channel,
                'device': device,
                'page_views': page_views,
                'session_duration': session_duration,
                'converted': converted,
                'revenue': revenue,
                'bounce_rate': 1 if page_views == 1 else 0
            })
        
        return pd.DataFrame(sessions)
    
    def save_all_datasets(self, output_dir: str = 'data') -> None:
        """
        Generate and save all sample datasets.
        
        Args:
            output_dir: Directory to save datasets
        """
        os.makedirs(output_dir, exist_ok=True)
        
        print("Generating sales data...")
        sales_data = self.generate_sales_data(n_customers=1000, n_transactions=5000)
        sales_data.to_csv(f'{output_dir}/sales_data.csv', index=False)
        
        print("Generating financial data...")
        financial_data = self.generate_financial_data(n_days=1000)
        financial_data.to_csv(f'{output_dir}/financial_data.csv', index=False)
        
        print("Generating e-commerce data...")
        ecommerce_data = self.generate_ecommerce_data(n_users=2000, n_sessions=10000)
        ecommerce_data.to_csv(f'{output_dir}/ecommerce_data.csv', index=False)
        
        print(f"All datasets saved to {output_dir}/")
        print(f"- Sales data: {len(sales_data)} transactions")
        print(f"- Financial data: {len(financial_data)} records")
        print(f"- E-commerce data: {len(ecommerce_data)} sessions")


if __name__ == "__main__":
    generator = SampleDataGenerator()
    generator.save_all_datasets()
