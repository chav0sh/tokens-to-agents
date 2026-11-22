"""The docs assistant: the small app Tokens to Agents builds, in one file.

It answers questions from app/handbook.md and names the document it used.

    uv run python app/assistant.py "What do I do if my computer is stolen?"  # needs the key
    uv run python app/assistant.py --explain "When do I need FIN-140?"  # what each search found
    uv run python app/assistant.py --eval  # the scoreboard, no model

Each block below is one chapter of the book.
"""

import functools
import re
import sys
from collections.abc import Callable
from pathlib import Path

from dotenv import load_dotenv
from fastembed import TextEmbedding
from fastembed.rerank.cross_encoder import TextCrossEncoder
from langchain_core.rate_limiters import InMemoryRateLimiter
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from rank_bm25 import BM25Okapi

# The NVIDIA key lives in the repository's .env file (git-ignored). Every app file imports this module first.
load_dotenv()  # finds the nearest .env, from this file's folder upward

# The hosted model's free tier limits requests per minute. Every model call in the app shares this one limiter:
# about one call every two seconds, so a demo that makes many calls waits instead of failing with 429.
RATE_LIMITER = InMemoryRateLimiter(requests_per_second=0.5, check_every_n_seconds=0.1, max_bucket_size=2)

HANDBOOK = Path(__file__).parent / "handbook.md"
TOP_K = 3  # how many chunks each search returns, and how many go into the prompt

# Words too common to tell chunks apart. Dropped before keyword search, in chunks and questions alike.
STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "do",
    "for",
    "from",
    "get",
    "have",
    "how",
    "i",
    "if",
    "in",
    "is",
    "it",
    "my",
    "of",
    "on",
    "or",
    "the",
    "to",
    "what",
    "when",
    "which",
    "who",
    "with",
}

# The eval set: a question and the number of the chunk that answers it. Known answers, so every change gets a score.
EVAL = [
    ("What do I do if my computer is stolen?", 8),
    ("How much time off do I get for a new baby?", 1),
    ("Can I work from my kitchen table on Fridays?", 7),
    ("I have the flu. Do I still get paid?", 9),
    ("How many vacation days do I have?", 4),
    ("What do I earn for extra hours?", 14),
    ("What is form HR-2192 for?", 11),
    ("What is HR-2912?", 12),
    ("What is FIN-401 for?", 13),
    ("What is HR-2219?", 3),
    ("When do I need FIN-140?", 6),
    ("What is form HR-2291 for?", 2),
]

Results = list[tuple[int, float]]  # (chunk id, score), best first


# --- Chunking (chapter 9): one chunk per paragraph, each carrying the title of its section. ---


def load_chunks() -> list[dict]:
    chunks, title = [], ""
    for block in re.split(r"\n\s*\n", HANDBOOK.read_text(encoding="utf-8").strip()):
        if block.startswith("# "):
            title = block[2:].strip()
        else:
            chunks.append({"id": len(chunks) + 1, "doc": title, "text": " ".join(block.split())})
    return chunks


CHUNKS = load_chunks()


# --- Embeddings (chapter 5) and the vector database (chapter 6). ---


@functools.cache
def embedder() -> TextEmbedding:
    return TextEmbedding("BAAI/bge-small-en-v1.5")  # 384 numbers per text; downloads once, runs on CPU


def embed(texts: list[str]) -> list[list[float]]:
    return [[float(x) for x in vector] for vector in embedder().embed(texts)]


@functools.cache
def vector_index() -> QdrantClient:
    qdrant = QdrantClient(":memory:")  # the same API as a Qdrant server, inside this process
    qdrant.create_collection("docs", vectors_config=VectorParams(size=384, distance=Distance.COSINE))
    vectors = embed([chunk["text"] for chunk in CHUNKS])
    qdrant.upsert(
        "docs",
        points=[PointStruct(id=c["id"], vector=v, payload=c) for c, v in zip(CHUNKS, vectors, strict=True)],
    )
    return qdrant


def vector_search(question: str) -> Results:
    """Nearest chunks by meaning; the score is cosine similarity."""
    hits = vector_index().query_points("docs", query=embed([question])[0], limit=TOP_K).points
    return [(int(hit.id), hit.score) for hit in hits]


# --- Keyword search (chapter 7). ---


def tokenize(text: str) -> list[str]:
    return [word for word in re.findall(r"[a-z0-9]+", text.lower()) if word not in STOP_WORDS]


