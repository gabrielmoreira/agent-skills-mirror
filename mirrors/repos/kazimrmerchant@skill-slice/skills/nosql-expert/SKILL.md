---
name: nosql-expert
description: "Models Cassandra, ScyllaDB, and DynamoDB access patterns as tables: high-cardinality partition keys, clustering or sort keys, single-table adjacency lists, GSIs, and duplicated lookup tables. Trigger on hot partitions, ALLOW FILTERING, or DynamoDB single-table design. Never apply MongoDB document schemas or SQL join thinking to these stores."
version: 1.0.1
risk: unknown
source: community
date_added: "2026-02-27"
---

# NoSQL Expert Patterns (Cassandra, ScyllaDB & DynamoDB)

## Overview

This skill provides professional mental models and design patterns for **distributed wide-column and key-value stores** (Apache Cassandra, ScyllaDB, and Amazon DynamoDB).

Unlike SQL (where you model data entities), or document stores (like MongoDB), these distributed systems require you to **model your queries first**. You cannot "add a query later" without migration or creating a new table/index.

> **The Golden Rule:** In SQL, you design the data model to answer *any* query. In NoSQL, you design the data model to answer *specific* queries efficiently.

### The Mental Shift: SQL vs. Distributed NoSQL

| Feature | SQL (Relational) | Distributed NoSQL (Cassandra/DynamoDB) |
| :--- | :--- | :--- |
| **Data modeling** | Model Entities + Relationships | Model **Queries** (Access Patterns) |
| **Joins** | CPU-intensive, at read time | **Pre-computed** (Denormalized) at write time |
| **Storage cost** | Expensive (minimize duplication) | Cheap (duplicate data for read speed) |
| **Consistency** | ACID (Strong) | **BASE (Eventual)** / Tunable |
| **Scalability** | Vertical (Bigger machine) | **Horizontal** (More nodes/shards) |

## When to Use

- **Designing for Scale**: Moving beyond simple single-node databases to distributed clusters.
- **Technology Selection**: Evaluating or using **Cassandra**, **ScyllaDB**, or **DynamoDB**.
- **Schema Modeling**: Designing tables, partition keys, sort keys, or single-table layouts.
- **Performance Tuning**: Troubleshooting "hot partitions", high latency, or uneven traffic in existing NoSQL systems.
- **Microservices**: Implementing "database-per-service" patterns where highly optimized reads are required.

## Prerequisites

- Target database identified (Cassandra/ScyllaDB or DynamoDB).
- A complete list of required **access patterns** (queries) before table design.
- Understanding of expected read/write volume and cardinality of candidate partition keys.
- If running locally on Windows (PowerShell), ensure `cqlsh` or AWS CLI v2 is installed and configured with placeholder credentials (`YOUR_KEY`).

## Procedure

### 1. Query-First Modeling (Access Patterns)

You typically cannot "add a query later" without migration or creating a new table/index.

1. **List all Entities** (User, Order, Product).
2. **List all Access Patterns** ("Get User by Email", "Get Orders by User sorted by Date").
3. **Design Table(s)** specifically to serve those patterns with a single lookup.
4. **Validate** that every access pattern maps to exactly one table or index.

### 2. Choose the Partition Key (PK)

Data is distributed across physical nodes based on the **Partition Key (PK)**.

