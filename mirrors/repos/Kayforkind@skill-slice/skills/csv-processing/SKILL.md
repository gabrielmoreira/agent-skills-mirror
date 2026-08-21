---
name: csv-processing
version: 1.1.1
description: "Reads and writes pandas CSV with pinned dtypes, explicit NA tokens, formula-injection sanitization, and chunked processing. Use when ingesting sensor logs, simulation results, or in-memory time-series CSVs. Not for Polars LazyFrame pipelines (polars), Kafka streams, or Parquet/Arrow as the native store."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

## Overview

CSV is the right tool when you need a human-readable, tool-agnostic interchange
format and the data comfortably fits in memory. This skill covers the full
lifecycle: reading with pinned dtypes, handling missing values explicitly,
accessing data safely, writing with formula-injection sanitization, building
results incrementally, and processing files that may exceed RAM via chunking.

## When to Use

Reach for this skill when:

- **Reading sensor data from CSV files** — exports from data loggers and lab
  equipment are almost always CSV because every downstream tool can open them.
- **Writing simulation results to CSV** — keeps results diffable in version
  control and openable in a spreadsheet without a custom viewer.
- **Processing time-series data with pandas** — pandas' indexed/resampling API
  turns awkward timestamp math into one-liners.
- **Handling missing values in datasets** — real-world feeds have gaps; deciding
  *explicitly* what "missing" means is half the job.
- **Data validation and schema enforcement** — catching a malformed column at
  the boundary is far cheaper than debugging a wrong number three steps later.
- **ETL pipelines with structured tabular data** — CSV is the lowest-common-
  denominator hand-off between systems that share nothing else.

### Do Not Use

Each of these has a concrete failure mode, not just a stylistic objection:

- **Real-time streaming data** (use Apache Kafka or Apache Pulsar) — CSV has no
  framing or backpressure, so you would be reinventing a message broker badly.
- **Binary formats** (prefer Parquet, Avro, or HDF5) — CSV stores everything as
  text, so numbers are re-parsed on every read and types are not preserved.
- **Datasets larger than RAM** (use Dask or Vaex) — `read_csv` loads the whole
  file by default; past your memory limit it simply crashes. If you must use
  CSV, the chunked pattern below bounds memory.
- **Strict typing requirements** (use Arrow-based formats) — CSV cannot
  distinguish `1` (int) from `1.0` (float) from `"1"` (string) on its own.
- **Sensitive data without sanitization** — a value beginning with `=`, `+`,
  `-`, or `@` becomes an executable formula when opened in a spreadsheet (CSV
  injection); sanitize before writing anything a human might open.
- **Untrusted CSV files** — the same injection risk applies on the read side if
  you forward cell contents into another formula-evaluating tool.

## Prerequisites

- Python 3.10+ with `pandas` installed.
- Optional: `pandera` for schema validation, `mprof` (memory_profiler) for
  memory profiling, `csvvalidator` for output structure validation.
- Windows host is primary (PowerShell). All path examples use Windows-style
  paths. On PowerShell, use forward slashes or escaped backslashes in Python
  strings.

Install dependencies if missing:

```powershell
pip install pandas pandera memory_profiler
```

## Procedure

### Step 1 — Reading CSV with Pinned Dtypes

Pin the dtypes and encoding instead of letting pandas infer them. Inference is
*data-dependent*: a column that holds only integers today may be inferred as
`float64` (or `object`) tomorrow the moment a null or a stray string appears,
silently changing every downstream calculation. Validating the column set up
front means callers never operate on a frame that is missing what they need.

