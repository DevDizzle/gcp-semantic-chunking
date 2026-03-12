# GCP-Native Semantic Chunking RAG

A portfolio-grade demonstration of building RAG on Google Cloud, explicitly comparing naive fixed-length chunking against layout-aware semantic chunking.

## Prerequisites
- Python 3.10+
- Google Cloud Project with the following APIs enabled:
  - Document AI (and a Layout Parser processor created)
  - Vertex AI (Embeddings, Vector Search, Gemini)
  - Firestore (Native mode)
  - Cloud Storage

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   Copy `.env.example` to `.env` and fill out your specific GCP resource IDs.

   ```bash
   cp .env.example .env
   ```
   *Note: For local development and testing, you can set `MOCK_GCP=True` in your `.env` to bypass real cloud calls.*

## Usage

### 1. Ingestion
Run the pipeline to parse a PDF, generate chunks, embed them, and sync to Firestore and Vector Search:
```bash
python -m src.ingest.pipeline gs://your-bucket/path/to/chapter14.pdf --chapter 14
```
**Dry run mode:** Validate chunking without hitting GCP:
```bash
python -m src.ingest.pipeline gs://your-bucket/path/to/chapter14.pdf --chapter 14 --dry-run
```

### 2. API Backend
Start the FastAPI server:
```bash
make run
```
This runs the API locally at `http://localhost:8000`.

### 3. Streamlit UI
Run the comparison frontend in a separate terminal:
```bash
streamlit run src/ui/app.py
```

### 4. Running Evaluations
You can run a batch evaluation on predefined questions:
```bash
python -m src.evals.run_eval --input data/evals/eval_questions.jsonl --output data/evals/eval_results.jsonl
```

## Testing
Run the test suite using pytest:
```bash
pytest tests/ -v
```

## Known Limitations
- The Document AI block parsing heuristics currently rely on simple string matching (e.g., `startswith("Table")`). In a production setting, this should leverage the full entity output of the Layout Parser.
- Vector Search index updates can take up to 15-30 minutes to propagate in GCP if using standard deployed indexes. For instant updates, consider streaming index deployments.
