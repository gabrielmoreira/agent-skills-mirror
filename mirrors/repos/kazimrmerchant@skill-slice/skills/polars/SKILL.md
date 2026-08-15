---
name: polars
description: "Builds in-memory Polars DataFrame and LazyFrame pipelines (scan_csv, expressions, group_by, over) on Arrow for RAM-fitting ETL. Use when pandas is too slow or migrating pandas code to Polars. Not for pandas CSV ingest hygiene (csv-processing) or larger-than-RAM Dask/Vaex jobs."
version: 1.0.1
license: https://github.com/pola-rs/polars/blob/main/LICENSE
metadata:
  skill-author: K-Dense Inc.
risk: unknown
source: community
---

# Polars

## When to Use

- You need a faster in-memory DataFrame workflow than pandas and the dataset still fits in RAM (roughly 1–100 GB).
- You are building ETL, analytics, or transformation pipelines that benefit from lazy evaluation, predicate/projection pushdown, and parallel execution.
- You want expression-based tabular operations on top of Apache Arrow semantics.
- You are migrating code from pandas to Polars and need correct API mappings.
- For larger-than-RAM data, switch to `dask` or `vaex` instead.

## Prerequisites

- Python 3.8+ available on PATH.
- A package manager such as `uv`, `pip`, or `conda`.
- On Windows (PowerShell), use forward slashes or raw strings in file paths to avoid backslash escaping issues:
  ```powershell
  python -c "import polars as pl; print(pl.__version__)"
  ```

## Procedure

### 1. Install Polars

```powershell
uv pip install polars
# or
pip install polars
```

Verify the install:

```powershell
python -c "import polars as pl; print(pl.__version__)"
```

### 2. Create a DataFrame and perform basic operations

```python
import polars as pl

df = pl.DataFrame({
    "name": ["Alice", "Bob", "Charlie"],
    "age": [25, 30, 35],
    "city": ["NY", "LA", "SF"],
})

# Select columns
df.select("name", "age")

# Filter rows — multiple conditions are comma-separated (cleaner than &)
df.filter(
    pl.col("age") > 25,
    pl.col("city") == "NY",
)

# Add or modify columns (all expressions run in parallel)
df.with_columns(
    age_plus_10=pl.col("age") + 10,
    name_upper=pl.col("name").str.to_uppercase(),
)
```

### 3. Choose eager vs lazy evaluation

**Eager (DataFrame)** — operations execute immediately:

```python
df = pl.read_csv("file.csv")          # Reads immediately
result = df.filter(pl.col("age") > 25)  # Executes immediately
```

**Lazy (LazyFrame)** — operations build an optimized query plan:

```python
lf = pl.scan_csv("file.csv")          # Does not read yet
result = (
    lf.filter(pl.col("age") > 25)
      .select("name", "age")
)
df = result.collect()                 # Now executes the optimized query
```

Use lazy when:
- The dataset is large.
- The pipeline is complex.
- Only some columns/rows are needed.
- Performance is critical.

Benefits: automatic query optimization, predicate pushdown, projection pushdown, parallel execution.

### 4. Common operations

**Select with expressions and regex:**

```python
df.select(
    pl.col("name"),
    (pl.col("age") * 2).alias("double_age"),
)

# All columns ending in _id
df.select(pl.col("^.*_id$"))
```

**Filter with complex conditions:**

```python
df.filter(
    (pl.col("age") > 25) | (pl.col("city") == "LA")
)
```

**Group by and aggregate:**

```python
df.group_by("city").agg(
    pl.col("age").mean().alias("avg_age"),
    pl.len().alias("count"),
)

# Multiple group keys
df.group_by("city", "department").agg(
    pl.col("salary").sum(),
)

# Conditional aggregation
df.group_by("city").agg(
    (pl.col("age") > 30).sum().alias("over_30"),
)
```

**Window functions with `over()`** — preserves row count:

```python
df.with_columns(
    avg_age_by_city=pl.col("age").mean().over("city"),
    rank_in_city=pl.col("salary").rank().over("city"),
)

# Multiple grouping columns
df.with_columns(
    group_avg=pl.col("value").mean().over("category", "region"),
)
```

Mapping strategies for `over()`:
- `group_to_rows` (default): preserves original row order.
- `explode`: faster but reorders rows by group.
- `join`: creates list columns.

### 5. Data I/O

Supported formats: CSV, Parquet, JSON, Excel, databases (via connectors), cloud storage (S3, Azure, GCS), BigQuery, and multiple/partitioned files.

**CSV:**

```python
# Eager
df = pl.read_csv("file.csv")
df.write_csv("output.csv")

# Lazy (preferred for large files)
lf = pl.scan_csv("file.csv")
result = lf.filter(...).select(...).collect()
```

**Parquet (recommended for performance):**

```python
df = pl.read_parquet("file.parquet")
df.write_parquet("output.parquet")
```

**JSON:**

```python
df = pl.read_json("file.json")
df.write_json("output.json")
```

### 6. Transformations

**Joins:**

