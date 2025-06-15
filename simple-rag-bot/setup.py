from setuptools import setup, find_packages

setup(
    name="simple-rag-bot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "chromadb",
        "google-generativeai",
        "python-docx",
        "PyPDF2",
    ],
    entry_points={
        'console_scripts': [
            'ragbot=src.main:main',
        ],
    },
)