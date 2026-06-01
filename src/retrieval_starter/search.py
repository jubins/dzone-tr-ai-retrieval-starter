"""Hybrid candidate generation: keyword search, vector search, and fusion.

Keyword search is good for exact terms (ids, error codes, short forms).
Vector search matches meaning. Reciprocal rank fusion (RRF) merges the two
ranked lists without needing calibrated scores.

The "embedding" here is a toy word-count vector so the demo needs no model.
Swap `embed`/`cosine` for a real embedding model to make it production-grade.
"""
from __future__ import annotations
import math
import re
from collections import Counter

from .chunking import Chunk


def tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def keyword_search(query: str, chunks: list[Chunk]) -> list[tuple[str, float]]:
    q = set(tokens(query))
    scored = [(c.chunk_id, float(len(q & set(tokens(c.text))))) for c in chunks]
    return sorted([s for s in scored if s[1] > 0], key=lambda s: -s[1])


def embed(text: str) -> Counter:
    return Counter(tokens(text))                  # toy embedding; replace in production


def cosine(a: Counter, b: Counter) -> float:
    common = set(a) & set(b)
    num = sum(a[t] * b[t] for t in common)
    da = math.sqrt(sum(v * v for v in a.values()))
    db = math.sqrt(sum(v * v for v in b.values()))
    return num / (da * db) if da and db else 0.0


def vector_search(query: str, chunks: list[Chunk]) -> list[tuple[str, float]]:
    qv = embed(query)
    scored = [(c.chunk_id, cosine(qv, embed(c.text))) for c in chunks]
    return sorted([s for s in scored if s[1] > 0], key=lambda s: -s[1])


def rrf(*ranked_lists: list[tuple[str, float]], k: int = 60) -> list[tuple[str, float]]:
    scores: dict[str, float] = {}
    for ranked in ranked_lists:
        for rank, (chunk_id, _) in enumerate(ranked):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (k + rank + 1)
    return sorted(scores.items(), key=lambda s: -s[1])
