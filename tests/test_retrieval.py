import sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from retrieval_starter.contracts import RetrievalRequest, Status
from retrieval_starter.corpus import DOCUMENTS
from retrieval_starter.indexer import Index, index_source, on_event
from retrieval_starter.retrieval import retrieve
from retrieval_starter.evaluate import load_eval_set, evaluate


class RetrievalTests(unittest.TestCase):
    def setUp(self):
        self.index = index_source(Index(), DOCUMENTS)

    def test_relevant_result_for_agent(self):
        res = retrieve(RetrievalRequest("refund a duplicate charge", "u", ["agent"]), self.index)
        self.assertIs(res.status, Status.OK)
        self.assertTrue(any("refunds" in r.source_id for r in res.results))

    def test_admin_only_doc_filtered_for_agent(self):
        res = retrieve(RetrievalRequest("internal SLA targets for escalations", "u", ["agent"]), self.index)
        self.assertTrue(all("internal" not in r.source_id for r in res.results))

    def test_admin_can_see_internal_doc(self):
        res = retrieve(RetrievalRequest("internal SLA targets for escalations", "u", ["admin"]), self.index)
        self.assertTrue(any("internal" in r.source_id for r in res.results))

    def test_newer_version_outranks_older(self):
        res = retrieve(RetrievalRequest("end of life date for plan v2", "u", ["agent"]), self.index)
        self.assertIn("kb/plans#v2", res.results[0].source_id)

    def test_empty_query_denied(self):
        res = retrieve(RetrievalRequest("   ", "u", ["agent"]), self.index)
        self.assertIs(res.status, Status.DENIED)

    def test_no_results_for_unknown_terms(self):
        res = retrieve(RetrievalRequest("xyzzy plugh nothing matches", "u", ["agent"]), self.index)
        self.assertIs(res.status, Status.NO_RESULTS)

    def test_upsert_is_idempotent(self):
        before = len(self.index.all_chunks())
        index_source(self.index, DOCUMENTS)          # index again
        self.assertEqual(before, len(self.index.all_chunks()))

    def test_deletion_trigger_removes_chunks(self):
        on_event(self.index, "record_deleted", record={"id": "kb/refunds#duplicate"})
        self.assertTrue(all(c.source_ref != "kb/refunds#duplicate" for c in self.index.all_chunks()))

    def test_eval_set_all_pass(self):
        report = evaluate(load_eval_set(Path(__file__).resolve().parents[1] / "config" / "eval_set.json"), self.index)
        self.assertEqual(report["passed"], report["total"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
