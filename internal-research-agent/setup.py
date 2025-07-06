#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="ira-cli",
    version="1.0.0",
    description="Internal Research Agent - AI-powered document research CLI",
    packages=find_packages(),
    install_requires=[
        "langchain>=0.1.1",
        "langchain-community>=0.0.20",
        "langchain-google-genai>=0.0.6",
        "langchain-chroma>=0.2.4",
        "langchain-tavily>=0.1.0",
        "chromadb>=0.4.22",
        "tavily-python>=0.3.1",
        "python-dotenv>=1.0.0",
        "click>=8.1.7",
        "rich>=13.7.0",
        "pydantic>=2.5.3",
        "pydantic-settings>=2.1.0",
        "unstructured>=0.11.8",
        "python-docx>=1.1.0",
        "PyPDF2>=3.0.1",
        "google-auth>=2.0.0",
        "google-api-python-client>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "ira-cli=ira_cli.cli:cli",
            "ira=ira_cli.cli:cli",
        ],
    },
    python_requires=">=3.8",
)