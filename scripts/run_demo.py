"""End-to-end demo. Run from the repo root with:

    python scripts/run_demo.py

It builds an index over the sample corpus, runs three queries through the
full retrieve() path, prints cited results, shows the context packet and a
log line, and finally runs the evaluation set.
"""
import sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from retrieval_starter.contracts import RetrievalRequest
from retrieval_starter.corpus import DOCUMENTS
from retrieval_starter.indexer import Index, index_source
from retrieval_starter.retrieval import retrieve
from retrieval_starter.app import render_for_status, build_context_packet
from retrieval_starter.monitoring import log_retrieval
from retrieval_starter.evaluate import load_eval_set, evaluate


def show(query, roles):
    index = INDEX
    req = RetrievalRequest(query=query, user_id="u_812", roles=roles)
    start = time.perf_counter()
    res = retrieve(req, index)
    latency = (time.perf_counter() - start) * 1000
    print(f"\nquery: {query!r}  roles={roles}")
    print(f"  status: {res.status.value}")
    for r in res.results:
        print(f"    [{r.source_id}] score={r.score} -> {r.snippet}")
    print(f"  view: {render_for_status(res)['view']}")
    print(f"  log: {log_retrieval(req, res, latency)}")
    return res


INDEX = index_source(Index(), DOCUMENTS)

if __name__ == "__main__":
    res = show("refund a duplicate charge", roles=["agent"])
    show("internal SLA targets for escalations", roles=["agent"])   # restricted -> filtered out
    show("end of life date for plan v2", roles=["agent"])           # newer version wins

    print("\ncontext packet for the model:")
    packet = build_context_packet("refund a duplicate charge", res)
    print(f"  question: {packet['question']}")
    print(f"  evidence ids: {[e['id'] for e in packet['evidence']]}")
    print(f"  instruction: {packet['instruction']}")

    print("\nevaluation:")
    report = evaluate(load_eval_set(Path(__file__).resolve().parents[1] / "config" / "eval_set.json"), INDEX)
    print(f"  pass_rate: {report['pass_rate']}  ({report['passed']}/{report['total']})")
    for row in report["cases"]:
        flag = "PASS" if row["ok"] else f"FAIL ({row['cause']})"
        print(f"    {flag}: {row['q']}")
