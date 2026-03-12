import os
import uuid
import argparse
from google.cloud import firestore
from src.ingest.parse_pdf import parse_pdf_document_ai
from src.ingest.normalize_layout import normalize_document_layout
from src.ingest.chunk_naive import create_naive_chunks
from src.ingest.chunk_semantic import create_semantic_chunks
from src.index.embed_chunks import embed_texts
from src.index.upsert_vector_index import upsert_to_vector_search
from src.schemas import DocumentRecord
from src.config import get_settings

def get_firestore_client():
    settings = get_settings()
    if settings.MOCK_GCP:
        return None
    return firestore.Client(project=settings.GCP_PROJECT_ID, database=settings.FIRESTORE_DATABASE)

def run_ingestion_pipeline(gcs_uri: str, document_id: str, chapter: str = "14", dry_run: bool = False):
    settings = get_settings()
    
    print(f"{'[DRY-RUN] ' if dry_run else ''}Ingesting {gcs_uri}...")
    print(f"{'[DRY-RUN] ' if dry_run else ''}Parsing PDF with Document AI Layout Parser...")
    
    documents = parse_pdf_document_ai(gcs_uri, settings.DOCAI_PROCESSOR_ID, settings.GCP_PROJECT_ID, location="us")
    
    print(f"{'[DRY-RUN] ' if dry_run else ''}Normalizing Document Layout...")
    layout = normalize_document_layout(documents)
    
    # Reconstruct full text for naive chunker since Document Layout doesn't populate doc.text
    document_text = "\n\n".join([b["text"] for b in layout])
    
    print(f"{'[DRY-RUN] ' if dry_run else ''}Generating Chunks...")
    naive_chunks = create_naive_chunks(document_text, document_id, chapter=chapter)
    semantic_chunks = create_semantic_chunks(layout, document_id, chapter=chapter)
    
    print(f"{'[DRY-RUN] ' if dry_run else ''}Generated {len(naive_chunks)} naive chunks and {len(semantic_chunks)} semantic chunks.")
    
    print("\n--- Sample Naive Chunk ---")
    if naive_chunks:
        print(naive_chunks[0].model_dump_json(indent=2))
    print("\n--- Sample Semantic Chunk ---")
    if semantic_chunks:
        print(semantic_chunks[0].model_dump_json(indent=2))
        
    if dry_run:
        print("[DRY-RUN] Skipping GCP uploads.")
        return

    print("Saving document metadata to Firestore...")
    db = get_firestore_client()
    doc_ref = db.collection(settings.FIRESTORE_COLLECTION_DOCUMENTS).document(document_id)
    doc_record = DocumentRecord(
        document_id=document_id,
        filename=os.path.basename(gcs_uri),
        gcs_uri=gcs_uri,
        status="parsed"
    )
    doc_ref.set(doc_record.model_dump())
    
    def process_and_upload(chunks, strategy):
        index_id = settings.VERTEX_VECTOR_INDEX_ID_NAIVE if strategy == "naive" else settings.VERTEX_VECTOR_INDEX_ID_SEMANTIC
        print(f"\nEmbedding {len(chunks)} {strategy} chunks...")
        
        texts = [c.text for c in chunks]
        BATCH_SIZE = 10
        embeddings = []
        for i in range(0, len(texts), BATCH_SIZE):
            batch = texts[i:i+BATCH_SIZE]
            embeddings.extend(embed_texts(batch))
        
        print(f"Saving {strategy} chunk metadata to Firestore...")
        datapoints = []
        for chunk, emb in zip(chunks, embeddings):
            chunk.vector_id = chunk.chunk_id
            
            # Save to Firestore
            db.collection(settings.FIRESTORE_COLLECTION_CHUNKS).document(chunk.chunk_id).set(chunk.model_dump())
            
            datapoints.append({
                "id": chunk.vector_id,
                "embedding": emb
            })
            
        print(f"Upserting to Vector Search index: {index_id}...")
        upsert_to_vector_search(index_id, datapoints)
        print(f"Successfully upserted {len(chunks)} {strategy} chunks.")
        return len(chunks)

    naive_count = process_and_upload(naive_chunks, "naive")
    semantic_count = process_and_upload(semantic_chunks, "semantic")
    
    # Calculate pages
    total_pages = 0
    for doc in documents:
        if hasattr(doc, "pages") and doc.pages:
            total_pages += len(doc.pages)
        elif hasattr(doc, "document_layout") and doc.document_layout.blocks:
            # Fallback for Layout Parser docs if pages list isn't populated
            page_nums = [b.page_span.page_end for b in doc.document_layout.blocks if hasattr(b, "page_span")]
            if page_nums:
                total_pages += max(page_nums)
    
    print("\n=======================================================")
    print("                INGESTION SUMMARY")
    print("=======================================================")
    print(f"📄 Pages parsed:              {total_pages}")
    print(f"🧩 Normalized elements count: {len(layout)}")
    print(f"🧱 Naive chunks count:        {naive_count}")
    print(f"🧠 Semantic chunks count:     {semantic_count}")
    print(f"🔢 Embeddings generated:      {naive_count + semantic_count}")
    print(f"💾 Firestore writes:          {naive_count + semantic_count + 1}")
    print(f"📈 Vector Search upserts:     {naive_count + semantic_count}")
    print("=======================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest a PDF into the RAG system.")
    parser.add_argument("gcs_uri", help="GCS URI of the PDF (e.g. gs://bucket/file.pdf)")
    parser.add_argument("--doc-id", default=str(uuid.uuid4()), help="Unique document ID")
    parser.add_argument("--chapter", default="14", help="Chapter number/name")
    parser.add_argument("--dry-run", action="store_true", help="Run without calling GCP APIs or writing state")
    
    args = parser.parse_args()
    
    run_ingestion_pipeline(args.gcs_uri, args.doc_id, args.chapter, args.dry_run)
