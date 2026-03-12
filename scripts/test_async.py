from google.cloud import aiplatform
aiplatform.init(project="profitscout-lx6bb", location="us-central1")
for idx in aiplatform.MatchingEngineIndex.list():
    print(idx.name, idx.display_name, idx.state)
