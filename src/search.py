import os
from dotenv import load_dotenv
from openai import OpenAI
from qdrant_client import QdrantClient

load_dotenv()
openai_client = OpenAI()
qdrant_client = QdrantClient(host="localhost", port=6333)

COLLECTION_NAME = "aapl_filings"
EMBEDDING_MODEL = "text-embedding-3-small"

def embed_query(query):
    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=[query]
    )
    return response.data[0].embedding

def search(query, top_k=5):
    query_vector = embed_query(query)

    results = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k
    )

    return results.points

if __name__ == "__main__":
    question = "What was Apple's total net sales in the most recent quarter?"

    results = search(question)

    print(f"Question: {question}\n")
    for i, result in enumerate(results):
        print(f"--- Result {i+1} (score: {result.score:.3f}) ---")
        print(f"Source: {result.payload['source']}")
        print(result.payload['text'][:300])
        print()