import os
import re
from google.cloud import documentai
from google.cloud import aiplatform

# Settings
PROJECT_ID = "profitscout-lx6bb"
LOCATION_DOCAI = "us"
LOCATION_VERTEX = "us-central1"
ENV_PATH = ".env"

def update_env(key, value):
    with open(ENV_PATH, "r") as f:
        content = f.read()
    
    # Replace if exists
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


# 2. Vertex AI
print("\n--- Vertex AI Vector Search ---")
aiplatform.init(project=PROJECT_ID, location=LOCATION_VERTEX)

# Function to get or create index
def get_or_create_index(display_name):
    for idx in aiplatform.MatchingEngineIndex.list():
        if idx.display_name == display_name:
            print(f"Found existing index '{display_name}': {idx.name}")
            return idx
    print(f"Creating new index '{display_name}' (this operation is async and takes ~30-45 mins to complete)...")
    idx = aiplatform.MatchingEngineIndex.create_tree_ah_index(
        display_name=display_name,
        dimensions=768, # text-embedding-004 has 768 dimensions
        approximate_neighbors_count=150,
        distance_measure_type="DOT_PRODUCT_DISTANCE",
        sync=False
    )
    # We can get the ID even if it's still creating
    print(f"Started creation of index '{display_name}': {idx.name}")
    return idx

naive_index = get_or_create_index("naive_index")
semantic_index = get_or_create_index("semantic_index")

update_env("VERTEX_VECTOR_INDEX_ID_NAIVE", naive_index.name.split("/")[-1])
update_env("VERTEX_VECTOR_INDEX_ID_SEMANTIC", semantic_index.name.split("/")[-1])

# Function to get or create endpoint
endpoint_display_name = "rag_index_endpoint"
endpoint = None
for ep in aiplatform.MatchingEngineIndexEndpoint.list():
    if ep.display_name == endpoint_display_name:
        endpoint = ep
        print(f"Found existing endpoint '{endpoint_display_name}': {endpoint.name}")
        break

if not endpoint:
    print(f"Creating new endpoint '{endpoint_display_name}' (this is async and takes ~30 mins)...")
    endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
        display_name=endpoint_display_name,
        sync=False
    )
    print(f"Started creation of endpoint: {endpoint.name}")

update_env("VERTEX_VECTOR_ENDPOINT_ID", endpoint.name.split("/")[-1])

print("\nInfrastructure provisioning started/completed!")
print("NOTE: Vertex AI Indexes and Endpoints take ~30-45 minutes to finish creating in Google Cloud.")
print("Once they are fully created, you will need to deploy the indexes to the endpoint in the GCP Console.")
