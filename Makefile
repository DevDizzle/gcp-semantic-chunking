.PHONY: install run deploy

install:
	pip install -r requirements.txt

run:
	uvicorn src.api.main:app --reload

deploy:
	gcloud run deploy semantic-rag-api --source . --region us-central1
