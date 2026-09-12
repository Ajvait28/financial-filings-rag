import os
from dotenv import load_dotenv
from openai import OpenAI
from search import search

load_dotenv()
client = OpenAI()

GENERATION_MODEL = "gpt-4o-mini"

def build_prompt(question, retrieved_chunks):
    context_blocks = []
    for chunk in retrieved_chunks:
        source = chunk.payload["source"]
        text = chunk.payload["text"]
        context_blocks.append(f"[Source: {source}]\n{text}")

    context = "\n\n---\n\n".join(context_blocks)

    prompt = f"""You are a financial analyst assistant. Answer the question using ONLY the context provided below, which comes from Apple's SEC filings.

If the context does not contain enough information to answer the question, say so clearly instead of guessing.

When you use a specific fact or number, cite which source filing it came from (e.g., "according to aapl_10q_2026-07-31").

Context:
{context}

Question: {question}

Answer:"""

    return prompt

def answer_question(question, top_k=10):
    retrieved_chunks = search(question, top_k=top_k)
    prompt = build_prompt(question, retrieved_chunks)

    response = client.chat.completions.create(
        model=GENERATION_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content, retrieved_chunks

if __name__ == "__main__":
    question = "What was Apple's total net sales in the most recent quarter?"

    answer, chunks = answer_question(question)

    print(f"Question: {question}\n")
    print(f"Answer:\n{answer}\n")
    print("--- Sources used ---")
    for chunk in chunks:
        print(f"- {chunk.payload['source']} (score: {chunk.score:.3f})")