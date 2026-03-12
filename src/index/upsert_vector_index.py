import json
import uuid
from google.cloud import aiplatform
from google.cloud import storage
from src.config import get_settings
from typing import List, Dict, Any

def upsert_to_vector_search(index_id: str, datapoints: List[Dict[str, Any]]):
    """
    Upserts embeddings to Vertex AI Vector Search using Batch Update.
    datapoints should contain 'id' and 'embedding'.
    """
    settings = get_settings()
    if settings.MOCK_GCP:
        return
        
    aiplatform.init(project=settings.GCP_PROJECT_ID, location=settings.GCP_LOCATION)
    
    # Write datapoints to JSONL in GCS
    bucket_name = "profitscout-lx6bb-pipeline-artifacts"
    blob_prefix = f"vector_uploads/{index_id}/{uuid.uuid4().hex}/"
    
    storage_client = storage.Client(project=settings.GCP_PROJECT_ID)
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(f"{blob_prefix}data.json")
    
    jsonl_content = ""
    for dp in datapoints:
        jsonl_content += json.dumps({"id": dp["id"], "embedding": dp["embedding"]}) + "\n"
        
    blob.upload_from_string(jsonl_content)
    
    # Format index resource name
    index_name = index_id
    if not index_name.startswith("projects/"):
        index_name = f"projects/{settings.GCP_PROJECT_ID}/locations/{settings.GCP_LOCATION}/indexes/{index_id}"
        
    print(f"Triggering batch update for index {index_name} from gs://{bucket_name}/{blob_prefix} ...")
    index = aiplatform.MatchingEngineIndex(index_name=index_name)
    
    index.update_embeddings(
        contents_delta_uri=f"gs://{bucket_name}/{blob_prefix}",
        is_complete_overwrite=False
    )