```python
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS: frozenset[str] = frozenset({"id", "timestamp", "value"})


def read_sensor_csv(path: str | Path) -> pd.DataFrame:
    """Read a sensor CSV into a typed, schema-checked DataFrame."""
    csv_path = Path(path)

    # Fail fast with an actionable message instead of a deep pandas traceback.
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")
    if not csv_path.is_file():
        raise ValueError(f"Expected a file, got a directory: {csv_path}")

    try:
        df = pd.read_csv(
            csv_path,
            dtype={"id": "int32", "value": "float64"},
            encoding="utf-8",
            parse_dates=["timestamp"],
            true_values=["yes", "true"],
            false_values=["no", "false"],
            on_bad_lines="warn",  # replaces the removed error_bad_lines flag
        )
    except UnicodeDecodeError as exc:
        raise ValueError(
            f"{csv_path} is not valid UTF-8; re-export it or pass the right encoding"
        ) from exc
    except pd.errors.EmptyDataError as exc:
        raise ValueError(f"{csv_path} is empty") from exc
    except pd.errors.ParserError as exc:
        raise ValueError(f"{csv_path} is malformed: {exc}") from exc

    # Enforce the contract before returning so downstream code can trust it.
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"{csv_path} is missing required column(s): {sorted(missing)}")

    return df


df = read_sensor_csv("data.csv")
print(f"Columns: {df.columns.tolist()}")
print(f"Shape: {df.shape}")
# .to_string() prints anywhere; use display() only inside Jupyter/IPython.
print(df.head(2).to_string())
```

> **HARD RULE — Engine selection:** The `pyarrow` engine can parse large files
> faster, but it supports a narrower set of `read_csv` keywords than the default
> C parser. Keep the C engine until profiling shows parsing is your bottleneck,
> then switch and re-test, because options like `true_values`/`false_values`
> may not carry over.

### Step 2 — Handling Missing Values Explicitly

The default NA handling is convenient but opinionated: pandas treats a long
list of tokens (`NA`, `null`, `N/A`, …) as missing. That backfires when one of
those tokens is a *legitimate* value in your data (e.g. `"NA"` as a region
code). By passing an explicit `na_values` list together with
`keep_default_na=False`, you make the missing-value contract visible and stop
pandas from guessing.

```python
from pathlib import Path

import pandas as pd

# These tokens — and only these — become NaN. Being explicit prevents pandas
# from silently converting valid strings into missing data, and prevents it
# from overlooking your own sentinel values.
NA_TOKENS: list[str] = ["", "NA", "null", "NaN", "None"]


def read_with_explicit_na(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(
        path,
        na_values=NA_TOKENS,
        keep_default_na=False,
        on_bad_lines="warn",
    )


def null_mask_for(df: pd.DataFrame, column: str) -> pd.Series:
    """Boolean mask of missing rows, treating empty/whitespace strings as missing.

    A plain .isna() is correct for numeric columns, but text columns often encode
    'missing' as an empty string that .isna() does not catch, so the test widens
    for string dtypes.
    """
    if column not in df.columns:
        raise KeyError(f"Column {column!r} not in DataFrame; have {df.columns.tolist()}")

    series = df[column]
    if pd.api.types.is_string_dtype(series):
        return series.isna() | (series.str.strip() == "")
    return series.isna()


df = read_with_explicit_na("data.csv")
print("Missing values per column:")
print(df.isna().sum().to_string())
```

### Step 3 — Accessing Data Safely

Prefer `.loc` over chained indexing such as `df[col][mask]`. Chained access
returns an ambiguous view-or-copy, which triggers `SettingWithCopyWarning` and
can make assignments land on a throwaway copy. `.loc` states the intent in one
step and behaves predictably. Validating requested columns up front turns a
cryptic `KeyError` deep in pandas into a clear message at the call site.

```python
import pandas as pd


def select_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Return a copy with only the requested columns, validating they exist first."""
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise KeyError(f"Unknown column(s): {missing}; available: {df.columns.tolist()}")
    return df.loc[:, columns].copy()


# Single column -> Series.
values: pd.Series = df.loc[:, "value"]

# Multiple columns -> DataFrame.
subset: pd.DataFrame = select_columns(df, ["id", "value"])

# Complex row filter. query() keeps the predicate readable and supports chained
# comparisons (30 <= elapsed_s < 60); both columns must exist in df.
recent_high: pd.DataFrame = df.query("value > 10 and 30 <= elapsed_s < 60")

# Keep only rows whose value is present (and non-empty for text columns).
valid_rows: pd.DataFrame = df[~null_mask_for(df, "value")]

# Optional column: fall back to a zero-filled Series so the rest of the pipeline
# never has to branch on whether the column was present.
flags: pd.Series = df.get("quality_flag", default=pd.Series(0, index=df.index))
```

