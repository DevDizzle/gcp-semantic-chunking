import sys
import os
import argparse
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api.retrieve import retrieve_chunks

def run_test(query: str):
    print(f"\nSearching for: '{query}'")
    print("-" * 50)
    
    print("\n--- Semantic Strategy ---")
    try:
        results = retrieve_chunks(query, strategy="semantic", top_k=3)
        for i, res in enumerate(results):
            print(f"\nResult {i+1} [Score: {res.score:.4f}] - Citation: {res.chunk.citation_label}")
            print(f"Content: {res.chunk.text[:200]}...")
    except Exception as e:
        print(f"Failed to query semantic index: {e}")

    print("\n--- Naive Strategy ---")
    try:
        results = retrieve_chunks(query, strategy="naive", top_k=3)
        for i, res in enumerate(results):
            print(f"\nResult {i+1} [Score: {res.score:.4f}] - Citation: {res.chunk.citation_label}")
            print(f"Content: {res.chunk.text[:200]}...")
    except Exception as e:
        print(f"Failed to query naive index: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test live retrieval.")
    parser.add_argument("--query", default="Explain depth-first search", help="Query to search")
    args = parser.parse_args()
    
    run_test(args.query)
