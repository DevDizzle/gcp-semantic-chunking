from google.cloud import documentai
client = documentai.DocumentProcessorServiceClient(client_options={"api_endpoint": "us-documentai.googleapis.com"})
parent = client.common_location_path("profitscout-lx6bb", "us")
response = client.fetch_processor_types(parent=parent)
for pt in response.processor_types:
    if "LAYOUT" in pt.type_ or "PARSER" in pt.type_:
        print(pt.type_)