### Step 4 — Writing CSV with Formula-Injection Sanitization

> **HARD RULE — CSV injection:** Spreadsheet apps treat a cell beginning with
> `=`, `+`, `-`, `@`, tab, or carriage return as the start of a formula. An
> attacker who controls a value can smuggle in
> `=HYPERLINK("http://evil.example","click")` or worse. Neutralize those cells
> before writing any file a human might open. This is non-negotiable for any
> output that may be opened in Excel, Google Sheets, or LibreOffice.

Also create the parent directory and confirm a non-empty write, so a missing
folder or a half-finished write fails loudly here rather than mysteriously
later.

```python
from pathlib import Path

import pandas as pd

# Leading formula triggers that spreadsheet apps will execute.
_FORMULA_PREFIXES: tuple[str, ...] = ("=", "+", "-", "@", "\t", "\r")


def sanitize_cell(value: object) -> object:
    """Prefix risky text cells with a single quote; pass non-strings through."""
    if isinstance(value, str) and value.startswith(_FORMULA_PREFIXES):
        return "'" + value
    return value


def sanitize_for_csv(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with every text column made safe against formula injection."""
    safe = df.copy()
    for column in safe.columns:
        if pd.api.types.is_object_dtype(safe[column]) or pd.api.types.is_string_dtype(
            safe[column]
        ):
            safe[column] = safe[column].map(sanitize_cell)
    return safe


def write_csv(df: pd.DataFrame, path: str | Path) -> Path:
    output_path = Path(path)
    # Create the directory tree so to_csv does not raise FileNotFoundError.
    output_path.parent.mkdir(parents=True, exist_ok=True)

    sanitize_for_csv(df).to_csv(
        output_path,
        index=False,
        encoding="utf-8",
        quotechar='"',  # default QUOTE_MINIMAL doubles embedded quotes for us
        date_format="%Y-%m-%d %H:%M:%S",
    )

    # A zero-byte file usually means an empty frame or an interrupted write.
    if output_path.stat().st_size == 0:
        raise IOError(f"Wrote an empty file to {output_path}")
    return output_path


data: dict[str, pd.Series | pd.Categorical] = {
    "time": pd.Series([0.0, 0.1, 0.2], dtype="float32"),
    "value": pd.Series([1.0, 2.0, 3.0], dtype="float32"),
    "label": pd.Categorical(["a", "b", "c"]),
}
write_csv(pd.DataFrame(data), "output.csv")
```

### Step 5 — Building Results Incrementally

> **HARD RULE — Never append to a DataFrame in a loop.** Each append copies the
> whole frame. Accumulate rows in a list of dicts and construct the DataFrame
> *once* at the end.

Using a typed `dataclass` for the row source gives you editor autocomplete and
catches field typos before runtime. The `exclude` argument keeps an internal
join key out of the exported artifact so it never leaks downstream.

```python
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True, slots=True)
class SensorReading:
    internal_id: int        # used for in-process joins, never exported
    time: pd.Timestamp
    value: float
    status: str
    valid: bool


def readings_to_csv(readings: list[SensorReading], path: str | Path) -> Path:
    if not readings:
        raise ValueError("Refusing to write a CSV from zero readings")

    rows: list[dict[str, str | int | float | None]] = []
    for reading in readings:
        rows.append(
            {
                "internal_id": reading.internal_id,
                "time": reading.time.isoformat(),
                "value": float(reading.value),
                # Keep status only for trusted rows; None becomes an empty cell.
                "status": str(reading.status) if reading.valid else None,
            }
        )

    # exclude drops internal_id from the written file so the internal join key
    # never ends up in an artifact we might share.
    df = pd.DataFrame.from_records(rows, index="time", exclude=["internal_id"])

    output_path = Path(path)
    df.to_csv(output_path, index=True, index_label="timestamp")
    return output_path


sample: list[SensorReading] = [
    SensorReading(1, pd.Timestamp("2026-06-16T00:00:00Z"), 1.0, "ok", True),
    SensorReading(2, pd.Timestamp("2026-06-16T00:01:00Z"), 2.0, "ok", False),
]
readings_to_csv(sample, "results.csv")
```

