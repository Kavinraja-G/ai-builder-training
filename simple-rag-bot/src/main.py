import os
import chromadb
from chromadb.utils import embedding_functions
from google import genai

from src.database.chroma_ops import process_and_add_documents
from src.conversation.manager import create_session
from src.query_processing.rag import conversational_rag_query

def main():
    # Initialize ChromaDB client with persistence
    db_client = chromadb.PersistentClient(path="chroma_db")

    # Configure sentence transformer embeddings
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    # Create or get existing collection
    collection = db_client.get_or_create_collection(
        name="documents_collection",
        embedding_function=sentence_transformer_ef
    )

    # Process and add documents from a folder
    folder_path = "./docs"
    process_and_add_documents(collection, folder_path)

    # Create a new conversation session
    session_id = create_session()

    # Initialize Gemini client
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    # Example query
    query = "Kavin has experience in ArgoCD?"
    response, sources = conversational_rag_query(
        collection,
        query,
        session_id,
        client
    )
    print(response)

if __name__ == "__main__":
    main()