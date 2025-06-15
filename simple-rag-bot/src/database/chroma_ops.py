import os
from src.document_processing.reader import read_document
from src.text_processing.chunker import split_text


def add_to_collection(collection, ids, texts, metadatas):
    """Add documents to collection in batches of 100."""
    if not texts:
        return

    batch_size = 100
    for i in range(0, len(texts), batch_size):
        end_idx = min(i + batch_size, len(texts))
        collection.add(
            documents=texts[i:end_idx],
            metadatas=metadatas[i:end_idx],
            ids=ids[i:end_idx]
        )


def process_document(file_path: str):
    """Process a single document and prepare it for ChromaDB. Returns document chunks with metadata."""
    try:
        # Read the document
        content = read_document(file_path)

        # Split into chunks
        chunks = split_text(content)

        # Prepare metadata
        file_name = os.path.basename(file_path)
        metadatas = [{"source": file_name, "chunk": i} for i in range(len(chunks))]
        ids = [f"{file_name}_chunk_{i}" for i in range(len(chunks))]

        return ids, chunks, metadatas
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return [], [], []


def process_and_add_documents(collection, folder_path: str):
    """Process all documents in a folder and add them to the ChromaDB collection."""
    files = [os.path.join(folder_path, file)
             for file in os.listdir(folder_path)
             if os.path.isfile(os.path.join(folder_path, file))]

    for file_path in files:
        print(f"Processing {os.path.basename(file_path)}...")
        ids, texts, metadatas = process_document(file_path)
        add_to_collection(collection, ids, texts, metadatas)
        print(f"Added {len(texts)} chunks to collection")


def semantic_search(collection, query: str, n_results: int = 2):
    """Perform semantic search on the collection and return the top n_results matches."""
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    return results


def get_context_with_sources(results):
    """Extract context and source information from search results. Returns combined text and source list."""
    # Combine document chunks into a single context
    context = "\n\n".join(results['documents'][0])

    # Format sources with metadata
    sources = [
        f"{meta['source']} (chunk {meta['chunk']})"
        for meta in results['metadatas'][0]
    ]

    return context, sources

## For learning purpose:
# def print_search_results(results):
#     """Print formatted search results with source information and relevance scores."""
#     print("\nSearch Results:\n" + "-" * 50)

#     for i in range(len(results['documents'][0])):
#         doc = results['documents'][0][i]
#         meta = results['metadatas'][0][i]
#         distance = results['distances'][0][i]

#         print(f"\nResult {i + 1}")
#         print(f"Source: {meta['source']}, Chunk {meta['chunk']}")
#         print(f"Distance: {distance}")
#         print(f"Content: {doc}\n")