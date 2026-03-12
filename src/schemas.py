from pydantic import BaseModel, Field
from typing import Optional, List

class DocumentRecord(BaseModel):
    document_id: str
    filename: str
    gcs_uri: str
    status: str = "uploaded"

class ChunkRecord(BaseModel):
    document_id: str
    parser_strategy: str
    chunk_id: str
    chapter: Optional[str] = None
    section_path: Optional[str] = None
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    content_type: Optional[str] = None
    citation_label: Optional[str] = None
    text: str
    vector_id: Optional[str] = None

class RetrievalResult(BaseModel):
    chunk: ChunkRecord
    score: float

class GeneratedAnswer(BaseModel):
    answer: str = Field(description="The synthesized answer to the user's question, fully grounded in the provided context.")
    evidence: List[str] = Field(description="List of raw quotes or facts from the text that support the answer.")
    citations: List[str] = Field(description="List of exact citation labels referenced in the answer.")
    insufficient_context: bool = Field(description="True if the provided context does not contain enough information to answer the question fully.")

class AnswerResult(BaseModel):
    query: str
    answer: str
    evidence: List[str]
    citations: List[str]
    insufficient_context: bool
    retrieved_chunks: List[RetrievalResult]
    strategy: str

class QueryRequest(BaseModel):
    query: str
    chapter: str = "14"
    strategy: str = "semantic" # "naive" or "semantic"
    top_k: int = 5

class CompareRequest(BaseModel):
    query: str
    chapter: str = "14"
    top_k: int = 5
