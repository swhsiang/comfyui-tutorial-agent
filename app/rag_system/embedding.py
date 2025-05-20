from google.genai import types
import os
from typing import List
from chatbot.genai_client import client
from chatbot.constants import EMBEDDING_MODEL_NAME


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