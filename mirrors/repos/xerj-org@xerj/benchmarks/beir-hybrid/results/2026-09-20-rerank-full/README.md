# Rerank full run — 2026-09-20 (300+ queries, 3 repeats, calibration)

The pilot's follow-up (../2026-09-20-rerank-pilot/): every judged query, three
repeats with shuffled query order, and a reliability curve over the Jev
probabilities themselves. Same node config as the pilot (locally built engine
at the fix commit, `--insecure --port 9420`, throwaway data dir, lexical
embedder, SciFact and NFCorpus loaded from the hybrid benchmark's corpus
files), model pinned `jev-1.13.0`, scoring byte-identical to `../../eval.py`.

Produced by `raw_bench_full.py <N> <dataset>`: BM25 top-30 shortlists fetched
once (deterministic), the fixed request shape (one noul per document, the
document inside its own question) sent 3× per dataset with the query order
shuffled between repeats, per-query medians taken over the repeats.
`{dataset}-full-run.json` holds the aggregates, the 10-bin reliability curve
and per-query BM25/median numbers.

## Headline numbers

| Dataset | BM25 nDCG@10 | Jev median nDCG@10 | W / L / T | input tokens | cost | wall p50 |
|---|---:|---:|---|---:|---:|---:|
| SciFact (300 q) | 0.6572 | 0.7410 | 82 / 30 / 188 | 9,589,068 | $0.4027 | 1.49 s/q |
| NFCorpus (323 q) | 0.3016 | 0.3312 | 118 / 74 / 131 | 7,618,170 | $0.3200 | 1.48 s/q |

Cost at $0.042/Mtok input-only. Zero failed requests in either dataset (NFCorpus
has 25 queries with an empty BM25 shortlist — those score 0.0 in both arms and
are included).

## The two findings beyond the ranking

**The provider is not deterministic.** Same request, three repeats: mean
per-document probability drift |Δ| 0.0077 (SciFact) / 0.0096 (NFCorpus), max
0.08, over 900 same-document pairs each. Small at the nDCG level — repeat means
spanned 0.7422–0.7474 (SciFact) and 0.3285–0.3316 (NFCorpus) — but any
comparison of Jev numbers tighter than ~±0.01 nDCG@10 is measuring noise.

**The probabilities are not calibrated to BEIR relevance.** ECE 0.1023 over
9,000 (probability, relevance) pairs on SciFact; 0.1332 over 7,186 on NFCorpus.
The curve is monotone — the model discriminates — but every bin above 0.2
overstates relevance, and bin 8 (mean confidence 0.85) is 42% relevant, not
85%. NFCorpus's bin 9 is 0.92 confidence / 0.55 accuracy. A Jev probability is
a usable *ordering* signal and an unusable *threshold* against graded
human-relevance labels: `min_score` on the raw probability cuts documents the
qrels call relevant. The reliability curves are in the JSON files, bin by bin.

Contrast, same day, same engine: the local history vote
(benchmarks/decisions-as-retrieval) measured ECE 0.012 on Banking77 — but that
is in-domain classification with labelled neighbours, a different task from
cross-domain relevance judgement. Neither number redeems the other; they say
"calibration is a property of the target, not the interface."
