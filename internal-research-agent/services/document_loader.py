"""
Document loading service for the Internal Research Agent.
"""
import os
from typing import List, Optional
from pathlib import Path

from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredWordDocumentLoader,
    TextLoader
)
from langchain.schema import Document

from utils.logger import logger
from ira_cli.config import settings


class DocumentLoader:
    """Service for loading documents from various file formats."""

    SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}

    def __init__(self, docs_path: Optional[str] = None):
        """
        Initialize the document loader.

        Args:
            docs_path: Path to documents directory
        """
        self.docs_path = Path(docs_path or settings.docs_path)
        if not self.docs_path.exists():
            raise FileNotFoundError(f"Documents path not found: {self.docs_path}")

    def get_supported_files(self) -> List[Path]:
        """
        Get all supported files in the documents directory.

        Returns:
            List of file paths
        """
        supported_files = []

        for file_path in self.docs_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                supported_files.append(file_path)

        logger.info(f"Found {len(supported_files)} supported files in {self.docs_path}")
        return supported_files

    def load_documents(self) -> List[Document]:
        """
        Load all supported documents from the documents directory.

        Returns:
            List of loaded documents
        """
        documents = []
        supported_files = self.get_supported_files()

        for file_path in supported_files:
            try:
                logger.info(f"Loading document: {file_path}")

                if file_path.suffix.lower() == ".pdf":
                    loader = PyPDFLoader(str(file_path))
                elif file_path.suffix.lower() == ".docx":
                    loader = UnstructuredWordDocumentLoader(str(file_path))
                elif file_path.suffix.lower() == ".txt":
                    loader = TextLoader(str(file_path))
                else:
                    logger.warning(f"Unsupported file type: {file_path}")
                    continue

                docs = loader.load()
                documents.extend(docs)
                logger.info(f"Successfully loaded {len(docs)} chunks from {file_path}")

            except Exception as e:
                logger.error(f"Error loading {file_path}: {str(e)}")
                continue

        logger.info(f"Total documents loaded: {len(documents)}")
        return documents

    def load_single_document(self, file_path: str) -> List[Document]:
        """
        Load a single document by file path.

        Args:
            file_path: Path to the document file

        Returns:
            List of loaded documents
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")

        try:
            logger.info(f"Loading single document: {file_path}")

            if file_path.suffix.lower() == ".pdf":
                loader = PyPDFLoader(str(file_path))
            elif file_path.suffix.lower() == ".docx":
                loader = UnstructuredWordDocumentLoader(str(file_path))
            elif file_path.suffix.lower() == ".txt":
                loader = TextLoader(str(file_path))

            docs = loader.load()
            logger.info(f"Successfully loaded {len(docs)} chunks from {file_path}")
            return docs

        except Exception as e:
            logger.error(f"Error loading {file_path}: {str(e)}")
            raise