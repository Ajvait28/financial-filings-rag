"""
Generates vector embeddings for every chunk in data/chunks/ using
OpenAI's embedding API, and saves the results (chunk text + metadata +
embedding vector together) to data/embeddings/, ready to be loaded into
Qdrant.

Requires OPENAI_API_KEY to be set in a .env file.
"""

import os
import json
import glob
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

CHUNKS_DIR = "data/chunks"
EMBEDDINGS_DIR = "data/embeddings"

EMBEDDING_MODEL = "text-embedding-3-small"

#Sends a batch of chunk texts to OpenAI's embedding API in a single call and returns one vector per text, in the same order.
#Batching like this is faster and cheaper than one API call per chunk.
def embed_batch(texts):
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts
    )
    return [item.embedding for item in response.data]

#Embeds every filing's chunks (one JSON file per filing) and writes out a matching file where each chunk record now also has its embedding vector attached, alongside its original text and metadata.
if __name__ == "__main__":
    os.makedirs(EMBEDDINGS_DIR, exist_ok=True)

    chunk_files = glob.glob(os.path.join(CHUNKS_DIR, "*.json"))

    for chunk_file in chunk_files:
        with open(chunk_file, "r", encoding="utf-8") as f:
            chunk_records = json.load(f)

        texts = [record["text"] for record in chunk_records]

        print(f"Embedding {len(texts)} chunks from {os.path.basename(chunk_file)}...")
        embeddings = embed_batch(texts)

        for record, embedding in zip(chunk_records, embeddings):
            record["embedding"] = embedding

        out_filename = os.path.basename(chunk_file).replace("_chunks.json", "_embedded.json")
        out_path = os.path.join(EMBEDDINGS_DIR, out_filename)

        #not pretty-printed (no indent) since each record now contains a 1536-number vector
        #formatting that nicely would bloat file size for no readability benefit
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(chunk_records, f)

        print(f"Saved to {out_path}")