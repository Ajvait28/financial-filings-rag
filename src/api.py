"""
FastAPI serving layer for the RAG pipeline. Exposes the whole
fetch->chunk->embed->retrieve->generate pipeline (already built and
loaded into Qdrant) as a simple HTTP API with two endpoints: a health
check and a question-answering endpoint.

Run locally with: uvicorn api:app --reload (from inside src/)
Or via Docker - see Dockerfile in the project root.
"""

from fastapi import FastAPI
from pydantic import BaseModel
from generate_answer import answer_question

app = FastAPI(title="Financial Filings RAG API")

#Pydantic models define the expected shape of requests/responses
#FastAPI uses these to auto-validate incoming JSON and to generate the interactive docs available at /docs.
class QuestionRequest(BaseModel):
    question: str
    top_k: int = 10

class AnswerResponse(BaseModel):
    answer: str
    sources: list[str]

#Simple liveness check - lets anything confirm the service is up without running the full RAG pipeline.
#Only responds to GET requests, so visiting this URL directly in a browser works as expected.
@app.get("/")
def health_check():
    return {"status": "ok"}

#The real endpoint: takes a question (and optional top_k override), runs it through the existing answer_question() pipeline unchanged, and returns a clean JSON response.
#Note this only accepts POST requests with a JSON body and visiting it directly in a browser (which always sends GET) won't work; use curl, the /docs page, or a proper HTTP client to call it.
@app.post("/ask", response_model=AnswerResponse)
def ask(request: QuestionRequest):
    answer, chunks = answer_question(request.question, top_k=request.top_k)
    sources = list(set(chunk.payload["source"] for chunk in chunks))  # dedupe repeated sources

    return AnswerResponse(answer=answer, sources=sources)