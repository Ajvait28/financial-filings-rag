import json
from collections import defaultdict

RESULTS_FILE = "data/eval_results.json"

with open(RESULTS_FILE, "r", encoding="utf-8") as f:
    results = json.load(f)

# overall metrics
total = len(results)
correct = sum(1 for r in results if r["answer_correct"] is True)
hallucinated = sum(1 for r in results if r["hallucinated"] is True)

retrieval_applicable = [r for r in results if r["retrieval_hit"] is not None]
retrieval_hits = sum(1 for r in retrieval_applicable if r["retrieval_hit"] is True)

print("=== Overall ===")
print(f"Accuracy: {correct}/{total} ({100*correct/total:.0f}%)")
print(f"Hallucination rate: {hallucinated}/{total} ({100*hallucinated/total:.0f}%)")
print(f"Retrieval hit rate: {retrieval_hits}/{len(retrieval_applicable)} ({100*retrieval_hits/len(retrieval_applicable):.0f}%)")

# per-category breakdown
by_category = defaultdict(list)
for r in results:
    by_category[r["category"]].append(r)

print("\n=== By category ===")
for category, items in by_category.items():
    n = len(items)
    cat_correct = sum(1 for r in items if r["answer_correct"] is True)
    cat_hallucinated = sum(1 for r in items if r["hallucinated"] is True)
    print(f"{category}: accuracy {cat_correct}/{n} ({100*cat_correct/n:.0f}%), hallucination {cat_hallucinated}/{n} ({100*cat_hallucinated/n:.0f}%)")