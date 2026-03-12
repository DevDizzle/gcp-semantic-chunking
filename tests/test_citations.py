from src.ingest.chunk_semantic import create_semantic_chunks
import uuid

def test_semantic_citations():
    layout = [
        {"text": "Sub-section", "block_type": "heading", "page_num": 1, "level": 1},
        {"text": "Content here.", "block_type": "paragraph", "page_num": 1, "level": 0}
    ]
    
    chunks = create_semantic_chunks(layout, str(uuid.uuid4()), "14")
    assert len(chunks) == 1
    
    chunk = chunks[0]
    assert chunk.citation_label == "14 - Sub-section"
