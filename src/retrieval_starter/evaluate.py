"""Evaluate retrieval quality on its own, before any generation.

Load an evaluation set, run each case through `retrieve`, check the result
against the case's pass rule, and classify the cause of any failure.
"""
from __future__ import annotations
import json
from pathlib import Path

from .contracts import RetrievalRequest, Status
from .indexer import Index
from .retrieval import retrieve


def load_eval_set(path: str | Path) -> list[dict]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _passes(case: dict, response) -> bool:
    rule = case["pass"]
    ids = [r.source_id for r in response.results]
    if rule == "relevant_cited_top3":
        return any(case["expect"] in cid for cid in ids[:3])
    if rule == "restricted_absent":
        return all(case["expect"] not in cid for cid in ids)
    if rule == "latest_version_only":
        return bool(ids) and case["expect"] in ids[0]
    if rule == "honest_no_answer":
        return response.status in (Status.NO_RESULTS, Status.LOW_CONFIDENCE)
    return False


def _classify_failure(case: dict, response) -> str:
    if response.status is Status.NO_RESULTS:
        return "recall (chunking/embedding)"
    if case.get("type") == "restricted":
        return "permissions"
    if case.get("type") == "outdated":
        return "ranking/freshness"
    return "ranking"


def evaluate(eval_set: list[dict], index: Index, roles=("agent",)) -> dict:
    rows, passed = [], 0
    for case in eval_set:
        req = RetrievalRequest(query=case["q"], user_id="eval", roles=list(roles))
        res = retrieve(req, index)
        ok = _passes(case, res)
        passed += int(ok)
        rows.append({"q": case["q"], "ok": ok,
                     "cause": None if ok else _classify_failure(case, res)})
    return {"total": len(eval_set), "passed": passed,
            "pass_rate": round(passed / len(eval_set), 3) if eval_set else 0.0,
            "cases": rows}
