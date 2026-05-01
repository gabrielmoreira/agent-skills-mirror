# Streaming Performance Optimization

## Table of Contents

- [Common Streaming Issues](#common-streaming-issues)
- [Trigger Interval Tuning](#trigger-interval-tuning)
- [Small File Prevention](#small-file-prevention)
- [Checkpoint Optimization](#checkpoint-optimization)
- [Monitoring Streaming Jobs](#monitoring-streaming-jobs)

## Common Streaming Issues

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Processing rate < input rate | Under-provisioned or bad partitioning | Scale executors, repartition |
| Many small Delta files | Too-frequent trigger intervals | Increase trigger interval |
| Checkpoint growing large | Too many micro-batches | Compact checkpoint files |
| High latency spikes | Garbage collection or shuffle spill | Increase memory, reduce shuffle |
| Duplicate records | Checkpoint corruption | Reset checkpoint, ensure idempotent writes |

## Trigger Interval Tuning

The trigger interval defines how often the streaming engine processes accumulated events.

```python
# Process every 1 minute (recommended starting point)
query = df.writeStream \
    .format("delta") \
    .option("checkpointLocation", "Files/checkpoint/my_stream") \
    .outputMode("append") \
    .trigger(processingTime="1 minute") \
    .toTable("streaming_table")
```

### Choosing the Right Interval

| Data Volume | Recommended Interval | Rationale |
|------------|---------------------|-----------|
| < 1,000 events/min | 5–10 minutes | Accumulate enough data for reasonable file sizes |
| 1,000–100,000 events/min | 1–2 minutes | Balance latency and file size |
| 100,000+ events/min | 10–30 seconds | High volume justifies frequent writes |

Longer intervals produce fewer, larger Delta files (healthier table). Shorter intervals
reduce latency but create more small files requiring more frequent OPTIMIZE.

## Small File Prevention

### Use Optimized Write

```python
spark.conf.set("spark.microsoft.delta.optimizeWrite.enabled", "true")

query = df.writeStream \
    .format("delta") \
    .option("checkpointLocation", "Files/checkpoint/my_stream") \
    .outputMode("append") \
    .trigger(processingTime="1 minute") \
    .toTable("streaming_table")
```

Optimized Write merges partitions before writing, producing larger files. Adds shuffle
overhead but significantly reduces small file accumulation.

### Use Repartition Before Write

```python
query = df \
    .repartition(48) \
    .writeStream \
    .format("delta") \
    .option("checkpointLocation", "Files/checkpoint/my_stream") \
    .outputMode("append") \
    .partitionBy("date_column") \
    .trigger(processingTime="1 minute") \
    .toTable("streaming_table")
```

Choose repartition count based on data volume per trigger:
- Target 128 MB–256 MB per partition per trigger
- Fewer partitions = fewer files per batch

### Schedule Regular OPTIMIZE

For streaming tables, schedule OPTIMIZE daily to compact small files:

```python
# Run in a separate maintenance notebook or job
spark.sql("OPTIMIZE streaming_table VORDER")
spark.sql("VACUUM streaming_table RETAIN 168 HOURS")
```

## Checkpoint Optimization

### Checkpoint Location

Always use the Files section of the Lakehouse (not Tables):

```python
.option("checkpointLocation", "Files/checkpoint/stream_name")
```

### Checkpoint Sizing

Monitor checkpoint directory size. Large checkpoints slow stream recovery.
If checkpoints grow excessively:

1. Ensure the streaming query uses append mode (not complete)
2. Avoid stateful operations with unbounded state
3. Set watermarks for windowed aggregations to bound state

```python
# Add watermark to limit state
df.withWatermark("event_time", "1 hour") \
  .groupBy(F.window("event_time", "5 minutes")) \
  .count()
```

## Monitoring Streaming Jobs

### Spark Structured Streaming UI

Available in Spark 3.1+ with these metrics:
- **Input Rate**: Events per second arriving
- **Process Rate**: Events per second processed
- **Input Rows**: Total rows per batch
- **Batch Duration**: Time to process each micro-batch
- **Operation Duration**: Breakdown of time spent in each operation

### Health Check Query

```python
# Get streaming query progress
for query in spark.streams.active:
    print(f"Name: {query.name}")
    print(f"Status: {query.status}")
    progress = query.lastProgress
    if progress:
        print(f"Input rows/sec: {progress['inputRowsPerSecond']:.0f}")
        print(f"Processed rows/sec: {progress['processedRowsPerSecond']:.0f}")
        print(f"Batch duration: {progress['batchDuration']} ms")
    print("---")
```

### Alert on Processing Lag

If `processedRowsPerSecond` consistently falls below `inputRowsPerSecond`, the stream
is falling behind. Scale executors, optimize the query, or increase trigger interval.

### Use Spark Job Definitions for Production Streams

Notebooks are excellent for development but Spark Job Definitions provide:
- Retry policies for automatic recovery from infrastructure failures
- Better monitoring and lifecycle management
- No idle session overhead
