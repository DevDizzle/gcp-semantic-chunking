import json
from google import genai
from google.genai import types
from src.schemas import AnswerResult, RetrievalResult, GeneratedAnswer
from src.config import get_settings
from typing import List

def generate_answer(query: str, retrieved_chunks: List[RetrievalResult], strategy: str) -> AnswerResult:
    settings = get_settings()
    
    if settings.MOCK_GCP:
        return AnswerResult(
            query=query,
            answer="Mock Answer",
            evidence=["Mock Evidence"],
            citations=["Mock Citation"],
            insufficient_context=False,
            retrieved_chunks=retrieved_chunks,
            strategy=strategy
        )

    client = genai.Client(vertexai=True, project=settings.GCP_PROJECT_ID, location=settings.VERTEX_GEMINI_LOCATION)
    
    context_str = ""
    for idx, r in enumerate(retrieved_chunks):
        label = r.chunk.citation_label or f"Chunk {idx}"
        context_str += f"[{label}]\n{r.chunk.text}\n\n"
        
    prompt = f"""You are an expert technical assistant answering questions based on the provided textbook excerpts.
    
Context:
{context_str}

Question: {query}

Instructions:
1. Answer the question using ONLY the provided context. Do not use outside knowledge.
2. If the context does not contain enough information to answer the question, set insufficient_context to true.
3. Extract exact quotes or facts as `evidence`.
4. Ensure every claim in the answer is backed by a specific citation label from the context (e.g. [Chapter 14 - Graph Search]). Put these in `citations`.
"""
    
    response = client.models.generate_content(
        model=settings.VERTEX_GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=GeneratedAnswer,
            temperature=0.1,
        )
    )
    
    if not response or not response.text:
        raise ValueError("Failed to generate an answer from Gemini.")
        
    try:
        data = json.loads(response.text)
        gen_answer = GeneratedAnswer(**data)
    except Exception as e:
        raise ValueError(f"Failed to parse structured output from Gemini: {e}")
        
    return AnswerResult(
        query=query,
        answer=gen_answer.answer,
        evidence=gen_answer.evidence,
        citations=gen_answer.citations,
        insufficient_context=gen_answer.insufficient_context,
        retrieved_chunks=retrieved_chunks,
        strategy=strategy
    )
