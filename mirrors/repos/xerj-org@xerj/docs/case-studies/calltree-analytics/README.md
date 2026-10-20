# Case study: deep-research analytics over support conversations (calltree.ai)

**Who:** [calltree.ai](https://calltree.ai) runs AI over customer support interactions.
They have per-customer embedding models that cluster conversations by issue type and
score them against canonical records (knowledgebase articles, team guidance), and
they want **"deep research" style reports** over past interactions — e.g.
*"of calls about wifi issues, how many are related to 2.4GHz vs 5GHz, and what are
the key issues?"* That single question bundles **retrieval, aggregation, labeling,
schema, and embedding** tasks.

**The problem:** there was no good place to do **SQL-style columnar analytics +
embedding retrieval together**. Shimming it onto DuckDB (OLAP) plus a separate
vector store meant ETL between systems, no joins across them, and a poor developer
experience.

**What this case study shows:** XERJ does this in one store — tested live on a
running engine with real 768-dim **EmbeddingGemma** embeddings over 130 support
conversations — **including a new engine feature built for this use case:
kNN + aggregations in a single request (rc.6).** Every number below is real output
from the scripts in this directory.

---

## The answer, in one request (with the rc.6 feature)

`03_deep_research.py`, real output:

```
"of calls about wifi issues, how many 2.4 vs 5GHz, and what are the key issues?"

retrieved 80 nearest wifi calls; aggregated in the same request:
  2.4GHz  29 (54%)  csat_p50=4.0  aht=897s  issues: channel-overlap, congestion, disconnects, legacy-device
  5GHz    25 (46%)  csat_p50=4.0  aht=924s  issues: range, disconnects, congestion

deep-research narrative (LLM over the retrieved examples):
  The key issue is that the 5GHz signal is weak in a nearby room, dropping to 2.4GHz
  and resulting in slower speeds.
```

One `POST /_search` did the **semantic retrieval** (kNN over "wifi issues"), the
**band split** (2.4 vs 5GHz), **key issues** per band, **CSAT** percentile and
**AHT** average, *and* returned example conversations — then one LLM call turned the
retrieved examples into the narrative. That is the whole deep-research loop.

---

## Step-by-step guide (runnable)

**Prereqs:** XERJ on `:9200`; Ollama serving an embedding model (`embeddinggemma`)
and an LLM (`qwen2.5`). Swap in your per-customer embedding model in step 2.

### 1. Data — conversations + canonical KB
```bash
python3 01_make_dataset.py     # 130 support convos (structured cols + free text) + 5 KB articles
```
Each conversation carries structured columns (`band`, `issue`, `device`, `csat`,
`handle_time_s`, `resolution`, `agent`, `channel`, `day`) and a `body`.

### 2. Embed + index (one store: columns + text + vectors)
```bash
python3 02_embed_index.py      # embed body -> dense_vector; index into `conversations` + `kb`
```
Mapping — the key point is **structured columns, full-text, and the vector live
together**:
```json
{ "band":{"type":"keyword"}, "issue":{"type":"keyword"}, "csat":{"type":"integer"},
  "handle_time_s":{"type":"integer"}, "body":{"type":"text"},
  "vec":{"type":"dense_vector","dims":768,"similarity":"cosine"} }
```

### 3. The research task
```bash
python3 03_deep_research.py     # the single-request kNN+aggs deep-research report
```

### The composable primitives (each is a real XERJ query)

| task in the question | XERJ primitive | notes |
|---|---|---|
| "calls about wifi issues" | `knn` over the topic vector | discriminates wifi from billing/TV: 74/100 nearest are wifi |
| "how many 2.4 vs 5GHz" | `terms`/`filters` agg **on the kNN slice** | rc.6 — one request |
| "key issues" | `terms` (raw) or `significant_terms` (two-step, see below) | over-represented issue labels |
| CSAT / AHT / trend | `percentiles`, `stats`, `avg`, `date_histogram` | compose in the same `aggs` |
| "vs canonical records" | `knn` into the `kb` index | nearest KB + cosine = distance-to-canonical |
| the narrative | `top_hits` / kNN hits → LLM | grounded evidence in the same response |

---

## The engine feature we built for this: kNN + aggregations (rc.6)

**The gap (before):** aggregations did **not** run alongside a `knn`/semantic query.
`knn`+`aggs`, `query.knn`+`aggs`, and `bool.filter:[knn]`+`aggs` all returned no
buckets. You had to do it in two steps (kNN → collect ids → separate filtered
aggregation) — the friction that made the DuckDB shim tempting.

**The fix (rc.6):** aggregations now run over the **retrieved top-`k` neighbour
set** (Elasticsearch top-level-knn semantics), independent of the `from`/`size` hit
page. Implementation: the shared kNN result assembler (`knn_result_from_scored`,
used by *all* three executors — HNSW, exact brute-force, multi-kNN) computes the
aggregation over the top-k sources when `aggs` is present. An `aggs`-bearing kNN
routes to the **exact brute-force** path, because ANN recall is <100% and aggregate
counts must be exact, not approximate.

**Validated:**
- Integration test `test_knn_plus_aggregations_single_request` — asserts the agg
  runs over the exact semantic slice (far docs excluded), passes; no kNN
  regressions.
- Live, above, with real embeddings.

**Request shape:**
```json
POST /conversations/_search
{ "query": { "knn": { "field": "vec", "query_vector": [...], "k": 200, "num_candidates": 400 } },
  "size": 3,
  "aggs": { "by_band": { "terms": { "field": "band" },
            "aggs": { "csat": { "percentiles": { "field":"csat","percents":[50] } } } } } }
```

**Honest limitation:** `significant_terms` over a kNN slice returns empty today — it
needs a background corpus the vector path doesn't yet supply. Use `terms` (raw
counts) inside a kNN slice, or the two-step pattern when you need statistical
significance against the whole index. (Filed as the rc.6 follow-up.)

