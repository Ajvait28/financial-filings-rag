"""
Splits cleaned filing text (from data/processed/) into overlapping,
token-sized chunks, and saves each filing's chunks as a JSON file in
data/chunks/, ready for embedding.

Chunking by tokens (rather than characters) matters because tokens are
what the embedding model actually processes - this keeps our chunk
sizes consistent with the model's real unit of measurement. Overlap
between consecutive chunks exists so a fact that happens to fall right
at a chunk boundary still appears whole in at least one chunk, instead
of being split and losing meaning in both.
"""

import os
import json
import tiktoken

PROCESSED_DIR = "data/processed"
CHUNKS_DIR = "data/chunks"

CHUNK_SIZE = 600
CHUNK_OVERLAP = 100

encoding = tiktoken.get_encoding("cl100k_base")

#Splits a block of text into overlapping token windows. Each new window starts (chunk_size - overlap) tokens after the previous one, so consecutive chunks share a stretch of text at their boundary.
def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    tokens = encoding.encode(text)
    chunks = []

    start = 0
    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)

        #Move forward, but overlap with previous chunk
        start += chunk_size - overlap

    return chunks

#Chunks every cleaned .txt filing in data/processed/, attaches source metadata to each chunk (so later steps can cite which filing an answer came from), and saves the results as one JSON file per filing.
if __name__ == "__main__":
    os.makedirs(CHUNKS_DIR, exist_ok=True)

    for filename in os.listdir(PROCESSED_DIR):
        if not filename.endswith(".txt"):
            continue

        filepath = os.path.join(PROCESSED_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = chunk_text(text)

        #store each chunk with a bit of metadata which will be necessary later to cite which filing/chunk an answer came from
        source_name = filename.replace(".txt", "")
        chunk_records = []
        for i, chunk in enumerate(chunks):
            chunk_records.append({
                "chunk_id": f"{source_name}_chunk{i}",
                "source": source_name,
                "text": chunk
            })

        out_path = os.path.join(CHUNKS_DIR, f"{source_name}_chunks.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(chunk_records, f, indent=2)

        print(f"{filename}: {len(chunks)} chunks -> {out_path}")