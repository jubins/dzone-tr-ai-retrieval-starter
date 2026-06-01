# AI Retrieval Starter

A small, **dependency-free** (Python standard library only) starter that shows how to
add production-style retrieval as a thin layer over existing data — without rebuilding
core systems.

This is the companion code for the article **"Connect Existing Data to AI Retrieval:
How to Build Production-Ready Search Without Rebuilding Core Systems."** The article
shows the functions that matter; this repo carries the boilerplate, sample data, and
tests so the whole thing runs end to end.

## Quick start

Requires Python 3.10+. No installation and no third-party packages.

```bash
git clone https://github.com/jubins/dzone-tr-ai-retrieval-starter.git
cd dzone-tr-ai-retrieval-starter

python scripts/run_demo.py        # build the index, run queries, evaluate
python -m unittest discover -s tests -v
```

The demo runs three queries through the full path, prints cited results, shows the
context packet handed to a model, prints a per-retrieval log line, and runs the
evaluation set (expect `pass_rate: 1.0`).

## How the article maps to this repo

Each focused snippet in the article is a real function or type here.

| Article snippet                          | File                                  | Key name(s)                         |
|------------------------------------------|---------------------------------------|-------------------------------------|
| RetrievalService interface               | `src/retrieval_starter/contracts.py`  | `RetrievalRequest`, `RetrievalResponse`, `Status`, `RetrievalService` |
| Chunk record                             | `src/retrieval_starter/chunking.py`   | `Chunk`, `chunk_record`, `stable_id` |
| Indexer with reprocessing/deletion       | `src/retrieval_starter/indexer.py`    | `Index`, `index_source`, `on_event` |
| The `retrieve()` pipeline                | `src/retrieval_starter/retrieval.py`  | `retrieve`                          |
| Hybrid search + RRF                      | `src/retrieval_starter/search.py`     | `keyword_search`, `vector_search`, `rrf` |
| Status drives user-facing behavior       | `src/retrieval_starter/app.py`        | `render_for_status`                 |
| Context packet handed to the model       | `src/retrieval_starter/app.py`        | `build_context_packet`              |
| Per-retrieval log + dashboard signals    | `src/retrieval_starter/monitoring.py` | `log_retrieval`, `DASHBOARD_SIGNALS`|
| Rollout flags, kill switches, owners     | `src/retrieval_starter/rollout.py`    | `Rollout`, `answers_enabled`        |
| Evaluation harness                       | `src/retrieval_starter/evaluate.py`   | `evaluate`, `load_eval_set`         |
| workflow.yaml / sources.yaml / eval_set  | `config/`                             | sample config and evaluation data   |

## Layout

```
dzone-tr-ai-retrieval-starter/
  config/            workflow.yaml, sources.yaml, eval_set.json
  src/retrieval_starter/
    contracts.py     the retrieval contract (request, response, status)
    corpus.py        sample in-memory documents (stand-in for your sources)
    chunking.py      Chunk type + chunking with stable ids
    indexer.py       in-memory index, upsert, reprocess/delete triggers
    search.py        keyword + vector search + reciprocal rank fusion
    retrieval.py     the retrieve() pipeline
    app.py           status -> behavior, context packet for the model
    monitoring.py    per-retrieval logging + dashboard signals
    rollout.py       feature flags, kill switches, incident owners
    evaluate.py      run the eval set and classify failures
  scripts/run_demo.py
  tests/test_retrieval.py
```

## From toy to production

The pieces are intentionally simple so the demo runs anywhere. To grow it:

1. **Embeddings** — replace the toy word-count vector in `search.py` (`embed`/`cosine`)
   with a real embedding model and cosine over those vectors.
2. **Storage** — move `Index` to a real keyword store (BM25/Elasticsearch/OpenSearch)
   and a real vector store; keep the same `retrieve()` shape.
3. **Sources** — point `corpus.py` at your actual data per `config/sources.yaml`, and
   apply the handling decision (index / live-fetch / exclude) per source.
4. **Permissions** — enforce your real access rules in the permission filter.
5. **Generation** — feed `build_context_packet(...)` to your model and require citations.
6. **Operations** — wire `log_retrieval` to your logging and `rollout.py` to your flags.

The contract in `contracts.py` is the stable boundary: you can change everything behind
it without breaking callers.

## License

MIT — see `LICENSE`.
