"""
Reads the graded eval_results.json (after manual grading via
review_eval.py + apply_grades.py) and computes summary metrics:
overall accuracy, hallucination rate, and retrieval hit rate, plus the
same breakdown per question category. This is the script that
produces the numbers used in the README's evaluation section.
"""

import json
from collections import defaultdict

RESULTS_FILE = "data/eval_results.json"

with open(RESULTS_FILE, "r", encoding="utf-8") as f:
    results = json.load(f)

#Overall metrics
total = len(results)
correct = sum(1 for r in results if r["answer_correct"] is True)
hallucinated = sum(1 for r in results if r["hallucinated"] is True)

#Retrieval hit rate excludes the intentionally unanswerable questions, since there's no expected source to check retrieval against for those
retrieval_applicable = [r for r in results if r["retrieval_hit"] is not None]
retrieval_hits = sum(1 for r in retrieval_applicable if r["retrieval_hit"] is True)

print("=== Overall ===")
print(f"Accuracy: {correct}/{total} ({100*correct/total:.0f}%)")
print(f"Hallucination rate: {hallucinated}/{total} ({100*hallucinated/total:.0f}%)")
print(f"Retrieval hit rate: {retrieval_hits}/{len(retrieval_applicable)} ({100*retrieval_hits/len(retrieval_applicable):.0f}%)")

#Breaking results down by category (rather than one flat number) is what actually makes this useful and it shows which question types the system struggles with, not just an overall score
by_category = defaultdict(list)
for r in results:
    by_category[r["category"]].append(r)

print("\n=== By category ===")
for category, items in by_category.items():
    n = len(items)
    cat_correct = sum(1 for r in items if r["answer_correct"] is True)
    cat_hallucinated = sum(1 for r in items if r["hallucinated"] is True)
    print(f"{category}: accuracy {cat_correct}/{n} ({100*cat_correct/n:.0f}%), hallucination {cat_hallucinated}/{n} ({100*cat_hallucinated/n:.0f}%)")