"""The retrieval contract: the fixed interface between the application
and everything behind it. Fix this first; change the internals later."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol


class Status(str, Enum):
    OK = "ok"
    NO_RESULTS = "no_results"
    STALE = "stale"
    DENIED = "denied"
    SOURCE_UNAVAILABLE = "source_unavailable"
    LOW_CONFIDENCE = "low_confidence"
    CONFLICT = "conflict"


@dataclass
class RetrievalRequest:
    query: str
    user_id: str
    roles: list[str]
    filters: dict[str, str] = field(default_factory=dict)
    freshness: str | None = None          # e.g. "<=24h"
    max_results: int = 5
    mode: str = "cited_answer"            # ranked_results | cited_answer | context_packet


@dataclass
class Result:
    source_id: str
    snippet: str
    citation: str
    timestamp: str | None = None
    score: float = 0.0


@dataclass
class RetrievalResponse:
    status: Status
    results: list[Result] = field(default_factory=list)
    retrieval_version: str = "2026.06.1"


class RetrievalService(Protocol):
    def retrieve(self, request: RetrievalRequest) -> RetrievalResponse: ...