- **Goal:** Even distribution of data and traffic.
- **Anti-Pattern:** Using a low-cardinality PK (e.g., `status="active"` or `gender="m"`) creates **Hot Partitions**, limiting throughput to a single node's capacity.
- **Best Practice:** Use high-cardinality keys (User IDs, Device IDs, Composite Keys).
- **Split Partition Risk:** For any single partition (e.g., a single user's orders), will it grow indefinitely? If a partition may exceed **10GB**, shard it (e.g., `USER#123#2024-01`).

### 3. Choose Clustering / Sort Keys

Within a partition, data is sorted on disk by the **Clustering Key (Cassandra)** or **Sort Key (DynamoDB)**.

- Enables efficient **Range Queries** (e.g., `WHERE user_id=X AND date > Y`).
- Pre-sorts data for specific retrieval requirements.

### 4. Single-Table Design (Adjacency Lists)

*Primary use: DynamoDB (but concepts apply elsewhere)*

Storing multiple entity types in one table to enable pre-joined reads.

| PK (Partition) | SK (Sort) | Data Fields... |
| :--- | :--- | :--- |
| `USER#123` | `PROFILE` | `{ name: "Ian", email: "..." }` |
| `USER#123` | `ORDER#998` | `{ total: 50.00, status: "shipped" }` |
| `USER#123` | `ORDER#999` | `{ total: 12.00, status: "pending" }` |

- **Query:** `PK="USER#123"`
- **Result:** Fetches User Profile AND all Orders in **one network request**.

### 5. Denormalization & Duplication

Store the same data in multiple tables to serve different query patterns.

- **Table A:** `users_by_id` (PK: uuid)
- **Table B:** `users_by_email` (PK: email)

*Trade-off: You must manage data consistency across tables (often using eventual consistency or batch writes).*

### 6. Apache Cassandra / ScyllaDB Specifics

- **Primary Key Structure:** `((Partition Key), Clustering Columns)`
- **No Joins, No Aggregates:** Do not try to `JOIN` or `GROUP BY`. Pre-calculate aggregates in a separate counter table.
- **Avoid `ALLOW FILTERING`:** If you see this in production, your data model is wrong. It implies a full cluster scan.
- **Writes are Cheap:** Inserts and Updates are just appends to the LSM tree. Don't worry about write volume as much as read efficiency.
- **Tombstones:** Deletes are expensive markers. Avoid high-velocity delete patterns (like queues) in standard tables.

### 7. AWS DynamoDB Specifics

- **GSI (Global Secondary Index):** Use GSIs to create alternative views of your data (e.g., "Search Orders by Date" instead of by User). GSIs are eventually consistent.
- **LSI (Local Secondary Index):** Sorts data differently *within* the same partition. Must be created at table creation time.
- **WCU / RCU:** Understand capacity modes. Single-table design helps optimize consumed capacity units.
- **TTL:** Use Time-To-Live attributes to automatically expire old data (free delete) without creating tombstones.

## Examples

### Cassandra: Users by Email Lookup

```sql
CREATE TABLE users_by_email (
  email text,
  user_id uuid,
  name text,
  created_at timestamp,
  PRIMARY KEY (email)
);
```

Query: `SELECT * FROM users_by_email WHERE email = 'ian@example.com';`

### DynamoDB: Single-Table User + Orders

```text
PK: USER#123          SK: PROFILE         -> { name, email }
PK: USER#123          SK: ORDER#2024-001 -> { total, status }
PK: USER#123          SK: ORDER#2024-002 -> { total, status }
```

Query: `Query PK=USER#123` returns the profile and all orders in one request.

## Pitfalls

- ❌ **Scatter-Gather:** Querying *all* partitions to find one item (Scan).
- ❌ **Hot Keys:** Putting all "Monday" data into one partition.
- ❌ **Relational Modeling:** Creating `Author` and `Book` tables and trying to join them in code. Instead, embed Book summaries in Author, or duplicate Author info in Books.
- ❌ **Low-Cardinality PK:** `status`, `gender`, or `country` as a partition key creates hot partitions.
- ❌ **Unbounded Partitions:** A single user's orders growing forever without sharding.
- ❌ **`ALLOW FILTERING` in Cassandra:** Indicates a broken data model requiring a full cluster scan.
- ❌ **High-Velocity Deletes:** Creates tombstones that degrade read performance in Cassandra.
- ❌ **Forgetting GSI Consistency:** GSIs are eventually consistent; do not use them for strong-consistency requirements.

## Verification

Before finalizing your NoSQL schema, run through this checklist:

- [ ] **Access Pattern Coverage:** Does every query pattern map to a specific table or index?
- [ ] **Cardinality Check:** Does the Partition Key have enough unique values to spread traffic evenly?
- [ ] **Split Partition Risk:** For any single partition (e.g., a single user's orders), will it grow indefinitely? (If > 10GB, shard the partition, e.g., `USER#123#2024-01`).
- [ ] **Consistency Requirement:** Can the application tolerate eventual consistency for this read pattern?
- [ ] **No Scans:** Are all production queries `SELECT`/`Query` by key, not `Scan`?
- [ ] **No `ALLOW FILTERING`:** Confirm no Cassandra queries use `ALLOW FILTERING`.

### Checkable Commands

Cassandra/ScyllaDB (Windows PowerShell, `cqlsh` on PATH):

```powershell
cqlsh localhost 9042 -e "DESCRIBE TABLE keyspace.users_by_email;"
cqlsh localhost 9042 -e "SELECT COUNT(*) FROM keyspace.users_by_email WHERE email='ian@example.com';"
```

DynamoDB (AWS CLI v2, placeholder credentials):

```powershell
aws dynamodb describe-table --table-name UsersOrders --endpoint-url http://localhost:8000
aws dynamodb query --table-name UsersOrders --key-condition-expression "PK = :pk" --expression-attribute-values '{":pk":{"S":"USER#123"}}' --endpoint-url http://localhost:8000
```

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
