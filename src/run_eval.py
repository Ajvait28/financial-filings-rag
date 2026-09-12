import json
from generate_answer import answer_question

EVAL_FILE = "data/eval_questions.json"
RESULTS_FILE = "data/eval_results.json"

def retrieval_hit(expected_source, retrieved_chunks):
    if expected_source is None:
        return None  # not applicable for unanswerable questions

    # expected_source can be a single source or a comma-separated list
    expected_sources = [s.strip() for s in expected_source.split(",")]
    retrieved_sources = set(chunk.payload["source"] for chunk in retrieved_chunks)

    hits = [src for src in expected_sources if src in retrieved_sources]
    return len(hits) == len(expected_sources)  # True only if ALL expected sources were retrieved

if __name__ == "__main__":
    with open(EVAL_FILE, "r", encoding="utf-8") as f:
        eval_questions = json.load(f)

    results = []

    for i, item in enumerate(eval_questions):
        question = item["question"]
        expected_answer = item["expected_answer"]
        expected_source = item["expected_source"]
        category = item["category"]

        print(f"[{i+1}/{len(eval_questions)}] {question}")

        answer, retrieved_chunks = answer_question(question)
        hit = retrieval_hit(expected_source, retrieved_chunks)

        results.append({
            "question": question,
            "expected_answer": expected_answer,
            "expected_source": expected_source,
            "category": category,
            "generated_answer": answer,
            "retrieved_sources": [chunk.payload["source"] for chunk in retrieved_chunks],
            "retrieval_hit": hit,
            "answer_correct": None,      # to be filled in manually
            "hallucinated": None         # to be filled in manually
        })

    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\nDone. Results saved to {RESULTS_FILE}")
    print("Next: open the file and fill in 'answer_correct' (true/false) and 'hallucinated' (true/false) for each question.")