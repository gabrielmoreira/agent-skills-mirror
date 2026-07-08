# Interval operations

polars-bio interval ops accept Polars DataFrames/LazyFrames (or file paths) with
`chrom`, `start`, `end` columns by default (configurable via `cols1`/`cols2`). All
return a **LazyFrame** by default; pass `output_type="polars.DataFrame"` for eager
results or call `.collect()`. The ClawBio CLI requests eager output.

## The eight operations

| Op | Inputs | Purpose | Key params |
|----|--------|---------|------------|
| `overlap` | 2 | overlapping interval pairs | `suffixes`, `overlap_output` ("join"/"left"), `cols1/2` |
| `nearest` | 2 | nearest interval(s) | `k`, `overlap`, `distance` |
| `count_overlaps` | 2 | overlap tally per interval | `suffixes`, `naive_query` |
| `coverage` | 2 | per-interval coverage | `cols1/2` |
| `subtract` | 2 | remove overlapping portions | `cols1/2` |
| `merge` | 1 | merge overlapping/bookended | `min_dist` |
| `cluster` | 1 | assign cluster IDs | `min_dist` |
| `complement` | 1 | gaps between intervals | `view_df` (contig bounds) |

> **Not in the Python API:** `expand` and `sort_bedframe` appear in conceptual docs but
> are **not** `polars_bio.*` functions in the current API — the ClawBio CLI omits them. Use native
> Polars expressions for padding/sorting.

## Output schemas (observed)

- `overlap` / `nearest`: suffixed columns `chrom_1,start_1,end_1,...,chrom_2,start_2,...`
  (`nearest` adds `distance`).
- `merge`: `chrom,start,end,n_intervals`.
- `cluster`: input columns + `cluster,cluster_start,cluster_end`.
- `coverage`: input columns + `coverage`.
- `count_overlaps`: input columns + `count`.
- `complement`: `chrom,start,end`.

## Notes & performance

- **Probe-build order**: for two-input ops the first DataFrame is the probe, the second
  the build (indexed). Pass the **larger** set first for best performance.
- **`complement` needs bounds**: without a `view_df` of contig sizes it spans
  `[0, i64::MAX)` per contig and warns — provide chromosome sizes for meaningful gaps.
- **INT32 positions**: coordinates are 32-bit (~2.1 Gb per contig limit).
- **Parallelism** defaults to 1 partition; raise with
  `pb.set_option("datafusion.execution.target_partitions", N)` for large inputs.
- **Method chaining**: the `.pb` accessor exists on `LazyFrame` (not `DataFrame`):
  `df.lazy().pb.overlap(other).filter(...).collect()`.
