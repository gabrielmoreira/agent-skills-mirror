---
name: nws-flood-thresholds
version: 1.1.1
description: "Downloads and parses NWS flood-stage thresholds (action/minor/moderate/major) for USGS gauges, then matches station IDs for labeling historical observations or a bulk snapshot. Use when asking at what stage flooding begins at a gauge, not how high the water is now. Not for live USGS levels, NWS forecasts, coastal or urban flooding without a river gauge, or locations outside the United States."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# NWS Flood Thresholds Guide

The National Weather Service (NWS) publishes the river stage (in feet) at which
each monitored gauge crosses from "watch it" into progressively more dangerous
flooding. This skill explains how to pull those *static* thresholds in bulk,
clean up the quirks in the published file, and match them back to USGS station
IDs. The emphasis throughout is on *why* each step exists, because the failure
modes here are quiet ones: a mislabeled column or a string-vs-number mismatch
does not crash, it just gives you wrong answers about whether a river flooded.

## When to Use

Reach for this skill when your question is "at what level does flooding begin
*here*?" rather than "how high is the water *right now*?". Concretely:

* You need the **action / minor / moderate / major** stage for one or many
  gauges, e.g. to label historical water-level observations as flood / no-flood.
* You are joining flood thresholds onto **USGS station data** and need the IDs to
  line up exactly (the matching is the part that usually breaks).
* You want a **single bulk snapshot** of every gauge in the country to load into
  a database, a notebook, or a downstream analytics job.

The thresholds are reference constants, so they are cheap to cache and reuse —
that is what makes a bulk download the right tool instead of per-station API
calls.

### When NOT to use

Each of these is a *capability boundary*, not an arbitrary rule — knowing the
reason lets you judge the edge cases:

* **You need real-time water levels.** This file is a static threshold table. It
  tells you the flood stage is 18 ft; it does not tell you the river is at 17.4
  ft today. Pair it with `usgs-water-data` for live readings.
* **You need a forecast.** Thresholds are historical/definitional. For "will it
  flood tomorrow?" use the NWS forecast products (`nws-forecast-api`).
* **You need non-riverine flooding** (coastal surge, urban flash flooding) that
  has no river gauge. Those phenomena are not represented in a gauge-stage table,
  so the data simply will not exist for them.
* **You need locations outside the United States.** NWS only covers US gauges.
* **You are in a locked-down environment that blocks outbound HTTP.** The skill
  fetches directly from NOAA servers; without a vetted proxy the download will
  fail. Know this up front rather than discovering it mid-pipeline.
* **You are on Python 3.8 or earlier.** The examples use pandas 2.x APIs (the
  nullable `string` dtype, `Series.mask`) and modern type-hint syntax, which need
  Python 3.9+ to import cleanly.

## Prerequisites

| Requirement | Detail |
|-------------|--------|
| Python | 3.9+ (3.10+ recommended for `\|` union syntax in type hints) |
| pandas | `>=2.2,<3` — pin in your venv to avoid parsing-behavior changes |
| requests | `>=2.32,<3` |
| OpenSSL | 3.0+ (NOAA updated TLS in 2025; older OpenSSL will fail the handshake) |
| Network | Outbound HTTPS to `water.noaa.gov` required |
| OS | Windows host is primary (PowerShell). All path examples use Windows-style paths. |

### Install dependencies (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install "pandas>=2.2,<3" "requests>=2.32,<3"
```

## Procedure

### Step 1 — Understand the data sources

There are two ways to get the data; the trade-off is breadth vs. immediacy.

**Option 1 — Bulk CSV (use this for more than a handful of stations).** One
request returns every gauge in the country, so you pay a single round trip and
can cache the result. This is almost always the right choice for analysis.

```text
https://water.noaa.gov/resources/downloads/reports/nwps_all_gauges_report.csv
```

**Option 2 — Individual station pages (use this for spot checks).** Good for
verifying one value against the official source, not for batch work — hitting it
per station is slow and rude to NOAA's servers.

```text
https://water.noaa.gov/gauges/<station_id>
```

Example: `https://water.noaa.gov/gauges/04118105`

