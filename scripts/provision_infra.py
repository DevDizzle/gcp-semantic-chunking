import os
import re
from google.cloud import documentai
from google.cloud import aiplatform_v1
from google.cloud.aiplatform_v1.types import Index, IndexEndpoint

# Settings
PROJECT_ID = "profitscout-lx6bb"
LOCATION_DOCAI = "us"
LOCATION_VERTEX = "us-central1"
ENV_PATH = ".env"

def update_env(key, value):
    with open(ENV_PATH, "r") as f:
        content = f.read()
    
    if re.search(rf"^{key}=.*", content, re.MULTILINE):
        content = re.sub(rf"^{key}=.*", f"{key}={value}", content, flags=re.MULTILINE)
    else:
        content += f"\n{key}={value}"
        
    with open(ENV_PATH, "w") as f:
        f.write(content)

print(f"Setting up infrastructure for project {PROJECT_ID}...")

# 1. Document AI
print("\n--- Document AI ---")
docai_client = documentai.DocumentProcessorServiceClient(client_options={"api_endpoint": f"{LOCATION_DOCAI}-documentai.googleapis.com"})
parent = docai_client.common_location_path(PROJECT_ID, LOCATION_DOCAI)

docai_proc_id = None
for p in docai_client.list_processors(parent=parent):
    if p.display_name == "rag-layout-parser":
        docai_proc_id = p.name.split("/")[-1]
        print(f"Found existing Document AI processor: {docai_proc_id}")
        break

if not docai_proc_id:
    print("Creating new Document AI Layout Parser...")
    processor = docai_client.create_processor(
        parent=parent,
        processor=documentai.Processor(
            display_name="rag-layout-parser",
            type_="LAYOUT_PARSER_PROCESSOR"
        )
    )
    docai_proc_id = processor.name.split("/")[-1]
    print(f"Created Document AI processor: {docai_proc_id}")

update_env("DOCAI_PROCESSOR_ID", docai_proc_id)

# 2. Vertex AI Vector Search
print("\n--- Vertex AI Vector Search ---")

idx_client = aiplatform_v1.IndexServiceClient(client_options={"api_endpoint": f"{LOCATION_VERTEX}-aiplatform.googleapis.com"})
ep_client = aiplatform_v1.IndexEndpointServiceClient(client_options={"api_endpoint": f"{LOCATION_VERTEX}-aiplatform.googleapis.com"})
parent_vertex = f"projects/{PROJECT_ID}/locations/{LOCATION_VERTEX}"

def create_index_if_not_exists(display_name):
    # Check if exists
    for idx in idx_client.list_indexes(parent=parent_vertex):
        if idx.display_name == display_name:
            idx_id = idx.name.split("/")[-1]
            print(f"Found existing index '{display_name}': {idx_id}")
            return idx_id
            
    print(f"Starting creation of new index '{display_name}'...")
    index = Index(
        display_name=display_name,
        description=f"{display_name} for RAG chunking",
        metadata={
            "config": {
                "dimensions": 768, # text-embedding-004
                "approximateNeighborsCount": 150,
                "distanceMeasureType": "DOT_PRODUCT_DISTANCE",
                "algorithmConfig": {
                    "treeAhConfig": {
                        "leafNodeEmbeddingCount": 500,
                        "leafNodesToSearchPercent": 10
                    }
                }
            }
        }
    )
    operation = idx_client.create_index(parent=parent_vertex, index=index)
    
    # operation name format: projects/<id>/locations/<loc>/indexes/<index_id>/operations/<op_id>
    idx_id = operation.operation.name.split("/operations/")[0].split("/")[-1]
    print(f"Creation started! Index ID: {idx_id}")
    return idx_id

naive_idx_id = create_index_if_not_exists("naive_index")
semantic_idx_id = create_index_if_not_exists("semantic_index")

update_env("VERTEX_VECTOR_INDEX_ID_NAIVE", naive_idx_id)
update_env("VERTEX_VECTOR_INDEX_ID_SEMANTIC", semantic_idx_id)

def create_endpoint_if_not_exists(display_name):
    for ep in ep_client.list_index_endpoints(parent=parent_vertex):
        if ep.display_name == display_name:
            ep_id = ep.name.split("/")[-1]
            print(f"Found existing endpoint '{display_name}': {ep_id}")
            return ep_id
            
    print(f"Starting creation of new endpoint '{display_name}'...")
    endpoint = IndexEndpoint(display_name=display_name)
    operation = ep_client.create_index_endpoint(parent=parent_vertex, index_endpoint=endpoint)
    
    ep_id = operation.operation.name.split("/operations/")[0].split("/")[-1]
    print(f"Creation started! Endpoint ID: {ep_id}")
    return ep_id

ep_id = create_endpoint_if_not_exists("rag_index_endpoint")
update_env("VERTEX_VECTOR_ENDPOINT_ID", ep_id)

print("\n---------------------------------------------------------")
print("✅ .env file successfully updated with IDs.")
print("⏳ IMPORTANT: Vertex AI Indexes and Endpoints take about 30-45 minutes to provision in the background.")
print("They must finish provisioning before you can deploy the indexes to the endpoint.")
print("We have provided a deployment script (scripts/deploy_indexes.py) for you to run once they are ready.")
