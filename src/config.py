import os
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    GCP_PROJECT_ID: str = ""
    GCP_LOCATION: str = "us-central1"
    
    FIRESTORE_DATABASE: str = "(default)"
    FIRESTORE_COLLECTION_CHUNKS: str = "chunk_records"
    FIRESTORE_COLLECTION_DOCUMENTS: str = "document_records"
    
    VERTEX_TEXT_EMBED_MODEL: str = "text-embedding-004"
    VERTEX_GEMINI_MODEL: str = "gemini-3.1-flash-lite-preview"
    VERTEX_GEMINI_LOCATION: str = "global"
    
    VERTEX_VECTOR_ENDPOINT_ID: str = ""
    VERTEX_VECTOR_INDEX_ID_NAIVE: str = ""
    VERTEX_VECTOR_INDEX_ID_SEMANTIC: str = ""
    VERTEX_VECTOR_DEPLOYED_INDEX_ID_NAIVE: str = ""
    VERTEX_VECTOR_DEPLOYED_INDEX_ID_SEMANTIC: str = ""
    
    DOCAI_PROCESSOR_ID: str = ""
    
    DEFAULT_TOP_K: int = 5
    
    # Allows bypassing real GCP calls during dev
    MOCK_GCP: bool = False

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    if not settings.MOCK_GCP:
        if not settings.GCP_PROJECT_ID:
            raise ValueError("GCP_PROJECT_ID is required unless MOCK_GCP=True")
    return settings
