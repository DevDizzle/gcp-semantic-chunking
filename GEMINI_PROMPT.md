# Gemini Build Prompt

Use this prompt with Gemini from the root of this project.

---

You are helping scaffold and implement a **GCP-native semantic chunking RAG demo** for textbook PDFs.

## Product goal
Build a project that compares:
1. **Naive fixed-size chunking with overlap**
2. **Layout-aware semantic chunking using Google Cloud Document AI Layout Parser**

The demo should show that semantic chunking produces better grounded retrieval and better citations for chapter-level Q&A over a textbook PDF.

## Non-negotiable architecture
Use **Google Cloud native services**.

### Required stack
- **Cloud Storage** for source PDFs and parser artifacts
- **Document AI Layout Parser** for document structure extraction
- **Firestore** as metadata/source-of-truth store
- **Vertex AI Embeddings** for chunk/query embeddings
- **Vertex AI Vector Search** as the primary retrieval index
- **Gemini on Vertex AI** for answer generation
- **Cloud Run** for backend services

### Important architectural rule
Do **not** use Firestore vector search as the main retrieval database for this project.
Use this pattern instead:
- Firestore stores document and chunk metadata
- Vertex AI Vector Search stores vectors
- retrieval joins Vector Search results back to Firestore chunk records

Reason:
We want the cleanest production path for multimodal retrieval, larger indexes, and enterprise GCP-native RAG.

## Project objective
Scaffold a working MVP focused on one textbook chapter first, ideally:
- `Chapter 14: Graph Algorithms`

The system must:
- ingest a PDF from GCS
- parse layout with Document AI
- create both naive and semantic chunks
- embed both chunk sets with the same text embedding model
- index each strategy separately in Vertex AI Vector Search
- retrieve top-k chunks for a user query
- generate a grounded Gemini answer with citations
- expose a side-by-side comparison UI for naive vs semantic retrieval

## Output I want from you
Generate the project in phases.

### Phase 1: repository scaffold
Create a Python-first backend scaffold with clear modules for:
- `src/ingest/parse_pdf.py`
- `src/ingest/normalize_layout.py`
- `src/ingest/chunk_naive.py`
- `src/ingest/chunk_semantic.py`
- `src/index/embed_chunks.py`
- `src/index/upsert_vector_index.py`
- `src/api/retrieve.py`
- `src/api/answer.py`
- `src/api/main.py`

Also create:
- `requirements.txt`
- `.env.example`
- `Makefile`
- `infra/terraform/README.md`
- `data/evals/eval_questions.jsonl`

### Phase 2: schemas
Define explicit Python dataclasses or Pydantic models for:
- `DocumentRecord`
- `ChunkRecord`
- `RetrievalResult`
- `AnswerResult`

Every chunk must preserve:
- `document_id`
- `parser_strategy`
- `chapter`
- `section_path`
- `page_start`
- `page_end`
- `content_type`
- `citation_label`
- `text`
- `vector_id`

### Phase 3: semantic chunking rules
Implement semantic chunking rules that:
- preserve heading hierarchy
- keep tables atomic
- keep figure captions attached to nearby explanatory text
- keep definitions/examples/theorems intact
- avoid splitting code/pseudocode blocks blindly
- split oversized content only at paragraph boundaries

### Phase 4: retrieval and answering
Implement:
- query embedding
- Vertex AI Vector Search retrieval
- Firestore metadata resolution
- Gemini grounded answering with citations

The answer pipeline must never invent citations.
If evidence is insufficient, it must say so.

### Phase 5: comparison mode
Implement a mode that runs the same query against:
- naive chunks
- semantic chunks

Return:
- both retrieval result sets
- both answers
- citation comparison metadata

## Constraints
- Python backend
- clean, production-style module boundaries
- strong typing
- concise comments only where needed
- no placeholder pseudo-architecture; create concrete files and runnable stubs

## Design notes
- Start with **text embeddings only** for both pipelines
- Leave a clear extension point for multimodal embeddings later
- Keep chapter filtering in the API
- Make citations first-class from day one
- Assume this project may later be generalized to UFSAR / technical specification PDFs

## Important technical note
I want you to be explicit about how to structure:
- Firestore collections
- Vector Search index IDs
- chunk IDs
- prompt templates for Gemini
- Cloud Run service boundaries

## Deliverable style
Work incrementally. First generate the repository scaffold and file contents. Then propose the next implementation step.
