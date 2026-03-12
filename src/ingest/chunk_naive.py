from src.schemas import ChunkRecord
from typing import List
import uuid

def create_naive_chunks(text: str, document_id: str, chapter: str = "14", chunk_size: int = 1000, overlap: int = 200) -> List[ChunkRecord]:
    """
    Creates naive chunks with fixed size and overlap.
    """
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk_text = text[start:end]
        
        chunk = ChunkRecord(
            document_id=document_id,
            parser_strategy="naive",
            chunk_id=str(uuid.uuid4()),
            chapter=chapter,
            section_path="Unknown",
            page_start=None,
            page_end=None,
            content_type="text",
            citation_label=f"Naive Chunk {len(chunks) + 1}",
            text=chunk_text
        )
        chunks.append(chunk)
        
        # Advance by chunk_size minus the overlap
        start += chunk_size - overlap
        
    return chunks
