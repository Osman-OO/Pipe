"""
Executive Dashboard

Interactive business intelligence dashboard for executive-level insights
and real-time analytics monitoring.

Author: Osman Abdullahi
Email: Osmandabdullahi@gmail.com
"""

import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Custom styling
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Executive Analytics Dashboard - Osman Abdullahi"

# Load data
def load_data():
    """Load and prepare data for dashboard."""
    try:
        sales_data = pd.read_csv('data/sales_data.csv')
        ecommerce_data = pd.read_csv('data/ecommerce_data.csv')
        financial_data = pd.read_csv('data/financial_data.csv')
        
        # Convert dates
        sales_data['date'] = pd.to_datetime(sales_data['date'])
        ecommerce_data['date'] = pd.to_datetime(ecommerce_data['date'])
        financial_data['date'] = pd.to_datetime(financial_data['date'])
        
        return sales_data, ecommerce_data, financial_data
    except FileNotFoundError:
        # Create sample data if files don't exist
        return create_sample_data()

def create_sample_data():
    """Create sample data for demonstration."""
    dates = pd.date_range('2023-01-01', '2024-12-31', freq='D')
    
    sales_data = pd.DataFrame({
        'date': np.random.choice(dates, 1000),
        'revenue': np.random.lognormal(5, 1, 1000),
        'customer_segment': np.random.choice(['Premium', 'Standard', 'Basic'], 1000),
        'category': np.random.choice(['Electronics', 'Clothing', 'Books'], 1000)
    })
    
    ecommerce_data = pd.DataFrame({
        'date': np.random.choice(dates, 500),
        'channel': np.random.choice(['Organic', 'Paid', 'Social'], 500),
        'converted': np.random.choice([0, 1], 500, p=[0.95, 0.05]),
        'revenue': np.random.lognormal(4, 0.8, 500)
    })
    
    financial_data = pd.DataFrame({
        'date': dates[:100],
        'symbol': np.repeat(['AAPL', 'GOOGL', 'MSFT'], 100//3 + 1)[:100],
        'close': np.random.lognormal(5, 0.2, 100),
        'returns': np.random.normal(0.001, 0.02, 100)
    })
    
    return sales_data, ecommerce_data, financial_data

# Load data
sales_data, ecommerce_data, financial_data = load_data()

# Calculate KPIs
def calculate_kpis():
    """Calculate key performance indicators."""
    total_revenue = sales_data['revenue'].sum()
    total_customers = sales_data.get('customer_id', pd.Series(range(len(sales_data)))).nunique()
    avg_order_value = sales_data['revenue'].mean()
    
    # Growth calculations (mock for demo)
    revenue_growth = 15.2  # %
    customer_growth = 8.7  # %
    
    return {
        'total_revenue': total_revenue,
        'total_customers': total_customers,
        'avg_order_value': avg_order_value,
        'revenue_growth': revenue_growth,
        'customer_growth': customer_growth
    }

kpis = calculate_kpis()

# Dashboard layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("📊 Executive Analytics Dashboard", 
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '10px'}),
        html.H3("Advanced Data Analytics Portfolio - Osman Abdullahi", 
                style={'textAlign': 'center', 'color': '#7f8c8d', 'marginBottom': '30px'}),
    ], style={'backgroundColor': '#ecf0f1', 'padding': '20px', 'marginBottom': '20px'}),
    
    # KPI Cards
    html.Div([
        html.Div([
            html.H3(f"${kpis['total_revenue']:,.0f}", style={'color': '#27ae60', 'margin': '0'}),
            html.P("Total Revenue", style={'margin': '5px 0'}),
            html.P(f"↗ {kpis['revenue_growth']}%", style={'color': '#27ae60', 'fontSize': '14px'})
        ], className='three columns', style={'textAlign': 'center', 'backgroundColor': '#fff', 
                                           'padding': '20px', 'margin': '10px', 'borderRadius': '5px',
                                           'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
        
        html.Div([
            html.H3(f"{kpis['total_customers']:,}", style={'color': '#3498db', 'margin': '0'}),
            html.P("Total Customers", style={'margin': '5px 0'}),
            html.P(f"↗ {kpis['customer_growth']}%", style={'color': '#27ae60', 'fontSize': '14px'})
        ], className='three columns', style={'textAlign': 'center', 'backgroundColor': '#fff', 
                                           'padding': '20px', 'margin': '10px', 'borderRadius': '5px',
                                           'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
        
        html.Div([
            html.H3(f"${kpis['avg_order_value']:.0f}", style={'color': '#e74c3c', 'margin': '0'}),
            html.P("Avg Order Value", style={'margin': '5px 0'}),
            html.P("↗ 5.3%", style={'color': '#27ae60', 'fontSize': '14px'})
        ], className='three columns', style={'textAlign': 'center', 'backgroundColor': '#fff', 
                                           'padding': '20px', 'margin': '10px', 'borderRadius': '5px',
                                           'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
        
        html.Div([
            html.H3("94.2%", style={'color': '#f39c12', 'margin': '0'}),
            html.P("Customer Satisfaction", style={'margin': '5px 0'}),
            html.P("↗ 2.1%", style={'color': '#27ae60', 'fontSize': '14px'})
        ], className='three columns', style={'textAlign': 'center', 'backgroundColor': '#fff', 
                                           'padding': '20px', 'margin': '10px', 'borderRadius': '5px',
                                           'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
    ], className='row'),
    
    # Charts Row 1
    html.Div([
        html.Div([
            dcc.Graph(id='revenue-trend')
        ], className='six columns'),
        
        html.Div([
            dcc.Graph(id='customer-segments')
        ], className='six columns'),
    ], className='row'),
    
    # Charts Row 2
    html.Div([
        html.Div([
            dcc.Graph(id='channel-performance')
        ], className='six columns'),
        
        html.Div([
            dcc.Graph(id='financial-performance')
        ], className='six columns'),
    ], className='row'),
    
    # Footer
    html.Div([
        html.P("📧 Contact: Osmandabdullahi@gmail.com | 💼 LinkedIn: linkedin.com/in/osman-abdullahi | 🐙 GitHub: github.com/Osman-OO",
               style={'textAlign': 'center', 'color': '#7f8c8d', 'marginTop': '30px'})
    ])
], style={'fontFamily': 'Arial, sans-serif', 'margin': '0 auto', 'maxWidth': '1200px'})

# Callbacks for interactive charts
@app.callback(
    Output('revenue-trend', 'figure'),
    Input('revenue-trend', 'id')
)
def update_revenue_trend(_):
    """Update revenue trend chart."""
    # Aggregate revenue by month
    monthly_revenue = sales_data.groupby(sales_data['date'].dt.to_period('M'))['revenue'].sum().reset_index()
    monthly_revenue['date'] = monthly_revenue['date'].astype(str)
    
    fig = px.line(monthly_revenue, x='date', y='revenue',
                  title='📈 Monthly Revenue Trend',
                  labels={'revenue': 'Revenue ($)', 'date': 'Month'})
    
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12),
        title_font_size=16
    )
    
    return fig

@app.callback(
    Output('customer-segments', 'figure'),
    Input('customer-segments', 'id')
)
def update_customer_segments(_):
    """Update customer segments chart."""
    segment_revenue = sales_data.groupby('customer_segment')['revenue'].sum().reset_index()
    
    fig = px.pie(segment_revenue, values='revenue', names='customer_segment',
                 title='💼 Revenue by Customer Segment')
    
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12),
        title_font_size=16
    )
    
    return fig

@app.callback(
    Output('channel-performance', 'figure'),
    Input('channel-performance', 'id')
)
def update_channel_performance(_):
    """Update channel performance chart."""
    if 'channel' in ecommerce_data.columns:
        channel_conv = ecommerce_data.groupby('channel')['converted'].mean().reset_index()
        channel_conv['converted'] = channel_conv['converted'] * 100
        
        fig = px.bar(channel_conv, x='channel', y='converted',
                     title='🎯 Conversion Rate by Channel (%)',
                     labels={'converted': 'Conversion Rate (%)', 'channel': 'Channel'})
    else:
        # Fallback chart
        sample_channels = ['Organic', 'Paid', 'Social', 'Email']
        sample_rates = [3.2, 4.8, 2.1, 6.5]
        
        fig = px.bar(x=sample_channels, y=sample_rates,
                     title='🎯 Conversion Rate by Channel (%)',
                     labels={'x': 'Channel', 'y': 'Conversion Rate (%)'})
    
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12),
        title_font_size=16
    )
    
    return fig

@app.callback(
    Output('financial-performance', 'figure'),
    Input('financial-performance', 'id')
)
def update_financial_performance(_):
    """Update financial performance chart."""
    if 'symbol' in financial_data.columns and 'returns' in financial_data.columns:
        avg_returns = financial_data.groupby('symbol')['returns'].mean().reset_index()
        avg_returns['returns'] = avg_returns['returns'] * 100
        
        fig = px.bar(avg_returns, x='symbol', y='returns',
                     title='📊 Average Returns by Asset (%)',
                     labels={'returns': 'Average Returns (%)', 'symbol': 'Asset'})
    else:
        # Fallback chart
        sample_assets = ['AAPL', 'GOOGL', 'MSFT', 'AMZN']
        sample_returns = [12.5, 15.2, 8.7, 18.3]
        
        fig = px.bar(x=sample_assets, y=sample_returns,
                     title='📊 Average Returns by Asset (%)',
                     labels={'x': 'Asset', 'y': 'Average Returns (%)'})
    
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12),
        title_font_size=16
    )
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
