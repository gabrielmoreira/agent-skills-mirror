---
title: SQL
category: Language
x-claim-provenance:
- claim: Read Committed is the default isolation level in PostgreSQL.
  source: https://www.postgresql.org/docs/current/transaction-iso.html
- claim: REPEATABLE READ is the default isolation level for InnoDB.
  source: https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-isolation-levels.html
  scope: MySQL 8.4.
- claim: In PostgreSQL, NOT IN yields null rather than true if the left-hand expression is null, or if there are no equal right-hand values and at least one right-hand row yields null.
  source: https://www.postgresql.org/docs/current/functions-subquery.html
- claim: In PostgreSQL, rows returned without a chosen sort are in an unspecified order that depends on scan and join plan types and on-disk order and must not be relied on.
  source: https://www.postgresql.org/docs/current/queries-order.html
- claim: A standard PostgreSQL index build locks the table against writes, while CREATE INDEX CONCURRENTLY builds without locking out writes but takes longer, cannot run inside a transaction block, and leaves an invalid index behind if it fails.
  source: https://www.postgresql.org/docs/current/sql-createindex.html
---

The exact database product and configured version, schema, collation, isolation defaults, migration framework, deployment topology, permissions, and representative data shape decide which syntax and features apply, and the same statement can behave differently across products. PostgreSQL defaults to Read Committed isolation while MySQL's InnoDB defaults to Repeatable Read, so code that relies on one product's default isolation is exposed to different anomalies on the other. Null, precision, collation, time zone, ordering, key and resource identity, constraint, transaction, locking, retry, and compatibility semantics at the boundary are behavioral contracts.

Query semantics run through joins, cardinalities, predicates, implicit casts, three-valued logic, grouping, window frames, ordering ties, duplicate handling, defaults, generated values, triggers, cascades, views, functions, and row-level security. Three-valued logic is the usual trap: in PostgreSQL, `x NOT IN (subquery)` is null rather than true once the subquery returns a null and no match, so the row silently drops out of a `WHERE` clause. Without `ORDER BY`, row order depends on the plan and physical layout and must not be relied on, even when it looks stable.

Data migration and schema migration are separate steps when their failure and rollback properties differ, and a DDL statement, backfill, index build, or type change may rewrite, lock, truncate, or replace data depending on the product and version. A plain `CREATE INDEX` in PostgreSQL blocks writes to the table for the whole build, while `CREATE INDEX CONCURRENTLY` keeps writes flowing but takes longer, cannot run inside a transaction block, and leaves an invalid index behind if it fails.

The real execution plan with representative statistics and parameters is the observable state for cost: estimated and actual rows can differ, and scans, seeks, join algorithms, spills, sorts, memory grants, partition pruning, lock waits, and parameter sensitivity show where cost goes. Schema renames and changes can reach:

- migrations and ORM-generated SQL
- prepared statements, connection settings, and transaction wrappers
- retries, replicas, and permissions
- background jobs and downstream consumers

Behavioral evidence covers empty, null, duplicate, boundary, concurrent, and failure cases inside the intended transaction and isolation behavior, and unordered result order is not a stable expectation. Migration evidence from a production-shaped disposable copy includes the actual plan, lock duration, write amplification, rollback or roll-forward path, and any destructive replacement that deployment would introduce. Verification evidence covers constraints, permissions, triggers, replication or read-after-write expectations, transaction atomicity, and data counts or checksums appropriate to the change, and a change must preserve collation, precision, ordering, and isolation semantics unless altering them is part of its requested outcome.
