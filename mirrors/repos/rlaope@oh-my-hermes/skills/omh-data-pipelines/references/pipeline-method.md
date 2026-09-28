# Pipeline Method

Load this while planning pipeline work. OMH prepares; the operator or the executor runs every job, query and check, and each step is `prepared` until its output is observed.

## 1. Idempotency: what makes a rerun safe

| Pattern | Use when | A row written twice |
| --- | --- | --- |
| natural-key upsert (`MERGE`, `INSERT ... ON CONFLICT`) | the sink row has a business key | updates in place |
| event-id dedupe within a window | events carry a stable id | dropped if inside the window; state the window |
| partition overwrite | the load is by date or hour | the partition is replaced whole |
| idempotency key on the producer | a service emits the events | the consumer ignores the repeat |

An `INSERT` or append with none of these is not idempotent. Fix the write before repairing the rows, or the repair is undone by the next rerun.

## 2. Schema change compatibility

| Change | Downstream impact |
| --- | --- |
| add a nullable column | additive; readers that select `*` may still break |
| widen a type (int to bigint) | widening; check readers with a fixed schema |
| rename or drop a column | breaking; adapt or retire every reader first |
| change a type's meaning or unit | breaking even when the type is unchanged |
| change the partition or key | breaking for every rerun and every incremental reader |

## 3. Replay and backfill

1. Bound the window and name the target partitions, tables or offsets.
2. Confirm the write is idempotent (section 1).
3. Pause or isolate downstream readers, or write to a staging target and swap.
4. Run the bounded window; record the observed row counts per partition.
5. Pass the quality gate (section 4), then publish or resume readers.
6. Rerun one partition and confirm nothing changes; that is the idempotency proof.

For a stream, name the consumer group and the offsets or timestamps to reset to, and whether downstream sinks dedupe by event id.

## 4. Data-quality gate

| Check | Stops the load when |
| --- | --- |
| row count against the prior comparable window | outside a stated band |
| uniqueness on the sink key | any duplicate |
| null rate on required columns | above a stated threshold |
| freshness | the newest row is older than the schedule allows |
| referential match to a parent table | orphans above a stated threshold |

## 5. Lineage

Take lineage from the orchestrator or transformation graph (the dbt manifest, the Airflow DAG, an OpenLineage record) first. Readers found only by searching queries, dashboards or exports are marked as such, because a search misses what it did not index.
