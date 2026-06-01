"""Sample in-memory corpus standing in for your real sources.

In production this data comes from your databases, document stores, and
ticketing systems. Here it is a small list so the demo runs anywhere.
Each document carries the roles allowed to read it (permission metadata)
and a last-updated timestamp (used for the freshness check).
"""
from __future__ import annotations

DOCUMENTS: list[dict] = [
    {"id": "kb/refunds#duplicate", "roles": ["agent"], "updated_at": "2026-05-20",
     "text": "How to refund a duplicate charge to a customer."},
    {"id": "kb/refunds#late", "roles": ["agent"], "updated_at": "2026-05-18",
     "text": "Refund policy for late or delayed payments."},
    {"id": "kb/billing#cycle", "roles": ["agent"], "updated_at": "2026-04-30",
     "text": "When the monthly billing cycle starts and ends."},
    {"id": "kb/plans#v1", "roles": ["agent"], "updated_at": "2024-01-10",
     "text": "End of life date for plan v1 (older version, superseded by v2)."},
    {"id": "kb/plans#v2", "roles": ["agent"], "updated_at": "2026-05-22",
     "text": "End of life date for plan v2 (current version)."},
    {"id": "kb/internal#sla", "roles": ["admin"], "updated_at": "2026-05-01",
     "text": "Internal SLA targets for billing escalations."},
]
