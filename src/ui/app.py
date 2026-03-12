import streamlit as st
import requests
import os

st.set_page_config(page_title="Semantic Chunking vs Naive RAG", layout="wide")

st.title("Semantic Chunking vs Naive RAG Comparison")

API_URL = os.environ.get("API_URL", "http://localhost:8000")

query = st.text_input("Ask a question about Chapter 14 (Graph Algorithms):", "What is the definition of a directed acyclic graph?")
top_k = st.slider("Number of retrieved chunks (top_k)", 1, 10, 5)

if st.button("Compare"):
    with st.spinner("Retrieving and generating answers..."):
        try:
            res = requests.post(f"{API_URL}/compare", json={"query": query, "chapter": "14", "top_k": top_k})
            res.raise_for_status()
            data = res.json()
            
            col1, col2 = st.columns(2)
            
            def render_answer_column(title, ans_data):
                st.header(title)
                
                if ans_data.get("insufficient_context", False):
                    st.warning("⚠️ Insufficient context to answer the question fully.")
                    
                st.success(f"**Answer:**\n\n{ans_data['answer']}")
                
                if ans_data.get("evidence"):
                    with st.expander("Extracted Evidence"):
                        for ev in ans_data["evidence"]:
                            st.markdown(f"- {ev}")
                            
                if ans_data.get("citations"):
                    st.caption("Citations: " + ", ".join(ans_data["citations"]))
                
                with st.expander("View Retrieved Chunks"):
                    for c in ans_data.get("retrieved_chunks", []):
                        st.markdown(f"**Score:** {c['score']:.4f}")
                        st.markdown(f"**Label:** {c['chunk']['citation_label']}")
                        st.text(c['chunk']['text'][:500] + "...")
                        st.divider()

            with col1:
                render_answer_column("Naive Chunking", data["naive"])

            with col2:
                render_answer_column("Semantic Chunking", data["semantic"])
                
        except requests.exceptions.ConnectionError:
            st.error(f"Could not connect to the API at {API_URL}. Make sure the backend is running.")
        except Exception as e:
            st.error(f"Error connecting to API: {e}")
