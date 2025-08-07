"""
Setup script for the Pipe package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="advanced-data-analytics-pipeline",
    version="1.0.0",
    author="Osman Abdullahi",
    author_email="Osmandabdullahi@gmail.com",
    description="Advanced Data Analytics Pipeline - Professional data processing, analysis, and visualization platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Osman-OO/advanced-data-analytics-pipeline",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "plotly>=5.0.0",
        "scikit-learn>=1.0.0",
        "scipy>=1.7.0",
        "requests>=2.25.0",
        "sqlalchemy>=1.4.0",
        "psycopg2-binary>=2.9.0",
        "openpyxl>=3.0.0",
        "configparser",
        "click>=8.0.0",
        "jupyter>=1.0.0",
        "dash>=2.0.0",
        "dash-bootstrap-components>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "flake8>=3.9.0",
            "black>=21.0.0",
            "mypy>=0.910",
            "pre-commit>=2.15.0",
        ],
        "ml": [
            "tensorflow>=2.6.0",
            "xgboost>=1.5.0",
            "lightgbm>=3.3.0",
            "statsmodels>=0.13.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "analytics-pipeline=pipe.app:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Data Scientists",
        "Intended Audience :: Business Analysts",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)