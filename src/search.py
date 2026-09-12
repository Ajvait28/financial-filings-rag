"""
Given a plain-text question, embeds it with the same model used for
the filing chunks, and retrieves the top-k most similar chunks from
Qdrant. This is the retrieval half of the RAG pipeline - no LLM
generation happens here, just nearest-neighbor vector search.

Connects to Qdrant Cloud if QDRANT_URL is set in .env, otherwise falls
back to a local Qdrant instance (same logic as load_qdrant.py).
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
from qdrant_client import QdrantClient

load_dotenv()
openai_client = OpenAI()
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

if QDRANT_URL:
    qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
else:
    QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
    qdrant_client = QdrantClient(host=QDRANT_HOST, port=6333)

COLLECTION_NAME = "aapl_filings"
EMBEDDING_MODEL = "text-embedding-3-small"

#Embeds a user's question using the same embedding model used for the filing chunks
#Query and chunks need to live in the same "embedding space" for similarity search to be meaningful.
def embed_query(query):
    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=[query]
    )
    return response.data[0].embedding

#Embeds the query and asks Qdrant for the top_k chunks whose vectors are closest to it (cosine similarity).
#Returns the raw Qdrant result objects, each carrying a similarity score and the chunk's payload (text, source filing, chunk id).
def search(query, top_k=5):
    query_vector = embed_query(query)

    results = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k
    )

    return results.points

#Quick manual test: run a sample question and print the top matches with their similarity scores, so retrieval quality can be eyeballed without involving the LLM generation step.
if __name__ == "__main__":
    question = "What was Apple's total net sales in the most recent quarter?"

    results = search(question)

    print(f"Question: {question}\n")
    for i, result in enumerate(results):
        print(f"--- Result {i+1} (score: {result.score:.3f}) ---")
        print(f"Source: {result.payload['source']}")
        print(result.payload['text'][:300])
        print()