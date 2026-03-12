import json
import os
import sys
sys.path.insert(0, os.path.abspath("."))
from src.api.retrieve import retrieve_chunks
from src.api.answer import generate_answer

questions = [
    "According to the caption of Table 14.1, what are the space requirements for an adjacency matrix compared to the other graph data structures, and what specific variables represent the vertices, edges, and degree?",
    "According to Proposition 14.22 regarding Topological Sorting, what specific graph representation must be used to achieve an O(n+m) running time, and what does it mean if the algorithm fails to include some vertices?",
    "When implementing the adaptable priority queue for Dijkstra's algorithm, what are the two specific implementation choices mentioned in the text, and what is the exact running time yielded by each?",
    "What are the two primary contributions to the overall running time of Kruskal's algorithm, and what is the time complexity stated for the first contribution (ordering the edges)?",
    "How does the textbook distinguish the notation for an undirected edge from a directed edge, and what alternative mathematical notation is sometimes used for undirected edges?"
]

output_file = "semantic_vs_naive_results.txt"

with open(output_file, "w") as f:
    f.write("SEMANTIC CHUNKING VS NAIVE CHUNKING: EVALUATION RESULTS\n")
    f.write("=" * 80 + "\n\n")

    for i, q in enumerate(questions):
        f.write(f"QUESTION {i+1}:\n{q}\n\n")
        print(f"Evaluating Question {i+1}...")
        
        # Naive Evaluation
        try:
            naive_retrieval = retrieve_chunks(q, "naive", top_k=3)
            naive_ans = generate_answer(q, naive_retrieval, "naive")
            f.write("--- NAIVE CHUNKING RESULT ---\n")
            f.write(f"Answer: {naive_ans.answer}\n")
            f.write(f"Citations: {', '.join(naive_ans.citations)}\n")
            if naive_ans.insufficient_context:
                f.write("WARNING: Model reported insufficient context.\n")
            f.write("Retrieved Chunks:\n")
            for r in naive_retrieval:
                f.write(f"  - [{r.chunk.citation_label}] (Score: {r.score:.4f}): {r.chunk.text[:150]}...\n")
            f.write("\n")
        except Exception as e:
            f.write(f"--- NAIVE CHUNKING RESULT ---\nERROR: {e}\n\n")

        # Semantic Evaluation
        try:
            semantic_retrieval = retrieve_chunks(q, "semantic", top_k=3)
            semantic_ans = generate_answer(q, semantic_retrieval, "semantic")
            f.write("--- SEMANTIC CHUNKING RESULT ---\n")
            f.write(f"Answer: {semantic_ans.answer}\n")
            f.write(f"Citations: {', '.join(semantic_ans.citations)}\n")
            if semantic_ans.insufficient_context:
                f.write("WARNING: Model reported insufficient context.\n")
            f.write("Retrieved Chunks:\n")
            for r in semantic_retrieval:
                f.write(f"  - [{r.chunk.citation_label}] (Score: {r.score:.4f}): {r.chunk.text[:150]}...\n")
            f.write("\n")
        except Exception as e:
            f.write(f"--- SEMANTIC CHUNKING RESULT ---\nERROR: {e}\n\n")
            
        f.write("=" * 80 + "\n\n")
        
print(f"Evaluation complete! Results saved to {output_file}")
