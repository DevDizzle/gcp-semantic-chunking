import os
from google.cloud import documentai
from google.cloud import aiplatform

PROJECT_ID = "profitscout-lx6bb"
LOCATION_DOCAI = "us"
LOCATION_VERTEX = "us-central1"

print("Setting up Document AI...")
client = documentai.DocumentProcessorServiceClient(client_options={"api_endpoint": "us-documentai.googleapis.com"})
parent = client.common_location_path(PROJECT_ID, LOCATION_DOCAI)

# Check if it already exists
processors = client.list_processors(parent=parent)
proc_id = None
for p in processors:
    if p.display_name == "rag-layout-parser":
        proc_id = p.name.split("/")[-1]
        print(f"Found existing processor: {proc_id}")
        break

if not proc_id:
    print("Creating Layout Parser...")
    processor = client.create_processor(
        parent=parent,
        processor=documentai.Processor(
            display_name="rag-layout-parser",
            type_="LAYOUT_PARSER"
        )
    )
    proc_id = processor.name.split("/")[-1]
    print(f"Created processor: {proc_id}")
