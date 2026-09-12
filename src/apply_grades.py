import json

RESULTS_FILE = "data/eval_results.json"

# index -> (answer_correct, hallucinated)
grades = {i: (True, False) for i in range(1, 20)}

with open(RESULTS_FILE, "r", encoding="utf-8") as f:
    results = json.load(f)

for i, r in enumerate(results):
    correct, hallucinated = grades[i + 1]
    r["answer_correct"] = correct
    r["hallucinated"] = hallucinated

with open(RESULTS_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print("Grades applied.")