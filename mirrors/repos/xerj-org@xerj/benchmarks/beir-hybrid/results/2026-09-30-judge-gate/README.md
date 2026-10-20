# Local-judge gate — 2026-09-30: the lexical judge LOSES, and that is the number

The rc.80 release gate for issue #1060's zero-token rerank, measured on the
release binary (`xerj v1.0.0-rc.78`, main @ a179e1ef3, the staged rc.80-gates
build — see `manifest.txt`). **Verdict: FAIL on the quality gate, PASS on the
cost line.** The gate's own rule — "Loses, does not ship, same rule as the
cross-encoder" — means the judge stays what PR #1077 shipped it as: opt-in,
named `lexical` in every response, with no quality claim. Nothing was tuned to
move these numbers: the gate arms carry **no `min_p`** (reorder-only — a
threshold can only remove recall, so it cannot be part of a passing attempt).

## The gate line, and what measured against it

| Gate row (verbatim from #1060) | Measured | Verdict |
|---|---|---|
| beats hybrid 0.699 SciFact by more than the 3-run spread | hybrid+judge **0.5967** vs measured hybrid 0.7045 (spread 0.0000); −0.1077, W/L/T 32/99/169 | **FAIL** |
| beats hybrid 0.345 NFCorpus by more than the 3-run spread | hybrid+judge **0.2924** vs measured hybrid 0.3419 (spread 0.0000); −0.0495, W/L/T 60/126/137 | **FAIL** |
| FiQA ≥ 0.30 (hosted Jev rerank 0.3638) | bm25+judge **0.1650** vs the 0.30 bar (and vs BM25 0.2382, −0.0732). hybrid+judge not measured: the hybrid first stage itself runs 13–26 s/query on the 57,638-doc index ([fiqa-quality-aborted.log](./fiqa-quality-aborted.log)); the FiQA row is measured on the BM25 top-30 shortlist, the same first stage the hosted 0.3638 reference used | **FAIL** |
| adds ≤ 40 ms p50 for top-30 on CPU | **+0.7 ms** SciFact / **+0.5 ms** NFCorpus / **+0.6 ms** FiQA added p50 (node pinned to 8 cores, client on the other 8); server-side `judged.took_ms` p50 **0 ms** on every dataset | **PASS** |

Full per-run output: `scifact-quality.log`, `nfcorpus-quality.log`,
`fiqa-quality.log`, `*-latency.log` in this directory; setup, sha256s and core
pinning in `manifest.txt`; harness is [`judge_gate.py`](../../judge_gate.py).

## Headline numbers (nDCG@10, 3 runs each, size-30 pages)

| Arm | SciFact (300 q) | NFCorpus (323 q) | FiQA (648 q) |
|---|---:|---:|---:|
| bm25 top-30 | 0.6572 | 0.3016 (25 empty) | 0.2382 |
| **hybrid top-30 (the bar)** | **0.7045** | **0.3419** | not measured (26 s/query) |
| bm25 top-30 + judge | 0.5966 | 0.2827 | 0.1650 |
| hybrid top-30 + judge | 0.5967 | 0.2924 | n/a (see above) |

Every arm reproduced to the fourth decimal across its 3 runs (spread 0.0000)
— the post-#940 deterministic path is deterministic on this binary, exactly as
the gate assumed. The BM25 arms reproduce the 2026-09-18 baseline runs
bit-for-bit (0.6572 / 0.3016 / 0.2382), which validates the harness against
the recorded numbers; the hybrid arm on this binary measures 0.7045 / 0.3419
against the rc.74-era 0.6993–0.7044 / 0.3446–0.3450 (same band on SciFact,
−0.003 on NFCorpus). The gate is judged against **like-for-like hybrids
measured in the same runs on the same node** — a stricter comparison than the
recorded bar, and it loses by more either way.

## Why it loses, plainly

The always-compiled judge is a **lexical scorer** — window-local BM25
saturation with page-local IDF, no semantic signal (`xerj-rerank/src/judge.rs`
says so in its own docstring). Both first stages already read those words:
BM25 ranked by them, and hybrid fused them with MiniLM vectors. Re-reading the
same words over the page with page-local statistics destroys information the
first stages had — corpus-level IDF and the vector arm — so the judged order
is a worse order. The effect is biggest exactly where the first stage is
strongest: on SciFact the judge gives back 10.8 points of the hybrid's lead;
on NFCorpus 5.0; even on BM25-only shortlists the judge is a regression
(−0.0605 SciFact, −0.0189 NFCorpus).

This is the same finding the 2026-09-18 run recorded for "BM25 top-30 →
reorder by MiniLM" (worse than fusing), one step further: **a second stage
that re-reads what the first stage already read is not worth running, from
either direction.** A local judge that ships needs the model arm (the
`decide-local` cross-encoder head), and it will have to beat these same
hybrid numbers under this same harness.

## The cost line, measured

The judge adds **+0.7 ms p50** (SciFact) and **+0.5 ms p50** (NFCorpus) to a
~0.9 s hybrid query on a node pinned to 8 cores — wall-clock, client pinned to
the other 8, one warmup pass first; the box carried co-tenant load throughout
(other rc.80 gate agents, and during the FiQA / late-NFCorpus window a runaway
client of this very run — manifest incident 2), so treat the absolute query
times as upper bounds (the
unjudged hybrid alone measured 220–370 ms p50 on an idle 32-thread box in the
2026-09-18 run). The response's own `judged.took_ms` reports p50 0 ms on
every dataset: the lexical scorer is sub-millisecond for a top-30 page of
~150–200-word abstracts. FiQA (longer documents): see `fiqa-latency.log` —
**+0.6 ms p50** added (BM25 top-30 base 0.8 s, judged 1.4 s wall — the base is dominated by `_source` rendering of 30 long forum posts, not the judge), `judged.took_ms` p50 0 ms.

## What a caller gets for the tokens

The feature's value line is "fewer irrelevant passages enter the context
window" — that is a threshold story, not a ranking story, and the ranking
numbers above say nothing about it. For the record, one informational arm with
`min_p` set (0.5, chosen once, not tuned): hybrid+judge with `min_p: 0.5` scores **0.0767** SciFact (kept 0.1 of 30 hits per page; 274 of 300 queries return an EMPTY page) and **0.1737** NFCorpus (kept 2.8; 176 of 323 empty) — `scifact-minp05.log`, `nfcorpus-minp05.log`. The lexical scale is a share-of-maximum-saturation, not a calibrated probability: on these corpora almost every hit scores below 0.5, so a round-number threshold deletes the page. A caller who wants the pruning behaviour must calibrate `min_p` against their own corpus, and the response's `judged` block is the only honest way to see what a value does.

## Reproduce

```sh
# datasets: see manifest.txt (sha256s); node on a private port in your band
taskset -c 0-7 xerj --insecure --embed-mode neural --port <p> -d <throwaway> &
python3 load.py scifact/corpus.jsonl scifact            # + nfcorpus, + fiqa
XERJ_URL=http://localhost:<p> python3 judge_gate.py scifact scifact quality 3
XERJ_URL=http://localhost:<p> taskset -c 8-15 python3 judge_gate.py scifact scifact latency
```
