import os
import chromadb
from chromadb.utils import embedding_functions
from google import genai
import argparse
from src.database.chroma_ops import process_and_add_documents
from src.conversation.manager import create_session
from src.query_processing.rag import conversational_rag_query


def setup_database():
    """Initialize and setup the database"""
    db_client = chromadb.PersistentClient(path="chroma_db")
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    collection = db_client.get_or_create_collection(
        name="documents_collection",
        embedding_function=sentence_transformer_ef
    )
    return collection


def main():
    parser = argparse.ArgumentParser(description='Simple RAG Bot CLI')
    parser.add_argument('--docs', type=str, default='./docs',
                      help='Path to documents folder (default: ./docs)')
    parser.add_argument('--query', type=str,
                      help='Query to process')
    parser.add_argument('--interactive', action='store_true',
                      help='Run in interactive mode')

    args = parser.parse_args()

    # Check for API key
    if not os.environ.get("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable is not set")
        print("Please set it using: export GEMINI_API_KEY='your-api-key'")
        return

    # Initialize components
    collection = setup_database()
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    session_id = create_session()

    # Process documents
    print(f"Processing documents from {args.docs}...")
    process_and_add_documents(collection, args.docs)

    if args.interactive:
        print("\nEntering interactive mode. Type 'exit' to quit.")
        while True:
            query = input("\nEnter your question: ")
            if query.lower() == 'exit':
                break

            response, sources = conversational_rag_query(
                collection,
                query,
                session_id,
                client
            )
            print("\nResponse:", response)
            print("\nSources:", sources)

    elif args.query:
        response, sources = conversational_rag_query(
            collection,
            args.query,
            session_id,
            client
        )
        print("\nResponse:", response)
        print("\nSources:", sources)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