### Step 2 — Understand the flood stage categories

NWS defines four escalating thresholds. The reason the table calls out **flood
stage** as primary is that it is the dividing line between "no flooding" and
"flooding" — the other three refine *how bad* it is.

| Category | CSV column | What it means | Why you'd use it |
|----------|------------|---------------|------------------|
| Action stage | `action stage` | Water is high enough to start monitoring / preparing. | Early-warning logic. |
| **Flood stage (minor)** | **`flood stage`** | Flooding begins: minor property impact, some public threat. | **The yes/no flood test — use this as the default threshold.** |
| Moderate flood stage | `moderate flood stage` | Structures inundated; evacuations possible. | Severity tiering. |
| Major flood stage | `major flood stage` | Extensive damage; significant evacuations. | Worst-case classification. |

> For a simple "did it flood?" question, compare the observed level against
> `flood stage`. Reach for the other three only when you need to grade severity.

### Step 3 — Save the reference implementation

Save the following as `nws_flood_thresholds.py` in your project. It is fully
typed, validates its inputs at the boundary, and turns NOAA's quirks (the
trailing-delimiter column, the `-9999` sentinel, IDs that look like numbers)
into explicit, documented handling instead of silent bugs.

```python
from __future__ import annotations

import io
import logging
import math
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Final, TypedDict

import pandas as pd
import requests

logger = logging.getLogger("nws_flood_thresholds")


# --- Configuration ------------------------------------------------------------
NWS_REPORT_URL: Final[str] = (
    "https://water.noaa.gov/resources/downloads/reports/nwps_all_gauges_report.csv"
)
DEFAULT_CACHE_PATH: Final[Path] = Path("cache") / "nwps_all_gauges_report.csv"

# NOAA writes -9999 (not a blank) when a gauge has no threshold for a category.
# Treated as a real number it would wreck any min / mean / percentile, so every
# reader below converts it to NaN at the point of parsing.
SENTINEL_NO_VALUE: Final[float] = -9999.0

# USGS site numbers are 8-character identifiers that are zero-padded on the left.
USGS_ID_WIDTH: Final[int] = 8

# The four threshold columns, ordered lowest to highest severity.
STAGE_COLUMNS: Final[tuple[str, ...]] = (
    "action stage",
    "flood stage",
    "moderate flood stage",
    "major flood stage",
)

# A bounded timeout: a hung socket should fail the run, not freeze it forever.
DEFAULT_TIMEOUT_SECONDS: Final[float] = 30.0


# --- Errors -------------------------------------------------------------------
class NwsThresholdError(RuntimeError):
    """Base class for every error this module raises deliberately."""


class NwsDownloadError(NwsThresholdError):
    """The report could not be fetched, came back empty, or failed to parse."""


class NwsSchemaError(NwsThresholdError):
    """The report parsed but is missing columns this skill depends on."""


# --- Typed result -------------------------------------------------------------
class StationThresholds(TypedDict):
    """Flood-stage thresholds for one gauge, in feet.

    A value of ``float('nan')`` means NOAA does not publish that category for the
    gauge (it was blank or the ``-9999`` sentinel). Test it with ``math.isnan``
    rather than comparing against a magic number, so missing data never gets
    mistaken for a real reading of -9999 ft.
    """

    name: str
    action: float
    flood: float
    moderate: float
    major: float


# --- Small, defensive parsers -------------------------------------------------
def normalize_usgs_id(raw: object) -> str:
    """Coerce any cell value to the canonical 8-char, zero-padded USGS id.

    USGS site numbers are identifiers, not integers. ``'04118105'`` must stay an
    8-character string; the moment it is read as a number it becomes ``4118105``
    and silently fails to match the report. We also drop the trailing ``.0`` that
    appears when a column was inferred as float somewhere upstream.
    """
    text = str(raw).strip()
    if text.endswith(".0"):
        text = text[:-2]
    return text.zfill(USGS_ID_WIDTH)


def parse_stage(raw: object) -> float:
    """Parse one stage cell to float, mapping blanks and ``-9999`` to NaN.

    Returning NaN instead of raising means a single malformed gauge cannot abort
    a batch of thousands; the NaN is trivial to filter or branch on downstream.
    """
    if raw is None:
        return math.nan
    text = str(raw).strip()
    if text == "" or text.lower() in {"nan", "none", "null", "<na>"}:
        return math.nan
    try:
        value = float(text)
    except (TypeError, ValueError):
        return math.nan
    if value == SENTINEL_NO_VALUE:
        return math.nan
    return value


# --- Schema check -------------------------------------------------------------
def validate_schema(df: pd.DataFrame) -> None:
    """Raise ``NwsSchemaError`` if the report lacks columns this skill relies on.

    NOAA reorders and occasionally renames report columns. Checking once, right
    after download, turns a confusing ``KeyError`` deep inside a later transform
    into a single clear message at the source.
    """
    required = {"usgs id", "location name", "state", *STAGE_COLUMNS}
    missing = required.difference(df.columns)
    if missing:
        raise NwsSchemaError(
            "NWS report is missing expected columns: "
            f"{sorted(missing)}. The published report layout may have changed."
        )


# --- Download + load ----------------------------------------------------------
def download_report(
    url: str = NWS_REPORT_URL,
    cache_path: Path = DEFAULT_CACHE_PATH,
    *,
    refresh: bool = False,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    session: requests.Session | None = None,
) -> pd.DataFrame:
    """Fetch (or load from cache) the NWS gauge report as a clean DataFrame.

    Why cache? The report is several megabytes and updates at most once a day, so
    re-fetching every run wastes NOAA bandwidth and your wall-clock time. Pass
    ``refresh=True`` to force a fresh download when you suspect the cache is stale.

    Why ``index_col=False``? Each NWS data row carries a trailing delimiter, so it
    has one more field than the header. Left to its defaults, pandas "absorbs"
    that extra field by promoting the first real column into the DataFrame index,
    which shifts every value one column to the left — ``usgs id`` ends up under
    ``location name`` and so on, with no error. ``index_col=False`` is pandas'
    documented fix for trailing-delimiter files and keeps the columns aligned.
    """
    if not url.lower().startswith("https://"):
        raise ValueError(f"Refusing to download over a non-HTTPS URL: {url!r}")
    if timeout <= 0:
        raise ValueError(f"timeout must be a positive number of seconds, got {timeout!r}")

    cache_path.parent.mkdir(parents=True, exist_ok=True)

    if refresh or not cache_path.is_file():
        logger.info("Downloading NWS gauge report from %s", url)
        http = session if session is not None else requests
        try:
            response = http.get(url, timeout=timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise NwsDownloadError(f"Failed to download NWS report from {url}: {exc}") from exc
        if not response.content:
            raise NwsDownloadError(f"NWS report at {url} responded with an empty body")
        cache_path.write_bytes(response.content)
    else:
        logger.debug("Using cached NWS gauge report at %s", cache_path)

    raw_text = cache_path.read_text(encoding="utf-8")
    if not raw_text.strip():
        raise NwsDownloadError(
            f"Cached NWS report at {cache_path} is empty; "
            "delete it and re-run with refresh=True."
        )

    try:
        frame = pd.read_csv(
            io.StringIO(raw_text),
            dtype="string",   # keep ids and codes as text; never infer numerics here
            header=0,
            index_col=False,  # see docstring: prevents the trailing-delimiter column shift
            low_memory=False, # read the whole file before inferring, avoids mixed-type warnings
        )
    except (pd.errors.ParserError, pd.errors.EmptyDataError) as exc:
        raise NwsDownloadError(f"Could not parse NWS report at {cache_path}: {exc}") from exc

    # Normalize headers (strip + lower-case) so lookups stay stable even if NOAA
    # changes the casing or spacing of a column label.
    frame.columns = [str(col).strip().lower() for col in frame.columns]

    validate_schema(frame)
    return frame


# --- Transforms ---------------------------------------------------------------
def coerce_stage_columns(
    df: pd.DataFrame,
    columns: Sequence[str] = STAGE_COLUMNS,
) -> pd.DataFrame:
    """Return a copy with the given stage columns as ``float64`` and sentinels as NaN.

    Convert right after loading: every downstream question ("is the river above
    flood stage?") is numeric. Doing the conversion once, centrally, means no
    caller has to remember the ``-9999`` sentinel or risk comparing a string to a
    number and getting a silently wrong answer.
    """
    result = df.copy()
    for col in columns:
        if col not in result.columns:
            raise NwsSchemaError(f"Expected stage column {col!r} is not present in the DataFrame")
        numeric = pd.to_numeric(result[col], errors="coerce")
        # mask() swaps only the sentinel for NaN and leaves real values untouched.
        result[col] = numeric.mask(numeric.eq(SENTINEL_NO_VALUE)).astype("float64")
    return result


def filter_by_state(df: pd.DataFrame, state_code: str) -> pd.DataFrame:
    """Return rows for one state that have a USGS id and a usable flood stage.

    The mask drops two classes of unusable rows on purpose. Gauges with an empty
    ``usgs id`` are NWS-only and cannot be joined to USGS data, so they would only
    create null keys. Gauges whose flood stage is missing or ``-9999`` carry no
    threshold to compare against, so keeping them would just inject NaNs into
    every later calculation.
    """
    if not isinstance(state_code, str) or len(state_code.strip()) != 2:
        raise ValueError(f"state_code must be a two-letter code, got {state_code!r}")
    required = {"state", "usgs id", "flood stage"}
    missing = required.difference(df.columns)
    if missing:
        raise NwsSchemaError(f"DataFrame is missing required columns: {sorted(missing)}")

    code = state_code.strip().upper()
    state = df["state"].astype("string").str.strip().str.upper()
    usgs = df["usgs id"].astype("string").str.strip()
    flood = pd.to_numeric(df["flood stage"], errors="coerce")

    mask = (
        state.eq(code)
        & usgs.notna()
        & usgs.ne("")
        & flood.notna()
        & flood.ne(SENTINEL_NO_VALUE)
    )
    return df.loc[mask].copy()


def build_threshold_dict(
    df: pd.DataFrame,
    station_ids: Iterable[str],
) -> dict[str, StationThresholds]:
    """Build ``{usgs_id: StationThresholds}`` for each requested id found in ``df``.

    Why normalize both sides? The caller's ids and the report's ids must be
    compared in the same canonical form (8-char, zero-padded) or ``'4118105'``
    will never match ``'04118105'``. We filter the frame to the requested ids
    first and iterate only the matched handful of rows, so the per-row loop stays
    cheap even though the full report has thousands of gauges.
    """
    required = {"usgs id", "location name", *STAGE_COLUMNS}
    missing = required.difference(df.columns)
    if missing:
        raise NwsSchemaError(f"DataFrame is missing required columns: {sorted(missing)}")

    wanted = {normalize_usgs_id(sid) for sid in station_ids}
    if not wanted:
        return {}

    canonical_ids = df["usgs id"].map(normalize_usgs_id)
    subset = df.loc[canonical_ids.isin(wanted)]

    thresholds: dict[str, StationThresholds] = {}
    for _, row in subset.iterrows():
        usgs_id = normalize_usgs_id(row["usgs id"])
        thresholds[usgs_id] = StationThresholds(
            name=str(row["location name"]),
            action=parse_stage(row["action stage"]),
            flood=parse_stage(row["flood stage"]),
            moderate=parse_stage(row["moderate flood stage"]),
            major=parse_stage(row["major flood stage"]),
        )
    return thresholds


def get_station_threshold(df: pd.DataFrame, usgs_id: str) -> StationThresholds | None:
    """Return one station's thresholds, or ``None`` if the gauge is not in the report."""
    if not isinstance(usgs_id, str) or not usgs_id.strip():
        raise ValueError(f"usgs_id must be a non-empty string, got {usgs_id!r}")
    return build_threshold_dict(df, [usgs_id]).get(normalize_usgs_id(usgs_id))
```

