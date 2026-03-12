import time
from google.cloud import aiplatform

PROJECT_ID = "profitscout-lx6bb"
LOCATION_VERTEX = "us-central1"

print("Checking if Vertex AI Vector Search resources are ready to deploy...")

aiplatform.init(project=PROJECT_ID, location=LOCATION_VERTEX)

# Load endpoint
endpoints = aiplatform.MatchingEngineIndexEndpoint.list(filter="display_name=rag_index_endpoint")
if not endpoints:
    print("❌ Endpoint 'rag_index_endpoint' not found or still creating.")
    exit(1)
endpoint = endpoints[0]

# Load Indexes
naive_indexes = aiplatform.MatchingEngineIndex.list(filter="display_name=naive_index")
semantic_indexes = aiplatform.MatchingEngineIndex.list(filter="display_name=semantic_index")

if not naive_indexes or not semantic_indexes:
    print("❌ One or both indexes not found or still creating.")
    exit(1)

naive_index = naive_indexes[0]
semantic_index = semantic_indexes[0]

print("✅ Endpoint and Indexes are ready!")

# Deploy Naive
print("\nDeploying Naive Index...")
try:
    endpoint.deploy_index(
        index=naive_index,
        deployed_index_id="naive_deployed_index",
        display_name="naive_deployed_index",
        sync=False
    )
    print("✅ Naive Index deployment started (this takes 20-30 minutes to complete in the background)!")
except Exception as e:
    print(f"⚠️ Could not deploy naive index (it might already be deployed or still provisioning): {e}")

# Deploy Semantic
print("\nDeploying Semantic Index...")
try:
    endpoint.deploy_index(
        index=semantic_index,
        deployed_index_id="semantic_deployed_index",
        display_name="semantic_deployed_index",
        sync=False
    )
    print("✅ Semantic Index deployment started (this takes 20-30 minutes to complete in the background)!")
except Exception as e:
    print(f"⚠️ Could not deploy semantic index: {e}")

print("\nDeployment step complete. You are now ready to run the ingestion pipeline to GCP!")
