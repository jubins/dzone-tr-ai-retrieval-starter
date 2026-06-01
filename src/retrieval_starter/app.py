"""Connect retrieval to the application or the model.

`render_for_status` maps each status to a user-facing behaviour.
`build_context_packet` packages retrieved evidence for a generation model
and tells it to answer only from that evidence and to cite source ids.
"""
from __future__ import annotations

from .contracts import RetrievalResponse, Status

VIEW = {
    Status.OK:                 "answer_with_citations",
    Status.LOW_CONFIDENCE:     "results_only",
    Status.CONFLICT:           "conflicting_sources",
    Status.STALE:              "answer_with_freshness_warning",
    Status.NO_RESULTS:         "no_reliable_answer",
    Status.DENIED:             "access_denied",   # no titles or snippets
    Status.SOURCE_UNAVAILABLE: "source_unavailable",
}


def render_for_status(response: RetrievalResponse) -> dict:
    view = VIEW.get(response.status, "source_unavailable")
    if view in ("access_denied", "no_reliable_answer", "source_unavailable"):
        return {"view": view}                  # show nothing sensitive
    return {"view": view, "results": response.results}


def build_context_packet(query: str, response: RetrievalResponse) -> dict:
    return {
        "question": query,
        "evidence": [
            {"id": r.source_id, "text": r.snippet, "cite": r.citation}
            for r in response.results
        ],
        "instruction": ("Answer only from the evidence; cite source ids; "
                        "if the evidence is not enough, say so."),
    }
