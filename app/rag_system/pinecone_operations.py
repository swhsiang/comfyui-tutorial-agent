import os
from pydantic import BaseModel
from rag_system.embedding import get_gemini_embedding
from pinecone import Pinecone, Index
from uuid import uuid4

# Configuration
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

class Metadata(BaseModel):
    text: str
    url: str
    name: str = "Unknown"
    date: str = "Unknown"

# Initialize Pinecone connection
pc = Pinecone(api_key=PINECONE_API_KEY)
pc_serverless = {"cloud": "aws", "region": "us-east-1"}


def initialize_pinecone_index(
    index_name: str, embedding_dimension: int, similarity_metric: str
) -> Index:
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


def upsert_embedding(index: Index, embedding: list, metadata: Metadata):
    """
    Upsert the embedding into the Pinecone index.

    Args:
        index (Index): Pinecone index.
        embedding (list): Embedding to upsert.
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


def query_pinecone(index: Index, query_str: str) -> list:
    """
    Query the Pinecone index with the given query string.

    Args:
        index (Index): Pinecone index.
        query_str (str): Query string.

    Returns:
        list: Query results.

    Example:
        >>> index = initialize_pinecone_index('example-index', 1536, 'cosine')
        >>> query_str = "how to use Comfy UI on my computer?"
        >>> results = query_pinecone(index, query_str)
        >>> print(results)

    Sample Output:
        {
            'matches': [
                {
                    'id': 'a',
                    'metadata': {
                        'text': 'Sure, here is the transcript for the episode:\n[00:00] John: Hello everyone, welcome to my channel.\n[00:02] John: Today, I will demonstrate how to use comfy UI on your computer with the fastest and completely free way.\n[00:08] John: No more error, no more incompatibility.\n[00:12] John: Google Colab.\n[00:16] John: Firstly, register a Google account.\n[00:19] John: If you do not have a Google account yet, you can register at the official website.\n[00:24] John: Secondly, log in to Google Cloud Drive.\n[00:28] John: You will have some free storage space on Google Cloud Drive, which is enough for beginners.\n[00:35] John: Thirdly, search comfy UI Collab and copy.\n[00:40] John: You need to use a search engine to search for Comfy UI Collab.\n[00:44] John: This will take you to a new collab notebook page.\n[00:50] John: Then, click copy to drive.\n[00:54] John: It will automatically open a new notebook named copy of comfy UI Collab.\n[01:00] John: Now this notebook is already in your Cloud Drive.\n[01:04] John: You can rename it whatever you want.\n[01:07] John: I renamed it here tutorial.\n[01:10] John: Fourthly, change the runtime.\n[01:12] John: You need to change the runtime if the default runtime is CPU.\n[01:16] John: Click the button and change it to T4 GPU.\n[01:21] John: Finally, run this notebook.\n[01:23] John: Don't forget to check use Google Drive and run the first cell.\n[01:28] John: Click connect Google Drive.\n[01:34] John: And Collab will connect to your own Google Cloud Drive.\n[01:35] John: It means you can use codes in this notebook to attach files in your Google Drive.\n[01:50] John: Well, it's done.\n[01:51] John: Now you can see comfy UI is already downloaded in your Google Drive.\n[02:00] John: If you want to download some checkpoint or Laura, use the second cell.\n[02:05] John: But here we skip this step.\n[02:09] John: Run comfy UI on the notebook.\n[02:14] John: Click the run button on the third cell and wait for comfy UI to finish configuring.\n[02:24] John: After the configuration is complete, you will see a URL in the execution window.\n[02:28] John: Click on it to enter the comfy UI interface.\n[02:31] John: Now you can see this is the comfy UI page, and a base checkpoint is already exist.\n[02:40] John: Enjoy your way to use comfy UI in cloud.\n[02:49] [END]',
                        'url': 'https://www.youtube.com/watch?v=prPqq8Wkw64'
                    },
                    'score': 0.82298,
                    'values': []
                }
            ],
            'namespace': '',
            'usage': {'read_units': 6}
        }
    """
    xq = get_gemini_embedding([query_str])[0]
    query_results = index.query(vector=xq.values, top_k=5, include_metadata=True)
    return query_results
 