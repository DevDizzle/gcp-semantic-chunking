# Architectural Decisions

## ADR-001: GCP-native stack only
Decision:
- Prefer GCP-managed services over third-party parsing/vector infra.

Why:
- aligns with portfolio and enterprise deployment story
- reduces architecture drift from future production use cases

---

## ADR-002: Document AI Layout Parser over generic PDF text extraction
Decision:
- Use Document AI Layout Parser for the semantic pipeline.

Why:
- preserves document structure better than plain PDF text extraction
- gives a defensible answer to the ingestion/chunking gap

Tradeoff:
- more setup and potentially more cost than naive text extraction

---

## ADR-003: Firestore is metadata store, not primary vector database
Decision:
- Use Firestore for metadata only.

Why:
- clean separation of concerns
- easier evolution of retrieval tier
- better fit for chapter/section/citation metadata

Tradeoff:
- two-step retrieval path instead of single-store design

---

## ADR-004: Vertex AI Vector Search is the primary retrieval engine
Decision:
- Use Vertex AI Vector Search for chunk embeddings.

Why:
- better path to ANN scale
- better GCP-native RAG architecture
- future support path for multimodal retrieval patterns

---

## ADR-005: Text embeddings first, multimodal second
Decision:
- MVP uses text embeddings only for both naive and semantic chunk pipelines.

Why:
- keeps the experiment controlled
- makes chunking quality the independent variable

Tradeoff:
- diagrams/tables may be under-modeled in MVP

---

## ADR-006: Two independent indexes for clean comparison
Decision:
- Maintain separate indexes for naive and semantic chunks.

Why:
- avoids contamination of retrieval results
- makes side-by-side evaluation straightforward

---

## ADR-007: Chapter-scoped retrieval for MVP
Decision:
- Restrict retrieval to one selected chapter during MVP.

Why:
- keeps evaluation tight
- reduces noise while validating chunking quality
- improves citation precision
