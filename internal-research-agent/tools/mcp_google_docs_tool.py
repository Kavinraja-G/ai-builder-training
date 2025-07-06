"""
MCP Google Docs Tool for integration with existing LangChain agent
Following the approach from: https://cobusgreyling.medium.com/using-langchain-with-model-context-protocol-mcp-e89b87ee3c4c
"""
import asyncio
import os
from pathlib import Path
from typing import Optional

from langchain.tools import BaseTool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools

from utils.logger import logger


class MCPGoogleDocsTool(BaseTool):
    """Tool for connecting to Google Docs MCP Server."""

    name: str = "google_docs_mcp"
    description: str = "Access Google Docs data from a specified folder. Use this tool to get insurance-related documents, policy information, claims procedures, and other company documents stored in Google Docs."
    mcp_server_path: Optional[str] = None
    _mcp_tools: Optional[list] = None

    def __init__(self, mcp_server_path: Optional[str] = None, **kwargs):
        """
        Initialize the MCP Google Docs tool.

        Args:
            mcp_server_path: Path to the MCP server script
        """
        if mcp_server_path is None:
            mcp_server_path = self._get_default_server_path()
        super().__init__(mcp_server_path=mcp_server_path, **kwargs)

    def _get_default_server_path(self) -> str:
        """Get the default path to the MCP server script."""
        project_root = Path(__file__).parent.parent
        return str(project_root / "mcp_server" / "google_docs_server.py")

    async def _load_mcp_tools(self):
        """Load tools from the MCP server."""
        try:
            print(f"Loading MCP tools from {self.mcp_server_path}")
            # Create server parameters for stdio connection
            server_params = StdioServerParameters(
                command="python",
                args=[self.mcp_server_path],
            )

            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize the connection
                    await session.initialize()

                    # Get tools from the MCP server
                    mcp_tools = await load_mcp_tools(session)
                    logger.info(f"Loaded {len(mcp_tools)} tools from MCP server")

                    return mcp_tools

        except Exception as e:
            logger.error(f"Error loading MCP tools: {e}")
            return []

    def _run(self, query: str) -> str:
        """
        Run the MCP Google Docs tool.

        Args:
            query: The query to process

        Returns:
            Tool output
        """
        try:
            # Run the async function in a new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                return loop.run_until_complete(self._run_async(query))
            finally:
                loop.close()

        except Exception as e:
            logger.error(f"MCP Google Docs Tool error: {e}")
            return f"Error: {str(e)}"

    async def _run_async(self, query: str) -> str:
        """
        Run the MCP Google Docs tool asynchronously.

        Args:
            query: The query to process

        Returns:
            Tool output
        """
        try:
            logger.info(f"Processing insurance query: {query}")

            # Create a fresh connection and execute the tool directly
            server_params = StdioServerParameters(
                command="python",
                args=[self.mcp_server_path],
            )

            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize the connection
                    await session.initialize()

                    # Call the tool directly
                    logger.info("Calling get_insurance_documents tool directly...")
                    result = await session.call_tool("get_insurance_documents", {})
                    logger.info("Tool execution completed successfully")
                    logger.info(f"Result content length: {len(result.content) if result.content else 0}")
                    logger.info(f"Result preview: {result.content[:200] if result.content else 'None'}...")
                    return result.content

        except Exception as e:
            logger.error(f"Error in async MCP tool execution: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return f"Error: {str(e)}"


def create_mcp_google_docs_tool(mcp_server_path: Optional[str] = None) -> MCPGoogleDocsTool:
    """
    Create an MCP Google Docs tool instance.

    Args:
        mcp_server_path: Path to the MCP server script

    Returns:
        Configured MCP Google Docs tool
    """
    return MCPGoogleDocsTool(mcp_server_path=mcp_server_path)