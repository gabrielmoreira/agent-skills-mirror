# Configuration & runtime options

polars-bio is configured via `pb.set_option(key, value)` / `pb.get_option(key)`, plus
logging and metadata helpers.

## Common options

| Option | Default | Purpose |
|--------|---------|---------|
| `datafusion.execution.target_partitions` | 1 | parallelism; set to `os.cpu_count()` for large data |
| `datafusion.bio.coordinate_system_zero_based` | False (1-based) | global coordinate fallback |
| `datafusion.bio.coordinate_system_check` | False | raise on missing coordinate metadata |

```python
import os, polars_bio as pb
pb.set_option("datafusion.execution.target_partitions", os.cpu_count())
```

## Coordinate systems

- `use_zero_based` controls the **output representation**, not how the input is parsed:
  `True` → 0-based half-open output, `False` → 1-based closed output, `None` → the global
  `datafusion.bio.coordinate_system_zero_based` fallback. The BED reader always knows the
  file is 0-based half-open on disk, so interval-op *results are identical* in either mode —
  only the displayed coordinates differ (1-based shifts each start +1).
- The ClawBio CLI defaults BED to **0-based half-open** output (BED-native, so
  `merge`/`complement`/`subtract`/`cluster` round-trip correctly) and exposes `--one-based`
  to force 1-based closed. The `io`, `sql`, and interval-op paths all honor this default —
  `sql` reconciles via `set_option` since `register_bed` takes no `use_zero_based` argument.
- Mismatched systems between two inputs raise `CoordinateSystemMismatchError`; missing
  metadata (with `coordinate_system_check=True`) raises `MissingCoordinateSystemError`.

## Metadata utilities

`get_metadata`, `set_source_metadata`, `print_metadata_json`, `print_metadata_summary`
inspect/assign the coordinate + source metadata attached to DataFrames and propagated
through operations.

## Logging

`pb.set_loglevel(level)` controls verbosity (the readers emit per-record warnings on
malformed input — e.g. a 3-column BED produces "Error reading record" with 0 rows).

## Platform notes

- Built on a recent Apache DataFusion stack (with a matching pyarrow floor).
- Robust predicate & projection pushdown on indexed formats.
- Python **3.11–3.14** supported (`<3.15,>=3.11`).