### Step 4 — Key columns reference

These are the columns the code above depends on. `validate_schema` checks for
exactly this set, so if NOAA renames one you get a clear error instead of a
mysterious empty result.

| Column name | Description |
|-------------|-------------|
| `usgs id` | USGS station id (8-char string, zero-padded on the left). |
| `location name` | Human-readable station / location name. |
| `state` | Two-letter state code. |
| `action stage` | Action threshold (feet). |
| `flood stage` | Minor flood threshold (feet) — the primary yes/no line. |
| `moderate flood stage` | Moderate flood threshold (feet). |
| `major flood stage` | Major flood threshold (feet). |

### Step 5 — Run the end-to-end example

This reuses the module above to download, clean, filter by state, and look up
specific stations — including the branch for a category NOAA does not publish.

```python
import math

# 1. Download (or load from cache) and validate the report in one call.
report = download_report(refresh=False)

# 2. Convert the four stage columns to numeric; sentinels become NaN.
report = coerce_stage_columns(report)

# 3. List California gauges that have a usable flood stage.
california = filter_by_state(report, "CA")
print(f"California gauges with a flood stage: {len(california)}")
print(
    california[["usgs id", "location name", "flood stage"]]
    .head(10)
    .to_string(index=False)
)

# 4. Look up specific stations and handle missing categories explicitly.
target_ids = ["04118105", "02334500"]
thresholds = build_threshold_dict(report, target_ids)
for station_id in target_ids:
    record = thresholds.get(normalize_usgs_id(station_id))
    if record is None:
        print(f"{station_id}: not present in the NWS report")
        continue
    flood = record["flood"]
    flood_text = "not published" if math.isnan(flood) else f"{flood:.1f} ft"
    print(f"{station_id} ({record['name']}): flood stage = {flood_text}")

# 5. Single-station convenience lookup.
single = get_station_threshold(report, "04118105")
if single is not None:
    print(f"Action stage for 04118105: {single['action']} ft")
```

