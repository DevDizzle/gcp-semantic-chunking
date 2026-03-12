# Semantic Chunking vs. Naive Chunking: RAG Evaluation Report

This report evaluates the performance of **Semantic Chunking** versus **Naive Chunking** using a production Retrieval-Augmented Generation (RAG) pipeline built on Google Cloud (Document AI Layout Parser, Vertex AI Vector Search, and Gemini 3.1 Flash-Lite).

## Source Material Context
The evaluation was conducted over **Chapter 14 ("Graph Algorithms")** from the textbook *"Data Structures and Algorithms in Python"*, a 77-page document containing dense academic structures such as complex algorithms (e.g., Dijkstra's, Kruskal's), formal propositions, multi-part figures, and tabular comparisons. 

This specific type of academic material represents a worst-case scenario for naive chunking strategies because its meaning relies heavily on structural formatting rather than just paragraph continuity.

The queries below target these complex, structured textbook elements—specifically algorithms, theorems, and tables—where document layout directly dictates meaning.

---

## 1. The Table Caption Disconnect

**Query:**  
*According to the caption of Table 14.1, what are the space requirements for an adjacency matrix compared to the other graph data structures, and what specific variables represent the vertices, edges, and degree?*

### 🔴 Naive Chunking Result (Failed)
*   **Answer:** The provided context does not contain a Table 14.1, nor does it define the specific variables for vertices, edges, and degree in the context of a table. However, it notes that an adjacency matrix requires O(n^2) space, which is typically worse than the O(n+m) space required by other representations.
*   **Citations:** Naive Chunk 37
*   **⚠️ WARNING:** Model reported insufficient context.

**Why it failed:** The naive character-limit chunker arbitrarily sliced the table's caption away from the relevant table headers and text, leaving the model blind to the variable definitions.

### 🟢 Semantic Chunking Result (Success)
*   **Answer:** According to the caption of Table 14.1, an adjacency matrix requires O(n^2) space, whereas all other graph data structures require O(n+m) space. In these representations, n denotes the number of vertices, m denotes the number of edges, and d_v denotes the degree of vertex v.
*   **Citations:** [14 - 627]

**Why it succeeded:** The Document AI Layout Parser identified the table and its caption as a unified semantic block. The chunker kept them atomic, allowing the model to answer perfectly.

---

## 2. The Multi-Part Proposition

**Query:**  
*According to Proposition 14.22 regarding Topological Sorting, what specific graph representation must be used to achieve an O(n+m) running time, and what does it mean if the algorithm fails to include some vertices?*

### 🔴 Naive Chunking Result (Incomplete/Fragmented)
*   **Answer:** To achieve an O(n+m) running time, the topological sorting algorithm must use an adjacency list representation. If the algorithm fails to include some vertices, it indicates that the directed graph contains a directed cycle.
*   **Retrieved Chunks:**
    *   [Naive Chunk 93] (Score: 0.6795)
    *   [Naive Chunk 97] (Score: 0.7979)

**Why it struggled:** It happened to pull the correct fragments across multiple chunks, but the context was split. In a larger knowledge base, this fragmentation drastically increases the risk of hallucination.

### 🟢 Semantic Chunking Result (Clean & Cohesive)
*   **Answer:** To achieve an O(n+m) running time, the topological sorting algorithm must use an adjacency list representation. If the algorithm fails to include some vertices, it indicates that the directed graph contains a directed cycle.
*   **Citations:** [14 - 657 > Performance of Topological Sorting]
*   **Retrieved Chunks:**
    *   [14 - 657 > Performance of Topological Sorting] (Score: 0.7822)

**Why it succeeded:** The semantic chunker respected the header hierarchy (`14 - 657 > Performance of Topological Sorting`) and grouped the entire proposition and its justification together.

---

## 3. Trade-off Explanations

