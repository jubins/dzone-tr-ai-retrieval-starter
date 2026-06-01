"""Turn source records into retrievable chunks.

A chunk is a small, self-contained piece of text with a stable id and a
link back to its source. A structured row becomes one short chunk; a long
document is split into overlapping passages.
"""
from __future__ import annotations
import hashlib
from dataclasses import dataclass, field


@dataclass
class Chunk:
    chunk_id: str                       # stable: hash(source_ref + version + offset)
    source_ref: str                     # e.g. "kb/refunds#duplicate"
    text: str
    embedding: list[float] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)   # source, permissions, updated_at, hash


def stable_id(source_ref: str, version: str, offset: int) -> str:
    raw = f"{source_ref}|{version}|{offset}".encode("utf-8")
    return hashlib.sha1(raw).hexdigest()[:16]


def content_hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]


def split_passages(text: str, size: int = 40, overlap: int = 10) -> list[str]:
    """Split long text into overlapping word windows. Short text stays as one chunk.
    `size`/`overlap` are word counts here for simplicity; in production use tokens
    (a few hundred per chunk, with a small overlap)."""
    words = text.split()
    if len(words) <= size:
        return [text]
    step = max(1, size - overlap)
    return [" ".join(words[i:i + size]) for i in range(0, len(words), step)]


def chunk_record(record: dict) -> list[Chunk]:
    version = record.get("updated_at", "0")
    chunks: list[Chunk] = []
    for offset, passage in enumerate(split_passages(record["text"])):
        chunks.append(Chunk(
            chunk_id=stable_id(record["id"], version, offset),
            source_ref=record["id"],
            text=passage,
            metadata={
                "source": record["id"].split("/")[0],
                "permissions": record.get("roles", []),
                "updated_at": record.get("updated_at"),
                "content_hash": content_hash(passage),
            },
        ))
    return chunks
