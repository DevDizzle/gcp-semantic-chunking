import os
from google import genai
from src.config import get_settings
from typing import List

def embed_texts(texts: List[str]) -> List[List[float]]:
    settings = get_settings()
    if settings.MOCK_GCP:
        # 768 is dimensionality for text-embedding-004
        return [[0.1] * 768 for _ in texts]

    client = genai.Client(vertexai=True, project=settings.GCP_PROJECT_ID, location=settings.GCP_LOCATION)
    response = client.models.embed_content(
        model=settings.VERTEX_TEXT_EMBED_MODEL,
        contents=texts
    )
    
    return [emb.values for emb in response.embeddings]
