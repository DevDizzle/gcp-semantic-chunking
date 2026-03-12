import os
import pytest
from src.api.retrieve import retrieve_chunks

def test_retrieve_mock_mode(monkeypatch):
    # Force Mock GCP behavior
    monkeypatch.setenv("MOCK_GCP", "True")
    
    # In Mock mode, retrieval should just return an empty list 
    # (unless we explicitly mocked the db). Currently mocked as returning []
    results = retrieve_chunks("What is BFS?", "semantic")
    assert isinstance(results, list)
    assert len(results) == 0