@functools.cache
def keyword_index() -> BM25Okapi:
    return BM25Okapi([tokenize(chunk["text"]) for chunk in CHUNKS])


def keyword_search(question: str) -> Results:
    """Chunks sharing the question's rarest words (BM25). Chunks that share no word are left out."""
    scores = keyword_index().get_scores(tokenize(question))
    best = sorted(range(len(CHUNKS)), key=lambda i: scores[i], reverse=True)[:TOP_K]
    return [(i + 1, float(scores[i])) for i in best if scores[i] > 0]


# --- Hybrid search and reranking (chapter 8). ---


def fuse(*result_lists: Results) -> Results:
    """Reciprocal rank fusion: each list gives a chunk 1 / (60 + its rank). Sum, then sort."""
    totals: dict[int, float] = {}
    for results in result_lists:
        for rank, (chunk_id, _) in enumerate(results, start=1):
            totals[chunk_id] = totals.get(chunk_id, 0) + 1 / (60 + rank)
    return sorted(totals.items(), key=lambda pair: pair[1], reverse=True)


@functools.cache
def reranker() -> TextCrossEncoder:
    return TextCrossEncoder("Xenova/ms-marco-MiniLM-L-6-v2")  # reads the question and one chunk together


def rerank(question: str, candidates: Results) -> Results:
    ids = [chunk_id for chunk_id, _ in candidates]
    scores = reranker().rerank(question, [CHUNKS[i - 1]["text"] for i in ids])
    return sorted(zip(ids, map(float, scores), strict=True), key=lambda pair: pair[1], reverse=True)


def retrieve(question: str) -> list[dict]:
    """The assistant's retrieval: both searches, fused, reranked, the best few."""
    candidates = fuse(vector_search(question), keyword_search(question))
    return [CHUNKS[chunk_id - 1] for chunk_id, _ in rerank(question, candidates)[:TOP_K]]


# --- RAG (chapter 4): retrieved chunks + the question -> a prompt -> the model. ---

SYSTEM = (
    "You answer employees' questions about company policy.\n"
    "Use only the passages below. If they don't contain the answer, say you don't know.\n"
    "Name the document you used."
)


def answer(question: str) -> str:
    # Imported here so --eval and --explain work without a model key.
    from langchain_nvidia_ai_endpoints import ChatNVIDIA

    passages = "\n".join(f"[{chunk['doc']}] {chunk['text']}" for chunk in retrieve(question))
    llm = ChatNVIDIA(  # reads NVIDIA_API_KEY from the environment
        model="nvidia/nemotron-3.5-lightning-30b-a3b",
        temperature=0,
        max_completion_tokens=200,
        model_kwargs={"chat_template_kwargs": {"enable_thinking": False}},  # no long reasoning for a lookup
        rate_limiter=RATE_LIMITER,
    )
    human = f"Passages:\n{passages}\n\nQuestion: {question}\n\nAnswer in one or two sentences, then the source."
    return str(llm.invoke([("system", SYSTEM), ("human", human)]).content)


# --- The scoreboard (chapter 4 introduces it, chapter 17 explains evals). ---

METHODS: dict[str, Callable[[str], Results]] = {
    "keyword": keyword_search,
    "vector": vector_search,
    "fused": lambda q: fuse(vector_search(q), keyword_search(q)),
    "fused + reranked": lambda q: rerank(q, fuse(vector_search(q), keyword_search(q))),
}


def is_first(results: Results, expected: int) -> bool:
    """The expected chunk is ranked first, alone: a tie for first place does not count."""
    if not results or results[0][0] != expected:
        return False
    return len(results) == 1 or results[1][1] < results[0][1]


def run_eval() -> None:
    for name, search in METHODS.items():
        found = [(search(question), expected) for question, expected in EVAL]
        first = sum(is_first(results, expected) for results, expected in found)
        present = sum(expected in [chunk_id for chunk_id, _ in results] for results, expected in found)
        print(f"{name:18} right chunk first: {first:2}/{len(EVAL)}   among the candidates: {present:2}/{len(EVAL)}")


def explain(question: str) -> None:
    for name, search in METHODS.items():
        print(f"{name:18}", [(chunk_id, round(score, 4)) for chunk_id, score in search(question)])


if __name__ == "__main__":
    if sys.argv[1:] == ["--eval"]:
        run_eval()
    elif len(sys.argv) == 3 and sys.argv[1] == "--explain":
        explain(sys.argv[2])
    elif len(sys.argv) == 2:
        print(answer(sys.argv[1]))
    else:
        print(__doc__)
