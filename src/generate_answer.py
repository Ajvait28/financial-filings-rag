"""
The generation half of the RAG pipeline: retrieves relevant chunks via
search.py, builds a prompt that constrains the LLM to answer only from
that retrieved context, and calls the LLM to produce a grounded,
cited answer.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
from search import search

load_dotenv()
client = OpenAI()

GENERATION_MODEL = "gpt-4o-mini"

#Assembles the actual prompt sent to the LLM: each retrieved chunk is labeled with its source filing, then the instructions constrain the
#model to answer only from that context, decline if the context is insufficient, and cite sources.
#This is what keeps the system "grounded" instead of letting the LLM answer from its own training data or make things up.
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

#Full RAG call: retrieves top_k chunks for the question, builds the grounded prompt, and generates an answer.
#temperature=0 keeps output as deterministic/factual as possible, appropriate for a financial Q&A system rather than creative writing.
#Returns both the answer text and the retrieved chunks, since callers need the chunks too (e.g. to report which sources were used).
def answer_question(question, top_k=10):
    retrieved_chunks = search(question, top_k=top_k)
    prompt = build_prompt(question, retrieved_chunks)

    response = client.chat.completions.create(
        model=GENERATION_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content, retrieved_chunks

#Quick manual test: ask a sample question and print the generated answer alongside which sources were retrieved for it.
if __name__ == "__main__":
    question = "What was Apple's total net sales in the most recent quarter?"

    answer, chunks = answer_question(question)

    print(f"Question: {question}\n")
    print(f"Answer:\n{answer}\n")
    print("--- Sources used ---")
    for chunk in chunks:
        print(f"- {chunk.payload['source']} (score: {chunk.score:.3f})")