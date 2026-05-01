# Dataflow Optimization

Performance tuning guide for Microsoft Fabric Dataflow Gen2 refreshes in Data Factory pipelines.

## Table of Contents

- [Understanding Dataflow Gen2 Performance](#understanding-dataflow-gen2-performance)
- [Query Folding](#query-folding)
- [Transformation Optimization](#transformation-optimization)
- [Connector-Specific Guidance](#connector-specific-guidance)
- [Staging and Buffering](#staging-and-buffering)
- [remediate Slow Refreshes](#remediate-slow-refreshes)

## Understanding Dataflow Gen2 Performance

Dataflow Gen2 uses the Power Query engine to extract, transform, and load data. Performance depends on:

1. **Query folding**: Whether transformations push down to the source
2. **Data volume**: Amount of data flowing through the dataflow
3. **Transformation complexity**: Number and type of transformation steps
4. **Destination type**: Lakehouse, Warehouse, or other Fabric items
5. **Connector capabilities**: Source system's ability to handle parallel reads

## Query Folding

Query folding is the most impactful optimization for Dataflow Gen2. When transformations fold, they execute on the source system rather than in the Power Query engine.

### Checking Fold Status

In the Power Query editor:

1. Right-click on a transformation step
2. Look for **View Native Query**
3. If available, the step folds; if grayed out, it does not

### Transformations That Typically Fold

- Filter rows (WHERE clause)
- Select/remove columns (SELECT)
- Sort rows (ORDER BY)
- Group by (GROUP BY)
- Rename columns (AS alias)
- Change data type (CAST)
- Merge queries (JOIN) from same source

### Transformations That Break Folding

- Add custom column with M expressions
- Pivot/unpivot columns
- Replace values with complex logic
- Merge queries from different sources
- Buffer table (forces full data pull)

### Best Practice

Apply all foldable transformations first, then add non-foldable steps. This minimizes the data volume processed by the Power Query engine.

## Transformation Optimization

### Reduce Early

Filter rows and remove unused columns as early as possible in the transformation chain. This reduces the data volume for all downstream steps.

### Avoid Unnecessary Type Conversions

Type conversions can break query folding and add processing overhead. Only convert types when the destination requires a specific type.

### Minimize Steps

Each transformation step adds overhead. Combine related operations where possible. For example, combine multiple filter conditions into a single step.

### Use Table.Buffer Strategically

`Table.Buffer` forces the entire result set into memory. Use only when:

- A table is referenced multiple times in different branches
- You need to prevent re-evaluation of an expensive upstream query
- The data set is small enough to fit in memory

Avoid `Table.Buffer` for large datasets as it can cause memory pressure and slow refreshes.

## Connector-Specific Guidance

### SQL Database Sources

- Enable query folding by using supported transformations
- Use native SQL queries for complex transformations that cannot fold
- Consider partition-aware reading for large tables

### File Sources (CSV, Parquet, JSON)

- Use Parquet format when possible (columnar, compressed)
- Filter by partition columns in file-based sources
- Avoid loading all files when only recent data is needed

### REST API Sources

- Implement pagination efficiently
- Cache responses when data does not change frequently
- Set appropriate timeout values for slow APIs

### SharePoint and Excel Sources

- Minimize the number of sheets/lists loaded
- Filter data at the source level when possible
- Consider exporting to CSV for large datasets

## Staging and Buffering

### When to Use Staging

Enable staging for dataflows that:

- Load large datasets (millions of rows)
- Have many transformation steps
- Target Fabric Warehouse as destination
- Experience timeout errors

### Staging Configuration

Staging uses an intermediate Lakehouse to buffer data between extract and load phases. This improves reliability for large data volumes but adds some overhead for small datasets.

## remediate Slow Refreshes

### Diagnostic Checklist

1. **Check query folding**: Verify critical steps fold to the source
2. **Review transformation count**: Minimize total steps
3. **Check data volume**: Add filters to reduce rows processed
4. **Monitor memory usage**: Look for memory pressure indicators
5. **Test connectivity**: Ensure source is responsive and not throttled
6. **Review refresh history**: Compare against previous successful runs

### Common Issues and Fixes

| Issue | Symptom | Fix |
|-------|---------|-----|
| No query folding | Full table scan on every refresh | Reorder steps to fold filters first |
| Too many columns | Slow data transfer | Remove unused columns early |
| Large lookup tables | Memory pressure | Buffer small lookups, paginate large ones |
| API rate limiting | Intermittent timeout errors | Add retry logic, reduce concurrency |
| Destination bottleneck | Transfer phase is slow | Enable staging, check destination health |
| Credential expiration | Authentication failures mid-refresh | Refresh credentials before scheduled runs |

### Performance Testing

1. Create a baseline by running the dataflow with minimal transformations
2. Add transformations incrementally and measure impact
3. Identify the step that causes the most significant slowdown
4. Optimize or restructure that specific step
5. Re-measure and compare against baseline