### Step 6 — Spot-check a single station against the official page

For verification of one value, compare against the NWS gauge page directly:

```text
https://water.noaa.gov/gauges/04118105
```

Open the URL in a browser or fetch it with `requests.get` and confirm the flood
stage shown matches what `get_station_threshold` returned.

## Pitfalls

### The 43-vs-44 column quirk (MOST COMMON BUG)

The NWS report has historically shipped data rows with **one more field than the
header row** because every row ends with a trailing comma. This is the single
most common source of "my columns are all shifted" bugs with this file.

The naive read — calling `pd.read_csv` with its default arguments — does not
error. Instead pandas quietly decides the extra field means the first column is a
row index, promotes it, and slides every remaining value one position left. Your
`usgs id` data then sits under the `location name` label, and nothing complains.

**Fix:** Always read with `index_col=False` (see `download_report`). This tells
pandas "do not treat any column as the index," so the trailing empty field is
dropped and the remaining columns line up with the header exactly. After parsing
we lower-case the headers and run `validate_schema`, so any *future* layout
change surfaces immediately rather than corrupting results downstream.

### Common issues & mitigations

| Issue | Cause | Why it bites | Mitigation |
|-------|-------|--------------|------------|
| Columns shifted by one | Trailing comma → 44 data fields vs 43 headers | pandas silently promotes a column to the index | Read with `index_col=False` (see `download_report`) |
| Stage value of `-9999` | NOAA's sentinel for "no threshold defined" | Treated as a real number it skews every aggregate | Map to NaN at parse time (`parse_stage`, `coerce_stage_columns`) |
| Empty `usgs id` | Gauge is NWS-only, no USGS counterpart | Produces null join keys against USGS data | Exclude when matching (`filter_by_state`); keep for NWS-only work |
| ID `04118105` won't match | Read as a number, leading zero lost | `4118105 != '04118105'` and the match fails | Always canonicalize via `normalize_usgs_id` |
| Missing thresholds for a known gauge | Station absent from the report | Lookups return `None` unexpectedly | Fall back to USGS stage-discharge tables or flag as unavailable |
| SSL/TLS handshake failure | Outdated OpenSSL after NOAA's 2025 TLS change | Download fails before any parsing | Run on OpenSSL 3.0+; keep `verify=True` (the default) |