See [`../../../engine/CHANGELOG-rc6.md`](../../../engine/CHANGELOG-rc6.md).

---

## Recommended architecture (embed → label → materialize → analyze)

The pattern that scales, and the mental-model shift away from "SQL+embedding in one
query":

```
             your per-customer embedding model
                        │  (at ingest)
   conversation ──► embed(body) ──► vector          ─┐
                    ├─ cluster/issue label           ─┤  materialize as
                    ├─ nearest_kb + kb_distance       ─┤  COLUMNS on the doc
                    └─ band, device, csat, aht …      ─┘
                              │
   XERJ  (one index · object-store backed · ES-wire)
                              │
   recurring reports  ─► columnar aggs on the label columns      (no kNN needed)
   ad-hoc "calls about X" ─► knn + aggs in one request (rc.6)
   report body ─► top_hits / knn hits → LLM synthesis
```

The expensive semantic work (labeling, distance-to-canonical) happens **once at
ingest by your model**; the recurring reports become plain, fast columnar
aggregations sitting next to the vectors and labels. "Minimize loss against
canonical records" becomes `avg(kb_distance)` by issue, with high-distance outliers
= novel/uncovered issues — a straight aggregation.

---

## Scaling guide

- **Object-store backend (your setup).** Segments live on object storage; hot
  segments are cached. Aggregations read columnar doc-values, so an analytics query
  scans columns, not `_source`. Because your time-to-answer is LLM-bound, the extra
  latency of a cold-segment fetch is usually in the noise — and warm reports are
  fast. Keep the columns you aggregate on (`band`, `issue`, `csat`, `kb_distance`,
  `day`) as typed fields so they get doc-values.
- **Sizing the semantic slice (`k` / `num_candidates`).** `k` is the neighbour pool
  the aggregation runs over; set it to how many conversations you want in the slice
  (e.g. `k: 500`). `num_candidates` is the ANN fan-out for the plain (non-agg) path;
  agg queries run exact brute-force, so `num_candidates` is ignored there — cost
  scales with corpus size × dims for the scan. For very large corpora, pre-filter
  with a cheap keyword/date `bool` before the vector step, or use the
  materialized-label path (no kNN) for recurring reports.
- **Ingest / labeling pipeline.** Do embedding + labeling + nearest-KB in your model
  at ingest and bulk-index the results; this is the same "index once, query cheaply"
  economics that makes the reports scale. Re-embedding on a model change is a
  reindex job, not a query-time cost.
- **Sharding & multi-tenant.** One index per customer (clean per-customer embedding
  space and deletion) or a shared index with a `customer` keyword filter; the vector
  `similarity`/dims are per-field, so per-customer models fit naturally as separate
  indices.
- **Cost lever.** The analytics are columnar aggregations on object-store-backed
  segments — you pay storage + occasional fetch, not a always-on OLAP cluster. The
  vector index (HNSW) is built for the plain-retrieval path; exact agg scans don't
  need it, so an analytics-heavy workload can even skip graph build to save memory.

---

## Comparison with other approaches

| approach | analytics | embeddings | one store? | the friction |
|---|---|---|---|---|
| **DuckDB shim + vector store** (your current) | ✅ great SQL | ✅ (separate) | ❌ | ETL between OLAP and vectors; no cross-system join; two things to operate |
| **Postgres + pgvector** | ✅ full SQL | ✅ | ✅ | vector search + large-scan analytics compete for the same OLTP engine; kNN+GROUP BY works but scales poorly on big corpora; no object-store columnar tier |
| **Elasticsearch / OpenSearch** | ✅ aggregations | ✅ kNN | ✅ | closest analog; kNN+aggs supported; heavier ops, JVM memory, and hot-storage cost model |
| **Warehouse (Snowflake/BigQuery/Databricks) + vector add-on** | ✅ best-in-class SQL | ⚠️ bolt-on | ⚠️ | great for the SQL half; embedding retrieval is a second-class citizen; latency + cost for interactive report loops |
| **Dedicated vector DB (Pinecone/Weaviate/Qdrant)** | ⚠️ limited aggs | ✅ | ✅ vectors | strong retrieval, weak columnar analytics; you'd still need a warehouse for the SQL half |
| **XERJ (this)** | ✅ ES-compatible aggs | ✅ kNN/semantic | ✅ | one store, object-store backed, **kNN+aggs in one request (rc.6)**; gaps: no fused RRF hybrid, thin SQL surface, `significant_terms`-over-kNN pending |

**Where XERJ fits calltree.ai specifically:** you already own the embedding/labeling
step; you want the *analytics + retrieval + evidence* in one place with an
object-store cost model and an ES-compatible surface. XERJ gives exactly that, and
the one real gap for your example task (aggregate a semantic slice in one call) is
now closed in rc.6.

## Honest limitations (what to weigh)

1. **Hybrid RRF isn't exposed** — approximate lexical+vector fusion with
   `bool.should[match, knn]` or re-rank client-side.
2. **SQL is a thin convenience layer** (`SELECT/WHERE/GROUP BY→terms/COUNT`) — don't
   port DuckDB SQL 1:1; drive the aggregation API (or generate its JSON).
3. **`significant_terms` over a kNN slice** returns empty (background not wired) —
   use `terms` in-slice or the two-step for significance.
4. **kNN quality is your embedding model's job** — XERJ stores/searches vectors; the
   clustering quality is your per-customer model, which is where you already invest.

## Run it
```bash
python3 01_make_dataset.py && python3 02_embed_index.py && python3 03_deep_research.py
```
