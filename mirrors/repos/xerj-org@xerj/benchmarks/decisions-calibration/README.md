# decisions-calibration — the #1063 gate measurement

Issue #1063's gate: **Jev FiQA rerank ECE 0.3109 → ≤ 0.10 on held-out**,
baseline `benchmarks/beir-hybrid/results/2026-09-20-rerank-full-fiqa`.

Two forms live here. The **rc.80 final form** is pair-level — 19,440 raw
(query, doc, p_raw, gold) rows re-scored for this gate — in
[`results/2026-09-30-pairlevel-fiqa/`](./results/2026-09-30-pairlevel-fiqa/).
The earlier bin-level reconstruction (`fiqa_gate.py`,
[`results/2026-09-30-calibration-gate.json`](
./results/2026-09-30-calibration-gate.json)) predates it and is retained as
history; its caveat — binned aggregates are smoothed, and smoothing flatters
calibration fits — is resolved below by measuring the real thing.

## Result (rc.80 final form, pair-level)

| quantity | ECE | Brier | meets ≤ 0.10? |
|---|---:|---:|---|
| raw, all 19,440 pairs (reproduces the published number exactly) | **0.3109** | 0.1807 | — |
| raw, held-out (120 queries, 3,600 pairs) | 0.2872 | 0.1625 | no |
| **isotonic (PAVA), held-out, query-level split** | **0.0088** | 0.0256 | **yes** |
| temperature, held-out, query-level split (T = 1.4589) | 0.3163 | 0.1597 | no |
| isotonic, secondary pair-level split | 0.0034 | 0.0233 | yes |
| temperature, secondary pair-level split (T = 1.4151) | 0.3376 | 0.1768 | no |

`results/2026-09-30-pairlevel-fiqa/gate.json` is the machine-readable run —
an ECE sits beside every probability-producing arm, which is the second half
of the gate. Reproduce stage 1 (paid, ~$0.21):
`python3 pairlevel_run.py --dataset-dir <fiqa> --out results/<label>`;
stage 2 (free, deterministic): `python3 pairlevel_gate.py --results <dir>`.
The bin-level script stays: `python3 fiqa_gate.py` (stdlib only).

## Method

Dataset FiQA-2018 BEIR test (zip sha256 in `provenance.json`), 57,638 docs
indexed into the release binary (`xerj v1.0.0-rc.78`, main @ a179e1ef3,
`--insecure --embed-mode lexical`, private port 9680, throwaway data dir —
the engine supplies the deterministic BM25 shortlists only). **Harness
validation before any paid call:** BM25 nDCG@10 over the regenerated top-30
shortlists came out **0.2382, bit-for-bit the 2026-09-20 baseline figure**
(which itself sat 0.002 from BEIR's published 0.236). Then one provider call
per query — the baseline's fixed request shape verbatim (model
`jev-1.13.0`, one noul per document, document = title + ". " + text[:1400]) —
648 paid calls (cap 50,000, enforced in the harness), 5,059,586 input tokens,
**$0.2125** at $0.042/Mtok input-only, zero fails, 4.3 min wall. Every row is
committed raw in `pairs.jsonl`; `shortlists.json` holds the candidate set
each probability is defined against; `provider-calls.log` audits the spend.

**Split** (deterministic, #940 — sha256, no RNG, no clock): held-out =
queries with `int(sha256(qid),16) % 5 == 0` — 120 of 648 queries, 3,600
pairs. Query-level on purpose: production fits calibration on history from
*past* queries and applies it to *new* ones (`/_decide/_calibration`), so the
held-out unit is the query; a pair-level split would leak sibling pairs and
per-query difficulty. The pair-level hash split is reported as the secondary
row — isotonic passes it too, so the verdict does not hinge on the choice.

## The bug the final form caught in this benchmark's own mirror

The first pair-level pass produced a nonsense fit (isotonic held-out 0.2372,
every knot squeezed below p = 0.27). The cause was in `fiqa_gate.py`'s PAVA,
not in the data and not in the engine: the block's first-x was recorded as
`len(blocks)` at append time, which stops equaling the pooled-point index
after the first backward pool — every knot created after a violation got its
x shifted down, so `apply()` mapped probabilities through a compressed
curve. Reproducer: points (1,0),(2,.5),(3,.2),(4,.6),(5,.8),(6,.9) yielded
knots at x = 1..5 instead of the correct 1,2,4,5,6.

Three things make this more than a local embarrassment:

- **The bin-level 0.0330 was never affected.** The even-bin fit points are
  strictly increasing, so no pooling occurs and the buggy and correct code
  coincide there — which is exactly why the Rust pinning test (asserting
  0.0330 ± 0.0005) and this mirror agreed and stayed green.
- **The shipped engine code was already correct.**
  `engine/crates/xerj-common/src/calibration.rs` carries the pooled index `i`
  (from `enumerate`) and expands block means back to every pooled point;
  no engine change was needed. Only the Python mirror diverged — the
  "mirrors the Rust implementation exactly" claim in the previous version of
  this README was true on the data it had been run on and false in general.
- **The pinning bound was too loose to bind.** The cross-check asserted
  ≤ 0.10, which both the wrong and the right Python number satisfy; an
  exact-value pin on a pooling input would have caught it.

The fixed mirror now reproduces the Rust representation exactly (blocks
carry the pooled index; every pooled point is a knot), was verified against
an independently structured naive run-pooling PAVA (agreement to 8.7e-19 at
all 98 pooled points), and still reproduces the bin-level 0.0330 to the
digit — so the committed bin-level result stands unchanged.

## Honest scope, updated

- **The binned-smoothing caveat is closed, in the gate's favour.** The fear
  was that bin-level aggregates flattered the isotonic fit; the pair-level
  measurement comes out *better* (0.0088 vs 0.0330), because 15,840 real
  pairs give the fit ~98 knots of support where the binned form gave it 5.
- **ECE alone flatters on a 96.9 %-negative dataset.** 92.0 % of held-out
  pairs calibrate below 0.1 against a near-zero base rate, so most of the
  ECE mass is easy. The Brier row (0.1625 → 0.0256) and the top-bin remap
  are the substance: the 183 held-out pairs with raw p ≥ 0.90 (actual
  relevance 0.4208) calibrate to 0.24–0.53. The number is now a threshold
  `min_score` can be argued from; it is still a *dataset-specific* mapping,
  and `/_decide/_calibration` publishes the fit beside the ECE so a node's
  own history speaks first.
- **Temperature fails, and is still shipped.** A single T on the log-odds
  flattens uniformly; the FiQA curve needs 0.93 → ~0.35 at the top while
  holding 0.05 → ~0.0002 at the bottom — a steep monotone remap. Its NLL
  optimum is T = 1.4589 and its held-out ECE barely moves (0.3163). It
  remains the right tool for thin or monotone-in-log-odds history, and its
  ECE is published beside it wherever it runs.
- **One paid repeat.** The provider is non-deterministic (the baseline
  measured per-document drift of mean 0.0148 / max 0.1 across repeats). A
  rerun of the paid stage will wobble within that band; this run's all-pairs
  raw ECE nonetheless landed exactly on the published 0.3109. The split and
  everything downstream of `pairs.jsonl` is bit-identical on rerun.
