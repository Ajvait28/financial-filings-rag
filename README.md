# Financial Filings RAG

A retrieval-augmented generation (RAG) system that answers questions about Apple's SEC filings (10-Qs) using real filing text, grounded citations, and a measured evaluation pipeline.

**Live demo:** https://financial-filings-rag.onrender.com
*(Free-tier hosting — the service spins down after inactivity, so the first request after a period of idle time may take 30-60 seconds to respond.)*

Try it:
```bash
curl -X POST https://financial-filings-rag.onrender.com/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What was Apple'\''s total net sales in the most recent quarter?", "top_k": 10}'
```

## What it does
Given a question like *"Why did Apple's iPhone revenue increase in Q3 2025?"*, the system:
1. Embeds the question and retrieves the most relevant chunks from Apple's actual 10-Q filings
2. Passes those chunks to an LLM, constrained to answer only from the retrieved context
3. Returns a grounded answer with source citations

## Architecture
```
EDGAR filings → clean/chunk → OpenAI embeddings → Qdrant (vector search)
                                                          ↓
                                            user question → retrieve top-k → GPT-4o-mini → cited answer
```

- **Data:** last 4 quarterly 10-Q filings for Apple, pulled directly from SEC EDGAR
- **Chunking:** overlapping 600-token windows (100-token overlap) via `tiktoken`
- **Embeddings:** OpenAI `text-embedding-3-small`
- **Vector store:** Qdrant (Qdrant Cloud in production, local Docker for development)
- **Generation:** GPT-4o-mini, prompted to answer only from retrieved context and cite sources
- **Serving:** FastAPI, containerized with Docker, deployed on Render

## Evaluation
Built a 19-question eval set spanning 5 categories: simple fact lookup, cross-quarter comparison, "most recent" date-relative questions, narrative/qualitative reasoning, and intentionally unanswerable questions — each graded for correctness and hallucination against ground truth pulled directly from the filings.

**Key finding:** an initial run (`top_k=5`) scored 79% accuracy with an 11% hallucination rate, concentrated in narrative questions. Debugging showed the correct answer chunk was often ranked 6th-7th — just outside the retrieval window — losing out to several near-duplicate regional-breakdown paragraphs that shared surface-level wording (e.g., multiple filings all containing "net sales increased ... due to higher net sales of iPhone" across different regions). Increasing `top_k` from 5 to 10 resolved this:

| Metric | top_k=5 | top_k=10 |
|---|---|---|
| Accuracy | 79% | 100% |
| Hallucination rate | 11% | 0% |
| Retrieval hit rate | 94% | 100% |

*(19 questions is a small eval set — the meaningful result here is the diagnosed failure mode and the controlled fix, not the specific percentage.)*

## Running it locally

**Requirements:** Python 3.12, Docker, an OpenAI API key, a Qdrant instance (local Docker or Qdrant Cloud)

```bash
git clone https://github.com/<your-username>/financial-filings-rag.git
cd financial-filings-rag
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:
```
OPENAI_API_KEY=your_key_here
QDRANT_URL=your_qdrant_cloud_url        # omit for local Docker Qdrant
QDRANT_API_KEY=your_qdrant_cloud_key    # omit for local Docker Qdrant
```

Run the pipeline (fetch → clean → chunk → embed → load):
```bash
python src/fetch_filings.py
python src/clean_filings.py
python src/chunk_filings.py
python src/embed_chunks.py
python src/load_qdrant.py
```

Run the API:
```bash
cd src
uvicorn api:app --reload
```

Or run it in Docker:
```bash
docker build -t financial-filings-rag .
docker run -p 8000:8000 --env-file .env financial-filings-rag
```

Run the eval suite:
```bash
python src/run_eval.py
python src/eval_summary.py
```

## Tech stack
Python, OpenAI API (embeddings + generation), Qdrant, FastAPI, Docker, Render, BeautifulSoup, tiktoken

## Known limitations
- Vector search has no built-in sense of recency — a question about "the most recent quarter" retrieves semantically similar chunks regardless of filing date; the LLM generally compensates by reasoning over filing dates in the retrieved context, but this isn't guaranteed.
- Small corpus (4 filings, 1 company) and small eval set (19 questions) — built as a focused proof of concept, not a production-scale system.
- Free-tier hosting means the live demo has a cold-start delay after inactivity.