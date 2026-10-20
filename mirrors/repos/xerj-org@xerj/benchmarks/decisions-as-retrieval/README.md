# Typed decisions without a model call: classification as retrieval

TypeSafe's Jev answers typed questions — pick one of N (`choice`), yes/no with a
probability (`noul`). Where a team already has **labelled history**, XERJ can answer the
same shape of question with no model call at all: index the labelled examples, classify
new text by a rank-weighted vote over its *k* nearest neighbours, and report the winning
label's vote share as the probability.

**Run:** 2026-09-18, `xerj v1.0.0-rc.74`, `--embed-mode neural` (all-MiniLM-L6-v2, CPU),
k = 10, 1,000 held-out test items per dataset (seeded shuffle). Raw output in
[`results/`](./results).

### Banking77 — 77-way intent routing (the `choice` shape). 10,003 labelled examples indexed.

| Arm | Accuracy | ECE | Decided at confidence ≥ 0.8 | …and right | ms/item |
|---|---:|---:|---:|---:|---:|
| BM25 — no model of any kind | 0.819 | 0.089 | 50.6% | 0.996 | 2.2 |
| MiniLM neighbours | 0.933 | **0.012** | **86.9%** | 0.979 | 8.6 |
| Hybrid RRF | **0.937** | 0.052 | 79.2% | 0.989 | 12.4 |

### SMS spam — yes/no detection (the `noul` shape). 4,000 labelled examples indexed.

| Arm | Accuracy | spam P / R / F1 | ECE | ms/item |
|---|---:|---|---:|---:|
| BM25 — no model of any kind | 0.983 | 0.964 / 0.925 / 0.944 | 0.017 | 0.9 |
| MiniLM neighbours | 0.982 | 0.910 / 0.973 / 0.940 | 0.009 | 74.5 |
| Hybrid RRF | **0.989** | 0.966 / 0.959 / **0.962** | 0.015 | 67.2 |

## What this is, and what it is not

- **It is not zero-shot, and Jev is.** These numbers need labelled examples; Jev needs
  none. Where there is no history — a new policy, a new category — this does not apply
  and a judge model does. We did not run Jev on these datasets and claim nothing about
  how it would score.
- **The probability is usable.** An expected calibration error of 0.01–0.02 means a
  reported 0.9 is right about nine times in ten, so the confidence can gate real
  decisions.
- **That gate is the point.** On Banking77, 87% of traffic clears confidence 0.8 and is
  routed at 97.9% accuracy with no tokens spent. Only the remaining 13% needs a judge
  model or a person. This is the same economics as semantic detections: a free local
  stage takes the bulk, and the paid stage sees only what is genuinely uncertain.
- **Spam detection at 98.3% needs no model at all** — plain BM25 over 4,000 examples,
  under a millisecond per message.
- Latency was measured on a machine that was also compiling; treat it as an upper bound.
  The gap between datasets is query length: short banking utterances embed in a few
  milliseconds, longer SMS bodies in tens.

## Release gates — MEASURED 2026-09-30 (rc.80 cut, commit `a179e1ef3`, `xerj v1.0.0-rc.78`)

Full tables, method, and raw per-row outputs in
[`results/2026-09-30-rc80gates/`](./results/2026-09-30-rc80gates/) (start at
`run-2026-09-30.md`). The tier-2 rows there were measured on a build of the same
commit with the `decide-local` cargo feature — **the stock release binary does not
include that feature** (`--decide-mode local` logs a warning and tier 2 stays off;
evidence in `stock-binary-noop.txt`), which the release cut needs to know
independently of any number below.

| gate (verbatim bar) | measured | verdict |
|---|---|---|
| #1057: zero-shot SMS acc ≥0.95, ECE ≤0.05 | SMS acc **0.9193**, ECE **0.287** (1,574 held-out rows, noul through `/_decide`) | **FAIL** |
| #1057: AG News ≥0.85 | acc **0.2599** (7,600 test rows, 4-way choice; chance 0.25) | **FAIL** |
| #1057: Banking77 reported, not gated | acc **0.1185**, ECE 0.0717, 0% at conf ≥0.8 (3,080 test rows) | reported |
| #1057 AC: p50 ≤50 ms, 30 questions, 8 cores | p50 **8.4 ms** (`/_decide` noul; 5-way choice 20.0 ms; 77-way 282.6 ms), node pinned `taskset -c 0-7` | **PASS** |
| #1057 AC: quantized weights, download ≤300 MB | downloads **0 MB** (no download path — local dir only); artifact 28.5 MiB **F32, not quantized** | size PASS, quantized NO |
| #1064: trained artifact vs zero-shot head, same rows | same weights — no second model exists; the measurable comparison is tier 1 vs tier 2 on identical rows: B77 **0.8289** vs **0.1185**; SMS **0.9848** vs **0.9193** | measured |
| #1061: after 2,000 cached hosted answers, ≥80% of later traffic answered by history at ≥0.8 conf, accuracy ≥0.97 | as shipped: **4.91%** at ≥0.8 conf, accuracy **0.0377** (the cache freezes at 12 docs — 2,000 is unreachable through the ladder); with 2,000 gold answers cached (the gate's premise): **19.72%** at ≥0.8 conf, accuracy **0.9953** | **FAIL** (accuracy bar passes only in the premise arm; the 80% share bar fails 4× under) |

One-line readings: tier 2 answers with real sub-10 ms latency on binary questions but
its Banking77 accuracy (0.1185) and zero-shot transfer (AG News ≈ chance) are far
under every bar, so per the issue's own rule it ships behind a flag with these
numbers published — and the flag (the cargo feature) is currently off in release
builds. The flywheel freezes at a tiny cache and answers later traffic from it at
3.3% accuracy; even with a correct 2,000-answer cache, confidence-0.8 coverage is
~20%, not 80%.

## Reproduce

```sh
xerj -c xerj.toml -d ./data --insecure --embed-mode neural &
B=https://raw.githubusercontent.com/PolyAI-LDN/task-specific-datasets/master/banking_data
curl -so b77_train.csv $B/train.csv; curl -so b77_test.csv $B/test.csv
curl -so sms.tsv https://raw.githubusercontent.com/justmarkham/pycon-2016-tutorial/master/data/sms.tsv
XERJ_URL=http://localhost:9410 python3 load.py
XERJ_URL=http://localhost:9410 N=1000 K=10 python3 eval.py
```
