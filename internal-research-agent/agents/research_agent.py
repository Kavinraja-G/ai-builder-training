"""
Research Agent for the Internal Research Agent application.
"""
from typing import List, Optional

from langchain.chains import RetrievalQA
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool, tool
from langchain_tavily import TavilySearch
from langchain_google_genai import ChatGoogleGenerativeAI

from services.document_loader import DocumentLoader
from services.vector_store import VectorStoreService
from tools.mcp_google_docs_tool import create_mcp_google_docs_tool
from utils.logger import logger
from ira_cli.config import settings


class ResearchAgent:
    """Main research agent that combines document retrieval and web search capabilities."""

    def __init__(self):
        """Initialize the research agent with all necessary components."""
        self.llm = ChatGoogleGenerativeAI(
            model=settings.model_name,
            temperature=settings.temperature,
            max_retries=settings.max_retries,
        )

        self.document_loader = DocumentLoader()
        self.vector_store_service = VectorStoreService()
        self.rag_chain = None
        self.agent = None

        logger.info("Research Agent initialized")

    def setup_rag_chain(self, force_recreate: bool = False) -> None:
        """
        Set up the RAG (Retrieval-Augmented Generation) chain.

        Args:
            force_recreate: Whether to recreate the vector store
        """
        logger.info("Setting up RAG chain")

        # Load documents
        documents = self.document_loader.load_documents()
        if not documents:
            logger.warning("No documents found to create RAG chain")
            return

        # Create vector store
        self.vector_store_service.create_vector_store(documents, force_recreate=force_recreate)

        # Create retriever
        retriever = self.vector_store_service.get_retriever()

        # Create RAG chain
        self.rag_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=retriever
        )

        logger.info("RAG chain setup complete")

    def setup_tools(self) -> List[Tool]:
        """
        Set up the tools for the agent.

        Returns:
            List of configured tools
        """
        tools = []

                # RAG tool for internal documents
        if self.rag_chain:
            rag_tool = Tool(
                name="InternalDocumentsRAG",
                func=self.rag_chain.run,
                description=(
                    "Useful for answering questions about internal HR policies, "
                    "compliance documents, and company procedures. Use this tool "
                    "when the question relates to internal company information."
                )
            )
            tools.append(rag_tool)
            logger.info("Added RAG tool for internal documents")
        else:
            logger.warning("RAG chain not set up - skipping RAG tool")

        # Web search tool
        try:
            search_tool = TavilySearch(max_results=settings.max_search_results)

            # Create a wrapper function for the search tool
            def web_search_wrapper(query: str) -> str:
                """Search the web for current information."""
                return search_tool.invoke({"query": query})

            web_tool = Tool(
                name="WebSearch",
                func=web_search_wrapper,
                description="Useful for searching the web for current information and recent events."
            )

            tools.append(web_tool)
            logger.info("Added web search tool")
        except Exception as e:
            logger.error(f"Failed to initialize search tool: {e}")

        # Google Docs MCP tool for Company X insurance queries
        try:
            google_docs_tool = create_mcp_google_docs_tool()
            tools.append(google_docs_tool)
            logger.info("Added Google Docs MCP tool for Company X insurance queries")
        except Exception as e:
            logger.error(f"Failed to initialize Google Docs MCP tool: {e}")

        return tools

    def initialize_agent(self, force_recreate: bool = False) -> None:
        """
        Initialize the agent with all tools and chains.

        Args:
            force_recreate: Whether to recreate the vector store
        """
        logger.info("Initializing research agent")

        # Set up RAG chain
        self.setup_rag_chain(force_recreate=force_recreate)

        # Set up tools
        tools = self.setup_tools()

        if not tools:
            raise ValueError("No tools available for the agent")

        # Initialize agent
        self.agent = initialize_agent(
            tools=tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=False,
            handle_parsing_errors=True
        )

        logger.info("Research agent initialization complete")

    def query(self, question: str) -> str:
        """
        Query the research agent with a question.

        Args:
            question: The question to ask

        Returns:
            Agent's response
        """
        if not self.agent:
            raise ValueError("Agent not initialized. Call initialize_agent() first.")

        logger.info(f"Processing query: {question}")

        try:
            response = self.agent.invoke(question)
            logger.info("Query processed successfully")
            return response
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            raise

    def add_documents(self, file_paths: List[str]) -> None:
        """
        Add new documents to the existing vector store.

        Args:
            file_paths: List of file paths to add
        """
        logger.info(f"Adding {len(file_paths)} new documents")

        new_documents = []
        for file_path in file_paths:
            try:
                docs = self.document_loader.load_single_document(file_path)
                new_documents.extend(docs)
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")
                continue

        if new_documents:
            self.vector_store_service.add_documents(new_documents)
            logger.info(f"Successfully added {len(new_documents)} document chunks")
        else:
            logger.warning("No new documents were successfully loaded")

    def get_vector_store_info(self) -> dict:
        """
        Get information about the vector store.

        Returns:
            Dictionary with vector store information
        """
        try:
            return self.vector_store_service.get_collection_info()
        except Exception as e:
            logger.error(f"Error getting vector store info: {e}")
            return {"error": str(e)}

    def search_documents(self, query: str, k: int = 4) -> List[str]:
        """
        Search for relevant documents in the vector store.

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of document contents
        """
        try:
            results = self.vector_store_service.similarity_search(query, k=k)
            return [doc.page_content for doc in results]
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise