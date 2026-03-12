import os
import re
from google.cloud import documentai
from google.cloud import storage
from google.api_core.client_options import ClientOptions

def parse_pdf_document_ai(gcs_uri: str, processor_id: str, project_id: str, location: str) -> documentai.Document:
    """
    Parses a PDF using Document AI Layout Parser via batch processing to support > 15 pages.
    """
    opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
    client = documentai.DocumentProcessorServiceClient(client_options=opts)
    
    name = client.processor_path(project_id, location, processor_id)
    
    output_gcs_uri = f"gs://profitscout-lx6bb-pipeline-artifacts/docai_output/{os.path.basename(gcs_uri)}/"
    
    request = documentai.BatchProcessRequest(
        name=name,
        input_documents=documentai.BatchDocumentsInputConfig(
            gcs_documents=documentai.GcsDocuments(
                documents=[documentai.GcsDocument(gcs_uri=gcs_uri, mime_type="application/pdf")]
            )
        ),
        document_output_config=documentai.DocumentOutputConfig(
            gcs_output_config=documentai.DocumentOutputConfig.GcsOutputConfig(
                gcs_uri=output_gcs_uri
            )
        )
    )
    
    print(f"Starting Document AI batch processing on {gcs_uri}...")
    operation = client.batch_process_documents(request)
    print("Waiting for operation to complete...")
    operation.result(timeout=600)
    
    print("Fetching results from GCS...")
    metadata = documentai.BatchProcessMetadata(operation.metadata)
    if metadata.state != documentai.BatchProcessMetadata.State.SUCCEEDED:
        raise ValueError(f"Batch Process Failed: {metadata.state_message}")
        
    status = metadata.individual_process_statuses[0]
    output_gcs_destination = status.output_gcs_destination
    
    storage_client = storage.Client(project=project_id)
    match = re.match(r"gs://([^/]+)/(.*)", output_gcs_destination)
    bucket_name = match.group(1)
    prefix = match.group(2)
    
    bucket = storage_client.get_bucket(bucket_name)
    blobs = list(bucket.list_blobs(prefix=prefix))
    
    blobs.sort(key=lambda x: x.name)
    
    shards = []
    for blob in blobs:
        if blob.name.endswith(".json"):
            json_string = blob.download_as_string()
            shard = documentai.Document.from_json(json_string)
            shards.append(shard)
                
    if not shards:
        raise ValueError("No output JSON found in GCS.")
        
    return shards
