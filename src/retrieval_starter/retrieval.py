"""The main retrieval path, written as one function with a clear order:
validate -> permission filter -> hybrid retrieve -> fuse -> rerank ->
confidence/freshness checks -> cited results.

Permissions are applied BEFORE retrieval so restricted content never enters
the candidate list.
"""
from __future__ import annotations

from .contracts import RetrievalRequest, RetrievalResponse, Result, Status
from .indexer import Index
from .search import keyword_search, vector_search, rrf

CONFIDENCE_MIN = 0.02          # set this from your evaluation data, not by guessing


def _allowed(chunks, roles):
    roleset = set(roles)
    return [c for c in chunks if roleset & set(c.metadata.get("permissions", []))]


def _is_stale(chunk, freshness: str | None) -> bool:
    # Demo rule: treat anything updated before 2025 as stale when freshness is set.
    if not freshness:
        return False
    return str(chunk.metadata.get("updated_at", "")) < "2025"


def _recency_bonus(chunk) -> float:
    # Tiny tiebreak so a newer version outranks an older one at the same relevance.
    year = str(chunk.metadata.get("updated_at", "0"))[:4]
    try:
        return (int(year) - 2000) / 100000.0
    except ValueError:
        return 0.0


def retrieve(request: RetrievalRequest, index: Index) -> RetrievalResponse:
    if not request.query.strip():
        return RetrievalResponse(status=Status.DENIED)

    allowed = _allowed(index.all_chunks(), request.roles)     # permission filter first
    by_id = {c.chunk_id: c for c in allowed}

    kw = keyword_search(request.query, allowed)               # exact terms
    vec = vector_search(request.query, allowed)               # meaning
    fused = rrf(kw, vec)                                       # combine the two lists

    if not fused:
        return RetrievalResponse(status=Status.NO_RESULTS)

    # Rerank: relevance first, with a small recency tiebreak (old ranks lower).
    fused = sorted(
        fused,
        key=lambda s: (s[1] + _recency_bonus(by_id[s[0]])) if s[0] in by_id else s[1],
        reverse=True,
    )
    top = fused[: request.max_results]
    if top[0][1] < CONFIDENCE_MIN:
        return RetrievalResponse(status=Status.LOW_CONFIDENCE)

    if all(_is_stale(by_id[cid], request.freshness) for cid, _ in top):
        return RetrievalResponse(status=Status.STALE)

    results = [
        Result(source_id=by_id[cid].source_ref, snippet=by_id[cid].text,
               citation=by_id[cid].source_ref, timestamp=by_id[cid].metadata.get("updated_at"),
               score=round(score, 3))
        for cid, score in top
    ]
    return RetrievalResponse(status=Status.OK, results=results)
