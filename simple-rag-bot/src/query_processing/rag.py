from google import genai
from src.conversation.manager import format_history_for_prompt, add_message


def contextualize_query(query: str, conversation_history: str, client: genai):
    """Convert follow-up questions into standalone queries using Gemini."""
    contextualize_prompt = """Given a chat history and the latest user question
    which might reference context in the chat history, formulate a standalone
    question which can be understood without the chat history. Do NOT answer
    the question, just reformulate it if needed and otherwise return it as is."""

    full_prompt = (
        f"{contextualize_prompt}\n\n"
        f"Chat history:\n{conversation_history}\n\n"
        f"Question:\n{query}"
    )

    try:
        completion = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=full_prompt
        )
        return completion.text
    except Exception as e:
        print(f"Error contextualizing query: {str(e)}")
        return query  # Fallback to original query


def get_prompt(context, conversation_history, query):
    """Generate prompt for the language model with context and conversation history."""
    prompt = f"""Based on the following context and conversation history, please provide a relevant and contextual response.
    If the answer cannot be derived from the context, only use the conversation history or say "I cannot answer this based on the provided information."

    Context from documents:
    {context}

    Previous conversation:
    {conversation_history}

    Human: {query}

    Assistant:"""
    return prompt


def generate_response(query: str, context: str, conversation_history: str = "", client: genai = None):
    """Generate a response using Gemini with context and conversation history."""
    prompt = get_prompt(context, conversation_history, query)

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )

    return response.text


def conversational_rag_query(
    collection,
    query: str,
    session_id: str,
    client: genai,
    n_chunks: int = 3
):
    """Perform RAG query with conversation history and return response with sources."""
    conversation_history = format_history_for_prompt(session_id)

    # Handle follow up questions
    query = contextualize_query(query, conversation_history, client)
    print("Contextualized Query:", query)

    # Get relevant chunks
    from src.database.chroma_ops import semantic_search, get_context_with_sources
    context, sources = get_context_with_sources(
        semantic_search(collection, query, n_chunks)
    )

    response = generate_response(query, context, conversation_history, client)

    # Add to conversation history
    add_message(session_id, "user", query)
    add_message(session_id, "assistant", response)

    return response, sources