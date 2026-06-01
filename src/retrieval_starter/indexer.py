"""Build and maintain a read-only index over the chunks.

The index here is a plain in-memory dict keyed by chunk_id. The point is
the lifecycle, not the storage: upsert by stable id avoids duplicates, and
deletion triggers remove chunks when a record is deleted or access changes.
"""
from __future__ import annotations
from .chunking import Chunk, chunk_record

# A trigger maps an event to the action that keeps the index correct.
REPROCESS_EVENTS = {"source_update", "schema_change", "embedding_change",
                    "chunking_change", "policy_change"}


class Index:
    def __init__(self) -> None:
        self._chunks: dict[str, Chunk] = {}

    def upsert(self, chunk: Chunk) -> None:
        self._chunks[chunk.chunk_id] = chunk     # upsert by id => no duplicates

    def delete_by_source(self, source_ref: str) -> int:
        gone = [cid for cid, c in self._chunks.items() if c.source_ref == source_ref]
        for cid in gone:
            del self._chunks[cid]
        return len(gone)

    def all_chunks(self) -> list[Chunk]:
        return list(self._chunks.values())


def index_source(index: Index, records: list[dict]) -> Index:
    for record in records:
        for chunk in chunk_record(record):       # row -> 1 chunk; doc -> passages
            index.upsert(chunk)
    return index


def on_event(index: Index, event: str, record: dict | None = None,
             records: list[dict] | None = None) -> Index:
    """Apply a lifecycle trigger to keep the index consistent."""
    if event in REPROCESS_EVENTS and records is not None:
        index_source(index, records)             # reindex affected scope
    elif event == "record_deleted" and record is not None:
        index.delete_by_source(record["id"])      # delete chunks AND (in prod) embeddings
    return index
