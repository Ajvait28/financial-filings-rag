import os
import json
import glob
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

EMBEDDINGS_DIR = "data/embeddings"
COLLECTION_NAME = "aapl_filings"
VECTOR_SIZE = 1536  # matches text-embedding-3-small's output size

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
client = QdrantClient(host=QDRANT_HOST, port=6333)

def create_collection():
    # wipes and recreates the collection - fine for now since we're
    # just building the pipeline, not running this against a live system
    if client.collection_exists(COLLECTION_NAME):
        client.delete_collection(COLLECTION_NAME)

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )

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