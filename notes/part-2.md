# Notes for Part 2 (Giving it context: chapters 4–9)

Ideas used, and where each came from. Restated in our own words on the pages.

| Idea | Source |
|---|---|
| RAG: retrieve relevant information, add it to the prompt, generate. A retriever plus a generator; indexing and querying are separate steps. | AIE ch. 6, "RAG", "RAG Architecture"; HOLLM ch. 8, "From Search to RAG"; PE ch. 5, "Retrieval-Augmented Generation" |
| Embedding-based retrieval: embed chunks and query, find nearest vectors. Exact k-NN is precise but slow; ANN trades accuracy for speed. | AIE ch. 6, "Embedding-based retrieval"; HOLLM ch. 8, "Dense Retrieval" |
| Vector search algorithms: LSH, HNSW (multi-layer graph), product quantization, IVF (clusters), Annoy (trees). Any database that stores vectors can be called a vector database. | AIE ch. 6, "Embedding-based retrieval" |
| Term-based retrieval: TF, IDF, BM25, the inverted index. | AIE ch. 6, "Term-based retrieval" |
| Hybrid search combines term-based and embedding-based retrieval. Reciprocal rank fusion sums 1 / (k + rank) over the retrievers; k is typically 60. | AIE ch. 6, "Combining retrieval algorithms" |
| A cheap retriever fetches candidates, a more precise and more expensive one reranks them. | AIE ch. 6, "Combining retrieval algorithms", "Reranking"; HOLLM ch. 8, "Reranking" |
| Chunking: fixed units, recursive splitting, document-specific splitting, overlap; smaller chunks are more diverse but lose context and cost more to index; no universal best size. | AIE ch. 6, "Chunking strategy" |
| Query rewriting and contextual retrieval (store each chunk with context about its document). | AIE ch. 6, "Query rewriting", "Contextual retrieval" |

## Computed or run, not from the books (2026-11-22)

- Everything numeric on the pages comes from `app/assistant.py` (`--eval`, `--explain`) or `notes/figures.py`:
  cosine similarities, BM25 scores and the by-hand calculation, fused and reranked scores, the 2-D map (first two
  principal directions, 32% of the variation), the scoreboard.
- Scoreboard, right chunk ranked first: keyword 7/12, vector 11/12, fused 8/12, fused then reranked 12/12.
  Right chunk among the candidates: 8, 12, 12, 12. A tie for first place counts as a miss.
- Models: `BAAI/bge-small-en-v1.5` (embeddings), `Xenova/ms-marco-MiniLM-L-6-v2` (reranker), both through fastembed.
  Qdrant runs in memory (`QdrantClient(":memory:")`).
- The two model answers quoted in chapter 4 are from one run on `nvidia/nemotron-3.5-lightning-30b-a3b`; that run
  used vector search only for retrieval. The finished app (fused and reranked) gave the same answer for the
  stolen-computer question.
- The HNSW drawing in chapter 6 is a sketch, not computed. The 200-page handbook sizes in chapter 9 are arithmetic
  on assumed inputs (100,000 words, 400-token chunks, 50 overlap).

## Not from the books and not run

- Tool tables (which products exist in each slot) are from general knowledge, not checked against each product's
  current docs. The code for fastembed, qdrant-client and rank-bm25 was run.
- An early run without stop-word removal ranked a chunk second on "is" and "for" alone; that run used an earlier,
  8-chunk version of the corpus, so chapter 7 mentions it without a number.

## Chapters 10–11 (graph databases, GraphRAG)

- **None of the three books covers graph databases or GraphRAG** (searched all three texts for "knowledge graph" and
  "GraphRAG": no hits). The chapters rest on code that was run and on general knowledge of the tools.
- Run on 2026-11-22 with `app/graph.py` against Neo4j 5.26 (a throwaway container on port 7688) and the `neo4j`
  Python driver: the four Cypher results in chapter 10, and the count of 5 people under Sara Holm.
- The SQL recursive query in chapter 10 was run in SQLite on the same data: same three people.
- Chapter 11's three answers are from one run on `nvidia/nemotron-3.5-lightning-30b-a3b`. A fourth variant (neutral
  facts such as "The director responsible for Maria Lind is Sara Holm") was also tried: the model then answered
  without naming anyone. It is not on the page. The resolved phrasing was right for four employees' questions
  (Maria Lind, Tom Ek, Ali Sund, Ida Falk), checked by reading the answers, not by an eval.
- Not checked against current docs: the tools tables (Memgraph, Neptune, Kùzu, Apache AGE, GQL, neo4j-graphrag,
  Microsoft GraphRAG, LlamaIndex, LightRAG) and the description of Microsoft's GraphRAG pipeline.