### Step 6 — Common Operations: Vectorize and Chunk

Two ideas carry most of the performance and clarity wins: **vectorize** instead
of looping (pandas pushes the work into C, so it is both faster and shorter),
and **chunk** files that might not fit in memory (trading a little speed for a
bounded memory footprint, which is what lets one function handle a 10 MB and a
10 GB file). Parse timestamps to tz-aware UTC so comparisons across machines
and timezones are unambiguous.

```python
from collections.abc import Iterator
from pathlib import Path

import pandas as pd


def summarize(df: pd.DataFrame, column: str) -> pd.Series:
    """Mean/std/min/max/count for one numeric column, validated up front."""
    if column not in df.columns:
        raise KeyError(f"{column!r} not found; columns are {df.columns.tolist()}")
    return df[column].agg(["mean", "std", "min", "max", "count"])


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add a vectorized delta column and normalize the timestamp to UTC."""
    required = {"col1", "col2", "timestamp"}
    missing = required - set(df.columns)
    if missing:
        raise KeyError(f"add_derived_columns needs column(s): {sorted(missing)}")

    out = df.copy()
    out["delta"] = out["col1"].sub(out["col2"], fill_value=0)  # vectorized, not a loop
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True)
    return out


def process_chunk(chunk: pd.DataFrame) -> int:
    """Validate one chunk and return how many rows are usable.

    Returning a count (instead of the rows) lets the caller keep a running total
    without holding every chunk in memory at once.
    """
    if "value" not in chunk.columns:
        raise KeyError("chunk is missing the 'value' column")
    usable = chunk.dropna(subset=["value"])
    usable = usable[usable["value"] >= 0]  # drop physically-impossible negatives
    return len(usable)


def process_large_csv(path: str | Path, chunk_rows: int = 10_000) -> int:
    """Stream a file that may exceed RAM, processing chunk_rows at a time."""
    if chunk_rows <= 0:
        raise ValueError(f"chunk_rows must be positive, got {chunk_rows}")

    total_usable = 0
    reader: Iterator[pd.DataFrame] = pd.read_csv(path, chunksize=chunk_rows)
    for chunk in reader:
        total_usable += process_chunk(chunk)
    return total_usable
```

## Examples

### Example 1 — Schema Validation with pandera

A declared schema turns "garbage in, garbage out" into "garbage in, exception
out", which is exactly what you want before data reaches a model or a report.

```python
from pathlib import Path

import pandas as pd
import pandera.pandas as pa
from pandera.errors import SchemaErrors


sensor_schema = pa.DataFrameSchema(
    {
        "sensor_id": pa.Column(int, checks=pa.Check.ge(0)),
        "value": pa.Column(float, nullable=True),
        "timestamp": pa.Column("datetime64[ns]", coerce=True),
    }
)


def load_clean_sensor_data(src: str | Path, dst: str | Path) -> pd.DataFrame:
    raw = pd.read_csv(src, parse_dates=["timestamp"])
    try:
        # lazy=True gathers every validation failure, not just the first one.
        validated = sensor_schema.validate(raw, lazy=True)
    except SchemaErrors as exc:
        raise ValueError(
            f"{src} failed schema validation:\n{exc.failure_cases}"
        ) from exc

    clean = validated.dropna(subset=["value"])
    clean.to_csv(dst, index=False)
    return clean


clean_df = load_clean_sensor_data("sensor_data.csv", "clean_sensor_data.csv")
```

### Example 2 — Resampling Time-Series Pipeline

```python
from pathlib import Path

import pandas as pd


def hourly_rollup(src: str | Path, dst: str | Path) -> pd.DataFrame:
    df = pd.read_csv(
        src,
        parse_dates=["timestamp"],
        dtype={"value": "float32"},
    ).set_index("timestamp")

    # resample assumes ordered timestamps; sort if the export was not ordered.
    if not df.index.is_monotonic_increasing:
        df = df.sort_index()

    hourly = (
        df.resample("1h")  # 'h' is the current alias; the old 'H' is deprecated
        .mean(numeric_only=True)
        .round(2)
        .assign(
            rolling_24h=lambda frame: frame["value"].rolling(24, min_periods=1).mean()
        )
    )
    hourly.to_csv(dst, float_format="%.3f")
    return hourly


rollup_df = hourly_rollup("timeseries.csv", "hourly_averages.csv")
```

