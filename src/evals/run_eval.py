import json
import argparse
from src.api.retrieve import retrieve_chunks
from src.api.answer import generate_answer

def run_evaluation(input_file: str, output_file: str):
    results = []
    
    print(f"Running evaluation on {input_file}...")
    with open(input_file, "r") as f:
        for line in f:
            if not line.strip():
                continue
            req = json.loads(line)
            query = req["query"]
            chapter = req.get("chapter", "14")
            
            print(f"Evaluating: {query}")
            
            # Naive
            naive_chunks = retrieve_chunks(query, "naive", top_k=5)
            naive_ans = generate_answer(query, naive_chunks, "naive")
            
            # Semantic
            sem_chunks = retrieve_chunks(query, "semantic", top_k=5)
            sem_ans = generate_answer(query, sem_chunks, "semantic")
            
            record = {
                "query": query,
                "naive_answer": naive_ans.answer,
                "naive_citations": naive_ans.citations,
                "naive_evidence": naive_ans.evidence,
                "semantic_answer": sem_ans.answer,
                "semantic_citations": sem_ans.citations,
                "semantic_evidence": sem_ans.evidence
            }
            results.append(record)
            
    with open(output_file, "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
            
    print(f"Evaluation complete. Results saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/evals/eval_questions.jsonl")
    parser.add_argument("--output", default="data/evals/eval_results.jsonl")
    args = parser.parse_args()
    run_evaluation(args.input, args.output)
