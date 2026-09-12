import os
import json
import tiktoken

PROCESSED_DIR = "data/processed"
CHUNKS_DIR = "data/chunks"

CHUNK_SIZE = 600      # tokens per chunk
CHUNK_OVERLAP = 100    # tokens of overlap between consecutive chunks

encoding = tiktoken.get_encoding("cl100k_base")

def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    tokens = encoding.encode(text)
    chunks = []

    start = 0
    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)

        start += chunk_size - overlap  # move forward, but overlap with previous chunk

    return chunks

if __name__ == "__main__":
    os.makedirs(CHUNKS_DIR, exist_ok=True)

    for filename in os.listdir(PROCESSED_DIR):
        if not filename.endswith(".txt"):
            continue

        filepath = os.path.join(PROCESSED_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = chunk_text(text)

        # store each chunk with a bit of metadata - we'll need this later
        # to cite which filing/chunk an answer came from
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