### Best practices (HARD RULES)

1. **Cache the CSV and refresh at most once a day.** The thresholds barely
   change, so frequent downloads only waste NOAA bandwidth and your time —
   `refresh=True` exists for the occasional forced refetch.
2. **Validate the schema on every load.** A renamed column should fail loudly at
   the source (`validate_schema`), not produce a quietly empty result three steps
   later.
3. **Convert thresholds to numeric immediately**, mapping `-9999` and blanks to
   NaN, so no comparison ever runs against a string or a sentinel.
4. **Treat USGS ids as zero-padded strings end to end.** The leading zero is real
   data; lose it once and every join silently misses rows.
5. **Pin compatible dependency ranges** (`pandas>=2.2,<3` and
   `requests>=2.32,<3`) in a virtual environment, so a future major release
   can't change parsing behavior under you without a deliberate upgrade.
6. **Never delete the cache file unless intentionally refreshing.** If the cache
   is empty or corrupt, delete it and re-run with `refresh=True` — do not
   silently work around a bad cache.

## Verification

Run each check below to confirm the pipeline is producing correct results.

### 1. Schema and column alignment

```python
from nws_flood_thresholds import download_report, validate_schema

report = download_report(refresh=False)
validate_schema(report)  # raises NwsSchemaError if columns are missing
print(report.columns.tolist())
# Confirm "usgs id" is the first data column (not absorbed into the index)
assert "usgs id" in report.columns
assert report.index.name is None  # no column was silently promoted
```

