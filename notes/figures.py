"""Prints the worked numbers the chapters quote that app/assistant.py --eval and --explain don't show.

Run: uv run python notes/figures.py
If the handbook or a question changes, rerun this and update the pages.
"""

import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))  # a notes script, not part of any package
import assistant  # noqa: E402  # pyright: ignore[reportMissingImports]

LABELS = [
    "1 parental leave",
    "2 form HR-2291",
    "3 form HR-2219",
    "4 holiday",
    "5 travel expenses",
    "6 form FIN-140",
    "7 work from home",
    "8 lost laptop",
    "9 sick leave",
    "10 new hires",
    "11 form HR-2192",
    "12 form HR-2912",
    "13 form FIN-401",
    "14 overtime",
]
QUESTIONS = ["What do I do if my computer is stolen?", "How much time off do I get for a new baby?"]


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def main() -> None:
    texts = [chunk["text"] for chunk in assistant.CHUNKS]
    vectors = assistant.embed(texts)

    print("== chapter 5: every chunk against 'What do I do if my computer is stolen?'")
    question_vector = assistant.embed([QUESTIONS[0]])[0]
    scores = sorted(((cosine(question_vector, v), i + 1) for i, v in enumerate(vectors)), reverse=True)
    print("  ", [(chunk_id, round(score, 2)) for score, chunk_id in scores])

    print("== chapter 5: phrases against 'parental leave'")
    phrases = ["parental leave", "time off for a new baby", "maternity", "holiday", "invoice", "laptop"]
    phrase_vectors = assistant.embed(phrases)
    for phrase, vector in zip(phrases[1:], phrase_vectors[1:], strict=True):
        print(f"   {phrase}: {cosine(phrase_vectors[0], vector):.2f}")

    print("== chapter 5: the map (first two principal directions of the 14 chunk vectors)")
    matrix = np.array(vectors + assistant.embed(QUESTIONS))
    mean = matrix[:14].mean(0)
    _, sizes, directions = np.linalg.svd(matrix[:14] - mean, full_matrices=False)
    points = (matrix - mean) @ directions[:2].T
    print("   share of the variation kept:", round(float((sizes[:2] ** 2).sum() / (sizes**2).sum()), 2))
    low, high = points.min(0), points.max(0)
    for label, (x, y) in zip(LABELS + QUESTIONS, points, strict=True):
        px = 60 + (x - low[0]) / (high[0] - low[0]) * 580
        py = 30 + (y - low[1]) / (high[1] - low[1]) * 320
        print(f"   {px:4.0f} {py:4.0f}  {label}")

    print("== chapter 7: BM25 by hand for 'When do I need FIN-140?' (k1 = 1.5, b = 0.75, rank-bm25's defaults)")
    documents = [assistant.tokenize(text) for text in texts]
    average = sum(len(d) for d in documents) / len(documents)
    query = assistant.tokenize("When do I need FIN-140?")
    print("   question tokens:", query, "| chunks:", len(documents), "| average length:", round(average, 2))
    for term in query:
        containing = sum(term in d for d in documents)
        idf = math.log((len(documents) - containing + 0.5) / (containing + 0.5))
        print(f"   '{term}': in {containing} chunks, idf {idf:.3f}")
        for chunk_id in (6, 13):
            words = documents[chunk_id - 1]
            frequency = words.count(term)
            part = frequency * 2.5 / (frequency + 1.5 * (0.25 + 0.75 * len(words) / average))
            print(f"      chunk {chunk_id}: appears {frequency}x, length {len(words)}, frequency part {part:.3f}")
    print("   rank-bm25 totals:", [(i, round(s, 3)) for i, s in assistant.keyword_search("When do I need FIN-140?")])

    # The data behind the scoreboard (chapter 4) and the search playground (chapter 8).
    rows = []
    for question, expected in assistant.EVAL:
        row: dict = {"q": question, "want": expected}
        for key, search in zip(["keyword", "vector", "fused", "reranked"], assistant.METHODS.values(), strict=True):
            results = search(question)
            row[key] = [[chunk_id, round(score, 4 if key == "fused" else 2)] for chunk_id, score in results]
            row[key + "First"] = assistant.is_first(results, expected)
        rows.append(row)
    data = {"labels": LABELS, "rows": rows}
    target = Path(__file__).parent.parent / "assets" / "eval-data.js"
    header = "// Written by notes/figures.py. Do not edit by hand.\nconst EVAL_DATA = "
    target.write_text(header + json.dumps(data) + ";\n", encoding="utf-8")
    print("== wrote", target.name)

    print("== chapter 9: sizes")
    tokens = round(100_000 * 100 / 75)
    print("   200 pages ~100,000 words ->", tokens, "tokens ->", round(tokens / 350), "chunks of 400 with 50 overlap")
    print(
        "   bytes per vector:", 384 * 4, "| 381 chunks:", 381 * 384 * 4, "| 1M chunks (GB):", 1_000_000 * 384 * 4 / 1e9
    )


if __name__ == "__main__":
    main()