```python
df1.join(df2, on="id", how="inner")
df1.join(df2, on="id", how="left")
df1.join(df2, left_on="user_id", right_on="id")
```

**Concatenation:**

```python
pl.concat([df1, df2], how="vertical")     # stack rows
pl.concat([df1, df2], how="horizontal")   # add columns
pl.concat([df1, df2], how="diagonal")     # union with different schemas
```

**Pivot and unpivot:**

```python
df.pivot(values="sales", index="date", columns="product")
df.unpivot(index="id", on=["col1", "col2"])
```

### 7. Pandas migration

Key conceptual differences:
- **No index**: Polars uses integer positions only.
- **Strict typing**: no silent type conversions.
- **Lazy evaluation**: available via LazyFrame.
- **Parallel by default**: operations are parallelized automatically.

| Operation | Pandas | Polars |
|-----------|--------|--------|
| Select column | `df["col"]` | `df.select("col")` |
| Filter | `df[df["col"] > 10]` | `df.filter(pl.col("col") > 10)` |
| Add column | `df.assign(x=...)` | `df.with_columns(x=...)` |
| Group by | `df.groupby("col").agg(...)` | `df.group_by("col").agg(...)` |
| Window | `df.groupby("col").transform(...)` | `df.with_columns(...over("col"))` |

Pandas sequential (slow):

```python
df.assign(
    col_a=lambda df_: df_.value * 10,
    col_b=lambda df_: df_.value * 100,
)
```

Polars parallel (fast):

```python
df.with_columns(
    col_a=pl.col("value") * 10,
    col_b=pl.col("value") * 100,
)
```

### 8. Performance best practices

1. **Use lazy evaluation for large datasets** — `scan_csv` instead of `read_csv`.
2. **Avoid Python functions in hot paths** — stay within the expression API; use `.map_elements()` only when necessary.
3. **Use streaming for very large data:**
   ```python
   lf.collect(streaming=True)
   ```
4. **Select only needed columns early:**
   ```python
   # Good
   lf.select("col1", "col2").filter(...)

   # Bad
   lf.filter(...).select("col1", "col2")
   ```
5. **Use appropriate data types:**
   - `Categorical` for low-cardinality strings.
   - Right-sized integers (`i32` vs `i64`).
   - Native date/datetime types for temporal data.

**Expression patterns:**

```python
# Conditional logic
pl.when(condition).then(value).otherwise(other_value)

# Regex column selection
df.select(pl.col("^.*_value$") * 2)

# Null handling
pl.col("x").fill_null(0)
pl.col("x").is_null()
pl.col("x").drop_nulls()
```

## Pitfalls

- **`read_csv` vs `scan_csv`**: `read_csv` is eager and loads the entire file immediately. For large files, always prefer `scan_csv` + `collect()` so predicate/projection pushdown can optimize.
- **No implicit index**: Polars has no row index. Code relying on `df.loc` or `df.iloc` semantics from pandas must be rewritten using `filter`, `select`, or `row`/`gather`.
- **Strict typing**: Polars will not silently coerce types. Mismatched types in joins or concatenations will raise. Cast explicitly with `.cast()`.
- **`map_elements` is slow**: it drops out of the parallel expression engine. Use native expressions wherever possible.
- **Column order in `over()`**: `group_to_rows` preserves original order; `explode` reorders. Choose deliberately.
- **`concat` schema mismatch**: vertical concat requires identical schemas. Use `how="diagonal"` when schemas differ.
- **Windows paths**: backslashes in string literals must be escaped or use raw strings / forward slashes.
- **Streaming is not a silver bullet**: `collect(streaming=True)` helps for larger-than-memory data but may be slower than in-memory collect for small data.

## Verification

1. **Confirm Polars is installed and importable:**
   ```powershell
   python -c "import polars as pl; print(pl.__version__)"
   ```
   Expected: a version string such as `1.x.x`.

2. **Confirm lazy optimization works:**
   ```python
   import polars as pl

   lf = pl.scan_csv("file.csv")
   q = lf.filter(pl.col("age") > 25).select("name", "age")
   print(q.explain())  # Should show predicate + projection pushdown
   df = q.collect()
   print(df.shape)
   ```

3. **Confirm a round-trip write/read:**
   ```python
   import polars as pl

   df = pl.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
   df.write_parquet("test.parquet")
   df2 = pl.read_parquet("test.parquet")
   assert df.equals(df2)
   print("round-trip OK")
   ```

4. **Confirm parallel `with_columns`:**
   ```python
   import polars as pl

   df = pl.DataFrame({"value": [1, 2, 3]})
   out = df.with_columns(
       col_a=pl.col("value") * 10,
       col_b=pl.col("value") * 100,
   )
   print(out)
   ```

## References

This skill does not ship a companion pack. Procedure sections above cover the execute path. For APIs beyond that, use the official Polars docs:

- Concepts (expressions, lazy, types): https://docs.pola.rs/user-guide/concepts/
- I/O: https://docs.pola.rs/user-guide/io/
- Transformations: https://docs.pola.rs/user-guide/transformations/
- pandas migration: https://docs.pola.rs/user-guide/migration/pandas/

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
