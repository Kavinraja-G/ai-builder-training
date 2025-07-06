"""
MCP Server package for Insurance Google Docs integration.
"""

from .insurance_docs_server import InsuranceDocsMCPServer, MCPServerProtocol

__version__ = "1.0.0"
__all__ = ["InsuranceDocsMCPServer", "MCPServerProtocol"]