### 2. Stage columns are numeric with sentinels removed

```python
from nws_flood_thresholds import download_report, coerce_stage_columns, STAGE_COLUMNS, SENTINEL_NO_VALUE

report = download_report()
report = coerce_stage_columns(report)
for col in STAGE_COLUMNS:
    assert report[col].dtype == "float64", f"{col} is {report[col].dtype}, expected float64"
    assert not report[col].eq(SENTINEL_NO_VALUE).any(), f"{col} still contains -9999 sentinel"
print("All stage columns are float64 with no -9999 sentinels.")
```

### 3. State filter returns expected row count

```python
from nws_flood_thresholds import download_report, coerce_stage_columns, filter_by_state

report = coerce_stage_columns(download_report())
ca = filter_by_state(report, "CA")
print(f"California gauges with a flood stage: {len(ca)}")
assert len(ca) > 0, "Expected non-zero California gauges"
```

### 4. Single-station lookup matches official NWS page

```python
from nws_flood_thresholds import download_report, coerce_stage_columns, get_station_threshold

report = coerce_stage_columns(download_report())
result = get_station_threshold(report, "04118105")
assert result is not None, "Station 04118105 should be in the report"
print(f"04118105 ({result['name']}): flood stage = {result['flood']} ft")
# Cross-check against https://water.noaa.gov/gauges/04118105
```

### 5. Forced refresh still parses cleanly

```python
from nws_flood_thresholds import download_report

report = download_report(refresh=True)
print(f"Refreshed report: {len(report)} rows, {len(report.columns)} columns")
```

### 6. No sentinels or empty IDs in filtered dataset

```python
from nws_flood_thresholds import download_report, coerce_stage_columns, filter_by_state, SENTINEL_NO_VALUE

report = coerce_stage_columns(download_report())
ca = filter_by_state(report, "CA")
assert ca["usgs id"].notna().all() and (ca["usgs id"].str.strip() != "").all()
assert not ca["flood stage"].eq(SENTINEL_NO_VALUE).any()
assert ca["flood stage"].notna().all()
print("Filtered dataset is clean: no empty IDs, no -9999, no NaN flood stages.")
```

## Related skills

* `usgs-water-data` — retrieve real-time or historical water levels to compare
  against these thresholds.
* `nws-forecast-api` — pull NWS weather and flood *forecasts* (the predictive
  counterpart to these static thresholds).
* `geospatial-analysis` — join thresholds to GIS layers for mapping and spatial
  queries.
