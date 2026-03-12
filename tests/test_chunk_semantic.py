import pytest
import json
import os
from src.ingest.chunk_semantic import create_semantic_chunks

def test_semantic_chunking_boundaries():
    fixture_path = os.path.join(os.path.dirname(__file__), "fixtures", "ch14_normalized_layout.json")
    with open(fixture_path, "r") as f:
        layout = json.load(f)
        
    chunks = create_semantic_chunks(layout, "doc_123", "14")
    
    # Expect 2 chunks because there is a top level heading "14. Graph Algorithms"
    # followed by "14.1 Breadth-First Search". The heading change flushes the previous block.
    # Actually wait:
    # 1. Heading level 1: flush (empty), adds heading.
    # 2. Paragraph: adds to chunk.
    # 3. Heading level 2: flush! (Chunk 1 has: "14. Graph Algorithms" + "Graphs are..."). Adds heading 2.
    # 4. Paragraph: adds.
    # 5. Code: adds.
    # 6. Table: adds, then FLUSHES IMMEDIATELY! (Chunk 2 has: heading + para + code + table)
    # 7. Paragraph: adds.
    # End of document: flush! (Chunk 3 has: trailing paragraph).
    
    assert len(chunks) == 3, f"Expected 3 chunks, got {len(chunks)}"
    
    chunk_1 = chunks[0]
    assert chunk_1.section_path == "14. Graph Algorithms"
    assert "Graphs are ubiquitous" in chunk_1.text
    
    chunk_2 = chunks[1]
    assert chunk_2.section_path == "14. Graph Algorithms > 14.1 Breadth-First Search"
    assert "Algorithm BFS" in chunk_2.text
    assert "Table 14.1" in chunk_2.text
    
    chunk_3 = chunks[2]
    assert "The queue ensures" in chunk_3.text
