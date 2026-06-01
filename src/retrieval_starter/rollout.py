"""Rollout flags, kill switches, and incident owners.

Roll out to one audience at a time; keep kill switches so any layer can be
turned off quickly; name incident types in advance and give each an owner.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Rollout:
    flags: dict[str, str] = field(default_factory=lambda: {
        "generated_answers": "team_only",     # off | team_only | on
        "hybrid_rerank": "on",
    })
    audience: list[str] = field(default_factory=lambda: ["support_team"])
    kill_switches: list[str] = field(default_factory=lambda: [
        "index", "source:ticket_history", "retrieval_config", "generated_answers",
    ])
    incident_owners: dict[str, str] = field(default_factory=lambda: {
        "wrong_source": "search_eng",
        "stale_answer": "data_eng",
        "unauthorized_exposure": "security",   # page immediately
        "missing_data": "data_eng",
        "reduced_quality": "search_eng",
    })


def answers_enabled(rollout: Rollout, roles: list[str]) -> bool:
    flag = rollout.flags.get("generated_answers", "off")
    if flag == "on":
        return True
    if flag == "team_only":
        return any(r in ("agent", "support_team") for r in roles)
    return False
