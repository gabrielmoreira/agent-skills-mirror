# BEIR: what XERJ's shipped retrieval scores, with a free local model

**Run:** 2026-09-18, `xerj v1.0.0-rc.74`, `--embed-mode neural` (built-in Candle BERT,
`sentence-transformers/all-MiniLM-L6-v2`, 384-dim, ~90 MB, CPU). One node, one shard,
default settings. Metric: nDCG@10 on each dataset's BEIR `test` split, computed by
`eval.py` from live queries — nothing is assumed or carried over.

| Arm | SciFact (300 q, 5,183 docs) | NFCorpus (323 q, 3,633 docs) |
|---|---:|---:|
| BM25 (`multi_match` on title, text) | 0.6572 | 0.3016 |
| MiniLM vectors only (`semantic`) | 0.6764 | 0.3291 |
| BM25 top-30 → reorder by MiniLM | 0.6855 | 0.3323 |
| **Hybrid RRF (`hybrid`, server-side)** | **0.6993** | **0.3448** |

Raw output: [`results/`](./results).

## The local-judge gate (#1060) — MEASURED 2026-09-30: FAIL on quality, PASS on cost

The rc.80 gate for the opt-in local `judge` stage (PR #1077), on the release
binary `xerj v1.0.0-rc.78`, same harness protocol (3 runs, shuffled order,
post-#940 deterministic path — every arm reproduced to the fourth decimal):

| Gate row (issue #1060, verbatim) | Measured | Verdict |
|---|---|---|
| beats hybrid 0.699 SciFact by more than the 3-run spread | hybrid+judge **0.5967** vs hybrid **0.7045** (spread 0.0000) — loses by 0.1077 | **FAIL** |
| beats hybrid 0.345 NFCorpus by more than the 3-run spread | hybrid+judge **0.2924** vs hybrid **0.3419** (spread 0.0000) — loses by 0.0495 | **FAIL** |
| FiQA ≥ 0.30 (hosted Jev rerank 0.3638) | bm25+judge **0.1650** ×3 runs, spread 0.0000 (vs BM25 0.2382; re-run raw log `results/2026-09-30-judge-gate/fiqa-quality-bm30arms.log` — the first attempt aborted mid-arm, see manifest) | **FAIL** |
| adds ≤ 40 ms p50 for top-30 on CPU | **+0.7 / +0.5 / +0.6 ms** added p50 (SciFact / NFCorpus / FiQA), node pinned to 8 cores; server-side `judged.took_ms` p50 0 ms | **PASS** |

The always-compiled judge is a lexical scorer with no semantic signal, and it
loses to both first stages on all three datasets. Per the gate's own rule the
stage stays opt-in and unnamed-by-default — no quality claim ships with it.
Full analysis, run logs and sha256s:
[`results/2026-09-30-judge-gate/`](./results/2026-09-30-judge-gate/);
harness: [`judge_gate.py`](./judge_gate.py).

## What this says

1. **Hybrid is the best arm XERJ has, on both datasets, and it already ships.** No new
   code is needed to get it.
2. **Reranking a BM25 shortlist with the same bi-encoder is worse than fusing with it.**
   That is why `xerj-rerank` has no "local MiniLM" provider: it would be a regression
   with a good name. A local second stage is only worth building with a cross-encoder,
   and only if it beats 0.699 / 0.345 here.

## Against hosted rerankers — read the caveat

Numbers published in [`hev/jev-rerank`](https://github.com/hev/jev-rerank)'s README for
the same datasets and metric:

| | SciFact | NFCorpus |
|---|---:|---:|
| Jev (TypeSafe AI) | 0.768 | 0.358 |
| Voyage rerank-3 | 0.755 | 0.357 |
| Cohere rerank-v3.5 | 0.745 | 0.340 |
| **XERJ hybrid, local MiniLM, no API** | **0.699** | **0.345** |

**We did not run those systems.** They rerank that project's own first-stage shortlist,
which is not ours, so this is the same dataset and metric but not a controlled
comparison. What can be said: on NFCorpus XERJ's free local hybrid is inside the band of
the hosted rerankers; on SciFact it is 4.6–6.9 points behind them. A controlled
comparison needs a `TYPESAFE_API_KEY` and the `rerank` stage, which now exists.

## Defects this run surfaced

- **Neural indexing was ~3–7 documents/second on CPU in this run.** SciFact (5,183
  short abstracts) took about 25 minutes. That is consistent with the ~3 docs/s figure
  recorded in `xerj-autoindex/src/infer/mod.rs`, and it is the binding constraint on any
  "index your mail on a laptop" story.
- **Hybrid and filtered-semantic queries cost ~220–370 ms p50** on a 5k-document index,
  against ~18 ms for BM25. Most of that is the per-query BERT forward pass on CPU; the
  machine was also compiling during the run, so treat the absolute values as upper
  bounds. The first SciFact vector-arm p50 (0.4 ms) is a **cache artefact** — an earlier
  aborted run had already embedded those queries — and must not be quoted.
- **BM25 returned zero hits for 25 of 323 NFCorpus queries** under default-OR
  `multi_match`. **Explained, and not a defect:** exactly 25 of the test queries
  share no token with any document's title or text — they are single words such
  as `deafness`, `eggnog`, `Fosamax` and `Zoloft` that occur nowhere in the
  corpus. [`lexical_gap.py`](./lexical_gap.py) counts them without a running
  node ([output](./results/nfcorpus-lexical-gap.txt)); the same check reports 0
  for SciFact, where BM25 also had `empty=0`. This is the dataset's lexical gap,
  and it is the clearest reason the vector arm matters on NFCorpus: no reorder
  of a BM25 shortlist can repair an empty list.

## Reproduce

```sh
# a throwaway node on private ports, neural embedder
xerj -c xerj.toml -d ./data --insecure --embed-mode neural &
curl -LO https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/scifact.zip && unzip scifact.zip
XERJ_URL=http://localhost:9410 python3 load.py scifact/corpus.jsonl scifact
XERJ_URL=http://localhost:9410 python3 eval.py 30 scifact
```

## Stemming gate (#1059, rc.79) — MEASURED 2026-09-30

Gate, verbatim: *"NFCorpus zero-hit queries 25 -> <=10; BEIR BM25 >= +0.01 over
0.657 SciFact / 0.302 NFCorpus."* Measured on the release binary (`xerj
v1.0.0-rc.78` version string, main @ `a179e1ef3`, includes the #1070 merge):
one node, private port, `--embed-mode lexical`, paired arms on the same node
that differ only in the create-time `settings.analysis.analyzer.default` PUT
body — `{"type":"stemmer"}` (the #1070 surface) vs omitted (the rc.74 baseline
path). Raw output: [`results/2026-09-30-stemming-1059/`](./results/2026-09-30-stemming-1059/)
([gate summary](./results/2026-09-30-stemming-1059/gate-summary.txt)).

| Sub-gate | Measured | Verdict |
|---|---|---|
| NFCorpus zero-hit queries 25 → ≤10 | 25 → **15** (std arm reproduces the committed 25-qid list exactly) | **FAIL** |
| BEIR BM25 ≥ +0.01 over 0.657 SciFact | 0.6572 → **0.6732** (+0.0160) | **PASS** |
| BEIR BM25 ≥ +0.01 over 0.302 NFCorpus | 0.3016 → **0.3195** (+0.0179) | **PASS** |

**Why the zero-hit sub-gate fails at 15.** Stemming repairs exactly the
inflection class — 10 of the 25 (bagels, leeks, pineapples, turnips, whiting,
deafness, antinutrients, airport scanners, canker sores, Alli). The remaining
15 (Fosamax, Zoloft, Mevacor, Splenda, eggnog, halibut, mesquite, okra, taro,
amnesia, myelopathy, Peoria, Tufts, Yale, Czechoslovakia) are single words
whose *stem* also occurs nowhere in the corpus — no stemmer can bridge a word
absent in every inflected form. Reaching ≤10 lexically is not possible on this
dataset; the vector arm remains the only repair for those queries. Measured
caveat: `GET _settings` does not echo the analysis block and `_analyze` shows
the standard path even on the stem arm — the declared default is provably
honoured by search (std "bagels" 0 hits / stem 1 hit; probe in
[`run-meta.txt`](./results/2026-09-30-stemming-1059/run-meta.txt)).
