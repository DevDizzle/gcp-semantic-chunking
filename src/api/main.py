from fastapi import FastAPI
from typing import Dict
from src.schemas import AnswerResult, QueryRequest, CompareRequest
from src.api.retrieve import retrieve_chunks
from src.api.answer import generate_answer
from src.config import get_settings

app = FastAPI(title="Semantic Chunking RAG API")

@app.on_event("startup")
def verify_settings():
    # Will fail fast if missing
    get_settings()

@app.post("/query", response_model=AnswerResult)
def ask_question(req: QueryRequest):
    """
    Endpoint to ask a question and get a grounded answer based on the selected strategy.
    """
    chunks = retrieve_chunks(req.query, strategy=req.strategy, top_k=req.top_k)
    answer = generate_answer(req.query, chunks, strategy=req.strategy)
    return answer

@app.post("/compare")
def compare_strategies(req: CompareRequest) -> Dict[str, AnswerResult]:
    """
    Endpoint to compare naive vs semantic chunking for the same query.
    """
    naive_chunks = retrieve_chunks(req.query, strategy="naive", top_k=req.top_k)
    naive_answer = generate_answer(req.query, naive_chunks, strategy="naive")
    
    semantic_chunks = retrieve_chunks(req.query, strategy="semantic", top_k=req.top_k)
    semantic_answer = generate_answer(req.query, semantic_chunks, strategy="semantic")
    
    return {
        "naive": naive_answer,
        "semantic": semantic_answer
    }
