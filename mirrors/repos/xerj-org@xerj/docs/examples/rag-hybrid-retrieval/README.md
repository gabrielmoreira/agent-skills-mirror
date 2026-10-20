# Hybrid retrieval for RAG chatbots (dropping in for pgvector, adding BM25)

A common RAG-chatbot shape: documents → chunks → embeddings → **pure cosine**
similarity (often Supabase/`pgvector`) → feed top-k to an LLM. It works well until
a user pastes an **exact term** — an error code, a function name, a config key, a
version — and dense-only retrieval quietly returns the *wrong* chunk. This example
shows that failure on a real corpus, and how XERJ fixes the **retrieval half** by
adding BM25 and fusing it with vectors (RRF) — same chunks, same embeddings.

**Tested live** against a running XERJ with real 768-dim EmbeddingGemma vectors over
18 doc chunks. Every number below is real output.

## Candid scope — what XERJ does and doesn't touch

RAG has several hard parts, and **most of them are not retrieval**:

| RAG concern | who owns it |
|---|---|
| chunking strategy (size, overlap, boundaries) | **your app** — XERJ doesn't chunk |
| which embedding model, how you embed | **your app** — XERJ stores/searches the vectors you send |
| LLM wiring, prompt, context assembly, streaming | **your app** |
| **retrieval: cosine + BM25 + hybrid fusion, filters, at scale** | **XERJ** |

So this is honest about its lane: if your pain is chunking or the LLM loop, XERJ
won't move that needle. If your retrieval is **pure cosine and you want hybrid**,
that's exactly the half this replaces — and it's a drop-in: keep your chunker,
embedder, and LLM; swap the `pgvector` similarity query for an XERJ hybrid query.

## The failure: dense-only buries exact terms

`03_retrieval_compare.py` — rank of the *correct* chunk (lower is better):

```
  exact-term query            cosine   BM25  hybrid
  E4304                           13      1       3
  createCheckoutSession           14      1       1
  WEBHOOK_SIGNING_SECRET           4      1       1
  v2.11                            1      1       1
```

Pure cosine puts the chunk that literally defines `E4304` at **#13** and
`createCheckoutSession` at **#14**. In a RAG chatbot that retrieves top-4 or top-5,
**those chunks never enter the context window** — the LLM never sees them. Asked
*"E4304"*, dense-only returns `E5012 — gateway timeout` at #1: a different error
that's *semantically adjacent* (both are "errors") but factually wrong. This is the
well-known lexical gap of dense retrieval: embeddings blur rare tokens (codes,
identifiers, versions) that users paste verbatim.

BM25 nails all of them at #1. **Hybrid (RRF)** keeps BM25's exactness (E4304 → #3,
inside a top-k window; the rest → #1) *and* keeps vectors' concept-matching, so it's
robust whether the query is an exact paste or a fuzzy question.

## Why it decides the answer, not just the ranking

Retrieval quality is answer quality in RAG. With the *wrong* chunk retrieved
(dense-only → `E5012`), the grounded LLM can only say *"the context doesn't cover
E4304"* — a refusal at best, a confident wrong answer at worst. With hybrid
retrieving a chunk that actually discusses E4304, the LLM answers correctly
(*"E4304 is not retryable"*). Same model, same prompt — **the retrieval changed the
outcome.**

## The hybrid query (RRF fusion, one request)

```json
POST /docchunks/_search
{ "query": { "hybrid": {
    "queries": [
      { "query": { "match": { "text": "<user question>" } }, "weight": 1.0 },
      { "query": { "knn":   { "field": "vec", "query_vector": [...], "num_candidates": 50 } }, "weight": 1.0 }
    ],
    "fusion": { "type": "rrf", "k": 60 } } },
  "size": 5 }
```
RRF fuses the two ranked lists by `Σ weight/(k + rank)` — rank-based, so it needs no
score normalization between BM25 and cosine (which live on different scales). Tune
`weight`s toward lexical for identifier-heavy corpora, toward vector for prose;
`linear` fusion is also available.

## Drop-in migration from pgvector

```
your pipeline (unchanged):   docs → chunk → embed(model)  ─┐
                                                            ▼
before:  INSERT into pgvector; SELECT ... ORDER BY embedding <=> query LIMIT k   (cosine only)
after:   bulk-index chunks {text, vec} into XERJ; POST _search {hybrid: rrf}     (BM25 + vector)
                                                            │
your LLM loop (unchanged):   retrieved chunks → prompt → answer
```
You send the same embedding vectors; you gain BM25 + hybrid + keyword filters
(`doc`, `section`, `version`) in the same query, and the retrieval leaves your
primary DB.

## Run it

Prereqs: XERJ on `:9200`, Ollama serving `embeddinggemma` (+ an LLM for the answer step).
```bash
python3 01_corpus.py            # 18 technical-doc chunks (identifiers + concepts)
python3 02_embed_index.py       # embed -> dense_vector; index `docchunks`
python3 03_retrieval_compare.py # the cosine vs BM25 vs hybrid rank table
```
Swap `embeddinggemma` for your model; the retrieval layer is model-agnostic.

## Honest limitations

- **Hybrid isn't automatically #1 for every exact term** — equal-weight RRF put
  `E4304` at #3 (diluted by cosine's #13). #3 is inside a normal top-k window (the
  point), but weight-tuning or a light query router (identifier-detected → lexical
  weight up) sharpens it.
- **Retrieval quality ≠ answer quality alone** — chunking and the prompt still
  matter; XERJ improves the retrieval input, not the generation.
- **Embedding quality is your model's job.** XERJ stores and searches vectors; it
  doesn't make them better.
