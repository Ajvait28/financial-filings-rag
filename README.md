# Financial Filings RAG

A retrieval-augmented generation (RAG) system that answers questions about Apple's SEC filings (10-Qs) using real filing text, grounded citations, and a measured evaluation pipeline.

## What it does
Given a question like "Why did Apple's iPhone revenue increase in Q3 2025?", the system:
1. Embeds the question and retrieves the most relevant chunks from Apple's actual 10-Q filings
2. Passes those chunks to an LLM, constrained to answer only from the retrieved context
3. Returns a grounded answer with source citations

## Pipeline
1. **Fetch** — pulls Apple's last 4 10-Q filings directly from SEC EDGAR
2. **Clean** — strips HTML/XBRL metadata into plain text
3. **Chunk** — splits filings into overlapping 600-token windows
4. **Embed** — OpenAI `text-embedding-3-small`, stored in a local Qdrant vector database
5. **Retrieve + Generate** — top-k similarity search, then GPT-4o-mini generates a cited answer

## Evaluation
Built a 19-question eval set across 5 categories (simple fact lookup, cross-quarter comparison, "most recent" date-relative questions, narrative/qualitative reasoning, and intentionally unanswerable questions), each graded for correctness and hallucination.

**Key finding:** an initial run (`top_k=5`) scored 79% accuracy with an 11% hallucination rate, concentrated in narrative questions. Debugging showed the correct answer chunk was often ranked 6th-7th, just outside the retrieval window, losing out to several near-duplicate regional-breakdown paragraphs that shared surface-level wording. Increasing `top_k` to 10 resolved this:

| Metric | top_k=5 | top_k=10 |
|---|---|---|
| Accuracy | 79% | 100% |
| Hallucination rate | 11% | 0% |
| Retrieval hit rate | 94% | 100% |

(Note: 19 questions is a small eval set — the meaningful result here is the diagnosed failure mode and the controlled fix, not the specific percentage.)

## Tech stack
Python, OpenAI API (embeddings + generation), Qdrant (Docker), BeautifulSoup, tiktoken

## Setup
[fill in once get to serving/deployment - venv, .env, docker run command, etc.]

## Status
Core RAG pipeline + eval harness complete. Next: serving via FastAPI + Docker, basic UI.