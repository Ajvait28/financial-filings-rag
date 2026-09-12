"""
Loads all embedded chunks (from data/embeddings/) into Qdrant, creating
a fresh collection each run. Connects to Qdrant Cloud if QDRANT_URL is
set in .env, otherwise falls back to a local Qdrant instance (either
run directly on localhost, or reachable via QDRANT_HOST when this
script runs inside Docker).
"""

import os
import json
import glob
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from dotenv import load_dotenv
load_dotenv()

EMBEDDINGS_DIR = "data/embeddings"
COLLECTION_NAME = "aapl_filings"
VECTOR_SIZE = 1536

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

#QDRANT_URL being set means we're pointed at Qdrant Cloud (production).
#Otherwise, fall back to a local Qdrant instance - QDRANT_HOST lets this same code work both when running directly on this machine ("localhost") and when running inside Docker, where "localhost" would incorrectly refer to the container itself instead of the host.
if QDRANT_URL:
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
else:
    QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
    client = QdrantClient(host=QDRANT_HOST, port=6333)

#Wipes and recreates the collection from scratch.
#Fine for our use case since we always reload the full corpus from source files rather than incrementally updating.
def create_collection():
    if client.collection_exists(COLLECTION_NAME):
        client.delete_collection(COLLECTION_NAME)

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )

#Reads every filing's embedded chunks and converts them into Qdrant PointStructs where each needs a unique integer id, its vector, and a payload
def load_all_chunks():
    embedding_files = glob.glob(os.path.join(EMBEDDINGS_DIR, "*.json"))

    points = []
    point_id = 0
    for filepath in embedding_files:
        with open(filepath, "r", encoding="utf-8") as f:
            records = json.load(f)

        for record in records:
            points.append(
                PointStruct(
                    id=point_id,
                    vector=record["embedding"],
                    payload={
                        "chunk_id": record["chunk_id"],
                        "source": record["source"],
                        "text": record["text"],
                    },
                )
            )
            point_id += 1

    return points

if __name__ == "__main__":
    print("Creating collection...")
    create_collection()

    print("Loading chunks...")
    points = load_all_chunks()

    print(f"Uploading {len(points)} points to Qdrant...")
    client.upsert(collection_name=COLLECTION_NAME, points=points)

    print("Done.")