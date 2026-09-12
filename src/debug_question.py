from search import search

question = "Why did Apple's iPhone revenue increase in the third quarter of 2025 compared to the third quarter of 2024?"

results = search(question, top_k=10)

for i, r in enumerate(results):
    print(f"--- Chunk {i+1} (source: {r.payload['source']}, score: {r.score:.3f}) ---")
    print(r.payload['text'][:500])
    print()