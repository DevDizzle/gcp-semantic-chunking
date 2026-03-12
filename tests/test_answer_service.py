import os
import pytest
from src.api.answer import generate_answer
from src.schemas import RetrievalResult, ChunkRecord
from src.config import get_settings

def test_generate_answer_mock_mode(monkeypatch):
    monkeypatch.setenv("MOCK_GCP", "True")
    get_settings.cache_clear()
    
    dummy_chunk = ChunkRecord(
        document_id="doc1",
        parser_strategy="semantic",
        chunk_id="chunk1",
        text="BFS uses a queue.",
        citation_label="14 - BFS"
    )
    
    retrieval_results = [RetrievalResult(chunk=dummy_chunk, score=0.9)]
    
    res = generate_answer("How does BFS work?", retrieval_results, "semantic")
    
    assert res.query == "How does BFS work?"
    assert res.strategy == "semantic"
    assert res.answer == "Mock Answer"
    assert len(res.retrieved_chunks) == 1
