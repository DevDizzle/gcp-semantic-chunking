# Infrastructure Setup

This directory contains Terraform configurations (to be added) for provisioning the required GCP resources:

1.  **Cloud Storage bucket**: For storing uploaded PDFs and Document AI JSON outputs.
2.  **Document AI Processor**: Specifically the Layout Parser for semantic understanding.
3.  **Firestore Database**: The source-of-truth for `DocumentRecord` and `ChunkRecord` metadata.
4.  **Vertex AI Vector Search Indexes**: Two separate indexes (Naive & Semantic) for A/B comparison.
5.  **Vertex AI Vector Search Endpoint**: To serve the indexes for retrieval.
6.  **Cloud Run Service**: To host the FastAPI backend.
