from pydantic import BaseModel
from typing import List
import os
from dotenv import load_dotenv
from pinecone import Pinecone
from chatbot.genai_client import client
from rag_system.pinecone_operations import initialize_pinecone_index, upsert_embedding, query_pinecone
from chatbot.constants import INDEX_NAME, EMBEDDING_DIMENSION, SIMILARITY_METRIC
# Load environment variables from .env.local file
load_dotenv(".env.local")

# Configuration
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# Initialize Pinecone connection
pc = Pinecone(api_key=PINECONE_API_KEY)
pc_serverless = {"cloud": "aws", "region": "us-east-1"}

class Metadata(BaseModel):
    text: str
    url: str
    name: str = "Unknown"
    date: str = "Unknown"


def generate_answer(context: str, query_str: str) -> str:
    """
    Generate an answer based on the provided context and query string.

    Args:
        context (str): Context for generating the answer.
        query_str (str): Query string.

    Returns:
        str: Generated answer text.
    """
    prompt = f"""Answer the question based on the context provided.
    Context: {context}
    Question: {query_str}"""
    ans = client.models.generate_content(
        model="gemini-2.0-flash-lite", contents=[prompt]
    )
    return ans.text


def handle_user_query(query: str) -> str:
    """
    Handle user queries by processing the query and retrieving relevant information.

    Args:
        query (str): User query.

    Returns:
        str: Response to the user query.
    """
    print(f"handle_user_query query: {query}")
    # Initialize Pinecone index
    index = initialize_pinecone_index(INDEX_NAME, EMBEDDING_DIMENSION, SIMILARITY_METRIC)
    # Query Pinecone
    query_results = query_pinecone(index, query)
    # Generate answer based on query results
    relevant_chunks = [match["metadata"]["text"] for match in query_results["matches"]]
    context = "\n\n".join(relevant_chunks)
    answer = generate_answer(context, query)
    print(f"handle_user_query answer: {answer}")
    return answer
