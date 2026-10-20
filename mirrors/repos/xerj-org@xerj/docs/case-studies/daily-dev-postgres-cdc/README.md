# Case study: auto-replicate Postgres → XERJ (CDC) + hybrid search — for daily.dev

**Who:** [Ido Shamun](https://github.com/idoshamun), founder of
[daily.dev](https://daily.dev) — the personalized developer news feed (1000+
sources, open-source API at
[`dailydotdev/daily-api`](https://github.com/dailydotdev/daily-api)). daily.dev
runs on Postgres and uses `pgvector` for semantic features.

**His ask:** *"Interesting! is it possible to replicate automatically from pg?"* —
i.e. keep a search/analytics copy in XERJ **in sync with Postgres automatically**,
then run **hybrid (keyword + vector) queries** over it, moving the search workload
off `pg tsvector + pgvector`.

**Answer: yes — and it's tested end-to-end below.** Real Postgres 16 + pgvector
0.8.2 with **logical replication**, a CDC consumer that streams every
INSERT/UPDATE/DELETE into XERJ (with EmbeddingGemma vectors), then hybrid search.
Every result here is real output from the scripts in this directory.

---

## Grounded in daily.dev's real schema

Modeled on the actual `Post` entity in `daily-api`
([`src/entity/posts/Post.ts`](https://github.com/dailydotdev/daily-api/blob/main/src/entity/posts/Post.ts)):
`title`, `summary`, `tagsStr`, `sourceId`, engagement (`views`, `upvotes`,
`comments`, `score`, `trending`), a **`tsv` tsvector** (they already do lexical
search in pg), and — crucially — a **`metadataChangedAt`** watermark column
(daily.dev bumps it on every change). We add a `pgvector` `embedding` column, which
is where the "moving off pgvector" question lives: **pg's `tsvector` and `pgvector`
don't fuse into one ranked hybrid result** — you run two queries and merge in app
code. That's the friction this removes.

---

## The pipeline (tested)

```
 Postgres (daily.dev `post` table, pgvector)
   │  logical replication slot  (WAL → logical decoding)
   ▼
 cdc_sync.py  — reads changed ids, fetches current rows,
   │            embeds title+summary, bulk-upserts / deletes
   ▼
 XERJ `posts` index  (text for BM25  +  dense_vector for kNN, one store)
   │
   ▼
 hybrid query  (BM25 + vector, one request)   +   rc.6 knn+aggregations
```

### 1. Automatic replication — proven live

Initial load streamed 8 posts. Then three live changes in Postgres:
```sql
UPDATE post SET upvotes=2500, trending=99 WHERE id='p7';   -- engagement update
INSERT INTO post (...) VALUES ('p9','WebAssembly beyond the browser', ...);  -- new post
DELETE FROM post WHERE id='p5';                             -- removed post
```
One `cdc_sync.py` pass (drains the slot → XERJ), real output:
```
[cdc] synced 2 upserts, 1 deletes to XERJ  changed ids: [('p7','UPDATE'),('p9','INSERT'),('p5','DELETE')]
  p7 upvotes now 2500 trending 99 (updated)
  p5 deleted from XERJ ✓
  p9 present: WebAssembly beyond the browser
```
The WAL slot captured every mutation; XERJ reflects the update, the insert, and the
delete — no manual reindex. Run the consumer on a loop (`--loops N`) or as a daemon
for continuous, near-real-time sync.

### 2. Hybrid search with **RRF fusion** — the thing pg can't do cleanly

XERJ has a first-class `hybrid` query with **reciprocal-rank fusion** built in — no
app-side merge. Query *"ditching the JVM search stack for something cheaper"*
(semantic; little literal overlap):

```json
POST /posts/_search
{ "query": { "hybrid": {
    "queries": [
      { "query": { "match": { "summary": "ditching the JVM search stack for something cheaper" } }, "weight": 1.0 },
      { "query": { "knn": { "field": "vec", "query_vector": [...], "num_candidates": 9 } }, "weight": 1.0 }
    ],
    "fusion": { "type": "rrf", "k": 60 } } } }
```
Real output:
```
LEXICAL only (BM25 ≈ pg tsvector):   Why we moved off Elasticsearch
VECTOR only (≈ pgvector):            Why we moved off Elasticsearch
                                     The cost of microservices   ← semantically near but off-topic
RRF HYBRID (fused, one request):     0.03279 Why we moved off Elasticsearch
                                     0.03175 The cost of microservices
                                     0.03151 Building a vector search engine from scratch
```
`fusion: rrf` fuses the two ranked lists by `Σ weight/(k + rank)` — no manual score
normalization (BM25 and cosine live on different scales; RRF is rank-based, so it
sidesteps that). `linear` fusion and per-query `weight`s are also supported. In
Postgres this is two separate queries (`tsvector` + `pgvector`) merged in app code;
here it's one query with principled fusion, and you can still layer engagement
(`upvotes`, `trending`) via function-score.

### 3. Bonus (rc.6): semantic slice + engagement analytics in one request
*"of posts about AI/ML, which sources, and avg upvotes?"* — one `knn`+`aggs` call
returns the source breakdown with average upvotes per source. (See the
[analytics case study](../calltree-analytics/) for that feature.)

---

## Step-by-step (runnable)

Prereqs: Docker, XERJ on `:9200`, Ollama serving `embeddinggemma`, `pip install psycopg2-binary`.

```bash
# 1. Postgres 16 + pgvector, logical replication ON
docker run -d --name pg-daily -e POSTGRES_PASSWORD=pw -e POSTGRES_DB=dailydev -p 5433:5432 \
  pgvector/pgvector:pg16 -c wal_level=logical -c max_replication_slots=4 -c max_wal_senders=4

# 2. schema (daily.dev-modeled) + trigger + logical replication slot
docker cp setup.sql pg-daily:/tmp/ && docker exec pg-daily psql -U postgres -d dailydev -f /tmp/setup.sql
#    …then INSERT your posts (see the seed block in the case study history)

# 3. initial sync + continuous CDC
python3 cdc_sync.py --init            # create the XERJ `posts` index + first drain
python3 cdc_sync.py --loops 100       # near-real-time: drain the slot every 2s

# 4. hybrid query (see the demo in this README)
```

`cdc_sync.py` uses the slot as a **change signal** (which ids changed + op), then
reads the *current* row from Postgres and upserts to XERJ — a robust CDC pattern
that avoids brittle decoder-format parsing and always converges to Postgres state.

### Push-streaming + LSN checkpointing (`cdc_stream.py`) — production shape

`cdc_sync.py` polls (`get_changes`). `cdc_stream.py` is the **true push-streaming**
consumer: psycopg2's `LogicalReplicationConnection.consume_stream()` **blocks on the
WAL** (no polling), and after each change is durably applied to XERJ it calls
`send_feedback(flush_lsn=…)` so Postgres advances the slot's `confirmed_flush_lsn`.

```bash
python3 cdc_stream.py     # blocks; applies changes the instant they commit
```

**Proven live** — an INSERT in Postgres appears in XERJ within seconds, no poll:
```
[stream] INSERT p10 -> XERJ (errors=False)  LSN=27860016  [checkpointing]
```

**Exactly-once-convergent (LSN checkpointing), proven:** stop the consumer → change
data while it's *down* (`UPDATE p1 upvotes=9999`, `INSERT p11`) → XERJ goes stale
(the WAL is retained by the slot) → **restart:**
```
[stream] consuming WAL from confirmed LSN ...
[stream] UPDATE p1 -> XERJ  LSN=27863424  [checkpointing]
[stream] INSERT p11 -> XERJ  LSN=27863976  [checkpointing]
  p1 upvotes: 9999   p11: Offline change test
```
It resumed from the last checkpoint and applied **exactly** the missed changes — no
re-sync, no loss. Combined with upsert/delete-by-id (idempotent replays), this gives
**at-least-once delivery that converges to Postgres state**; the LSN feedback means
a crash never loses a change and never forces a full rebuild.

---

## Production CDC options (honest tradeoffs)

| approach | latency | setup | notes |
|---|---|--:|---|
| **`test_decoding` slot** (this demo) | seconds (polled `get_changes`) | built-in | readable output; great for a consumer you own; the pattern shown here |
| **`pgoutput` slot** (built-in) | streaming | built-in | native logical-replication protocol; binary — consume via a client lib |
| **`wal2json` slot** | streaming | plugin | JSON change events; easy to parse; needs the plugin installed |
| **Debezium (Kafka Connect)** | streaming | heavier | industry standard for large fleets; exactly-once, schema history, many sinks |
| **watermark polling** (`metadata_changed_at > last_seen`) | seconds–minutes | trivial | daily.dev's schema already has the column; no slot; simplest, at-least-once |

For daily.dev's scale, **Debezium → the consumer**, or a **`pgoutput` slot** read
by a small service, is the production shape; the `test_decoding` consumer here is
the same logic without the Kafka footprint. All of them feed the identical
transform+embed+bulk step.

## Scaling

- **Embedding is the cost, not the sync.** Only changed rows are re-embedded (the
  slot tells you which). A stats-only update (`upvotes`) can skip re-embedding —
  gate on whether `title`/`summary` changed. Batch embeds for throughput.
- **Backfill once, stream forever.** Initial load is a bulk pass; steady state is
  just the change stream. Re-embedding on a model change is a backfill job, not a
  query-time cost.
- **Object-store-backed XERJ** keeps the search copy cheap; hot segments cache.
- **Multi-tenant / per-source:** filter by `source_id`, or per-tenant indices; the
  vector `similarity`/dims are per-field so different embedding models coexist.
- **Ranking:** fold `upvotes`/`trending`/recency into the hybrid score with
  function-score / boosts — feed ranking and search share one index.

## Comparison with staying on pg/pgvector

| | Postgres + pgvector + tsvector | XERJ (CDC from pg) |
|---|---|---|
| hybrid keyword+vector ranking | two queries merged in app code | **one query, fused ranking** |
| search load vs OLTP | competes with primary DB | **offloaded**; pg stays transactional |
| aggregations over a semantic slice | awkward | `knn`+`aggs` in one request (rc.6) |
| keeping in sync | you build it | **logical-replication CDC**, shown here |
| BM25 relevance | `ts_rank` (coarse) | real BM25 + analyzers |
| operational model | one DB (simple) | +1 system, but search/analytics isolated |

**When to stay on pg:** small corpora, low query volume, simplicity over search
quality. **When XERJ wins for daily.dev:** feed/search at scale where hybrid
ranking + engagement signals + analytics matter and you don't want search load on
the primary, kept in sync automatically.

## Honest limitations

1. **Embedding model is yours** — retrieval quality is the model's job; XERJ stores
   and searches the vectors.
2. **RRF `k` and weights need tuning** per corpus — RRF removes the BM25-vs-cosine
   scale problem, but the fusion constant `k` and per-query `weight`s still shape
   ranking; A/B them against click/upvote signals.
3. **`learned` fusion is not implemented** — `rrf` and `linear` are; a learned
   fuser (train weights on engagement) is a future item.
4. **Backfill embeds cost** — a model change means re-embedding the corpus (a
   backfill job); steady-state CDC only re-embeds changed rows (and can skip
   re-embed on stats-only updates).

## Resolved (previously listed as gaps)
- ~~No fused RRF node~~ → **RRF exists and is first-class** (`hybrid` + `fusion:rrf`);
  the earlier note was a request-syntax error. `weight`s and `linear` also supported.
- ~~`test_decoding` only polled~~ → **`cdc_stream.py` is true push-streaming** via
  `consume_stream()` (no polling).
- ~~Exactly-once needs care~~ → **LSN checkpointing implemented** (`send_feedback`);
  proven to resume from the last confirmed LSN and catch offline changes with no loss.

## Files
- [`setup.sql`](setup.sql) — daily.dev-modeled schema + trigger + logical slot.
- [`cdc_sync.py`](cdc_sync.py) — polled CDC consumer (slot → embed → XERJ bulk).
- [`cdc_stream.py`](cdc_stream.py) — **push-streaming** consumer + **LSN checkpointing**
  (the production shape).
