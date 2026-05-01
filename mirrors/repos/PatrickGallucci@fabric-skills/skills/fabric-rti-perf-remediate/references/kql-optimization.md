# KQL Query Optimization for Fabric Real-Time Intelligence

## Table of Contents

1. [Core Principles](#core-principles)
2. [Filter Early and Selectively](#filter-early-and-selectively)
3. [String Operator Selection](#string-operator-selection)
4. [Join Optimization](#join-optimization)
5. [Summarize Optimization](#summarize-optimization)
6. [Materialized Views](#materialized-views)
7. [Dynamic Column Handling](#dynamic-column-handling)
8. [Common Anti-Patterns](#common-anti-patterns)
9. [Query Profiling Techniques](#query-profiling-techniques)

---

## Core Principles

KQL query performance depends directly on the volume of data processed. Every optimization targets one goal: reduce the data scanned as early as possible in the query pipeline.

Priority order for predicate placement:

1. `datetime` column filters first (leverages time-partitioned index)
2. `string` / `dynamic` filters using term-level operators (leverages inverted index)
3. Selective numeric filters
4. Full-scan predicates last (e.g., `contains` without term match)

---

## Filter Early and Selectively

### Always filter on time first

```kql
// GOOD: Time filter reduces data shards immediately
MyTable
| where Timestamp > ago(1h)
| where UserId == "user-123"
| summarize count() by bin(Timestamp, 5m)

// BAD: No time filter — scans entire retention window
MyTable
| where UserId == "user-123"
| summarize count() by bin(Timestamp, 5m)
```

### Reference only needed tables

```kql
// GOOD: Specific table reference
Events
| where EventType == "Click"

// BAD: Wildcard union scans every table
union *
| where SourceTable == "Events"
| where EventType == "Click"
```

### Use unqualified entity names

Reference tables as `MyTable` not `database("DB").MyTable` when querying within the same database. Qualified names prevent short-circuit optimizations.

---

## String Operator Selection

| Scenario | Use | Avoid | Why |
|----------|-----|-------|-----|
| Full token match | `has` | `contains` | `has` uses the inverted term index |
| Case-sensitive exact | `==` | `=~` | Avoids case normalization overhead |
| Case-sensitive membership | `in` | `in~` | Same reason |
| Substring required | `contains_cs` | `contains` | Case-sensitive is cheaper |
| Specific column | `where Col has "val"` | `where * has "val"` | `*` scans all columns |

### Rare value lookup in dynamic columns

```kql
// GOOD: Two-stage filter — term index first, then JSON parse
MyTable
| where DynamicCol has "rare-value"
| where DynamicCol.SomeKey == "rare-value"

// BAD: JSON parse on every row
MyTable
| where DynamicCol.SomeKey == "rare-value"
```

---

## Join Optimization

### General Rules

- Place the **smaller table on the left** (first in the join)
- Use `in` instead of `left semi join` when filtering by a single column
- Use `lookup` operator when the right side is small (< tens of MB)

### Strategy hints

| Scenario | Hint | Notes |
|----------|------|-------|
| Left side small (< 100 MB) | `hint.strategy=broadcast` | Broadcasts small table to all nodes |
| Both sides large, high-cardinality key | `hint.shufflekey=<key>` | Distributes by key for parallel processing |
| Right side small | Use `lookup` operator | Avoids full join overhead |

```kql
// GOOD: Broadcast hint for small left table
SmallLookup
| join hint.strategy=broadcast (LargeEvents) on UserId

// GOOD: Shuffle hint for large-large join
LargeTableA
| join hint.shufflekey=DeviceId (LargeTableB) on DeviceId
```

---

## Summarize Optimization

### Use shuffle for high-cardinality group keys

```kql
// GOOD: Shuffle when grouping by millions of distinct values
Events
| summarize hint.shufflekey=UserId count() by UserId, bin(Timestamp, 1h)
```

### Materialize repeated subexpressions

```kql
// GOOD: Compute once, reference many
let baseData = materialize(
    Events
    | where Timestamp > ago(1d)
    | where EventType in ("Click", "View", "Purchase")
);
let clicks = baseData | where EventType == "Click" | summarize Clicks = count();
let views  = baseData | where EventType == "View"  | summarize Views = count();
clicks | union views
```

---

## Materialized Views

Materialized views pre-compute aggregations and store results for fast retrieval. They are essential for dashboards and repeated analytical queries.

### When to use materialized views

- Repeated aggregation queries hitting the same base table
- Dashboard queries requiring sub-second response
- Deduplication using `arg_max` or `arg_min`
- Downsampled time-series for long retention

### Creating a materialized view

```kql
.create materialized-view EventCounts on table Events
{
    Events
    | summarize Count = count(), AvgDuration = avg(Duration)
        by EventType, bin(Timestamp, 1h)
}
```

### Querying only the materialized part

```kql
// GOOD: Reads only pre-computed data (fastest)
materialized_view('EventCounts')
| where Timestamp > ago(7d)

// OK: Merges materialized data with delta (slower but fully fresh)
EventCounts
| where Timestamp > ago(7d)
```

### Monitoring materialized view health

```kql
.show materialized-views
| project Name, IsHealthy, MaterializedTo, LastRun, 
    AgeMinutes = datetime_diff('minute', now(), MaterializedTo)
```

If `AgeMinutes` is large, the view is falling behind. Common causes: high ingestion volume, complex aggregation logic, or insufficient compute.

---

## Dynamic Column Handling

### Extract fields at ingestion time

If most queries parse dynamic columns across millions of rows, use an **update policy** to extract fields during ingestion rather than at query time.

```kql
// Update policy function
.create function ExtractFields() {
    RawEvents
    | extend 
        UserId = tostring(Properties.userId),
        Action = tostring(Properties.action),
        Duration = todouble(Properties.duration)
    | project-away Properties
}

.alter table ProcessedEvents policy update 
@'[{"IsEnabled": true, "Source": "RawEvents", "Query": "ExtractFields()", "IsTransactional": true}]'
```

---

## Common Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| No time filter | Scans full retention | Add `where Timestamp > ago(...)` |
| `contains` for token search | Skips term index | Use `has` or `has_cs` |
| `tolower(Col) == "val"` | Transforms every row | Use `Col =~ "val"` |
| `union *` | Scans all tables | List specific tables |
| Filter on calculated column | Prevents index use | Filter on table column directly |
| Large cross-database joins | Network overhead | Run query where most data lives |
| Unbound queries (no `limit`) | Returns GB of results | Add `limit` or `count` during development |
| `extract()` when `parse` works | Multiple regex passes | Use `parse` for uniform formats |

---

## Query Profiling Techniques

### Check query statistics

After running a query in the KQL Queryset, review the **Query stats** panel for:

- Total CPU time
- Total data scanned
- Memory peak usage
- Cache hit percentage (hot vs cold storage access)

### Use `.show queries` for historical analysis

```kql
.show queries
| where StartedOn > ago(1h)
| where State == "Completed"
| project User, Text, Duration, TotalCPU, MemoryPeak, CacheStatistics
| order by TotalCPU desc
| take 20
```

### Explain query plan

```kql
// View the query execution plan
.show query plan 
<| Events | where Timestamp > ago(1d) | summarize count() by EventType
```

This reveals which operators consume the most resources and whether indexes are being used effectively.
