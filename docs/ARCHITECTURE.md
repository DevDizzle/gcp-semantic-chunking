# Architecture

This project implements a GCP-native, end-to-end RAG (Retrieval-Augmented Generation) pipeline comparing Naive Chunking with Semantic Chunking.

## Cloud Architecture
- **Document Store**: Cloud Storage (GCS) holds raw PDFs.
- **Parser**: Document AI Layout Parser extracts spatial structures (paragraphs, headings, tables).
- **Metadata DB**: Firestore stores `DocumentRecord` and `ChunkRecord` collections.
- **Embeddings**: Vertex AI Text Embeddings (`text-embedding-004`).
- **Vector Search**: Vertex AI Matching Engine (Vector Search) endpoints. Two indexes are maintained: one for Naive chunks, one for Semantic chunks.
- **LLM Engine**: Gemini on Vertex AI (`gemini-3.1-flash-lite`).
- **Backend**: FastAPI (deployable to Cloud Run).
- **Frontend**: Streamlit Comparison UI.

## Data Flow
1. **Ingestion**: 
   - A PDF is sent to Document AI.
   - Output is parsed. Semantic chunking honors document hierarchy. Naive chunking slices by length.
   - Text chunks are embedded via Vertex AI.
   - Metadata is saved to Firestore.
   - Embeddings are upserted to Vector Search.
2. **Retrieval**: 
   - User query is embedded.
   - KNN search runs against the chosen Vector Search index to retrieve `chunk_id`s.
   - Full chunk metadata is hydrated from Firestore using batched gets.
3. **Generation**:
   - Chunks are assembled into context.
   - Gemini GenerativeModel generates a JSON-structured response with an answer, exact extracted evidence, and citation references.
