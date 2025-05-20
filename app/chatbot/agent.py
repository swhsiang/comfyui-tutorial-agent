from google.genai import types
from google import genai
from pydantic import BaseModel
from typing import List
import os
from dotenv import load_dotenv
from pinecone import Pinecone
from pinecone.data.index import Index
from uuid import uuid4
# Load environment variables from .env.local file
load_dotenv(".env.local")

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
EMBEDDING_MODEL_NAME = "models/gemini-embedding-exp-03-07"
INDEX_NAME = "yt-comfy-ui-tutorial"
INDEX_NAMESPACE = ""
EMBEDDING_DIMENSION = 1536
SIMILARITY_METRIC = "cosine"

# Initialize Google Generative AI client
client = genai.Client(api_key=GEMINI_API_KEY)

# Initialize Pinecone connection
pc = Pinecone(api_key=PINECONE_API_KEY)
pc_serverless = {"cloud": "aws", "region": "us-east-1"}

class Metadata(BaseModel):
    text: str
    url: str
    name: str = "Unknown"
    date: str = "Unknown"


def get_gemini_embedding(texts: List[str]) -> List:
    """
    Get embeddings for the given texts using the Gemini embedding model.

    Args:
        texts (List[str]): List of texts to embed.

    Returns:
        List: List of embeddings.
    """
    embedding_resp = client.models.embed_content(
        model=EMBEDDING_MODEL_NAME,
        contents=texts,
        config=types.EmbedContentConfig(
            task_type="retrieval_document",
            title="YouTube Transcript Chunk",
            output_dimensionality=1536,
        ),
    )
    return embedding_resp.embeddings


def initialize_pinecone_index(index_name: str, embedding_dimension: int, similarity_metric: str) -> Index:
    """
    Initialize the Pinecone index if it does not already exist.

    Args:
        index_name (str): Name of the Pinecone index.
        embedding_dimension (int): Dimension of the embeddings.
        similarity_metric (str): Similarity metric to use.

    Returns:
        Index: Initialized Pinecone index.
    """
    indexes = pc.list_indexes()
    index_names = [index["name"] for index in indexes]

    if index_name not in index_names:
        pc.create_index(
            name=index_name,
            dimension=embedding_dimension,
            metric=similarity_metric,
            spec=pc_serverless,
            vector_type="dense",
        )
    return pc.Index(index_name)


def upsert_embedding(index: Index, embedding: List, metadata: Metadata):
    """
    Upsert the embedding into the Pinecone index.

    Args:
        index (Index): Pinecone index.
        embedding (List): Embedding to upsert.
        metadata (Metadata): Metadata associated with the embedding.
    """
    embedding_to_upsert = [
        (
            str(uuid4()),  # You might want to use a unique ID here
            embedding[0].values,
            metadata.model_dump(),
        )
    ]
    index.upsert(vectors=embedding_to_upsert)


def query_pinecone(index: Index, query_str: str) -> List:
    """
    Query the Pinecone index with the given query string.

    Args:
        index (Index): Pinecone index.
        query_str (str): Query string.

    Returns:
        List: Query results.
    """
    xq = get_gemini_embedding([query_str])[0]
    query_results = index.query(vector=xq.values, top_k=5, include_metadata=True)
    return query_results


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