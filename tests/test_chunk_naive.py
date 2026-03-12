from src.ingest.chunk_naive import create_naive_chunks

def test_naive_chunking():
    text = "A" * 1500
    
    chunks = create_naive_chunks(text, "doc_1", "14", chunk_size=1000, overlap=200)
    
    # 1500 chars with 1000 size and 200 overlap:
    # Chunk 1: 0 - 1000
    # Next start = 1000 - 200 = 800
    # Chunk 2: 800 - 1500
    assert len(chunks) == 2
    assert len(chunks[0].text) == 1000
    assert len(chunks[1].text) == 700
    assert chunks[0].parser_strategy == "naive"
