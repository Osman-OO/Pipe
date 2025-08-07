#!/usr/bin/env python3
"""
Advanced Data Analytics Pipeline - Main Application

Professional data analytics platform with comprehensive business intelligence,
statistical analysis, and machine learning capabilities.

Author: Osman Abdullahi
Email: Osmandabdullahi@gmail.com
"""

import sys
import os
import argparse
import logging
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional

# Import analytics modules
from .analytics.statistical_analysis import StatisticalAnalyzer
from .analytics.business_intelligence import BusinessIntelligence
from .ml.customer_segmentation import CustomerSegmentation


class AdvancedAnalyticsPipeline:
    """
    Advanced Data Analytics Pipeline - Professional analytics platform.
    
    Features:
    - Statistical analysis and hypothesis testing
    - Business intelligence and KPI calculation
    - Customer segmentation and behavioral analysis
    - Machine learning and predictive modeling
    - Interactive dashboards and reporting
    """
    
    def __init__(self):
        """Initialize the analytics pipeline."""
        self.logger = None
        self.data = None
        self.results = {}
        
    def process_options(self):
        """Process command line arguments."""
        parser = argparse.ArgumentParser(
            description='Advanced Data Analytics Pipeline - Professional Business Intelligence Platform',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s --dataset sales --analysis comprehensive
  %(prog)s --dashboard --port 8050
  %(prog)s --segment-customers --method rfm
  %(prog)s --generate-report --type executive
            """
        )
        
        # Data input options
        parser.add_argument('--dataset', choices=['sales', 'financial', 'ecommerce'], 
                          help='Dataset to analyze')
        parser.add_argument('--data-file', help='Custom data file path')
        
        # Analysis options
        parser.add_argument('--analysis', choices=['statistical', 'business', 'comprehensive'],
                          help='Type of analysis to perform')
        parser.add_argument('--segment-customers', action='store_true',
                          help='Perform customer segmentation analysis')
        parser.add_argument('--method', choices=['rfm', 'kmeans', 'dbscan'], default='rfm',
                          help='Segmentation method')
        
        # Output options
        parser.add_argument('--dashboard', action='store_true',
                          help='Launch interactive dashboard')
        parser.add_argument('--port', type=int, default=8050,
                          help='Dashboard port (default: 8050)')
        parser.add_argument('--generate-report', action='store_true',
                          help='Generate analysis report')
        parser.add_argument('--report-type', choices=['executive', 'technical', 'comprehensive'],
                          default='comprehensive', help='Type of report to generate')
        parser.add_argument('--output-dir', default='reports',
                          help='Output directory for reports')
        
        # Configuration options
        parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
        parser.add_argument('-d', '--debug', action='store_true', help='Enable debug logging')
        
        self.args = parser.parse_args()
        
    def setup_logging(self):
        """Configure logging system."""
        level = logging.INFO
        if self.args.debug:
            level = logging.DEBUG
            
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout) if self.args.verbose else logging.NullHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("🚀 Advanced Data Analytics Pipeline initialized")
        
    def load_data(self) -> pd.DataFrame:
        """Load data for analysis."""
        if self.args.data_file:
            self.logger.info(f"📂 Loading custom data file: {self.args.data_file}")
            return pd.read_csv(self.args.data_file)
            
        elif self.args.dataset:
            data_file = f"data/{self.args.dataset}_data.csv"
            if os.path.exists(data_file):
                self.logger.info(f"📊 Loading {self.args.dataset} dataset")
                data = pd.read_csv(data_file)
                
                # Convert date columns
                if 'date' in data.columns:
                    data['date'] = pd.to_datetime(data['date'])
                    
                return data
            else:
                self.logger.error(f"❌ Dataset file not found: {data_file}")
                sys.exit(1)
        else:
            self.logger.error("❌ No dataset specified. Use --dataset or --data-file")
            sys.exit(1)
            
    def run_statistical_analysis(self) -> Dict:
        """Run comprehensive statistical analysis."""
        self.logger.info("📈 Running statistical analysis...")
        
        analyzer = StatisticalAnalyzer(self.data)
        
        # Descriptive statistics
        numeric_columns = self.data.select_dtypes(include=['number']).columns.tolist()
        desc_stats = analyzer.descriptive_statistics(numeric_columns)
        
        # Correlation analysis
        correlation = analyzer.correlation_analysis(method='pearson')
        
        results = {
            'descriptive_statistics': desc_stats,
            'correlation_matrix': correlation,
            'analysis_date': datetime.now().isoformat()
        }
        
        # Hypothesis testing if categorical columns exist
        categorical_cols = self.data.select_dtypes(include=['object']).columns.tolist()
        if categorical_cols and numeric_columns:
            try:
                hypothesis_result = analyzer.hypothesis_testing(
                    group_col=categorical_cols[0],
                    value_col=numeric_columns[0],
                    test_type='anova'
                )
                results['hypothesis_testing'] = hypothesis_result
            except Exception as e:
                self.logger.warning(f"⚠️ Hypothesis testing failed: {e}")
        
        self.results['statistical_analysis'] = results
        return results
        
    def run_business_intelligence(self) -> Dict:
        """Run business intelligence analysis."""
        self.logger.info("💼 Running business intelligence analysis...")
        
        bi_analyzer = BusinessIntelligence(self.data, date_col='date')
        
        # Revenue analytics
        revenue_col = 'revenue' if 'revenue' in self.data.columns else self.data.select_dtypes(include=['number']).columns[0]
        revenue_analytics = bi_analyzer.revenue_analytics(revenue_col=revenue_col, period='monthly')
        
        # Customer analytics if customer data exists
        customer_col = None
        for col in ['customer_id', 'user_id', 'id']:
            if col in self.data.columns:
                customer_col = col
                break
                
        if customer_col:
            customer_analytics = bi_analyzer.customer_analytics(
                customer_col=customer_col,
                revenue_col=revenue_col
            )
        else:
            customer_analytics = None
            
        # Performance indicators
        kpis = bi_analyzer.performance_indicators()
        
        # Executive summary
        executive_summary = bi_analyzer.generate_executive_summary()
        
        results = {
            'revenue_analytics': revenue_analytics,
            'customer_analytics': customer_analytics,
            'kpis': kpis,
            'executive_summary': executive_summary,
            'analysis_date': datetime.now().isoformat()
        }
        
        self.results['business_intelligence'] = results
        return results
        
    def run_customer_segmentation(self) -> Dict:
        """Run customer segmentation analysis."""
        self.logger.info("🎯 Running customer segmentation analysis...")
        
        segmentation = CustomerSegmentation(self.data)
        
        # Find required columns
        customer_col = None
        for col in ['customer_id', 'user_id', 'id']:
            if col in self.data.columns:
                customer_col = col
                break
                
        if not customer_col:
            self.logger.error("❌ No customer ID column found")
            return {}
            
        revenue_col = 'revenue' if 'revenue' in self.data.columns else self.data.select_dtypes(include=['number']).columns[0]
        
        # Calculate RFM
        rfm_data = segmentation.calculate_rfm(
            customer_col=customer_col,
            date_col='date',
            revenue_col=revenue_col
        )
        
        # Create segments
        segments = segmentation.create_customer_segments(method=self.args.method)
        
        # Analyze segments
        analysis = segmentation.analyze_segments()
        
        # Generate recommendations
        recommendations = segmentation.generate_recommendations()
        
        results = {
            'rfm_data': rfm_data,
            'segments': segments,
            'analysis': analysis,
            'recommendations': recommendations,
            'method': self.args.method,
            'analysis_date': datetime.now().isoformat()
        }
        
        self.results['customer_segmentation'] = results
        return results
        
    def launch_dashboard(self):
        """Launch interactive dashboard."""
        self.logger.info(f"🚀 Launching dashboard on port {self.args.port}")
        
        try:
            # Import dashboard
            from ..dashboards.executive_dashboard import app
            app.run_server(debug=False, host='0.0.0.0', port=self.args.port)
        except ImportError:
            self.logger.error("❌ Dashboard dependencies not installed. Install with: pip install dash plotly")
            sys.exit(1)
            
    def generate_report(self):
        """Generate analysis report."""
        self.logger.info(f"📋 Generating {self.args.report_type} report...")
        
        # Ensure output directory exists
        os.makedirs(self.args.output_dir, exist_ok=True)
        
        # Generate report content
        report_content = self._create_report_content()
        
        # Save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.args.output_dir}/{self.args.report_type}_report_{timestamp}.md"
        
        with open(filename, 'w') as f:
            f.write(report_content)
            
        self.logger.info(f"✅ Report saved to {filename}")
        
    def _create_report_content(self) -> str:
        """Create report content based on analysis results."""
        report = f"# {self.args.report_type.title()} Analytics Report\n\n"
        report += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"**Dataset**: {self.args.dataset or 'Custom'}\n"
        report += f"**Records**: {len(self.data):,}\n\n"
        
        # Add analysis results
        for analysis_type, results in self.results.items():
            report += f"## {analysis_type.replace('_', ' ').title()}\n\n"
            
            if analysis_type == 'statistical_analysis':
                report += "### Key Statistics\n\n"
                if 'descriptive_statistics' in results:
                    for col, stats in results['descriptive_statistics'].items():
                        report += f"**{col}**:\n"
                        report += f"- Mean: {stats['mean']:.2f}\n"
                        report += f"- Median: {stats['median']:.2f}\n"
                        report += f"- Std Dev: {stats['std']:.2f}\n\n"
                        
            elif analysis_type == 'business_intelligence':
                if 'executive_summary' in results:
                    report += results['executive_summary']
                    
        return report
        
    def run(self):
        """Main execution method."""
        self.process_options()
        self.setup_logging()
        
        # Handle dashboard launch
        if self.args.dashboard:
            self.launch_dashboard()
            return
            
        # Load data
        self.data = self.load_data()
        self.logger.info(f"📊 Loaded dataset with {len(self.data):,} records and {len(self.data.columns)} columns")
        
        # Run analyses based on arguments
        if self.args.analysis == 'statistical' or self.args.analysis == 'comprehensive':
            self.run_statistical_analysis()
            
        if self.args.analysis == 'business' or self.args.analysis == 'comprehensive':
            self.run_business_intelligence()
            
        if self.args.segment_customers:
            self.run_customer_segmentation()
            
        # Generate report if requested
        if self.args.generate_report:
            self.generate_report()
            
        self.logger.info("✅ Analysis complete!")


def main():
    """Main entry point."""
    pipeline = AdvancedAnalyticsPipeline()
    pipeline.run()


if __name__ == '__main__':
    main()
