# Performance Optimization Patterns for Fabric User Data Functions

Detailed code patterns and techniques for optimizing User Data Functions performance within Fabric's serverless execution model.

## Table of Contents

- [Data Source Query Optimization](#data-source-query-optimization)
- [Python Code Optimization](#python-code-optimization)
- [Connection Management](#connection-management)
- [Response Shaping](#response-shaping)
- [Cold Start Mitigation](#cold-start-mitigation)
- [Error Handling for Performance](#error-handling-for-performance)
- [Anti-Patterns to Avoid](#anti-patterns-to-avoid)

---

## Data Source Query Optimization

### Warehouse and SQL Database Connections

When using `FabricSqlConnection`, the query you execute is the primary performance lever.

**Slow pattern:**

```python
@udf.connection(argName="myWarehouse", alias="wh1")
@udf.function()
def get_all_data(myWarehouse: fn.FabricSqlConnection) -> list:
    conn = myWarehouse.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LargeTable")  # Full table scan
    rows = [dict(zip([c[0] for c in cursor.description], r)) for r in cursor]
    cursor.close()
    conn.close()
    return rows
```

**Optimized pattern:**

```python
@udf.connection(argName="myWarehouse", alias="wh1")
@udf.function()
def get_filtered_data(myWarehouse: fn.FabricSqlConnection, category: str, limit: int) -> list:
    conn = myWarehouse.connect()
    cursor = conn.cursor()

    # Select only needed columns, filter early, limit results
    cursor.execute(
        "SELECT ProductId, ProductName, Price "
        "FROM Products "
        "WHERE Category = ? "
        "ORDER BY Price DESC "
        "OFFSET 0 ROWS FETCH NEXT ? ROWS ONLY",
        (category, min(limit, 1000))
    )

    columns = [c[0] for c in cursor.description]
    rows = [dict(zip(columns, r)) for r in cursor]
    cursor.close()
    conn.close()
    return rows
```

**Key principles:**

- Select only the columns you need (never `SELECT *`)
- Push filtering to the query with WHERE clauses
- Use parameterized queries to prevent SQL injection and enable plan caching
- Limit result sets with TOP/FETCH NEXT
- Use appropriate data types in WHERE clauses to avoid implicit conversions

### Lakehouse File Connections

When using `FabricLakehouseClient`, file I/O is the bottleneck.

**Optimized CSV reading:**

```python
@udf.connection(argName="myLakehouse", alias="lh1")
@udf.function()
def read_filtered_csv(myLakehouse: fn.FabricLakehouseClient, filename: str) -> str:
    import pandas as pd
    from io import StringIO

    connection = myLakehouse.connectToFiles()
    file_client = connection.get_file_client(filename)
    download = file_client.download_file()
    csv_data = download.readall()

    # Read only needed columns with dtype optimization
    df = pd.read_csv(
        StringIO(csv_data.decode('utf-8')),
        usecols=['Id', 'Name', 'Value'],   # Only needed columns
        dtype={'Id': 'int32', 'Value': 'float32'},  # Smaller dtypes
        nrows=10000  # Limit rows if appropriate
    )

    file_client.close()
    connection.close()

    return df.to_json(orient='records')
```

**Key principles:**

- Use `usecols` to read only required columns
- Specify `dtype` to minimize memory consumption
- Use `nrows` when full dataset is not needed
- Close connections explicitly in a try/finally block
- For Parquet files, use column pruning and predicate pushdown

---

## Python Code Optimization

### Efficient Data Processing

**Avoid iterrows (slow):**

```python
# Slow - iterates row by row
result = ""
for index, row in df.iterrows():
    result += "[" + ",".join([str(item) for item in row]) + "]"
```

**Use vectorized operations (fast):**

```python
# Fast - vectorized string operations
result = df.apply(lambda row: "[" + ",".join(row.astype(str)) + "]", axis=1)
return "\n".join(result)
```

**Even better - use built-in serialization:**

```python
return df.to_json(orient='records')
```

### Memory-Efficient Processing

For large datasets approaching the 30 MB response limit:

```python
import logging

@udf.function()
def process_large_dataset(query_param: str) -> list:
    # Process in chunks instead of loading everything
    chunk_size = 5000
    results = []

    for offset in range(0, max_rows, chunk_size):
        chunk = fetch_chunk(query_param, offset, chunk_size)
        processed = [transform(row) for row in chunk]
        results.extend(processed)

        if len(results) * avg_row_size > 25_000_000:
            logging.warning(f"Approaching response limit at {len(results)} rows")
            break

    return results
```

### String Operations

```python
# Slow - string concatenation in loops
result = ""
for item in large_list:
    result = result + str(item) + ","

# Fast - join with list comprehension
result = ",".join(str(item) for item in large_list)
```

---

## Connection Management

### Always Use try/finally for Cleanup

```python
@udf.connection(argName="myWarehouse", alias="wh1")
@udf.function()
def safe_query(myWarehouse: fn.FabricSqlConnection, param: str) -> list:
    conn = None
    cursor = None
    try:
        conn = myWarehouse.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT Id, Name FROM Products WHERE Category = ?", (param,))
        columns = [c[0] for c in cursor.description]
        return [dict(zip(columns, r)) for r in cursor]
    except Exception as e:
        logging.error(f"Query failed: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
```

### Minimize Connection Scope

Open connections as late as possible and close them as early as possible. Do not hold connections open during CPU-intensive processing.

```python
@udf.connection(argName="myWarehouse", alias="wh1")
@udf.function()
def compute_and_query(myWarehouse: fn.FabricSqlConnection, input_data: str) -> str:
    # Phase 1: CPU work (no connection needed)
    processed = heavy_computation(input_data)

    # Phase 2: Short-lived connection for data retrieval
    conn = myWarehouse.connect()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT Value FROM Lookup WHERE Key = ?", (processed,))
        row = cursor.fetchone()
        return str(row[0]) if row else "NOT_FOUND"
    finally:
        conn.close()
```

---

## Response Shaping

### Pagination Pattern

```python
@udf.connection(argName="myWarehouse", alias="wh1")
@udf.function()
def get_paged_results(myWarehouse: fn.FabricSqlConnection, page: int, page_size: int) -> str:
    import json

    page_size = min(page_size, 500)  # Cap page size
    offset = page * page_size

    conn = myWarehouse.connect()
    try:
        cursor = conn.cursor()

        # Get total count
        cursor.execute("SELECT COUNT(*) FROM Products")
        total = cursor.fetchone()[0]

        # Get page
        cursor.execute(
            "SELECT Id, Name, Price FROM Products "
            "ORDER BY Id "
            "OFFSET ? ROWS FETCH NEXT ? ROWS ONLY",
            (offset, page_size)
        )
        columns = [c[0] for c in cursor.description]
        rows = [dict(zip(columns, r)) for r in cursor]

        return json.dumps({
            "data": rows,
            "page": page,
            "pageSize": page_size,
            "totalRows": total,
            "totalPages": (total + page_size - 1) // page_size
        })
    finally:
        conn.close()
```

### Summary/Aggregation Pattern

Instead of returning raw data, return pre-aggregated summaries:

```python
@udf.connection(argName="myWarehouse", alias="wh1")
@udf.function()
def get_sales_summary(myWarehouse: fn.FabricSqlConnection, year: int) -> str:
    import json

    conn = myWarehouse.connect()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Region, COUNT(*) AS OrderCount,
                   SUM(Amount) AS TotalAmount,
                   AVG(Amount) AS AvgAmount
            FROM Sales
            WHERE YEAR(OrderDate) = ?
            GROUP BY Region
            ORDER BY TotalAmount DESC
        """, (year,))
        columns = [c[0] for c in cursor.description]
        return json.dumps([dict(zip(columns, r)) for r in cursor])
    finally:
        conn.close()
```

---

## Cold Start Mitigation

### Lazy Import Pattern

```python
import logging
import fabric.functions as fn

udf = fn.UserDataFunctions()

# Do NOT import heavy libraries at top level
# import pandas as pd        # Adds to cold start
# import numpy as np         # Adds to cold start

@udf.function()
def lightweight_function(name: str) -> str:
    """Fast function - no heavy imports needed."""
    return f"Hello, {name}"

@udf.function()
def data_function(query: str) -> str:
    """Only imports pandas when this specific function is called."""
    import pandas as pd
    # ... use pandas here
```

### Warm-Up Scheduling

Create a lightweight health-check function and call it on a schedule from a Pipeline:

```python
@udf.function()
def health_check() -> str:
    """Lightweight function to keep the runtime warm."""
    return "OK"
```

Configure a Pipeline with a scheduled trigger to invoke `health_check` every 10-15 minutes during business hours.

---

## Error Handling for Performance

### Timeout-Aware Pattern

```python
import logging
import time

TIMEOUT_SECONDS = 240
WARN_THRESHOLD = 0.75  # Warn at 75% of timeout

@udf.function()
def timeout_aware_function(param: str) -> str:
    start = time.perf_counter()

    for batch in get_batches(param):
        elapsed = time.perf_counter() - start
        remaining = TIMEOUT_SECONDS - elapsed

        if remaining < TIMEOUT_SECONDS * (1 - WARN_THRESHOLD):
            logging.warning(f"Approaching timeout: {elapsed:.1f}s elapsed, {remaining:.1f}s remaining")

        if remaining < 10:
            logging.error(f"Aborting to avoid timeout. Processed {batch.index} batches.")
            return f"PARTIAL: Processed {batch.index} of {batch.total} batches"

        process_batch(batch)

    return "COMPLETE"
```

---

## Anti-Patterns to Avoid

| Anti-Pattern | Why It's Bad | Better Alternative |
|---|---|---|
| `SELECT *` from large tables | Transfers unnecessary data, wastes time and memory | Select only needed columns |
| String concatenation in loops | O(n²) memory allocation | Use `"".join()` or list comprehension |
| `df.iterrows()` for processing | Extremely slow row-by-row iteration | Vectorized pandas operations or `.apply()` |
| Top-level imports of heavy libraries | Increases cold start for ALL functions | Lazy imports inside function body |
| No connection cleanup | Connection leaks degrade performance over time | Always use try/finally |
| Unbounded query results | Risk of timeout or response size limit | Always use LIMIT/TOP and pagination |
| Logging every row in a loop | Excessive log volume, hits 250 MB daily limit | Log summaries and milestones |
| Catching and silencing exceptions | Hides performance-degrading errors | Log errors with context, re-raise when appropriate |
| Hardcoded sleep/delays | Wastes execution time budget | Use event-driven patterns or polling with backoff |
| Publishing frequently during dev | Each publish triggers storage writes (CU cost) | Batch changes, use Test mode in Develop |
