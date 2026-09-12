from fastapi import FastAPI
from pydantic import BaseModel
from generate_answer import answer_question

app = FastAPI(title="Financial Filings RAG API")

class QuestionRequest(BaseModel):
    question: str
    top_k: int = 10

class AnswerResponse(BaseModel):
    answer: str
    sources: list[str]

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.post("/ask", response_model=AnswerResponse)
def ask(request: QuestionRequest):
    answer, chunks = answer_question(request.question, top_k=request.top_k)
    sources = list(set(chunk.payload["source"] for chunk in chunks))

    return AnswerResponse(answer=answer, sources=sources)