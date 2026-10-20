# FiQA rerank full run — 2026-09-20 (648 queries, 3 repeats)

Third BEIR dataset through the same harness as
`../2026-09-20-rerank-full/` (SciFact + NFCorpus), added so the measured-Jev
board covers a finance-domain QA corpus with sparse relevance judgements —
the regime where a general-purpose judge is most often wrong-when-confident.

## Dataset and provenance

**FiQA-2018**, the BEIR `test` split: 57,638 corpus documents, 648 judged
test queries, graded qrels — the same files every BEIR paper uses.

- Task page: https://arxiv.org/abs/2104.08663 (BEIR, Thakur et al., 2021)
- Canonical BEIR distribution: the `fiqa` corpus/queries/qrels from
  https://github.com/beir-cellar/beir (MIT), mirrored at
  `https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/fiqa.zip`
- SHA of the zip we fetched is recorded in the local run log; nothing here
  was re-tokenised or re-cut — corpus.jsonl / queries.jsonl / qrels/test.tsv
  are the archive's files verbatim.

**Harness validation before any model was called:** local BM25 nDCG@10 on the
648 test queries came out **0.2382**, against BEIR's published BM25 figure of
**0.236** for FiQA (BM25 from the BEIR paper's table, reproduced by many
independent runs since). Within 0.002 — the harness scores the way the
reference scores. The same BM25 figure reproduced identically (0.2382, three
times, and again bit-for-bit after the WAND fast path landed in the engine,
cf6a9989).

## Headline numbers

| Dataset | BM25 nDCG@10 | Jev median nDCG@10 | W / L / T | input tokens | cost | wall p50 |
|---|---:|---:|---|---:|---:|---:|
| FiQA (648 q) | 0.2382 | 0.3638 | 249 / 57 / 342 | 15,178,758 | $0.6375 | 1.23 s/q |

Cost at $0.042/Mtok input-only. Zero failed requests; zero queries with an
empty BM25 shortlist (FiQA's queries are vocabulary-rich, unlike NFCorpus's
25 empties). Model pinned `jev-1.13.0`, one noul per document, medians over
three shuffled repeats — the fixed request shape from the pilot's autopsy.

FiQA is the judge's **biggest lift of the three datasets** (+0.126 over BM25;
SciFact +0.084, NFCorpus +0.030) and the reason is visible in the shortlist:
finance QA relevance is phrase-level ("business expense on a business trip"),
and BM25's word-overlap ranking leaves real relevant documents far below
rank 10 where the judge, reading the document, recovers them.

## The finding: the confidence is worse than useless as a threshold here

ECE **0.3109** over 19,440 (probability, relevance) pairs — three times
SciFact's 0.1023. The curve is still monotone (the judge discriminates), but
the top bin is the whole story: **mean confidence 0.93, actual relevance
0.34**. Bin-by-bin curve in `fiqa-full-run.json`. On a sparse-judgement
corpus a Jev probability near 1.0 still means "about a one-in-three chance
the qrels call this relevant" — which is exactly the failure mode of
thresholding a raw probability. The ordering is worth +0.126 nDCG; the number
itself must never gate.

## Reproduce

```sh
# corpus: fetch the BEIR fiqa.zip, extract corpus.jsonl / queries.jsonl / qrels/test.tsv
python3 load.py fiqa/corpus.jsonl fiqa          # this repo's loader, title+text fields
XERJ_URL=http://localhost:<port> python3 raw_bench_full.py 648 fiqa
# -> fiqa-full-run.json (aggregates, reliability curve, per-query numbers)
```

Run log: repeat 1 bm25=0.2382 jev=0.3648 · repeat 2 bm25=0.2382 jev=0.3622 ·
repeat 3 bm25=0.2382 jev=0.3636 — the BM25 arm is deterministic across
repeats (same engine, same index), the Jev arm wobbles ±0.0013, consistent
with the provider non-determinism measured on the other two datasets.
