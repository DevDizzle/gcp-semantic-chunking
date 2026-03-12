from google.cloud import aiplatform_v1
from google.cloud.aiplatform_v1.types import Index

client = aiplatform_v1.IndexServiceClient(client_options={"api_endpoint": "us-central1-aiplatform.googleapis.com"})
parent = f"projects/profitscout-lx6bb/locations/us-central1"

index = Index(
    display_name="naive_index_test",
    description="Naive chunking index",
    metadata={
        "config": {
            "dimensions": 768,
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

print("Starting index creation...")
operation = client.create_index(parent=parent, index=index)
print("Operation name:", operation.operation.name)
print("Operation metadata:", operation.metadata)
