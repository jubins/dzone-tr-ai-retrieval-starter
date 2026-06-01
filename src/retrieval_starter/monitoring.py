"""Per-retrieval logging and the dashboard signals worth watching.

Record one structured log line per retrieval so any answer can be
reconstructed later.
"""
from __future__ import annotations
import json
import time

from .contracts import RetrievalRequest, RetrievalResponse

# Signals to chart over time.
DASHBOARD_SIGNALS = [
    "latency_p95", "index_lag", "source_freshness",
    "empty_result_rate", "low_confidence_rate", "top_failing_queries",
]


def log_retrieval(request: RetrievalRequest, response: RetrievalResponse,
                  latency_ms: float) -> str:
    line = {
        "query": request.query,
        "filters": request.filters,
        "user_roles": request.roles,
        "pattern": "hybrid",
        "source_ids": [r.source_id for r in response.results],
        "retrieval_version": response.retrieval_version,
        "status": response.status.value,
        "latency_ms": round(latency_ms, 1),
        "top_score": response.results[0].score if response.results else None,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    return json.dumps(line)
