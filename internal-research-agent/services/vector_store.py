"""
Vector store service for the Internal Research Agent.
"""
from typing import List, Optional
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.schema import Document

from utils.logger import logger
from ira_cli.config import settings


class VectorStoreService:
    """Service for managing document embeddings and vector storage."""

    def __init__(self, vector_store_path: Optional[str] = None):
        """
        Initialize the vector store service.

        Args:
            vector_store_path: Path to vector store directory
        """
        self.vector_store_path = Path(vector_store_path or settings.vector_store_path)
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )
        self._vector_store = None

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks for embedding.

        Args:
            documents: List of documents to split

        Returns:
            List of document chunks
        """
        logger.info(f"Splitting {len(documents)} documents into chunks")
        chunks = self.text_splitter.split_documents(documents)
        logger.info(f"Created {len(chunks)} chunks")
        return chunks

    def create_vector_store(self, documents: List[Document], force_recreate: bool = False) -> Chroma:
        """
        Create or load a vector store from documents.

        Args:
            documents: List of documents to embed
            force_recreate: Whether to recreate the vector store even if it exists

        Returns:
            Chroma vector store instance
        """
        if self._vector_store is not None and not force_recreate:
            return self._vector_store

        # Check if vector store already exists
        if self.vector_store_path.exists() and not force_recreate:
            logger.info(f"Loading existing vector store from {self.vector_store_path}")
            try:
                self._vector_store = Chroma(
                    persist_directory=str(self.vector_store_path),
                    embedding_function=self.embeddings
                )
                logger.info("Successfully loaded existing vector store")
                return self._vector_store
            except Exception as e:
                logger.warning(f"Failed to load existing vector store: {e}")

        # Create new vector store
        logger.info("Creating new vector store")
        chunks = self.split_documents(documents)

        try:
            self._vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=str(self.vector_store_path)
            )
            logger.info(f"Successfully created vector store with {len(chunks)} chunks")
            return self._vector_store
        except Exception as e:
            logger.error(f"Error creating vector store: {e}")
            raise

    def get_retriever(self, k: int = 4) -> Chroma:
        """
        Get a retriever from the vector store.

        Args:
            k: Number of documents to retrieve

        Returns:
            Retriever instance
        """
        if self._vector_store is None:
            raise ValueError("Vector store not initialized. Call create_vector_store() first.")

        return self._vector_store.as_retriever(search_kwargs={"k": k})

    def add_documents(self, documents: List[Document]) -> None:
        """
        Add new documents to the existing vector store.

        Args:
            documents: List of documents to add
        """
        if self._vector_store is None:
            raise ValueError("Vector store not initialized. Call create_vector_store() first.")

        logger.info(f"Adding {len(documents)} new documents to vector store")
        chunks = self.split_documents(documents)

        try:
            self._vector_store.add_documents(chunks)
            logger.info(f"Successfully added {len(chunks)} chunks to vector store")
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """
        Perform similarity search on the vector store.

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of similar documents
        """
        if self._vector_store is None:
            raise ValueError("Vector store not initialized. Call create_vector_store() first.")

        try:
            results = self._vector_store.similarity_search(query, k=k)
            logger.info(f"Found {len(results)} similar documents for query: {query}")
            return results
        except Exception as e:
            logger.error(f"Error performing similarity search: {e}")
            raise

    def get_collection_info(self) -> dict:
        """
        Get information about the vector store collection.

        Returns:
            Dictionary with collection information
        """
        if self._vector_store is None:
            raise ValueError("Vector store not initialized. Call create_vector_store() first.")

        try:
            collection = self._vector_store._collection
            count = collection.count()
            return {
                "total_documents": count,
                "vector_store_path": str(self.vector_store_path),
                "embedding_model": "models/embedding-001"
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            raise