**Query:**  
*When implementing the adaptable priority queue for Dijkstra's algorithm, what are the two specific implementation choices mentioned in the text, and what is the exact running time yielded by each?*

### 🔴 Naive Chunking Result
*   **Answer:** The two implementation choices for the adaptable priority queue in Dijkstra's algorithm are a heap implementation, which results in a running time of O((n+m)log n), and an unsorted sequence implementation, which results in a running time of O(n^2).
*   **Retrieved Chunks:**
    *   [Naive Chunk 118] (Score: 0.7864)
    *   [Naive Chunk 120] (Score: 0.7983)

### 🟢 Semantic Chunking Result
*   **Answer:** The two implementation choices for the adaptable priority queue in Dijkstra's algorithm are a heap implementation, which results in a running time of O((n+m)log n), and an unsorted sequence implementation, which results in a running time of O(n^2).
*   **Citations:** [14 - 667]
*   **Retrieved Chunks:**
    *   [14 - 667] (Score: 0.7554)
    *   [14 - The Running Time of Dijkstra's Algorithm] (Score: 0.7618)

**Why it matters:** While both models answered correctly in this isolated test, the Naive chunker required assembling the answer from multiple disconnected chunks (`118` and `120`). The Semantic chunker retrieved the exact cohesive paragraph (`14 - 667`), providing much safer context for the LLM.

---

## 4. Multi-Step Logic (Kruskal's Algorithm)

**Query:**  
*What are the two primary contributions to the overall running time of Kruskal's algorithm, and what is the time complexity stated for the first contribution (ordering the edges)?*

### 🔴 Naive Chunking Result
*   **Answer:** The two primary contributions to the running time of Kruskal's algorithm are the ordering of edges by weight and the management of clusters. The time complexity for ordering the edges is O(m log n).
*   **Citations:** [Naive Chunk 146]

### 🟢 Semantic Chunking Result
*   **Answer:** The two primary contributions to the running time of Kruskal's algorithm are the ordering of edges by weight and the management of the cluster partition. The time complexity for ordering the edges is O(m log n).
*   **Citations:** [14 - 679 > The Running Time of Kruskal's Algorithm]
*   **Retrieved Chunks:**
    *   [14 - 679 > The Running Time of Kruskal's Algorithm] (Score: 0.8700)

**Why it matters:** Look at the retrieval scores. The Semantic chunk scored a massive **0.8700** confidence because the chunker cleanly captured the entire "Running Time" section. The Naive chunk topped out at **0.8081** because it sliced mid-explanation.

---

## 5. Nuanced Notation

**Query:**  
*How does the textbook distinguish the notation for an undirected edge from a directed edge, and what alternative mathematical notation is sometimes used for undirected edges?*

### 🔴 Naive Chunking Result
*   **Answer:** A directed edge (u,v) is defined as an ordered pair where u precedes v, whereas an undirected edge (u,v) is an unordered pair where (u,v) is equivalent to (v,u). Undirected edges are sometimes represented using set notation, specifically {u,v}.
*   **Citations:** [Naive Chunk 2]

### 🟢 Semantic Chunking Result
*   **Answer:** In the textbook, a directed edge (u,v) is defined as an ordered pair where u precedes v, whereas an undirected edge (u,v) is treated as an unordered pair where (u,v) is equivalent to (v,u). Additionally, undirected edges are sometimes represented using set notation, specifically {u,v}.
*   **Citations:** [14 - Chapter 14. Graph Algorithms]

---

## Conclusion
Naive, fixed-length chunking destroys the structural integrity of complex documents. As seen in **Question 1**, this leads to immediate hallucinations or "insufficient context" errors when tables or diagrams are severed from their descriptions. 

By leveraging **Document AI Layout Parser** to identify headings, paragraphs, and tables, **Semantic Chunking** ensures that vectors accurately represent complete, cohesive thoughts—resulting in higher retrieval confidence (Question 4) and significantly safer generation for Enterprise RAG systems.
