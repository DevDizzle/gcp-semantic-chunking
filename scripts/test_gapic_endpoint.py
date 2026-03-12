from google.cloud import aiplatform_v1
from google.cloud.aiplatform_v1.types import IndexEndpoint

client = aiplatform_v1.IndexEndpointServiceClient(client_options={"api_endpoint": "us-central1-aiplatform.googleapis.com"})
parent = f"projects/profitscout-lx6bb/locations/us-central1"

endpoint = IndexEndpoint(
    display_name="rag_endpoint_test"
)
operation = client.create_index_endpoint(parent=parent, index_endpoint=endpoint)
print("Operation name:", operation.operation.name)
