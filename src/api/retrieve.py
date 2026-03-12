from google.cloud import aiplatform
from google.cloud import firestore
from src.schemas import RetrievalResult, ChunkRecord
from src.index.embed_chunks import embed_texts
from src.config import get_settings
from typing import List

def get_firestore_client():
    settings = get_settings()
    if settings.MOCK_GCP:
        return None
    return firestore.Client(project=settings.GCP_PROJECT_ID, database=settings.FIRESTORE_DATABASE)

def retrieve_chunks(query: str, strategy: str, top_k: int = 5) -> List[RetrievalResult]:
    settings = get_settings()
    if settings.MOCK_GCP:
        return []

    if strategy == "naive":
        deployed_index_id = settings.VERTEX_VECTOR_DEPLOYED_INDEX_ID_NAIVE
    else:
        deployed_index_id = settings.VERTEX_VECTOR_DEPLOYED_INDEX_ID_SEMANTIC
        
    if not settings.VERTEX_VECTOR_ENDPOINT_ID or not deployed_index_id:
        raise ValueError(f"Missing Vector Search endpoint or deployed index ID for strategy: {strategy}")

    # Use the shared embed_texts function which now uses google.genai
    query_emb = embed_texts([query])[0]
    
    aiplatform.init(project=settings.GCP_PROJECT_ID, location=settings.GCP_LOCATION)
    
    endpoint_name = settings.VERTEX_VECTOR_ENDPOINT_ID
    if not endpoint_name.startswith("projects/"):
        endpoint_name = f"projects/{settings.GCP_PROJECT_ID}/locations/{settings.GCP_LOCATION}/indexEndpoints/{settings.VERTEX_VECTOR_ENDPOINT_ID}"
        
    index_endpoint = aiplatform.MatchingEngineIndexEndpoint(index_endpoint_name=endpoint_name)
    response = index_endpoint.find_neighbors(
        deployed_index_id=deployed_index_id,
        queries=[query_emb],
        num_neighbors=top_k
    )
    
    if not response or not response[0]:
        return []
        
    neighbors = response[0]
    
    db = get_firestore_client()
    results = []
    
    # Optimize with batched get
    chunk_ids = [n.id for n in neighbors]
    if not chunk_ids:
        return []
        
    refs = [db.collection(settings.FIRESTORE_COLLECTION_CHUNKS).document(cid) for cid in chunk_ids]
    docs = db.get_all(refs)
    
    # map distances
    dist_map = {n.id: n.distance for n in neighbors}
    
    for doc in docs:
        if doc.exists:
            chunk_record = ChunkRecord(**doc.to_dict())
            results.append(RetrievalResult(chunk=chunk_record, score=dist_map.get(doc.id, 0.0)))
            
    # Sort by score descending (or ascending depending on distance metric, matching engine usually returns distances where lower is better/closer)
    results.sort(key=lambda x: x.score)
    return results
