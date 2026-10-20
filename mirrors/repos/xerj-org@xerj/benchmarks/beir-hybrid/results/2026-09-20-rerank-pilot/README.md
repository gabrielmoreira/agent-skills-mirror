# Rerank pilot — 2026-09-20 (real provider, first controlled numbers)

Node: locally built engine at the fix commit, `--insecure --port 9420
--data-dir <throwaway>`, default lexical embedder (no vectors — the BM25 arm
needs none), `TYPESAFE_API_KEY` from the environment. SciFact loaded from the
same corpus files as the hybrid benchmark (`load.py` upstream). Model pinned
`jev-1.13.0` on every request; the response's `model` field was logged and
echoed it. Scoring (`ndcg10`, qrels parsing, the `multi_match` BM25 query) is
byte-identical to `../../eval.py`.

| Row in docs/RERANK.md | Produced by |
|---|---|
| XERJ BM25 shortlist 0.7750 | `eval_rerank.py 40 scifact` — BM25 arm |
| XERJ BM25 → stage 0.8299 | `eval_rerank.py 40 scifact` — rerank arm (this commit's build) |
| stage as shipped before the fix 0.3822 | the same runner against the rc.75 musl binary, 2026-09-20 earlier the same day (log kept in the research notes; runner unchanged) |
| raw provider API, fixed shape 0.8389 | `raw_bench.py 40` — same shortlists, requests built client-side |

`scifact-rerank-pilot.jsonl` is the per-query log of the first two rows:
`{qid, bm25, jev, applied, judged, unjudged, partial_failures, in_tok, out_tok,
took_ms}`. Aggregates: paired vs BM25 9 wins / 6 losses / 25 ties; 1,200/1,200
judged; 0 degraded; stage p50 399 ms / p95 515 ms; 402,165 input +
21,360 output tokens = $0.0169 at $0.042/Mtok input-only.

The provider is not deterministic: re-asking the same window keeps 9–17 of 30
probabilities identical and moves the rest by up to ±0.05 (probe output in the
runner's stdout, method in its tail). Corpus text was sent to
api.typesafe.ai — that is what the `rerank` stage does, and the only run in
this directory that does.
