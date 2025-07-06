#!/usr/bin/env python3
"""
Google Docs MCP Server using FastMCP
Following the approach from: https://cobusgreyling.medium.com/using-langchain-with-model-context-protocol-mcp-e89b87ee3c4c
"""
import os
from pathlib import Path
from typing import List, Dict, Any

from mcp.server.fastmcp import FastMCP
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Add the project root to Python path
project_root = Path(__file__).parent.parent
import sys
sys.path.insert(0, str(project_root))

from utils.logger import logger


class GoogleDocsMCPServer:
    """Google Docs MCP Server using FastMCP."""

    def __init__(self, credentials_path: str = None, folder_id: str = None):
        """
        Initialize the Google Docs MCP server.

        Args:
            credentials_path: Path to Google service account credentials JSON file
            folder_id: Google Drive folder ID containing documents
        """
        self.credentials_path = credentials_path or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.folder_id = folder_id or os.getenv("GOOGLE_FOLDER_ID")
        self.drive_service = None
        self.docs_service = None

        self._initialize_services()
        logger.info("Google Docs MCP Server initialized")

    def _initialize_services(self):
        """Initialize Google Drive and Docs API services."""
        try:
            logger.info(f"Initializing Google services with credentials: {self.credentials_path}")

            if not self.credentials_path:
                logger.error("Credentials path not set")
                return

            if not Path(self.credentials_path).exists():
                logger.error(f"Credentials file not found at: {self.credentials_path}")
                return

            logger.info("Loading service account credentials...")
            # Load credentials from service account file
            credentials = Credentials.from_service_account_file(
                self.credentials_path,
                scopes=[
                    'https://www.googleapis.com/auth/drive.readonly',
                    'https://www.googleapis.com/auth/documents.readonly'
                ]
            )
            logger.info("Credentials loaded successfully")

            # Build the Google Drive and Docs services
            logger.info("Building Google Drive service...")
            self.drive_service = build('drive', 'v3', credentials=credentials)
            logger.info("Building Google Docs service...")
            self.docs_service = build('docs', 'v1', credentials=credentials)
            logger.info("Google Drive and Docs API services initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Google services: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            self.drive_service = None
            self.docs_service = None

    def get_documents_in_folder(self) -> List[Dict[str, str]]:
        """Get all Google Docs in the specified folder."""
        logger.info(f"Checking folder ID: {self.folder_id}")
        logger.info(f"Drive service available: {self.drive_service is not None}")

        if not self.drive_service:
            logger.error("Drive service not available")
            return []

        if not self.folder_id:
            logger.error("Folder ID not set")
            return []

        try:
            query = f"'{self.folder_id}' in parents and mimeType='application/vnd.google-apps.document'"
            logger.info(f"Executing query: {query}")

            results = self.drive_service.files().list(
                q=query,
                fields="files(id,name,description,createdTime,modifiedTime)",
                orderBy="modifiedTime desc"
            ).execute()

            documents = results.get('files', [])
            logger.info(f"Found {len(documents)} documents in folder")

            if documents:
                for doc in documents:
                    logger.info(f"Document: {doc.get('name', 'Unknown')} (ID: {doc.get('id', 'Unknown')})")

            return [
                {
                    "id": doc["id"],
                    "name": doc["name"],
                    "description": doc.get("description", ""),
                    "created": doc.get("createdTime", ""),
                    "modified": doc.get("modifiedTime", "")
                }
                for doc in documents
            ]

        except Exception as e:
            logger.error(f"Error getting documents from folder: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return []

    def get_document_content(self, doc_id: str) -> str:
        """Get content from a Google Doc."""
        if not self.docs_service:
            return "Google Docs API not available"

        try:
            document = self.docs_service.documents().get(documentId=doc_id).execute()

            content = document.get('body', {}).get('content', [])
            text_content = []

            for element in content:
                if 'paragraph' in element:
                    for para_element in element['paragraph']['elements']:
                        if 'textRun' in para_element:
                            text_content.append(para_element['textRun']['content'])

            return ''.join(text_content).strip()

        except HttpError as e:
            logger.error(f"Google Docs API error: {e}")
            return f"Error accessing document: {str(e)}"
        except Exception as e:
            logger.error(f"Error retrieving Google Doc content: {e}")
            return f"Error: {str(e)}"


def create_mcp_server():
    """Create and configure the MCP server."""
    mcp = FastMCP("Google Docs")

    # Initialize the Google Docs server
    docs_server = GoogleDocsMCPServer()

    @mcp.tool()
    def get_insurance_documents() -> str:
        """
        Get all insurance documents from the Google Drive folder.

        Returns:
            All insurance documents with their content
        """
        try:
            logger.info("get_insurance_documents tool called")
            documents = docs_server.get_documents_in_folder()
            logger.info(f"Found {len(documents) if documents else 0} documents")

            if not documents:
                logger.info("No documents found, returning message")
                return "No insurance documents found in the specified folder."

            # Get content for each document
            docs_with_content = []
            for i, doc in enumerate(documents):
                logger.info(f"Processing document {i+1}/{len(documents)}: {doc.get('name', 'Unknown')}")
                content = docs_server.get_document_content(doc["id"])
                docs_with_content.append({
                    **doc,
                    "content": content
                })

            import json
            result = json.dumps(docs_with_content, indent=2)
            logger.info(f"Successfully processed {len(docs_with_content)} documents")
            return result

        except Exception as e:
            logger.error(f"Error getting insurance documents: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return f"Error: {str(e)}"

    @mcp.tool()
    def list_documents() -> str:
        """
        List all available documents in the folder.

        Returns:
            List of document names and metadata
        """
        try:
            documents = docs_server.get_documents_in_folder()

            if not documents:
                return "No documents found in the specified folder."

            result = "Available Documents:\n\n"
            for i, doc in enumerate(documents, 1):
                result += f"{i}. {doc['name']}\n"
                if doc.get('description'):
                    result += f"   Description: {doc['description']}\n"
                result += f"   Modified: {doc.get('modified', 'Unknown')}\n\n"

            logger.info(f"Available Documents: {len(documents)}")
            return result

        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    def get_document_by_name(document_name: str) -> str:
        """
        Get content of a specific document by name.

        Args:
            document_name: Name of the document to retrieve

        Returns:
            Document content
        """
        try:
            documents = docs_server.get_documents_in_folder()

            # Find document by name (case-insensitive)
            target_doc = None
            for doc in documents:
                if doc["name"].lower() == document_name.lower():
                    target_doc = doc
                    break

            if not target_doc:
                available_names = [doc["name"] for doc in documents]
                return f"Document '{document_name}' not found. Available documents: {', '.join(available_names)}"

            content = docs_server.get_document_content(target_doc["id"])

            return f"Document: {target_doc['name']}\n\n{content}"

        except Exception as e:
            logger.error(f"Error getting document by name: {e}")
            return f"Error retrieving document: {str(e)}"

    return mcp


if __name__ == "__main__":
    # Create and run the MCP server
    mcp = create_mcp_server()
    mcp.run(transport="stdio")