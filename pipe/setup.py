"""
Setup script for the Pipe package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pipe",
    version="0.1.0",
    author="Osman Abdullahi",
    author_email="Osmandabdullahi@gmail.com",
    description="A lightweight, plugin-based data pipeline processor",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Osman-OO/pipe",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=[
        "configparser",
    ],
    extras_require={
        "dev": [
            "pytest",
            "flake8",
            "mypy",
        ],
    },
    entry_points={
        "console_scripts": [
            "pipe=pipe.core.app:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
) 