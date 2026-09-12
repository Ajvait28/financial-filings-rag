import json

RESULTS_FILE = "data/eval_results.json"

with open(RESULTS_FILE, "r", encoding="utf-8") as f:
    results = json.load(f)

for i, r in enumerate(results):
    print(f"\n{'='*80}")
    print(f"[{i+1}/{len(results)}] Category: {r['category']}")
    print(f"Question: {r['question']}")
    print(f"\nExpected answer: {r['expected_answer']}")
    print(f"Expected source(s): {r['expected_source']}")
    print(f"\nGenerated answer:\n{r['generated_answer']}")
    print(f"\nRetrieved sources: {r['retrieved_sources']}")
    print(f"Retrieval hit (automatic check): {r['retrieval_hit']}")