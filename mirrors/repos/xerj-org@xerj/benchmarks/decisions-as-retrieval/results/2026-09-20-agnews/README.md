# AG News — 4-way topic classification, 120k-deep history (2026-09-20)

The scale end of the vote's range: **120,000 labelled train items** indexed,
the full **7,600-item test set** classified, k = 10, rank-weighted 1/(i+1),
BM25 neighbours only — no model of any kind, no embedder, the default lexical
node. This is the workload the System One wire answers (`/v1/systemone`,
`/_decide`), and it is the workload that motivated the engine's WAND fast
path (engine cf6a9989): a full news item is a ~40-clause disjunction whose
match set is most of the index.

## Dataset and provenance

**AG News** via HuggingFace `fancyzhx/ag_news` — the standard 4-class topic
classification corpus (World / Sports / Business / SciTech), 120,000 train /
7,600 test, originally by Zhang et al., *Character-level Convolutional
Networks for Text Classification*, NeurIPS 2015
(https://arxiv.org/abs/1509.01626). Downloaded as parquet from
https://huggingface.co/datasets/fancyzhx/ag_news and converted to TSV
(`label\ttext`) with pandas+pyarrow; the conversion script is not checked in
because it is two lines — the dataset card's own `train`/`test` splits used
verbatim, no re-cutting, no shuffling.

## Headline numbers (all three runs, identical index, identical items)

| Binary | ms/item | Accuracy | ECE | ≥0.8 conf | …and right | no-hit |
|---|---:|---:|---:|---:|---:|---:|
| pre-WAND (284d1f8f) | 68.7 | 0.9182 | 0.019 | 83.1% | 0.9669 | 0 |
| WAND first cut | 51.2 | 0.9182 | 0.019 | 83.1% | 0.9669 | 0 |
| WAND + alloc-free loop (cf6a9989) | **34.2** | 0.9182 | 0.019 | 83.1% | 0.9669 | 0 |

The point of the three rows: **2.0× end-to-end latency, bit-identical
decisions** — same 7,600 labels, same confidence bands, same ECE. Keep-alive
HTTP, one connection, distinct items (no cache reuse — every item is new,
which is the real workload). Run logs: `run-2026-09-20.txt`.

Same-box wire comparison for the same workload class: the hosted Jev API
measured p50 1,230 ms per query on the FiQA rerank run, its fastest of the
three datasets (see
`../../../beir-hybrid/results/2026-09-20-rerank-full-fiqa/`; SciFact and
NFCorpus measured 1.49 s and 1.48 s); the local vote on
120k history answers `/v1/systemone` at p50 42.7 ms (300 distinct items,
final binary). Different tools — the vote needs this labelled history, Jev
needs nothing — so this is a cost/latency/egress contrast, not a quality
race (Jev was not run on AG News; no Jev row belongs on this dataset).

## What the numbers mean

- **92% of 4-way routing decisions made locally, free, with no egress** — and
  83% of them at ≥0.8 confidence, where the vote is right 96.7% of the time.
  The ECE of 0.019 means the confidence can gate: send the uncertain 17% to
  a judge or a person.
- **Why AG News is easy for retrieval**: the four topics have disjoint
  vocabularies (scoreboard, ticker, spacecraft). The vote is not
  understanding news; it is finding the ten most lexically similar
  headlines in 120k history and reading their labels. Banking77 (77 near-
  duplicate intents) is the hard in-domain case; this is the high-volume
  cheap one.
- **Latency scales with the match set, not the corpus**: 120k docs, but the
  cost driver is that a 40-token item matches nearly everything, so nearly
  every doc is scored. Shorter texts against the same index are far under
  this (SMS: 0.9 ms/item at 4k history). No TB-scale claim is being made
  here; this is one shape at one scale, measured.

## Reproduce

```sh
# 1. dataset: HF fancyzhx/ag_news -> TSV (label<TAB>text), train + test
xerj --insecure --port 9460 --data-dir ./agnews-data &
python3 agnews_vote.py                      # indexes 120k train, runs 7,600 test items
# A/B against an older binary: boot both, then
python3 vote_eval.py <port>                 # keep-alive eval, prints acc/ECE/ms-item
```
