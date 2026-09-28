# Engine Lock Tables

Load this while planning database work. OMH never connects to a database: every statement, plan, and lock wait below is something the executor or operator runs and reports back. Lock behaviour differs by engine and by version, so state both before reading a row here, and when the version is unknown plan for the most restrictive row.

## 1. PostgreSQL lock modes by statement

| Statement | Lock taken | Blocks | Online alternative |
| --- | --- | --- | --- |
| `CREATE INDEX` | `SHARE` | writes for the whole build | `CREATE INDEX CONCURRENTLY` (`SHARE UPDATE EXCLUSIVE`; no transaction block; an invalid index is left behind on failure and must be dropped) |
| `DROP INDEX` | `ACCESS EXCLUSIVE` | reads and writes | `DROP INDEX CONCURRENTLY` |
| `ALTER TABLE ... ADD COLUMN` (nullable, or constant default on 11+) | `ACCESS EXCLUSIVE`, brief | everything, while queued behind long transactions | set `lock_timeout` and retry |
| `ALTER TABLE ... ADD COLUMN ... DEFAULT volatile()` | `ACCESS EXCLUSIVE` + table rewrite | everything for the rewrite | add nullable, backfill in batches, then set the default |
| `ALTER TABLE ... SET NOT NULL` | `ACCESS EXCLUSIVE` + full scan | everything for the scan | `ADD CONSTRAINT ... CHECK (col IS NOT NULL) NOT VALID`, `VALIDATE CONSTRAINT`, then `SET NOT NULL` (12+ skips the scan) |
| `ALTER TABLE ... ADD FOREIGN KEY` | `SHARE ROW EXCLUSIVE` on both tables + scan | writes | `ADD CONSTRAINT ... NOT VALID`, then `VALIDATE CONSTRAINT` |
| `ALTER TABLE ... ALTER COLUMN TYPE` | `ACCESS EXCLUSIVE` + rewrite (most types) | everything | new column, dual write, backfill, switch, drop |
| `VACUUM FULL`, `CLUSTER` | `ACCESS EXCLUSIVE` + rewrite | everything | `pg_repack` or plain `VACUUM` |

Every DDL statement on a live table runs under `SET lock_timeout = '2s'` (or the service's tolerance) with a retry. Without it, a statement queued behind one long transaction blocks every query that arrives after it, which is how a sub-second `ALTER` becomes an outage.

## 2. MySQL (InnoDB) online DDL

| Operation | `ALGORITHM` | `LOCK` | Note |
| --- | --- | --- | --- |
| Add a secondary index | `INPLACE` | `NONE` | concurrent DML allowed; brief metadata lock at start and end |
| Add a column (8.0.12+, last position) | `INSTANT` | none | no rebuild |
| Add a column elsewhere, or before 8.0.12 | `INPLACE` with rebuild | `NONE` | rebuilds the table |
| Change a column type | `COPY` | `SHARED` | blocks writes; use `gh-ost` or `pt-online-schema-change` |
| Drop the primary key | `COPY` | `SHARED` | blocks writes |

State `ALGORITHM=... , LOCK=...` explicitly in the statement so the server refuses instead of silently falling back to a blocking copy. Every DDL still waits for a metadata lock; a long transaction holds it up and queues everything behind it, so bound it with `lock_wait_timeout`.

## 3. Online migration order

1. **Expand**: add the new column, table, or index without breaking current code.
2. **Backfill** in batches keyed on the primary key: a bounded row count per batch, a pause between batches, progress recorded, restartable.
3. **Switch**: deploy code that reads the new shape; dual-write while both exist.
4. **Contract**: drop the old shape only after the switch is observed in production.

Every step carries its statement, the lock it takes and for how long, its timeout, and its rollback. A plan with any step missing lock behaviour or rollback is not ready.

## 4. Index selection and sizing

| Need | Index type |
| --- | --- |
| Equality and range on scalar columns | B-tree, most selective equality column first, range column last |
| Array, JSONB containment, full-text | GIN |
| Geometric, range overlap, nearest neighbour | GiST |
| Huge append-only table ordered by time | BRIN |
| Query touches a known subset | partial index with that `WHERE` |
| Query reads few columns | covering index (`INCLUDE`) for an index-only scan |

Size before proposing: rows times (key width plus about 20 bytes of per-entry overhead), plus fill-factor slack. Every index adds a write per insert and per update of its columns; name that cost next to the read it saves. Cite the observed plan the index changes (`EXPLAIN (ANALYZE, BUFFERS)`), and re-read the plan after the build.

## 5. N+1 queries

The symptom is one query for the list and one more per row, and the count scales with page size. Confirm it from the query log or the ORM's statement counter, not from reading the code. Fix it with an eager load (`JOIN`, `IN (...)` batch, or the ORM's preload) and pin it with a test that asserts the statement count for a page of N rows.

## 6. When to partition or shard

Project rows, bytes, and write rate for 12 to 24 months. Partition when one table's maintenance (vacuum, index builds, retention deletes) outgrows its window; partitioning keeps one node. Shard only when a single primary cannot hold the write rate or the working set after vertical scaling, read replicas, and partitioning; name the shard key, the cross-shard queries it breaks, and the rebalancing plan.