## Pitfalls

1. **Dtype inference is data-dependent.** A column of pure integers becomes
   `float64` the moment a null appears. Always pin dtypes explicitly with the
   `dtype=` parameter.

2. **Default NA tokens clobber legitimate values.** `"NA"` as a region code
   becomes `NaN` silently. Use `na_values=[...]` with `keep_default_na=False`
   to make the contract explicit.

3. **Chained indexing causes `SettingWithCopyWarning`.** `df[col][mask] = x`
   may write to a copy, not the original. Always use `.loc` for assignment.

4. **CSV formula injection on write.** Any cell starting with `=`, `+`, `-`,
   `@`, `\t`, or `\r` is executed as a formula in spreadsheet apps. Always run
   `sanitize_for_csv` before writing.

5. **Appending to a DataFrame in a loop is O(n²).** Each `pd.concat` or
   `append` copies the entire frame. Accumulate dicts in a list, build once.

6. **`error_bad_lines` is removed.** Use `on_bad_lines="warn"` (or `"skip"`,
   `"error"`) instead. The old flag was deprecated and removed in pandas 2.0+.

7. **`'H'` frequency alias is deprecated.** Use `'1h'` or `'h'` for hourly
   resampling. The uppercase `'H'` triggers a `FutureWarning` in recent pandas.

8. **Empty-string vs NaN in text columns.** `.isna()` does not catch empty
   strings. Use `null_mask_for` which checks `series.str.strip() == ""` for
   string dtypes.

9. **Zero-byte output files.** A missing parent directory or an interrupted
   write can produce an empty file. Always check `stat().st_size` after
   writing and `mkdir(parents=True, exist_ok=True)` before.

10. **pyarrow engine keyword differences.** Switching to `engine="pyarrow"`
    may silently drop support for `true_values`, `false_values`, and other
    C-engine-only options. Re-test after switching.

## Verification

Each check targets a specific class of bug, so run the ones relevant to your
change:

1. **Run tests with fail-fast verbose output:**

```powershell
pytest -xvs
```

2. **Validate output structure with csvvalidator:**

```powershell
csvvalidator output.csv --schema schema.json
```

3. **Profile memory to catch frames that grew past RAM:**

```powershell
mprof run --python python_script.py
mprof plot
```

4. **Schema compliance with pandera** — guarantees every column's type and
   constraints hold, not just that the file parsed.

5. **Edge cases (empty files, malformed rows, all-null columns)** — these are
   where silent type coercion and NA handling break.

6. **Benchmark read/write** — guards against a "small" refactor that
   accidentally drops the fast path (vectorization, chunking).

### Roundtrip Test Example

```python
from pathlib import Path

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal


@pytest.fixture
def sample_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id": pd.array([1, 2, 3], dtype="int32"),
            "value": [1.1, 2.2, 3.3],
            "valid": [True, False, True],
        }
    )


def test_csv_roundtrip(tmp_path: Path, sample_data: pd.DataFrame) -> None:
    """A frame written then read back should be equal, modulo dtype narrowing.

    We relax dtype checks because the text format does not preserve int32 vs
    int64 — the contract we care about is that the *values* survive the trip.
    """
    target = tmp_path / "test.csv"
    sample_data.to_csv(target, index=False)

    loaded = pd.read_csv(target, dtype={"id": "int32"})

    assert_frame_equal(loaded, sample_data, check_dtype=False)
```

## Related Skills

- **pandas-data-analysis** (v2.1+) — grouping, joins, and reshaping once the
  data is loaded.
- **time-series-processing** (v3.0+) — resampling, gap-filling, and rolling
  windows in depth.
- **data-cleaning** (v2.0+) — deduplication, outlier handling, and
  normalization.
- **file-io-operations** (v1.5+) — atomic writes, path handling, and encoding
  edge cases.
- **data-validation** (v1.3+) — schema definition and contract testing with
  pandera.
- **memory-optimization** (v2.2+) — dtype downcasting and chunked/streaming
  patterns.
