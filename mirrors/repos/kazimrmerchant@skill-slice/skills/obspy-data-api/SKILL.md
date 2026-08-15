---
name: obspy-data-api
version: 1.1.1
description: "Parses seismological formats (MiniSEED, SAC, QuakeML, StationXML) into ObsPy Stream/Trace, Catalog/Event, and Inventory objects. Use when ingesting waveforms, event catalogs, or station metadata for processing or SeisBench. Not for generic non-seismic time series (NumPy/pandas). Never pass untrusted paths or URLs straight to read()."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

## When to Use

Reach for the ObsPy data API when you need to turn heterogeneous seismological files into a small, consistent set of in-memory objects. Seismic data ships in dozens of historical formats (MiniSEED, SAC, GSE2, SEISAN, Q, and more), and metadata arrives as QuakeML or FDSN StationXML. ObsPy normalizes all of that into three parallel object hierarchies — waveforms (`Stream`/`Trace`), event catalogs (`Catalog`/`Event`), and station inventories (`Inventory`) — so the rest of your pipeline can target one stable API instead of writing a parser per format.

**Trigger keywords:** seismology, seismic, waveform, MiniSEED, SAC, GSE2, SEISAN, QuakeML, StationXML, FDSN, earthquake, seismogram, trace, stream, catalog, inventory, instrument response, ObsPy, SeisBench.

That normalization is the real value: once data is in a `Trace`, downstream consumers such as ObsPy's own signal-processing routines (filtering, response removal, resampling) or SeisBench's machine-learning models all expect the same shape. Use this API whenever you are:

1. Ingesting seismic data for processing.
2. Converting custom arrays into standard objects.
3. Round-tripping metadata between formats.

### Do Not Use

Prefer something lighter for generic, non-seismic time series. ObsPy pulls in a large scientific stack (NumPy, SciPy, and optional Matplotlib) and models domain concepts — networks, stations, channels, instrument responses, QuakeML event trees — that add friction when all you have is a plain array. For non-seismic signals, NumPy or pandas is simpler and clearer; only adopt ObsPy when you actually benefit from its format support or seismology helpers.

Do not trust `read()` to silently sort out unexpected inputs. It auto-detects a format by trying each registered reader in turn, so feeding it an unsupported or removed format produces confusing, slow-to-surface errors. Pin the formats you expect (see `SUPPORTED_WAVEFORM_FORMATS` below) so a bad input fails loudly and immediately instead of being mis-parsed.

Treat any caller-controlled path or URL as hostile. `read()`, `read_events()`, and `read_inventory()` all accept a URL *or* a local path through the same argument, and ObsPy will fetch `http(s)`/`ftp` URLs server-side (it downloads to a temp file whenever `"://"` appears near the start of the string). If part of that string comes from an untrusted source, an attacker can request `file:///etc/passwd`, traverse upward with `../`, or point the loader at an internal service (SSRF). That is *why* the helpers below validate the URL scheme against an allow-list and confine local reads to a known base directory rather than passing raw input straight to the reader.

## Prerequisites

- Python 3.10+ (uses `from __future__ import annotations`, `frozenset[str]` syntax, `Path.is_relative_to`).
- ObsPy installed: `pip install obspy` (pulls NumPy, SciPy, and optional Matplotlib).
- No network access required for bundled example data (`read()` with no arguments loads ObsPy's packaged sample seismogram).
- Windows host is primary (PowerShell). Local paths like `~\agent-skills\library\obspy-data-api\` are expected; the `_looks_like_url` helper correctly distinguishes Windows drive letters (e.g. `C:\data\trace.mseed`) from genuine URLs.

## Procedure

### 1. Understand the Data Model

There is one mental model that covers the whole API: each kind of seismic information has a **container** that is iterated to yield **element objects**, plus a `read_*` entry point and a `.write()` method for round-tripping.

| Kind | Read with | Container | Element(s) |
|------|-----------|-----------|------------|
| Waveforms | `read()` | `Stream` | `Trace` |
| Events | `read_events()` | `Catalog` | `Event` |
| Stations | `read_inventory()` | `Inventory` | `Network` → `Station` → `Channel` |

The containers are list-like because a single deployment naturally produces many elements — a three-component sensor yields three traces, a catalog holds many events, a network holds many stations. Processing helpers live on the *element* objects (and, for convenience, on `Stream`), so you can chain operations close to the data they act on.

### 2. Work with Waveform Data (`Stream` and `Trace`)

A `Stream` is a list-like collection of `Trace` objects, where each `Trace` is a gap-less, continuous time series plus its metadata.

Each `Trace` exposes:

- `data` → a NumPy `ndarray` holding the actual samples.
- `stats` → a dict-like `Stats` object holding metadata. Both `stats.starttime` and `stats.endtime` are `UTCDateTime` objects.

**`Trace.stats` fields (and why they are grouped):**

- `network`, `station`, `location`, `channel` — the SEED identifiers that pin down the physical site and the specific instrument/component.
- `starttime`, `sampling_rate`, `delta`, `endtime`, `npts` — these are interrelated: given `starttime`, `sampling_rate` (or its inverse `delta`), and `npts` (sample count), ObsPy derives `endtime`. Setting one recomputes the others, which is why you change timing through these fields rather than editing `endtime` directly.

**Common `Trace` methods** (each mutates the trace in place, so copy first if you need the original):

- `taper()` — applies a window taper to reduce edge effects before filtering.
- `filter()` — applies a frequency-domain or IIR filter.
- `resample()` — resamples the data in the frequency domain.
- `integrate()` — integrates with respect to time (e.g. velocity → displacement).
- `remove_response()` — deconvolves the instrument response to recover ground motion in physical units.

### 3. Work with Event Metadata (`Catalog` and `Event`)

Event metadata follows the de-facto standard [QuakeML](https://quake.ethz.ch/quakeml/). Use `read_events()` to load and `Catalog.write()` to export.

**Hierarchy:** `Catalog` → `events` → `Event` (multiple)

An `Event` is a tree, because a single seismic event can have several competing solutions (different agencies, methods, or revisions):

- `origins` → `Origin` (multiple): `time`, `latitude`, `longitude`, `depth` (in **meters**), `depth_type`, `quality`, `evaluation_mode`, `evaluation_status`, `creation_info`, and the `arrivals`/`comments` containers.
- `magnitudes` → `Magnitude` (multiple): `mag`, `magnitude_type`, `station_count`, `azimuthal_gap`, `evaluation_mode`, `evaluation_status`, `creation_info`.
- `picks` → `Pick` (multiple): individual phase arrival picks (`time`, `waveform_id`, `phase_hint`, `polarity`, `evaluation_mode`).
- `focal_mechanisms` → `FocalMechanism` (multiple): `nodal_planes`, `principal_axes`, `moment_tensor`, `evaluation_mode`.
- Plus `amplitudes`, `station_magnitudes`, `event_descriptions`, `comments`, and the `event_type`/`creation_info` fields.

Because there can be many solutions, `Event` also stores `preferred_origin_id`, `preferred_magnitude_id`, and `preferred_focal_mechanism_id`, with helper methods `preferred_origin()`, `preferred_magnitude()`, and `preferred_focal_mechanism()` to fetch the chosen one. **Prefer those helpers over indexing `origins[0]`**, which is not guaranteed to be the authoritative solution.

### 4. Work with Station Metadata (`Inventory`)

Station metadata follows [FDSN StationXML](https://www.fdsn.org/xml/station/), the human-readable XML replacement for Dataless SEED. Use `read_inventory()` to load and `Inventory.write()` to export.

**Hierarchy:** `Inventory` → `networks` → `Network` → `stations` → `Station` → `channels` → `Channel`

- **Network:** `code`, `description`, `start_date`, `end_date`, `restricted_status`, `total_number_of_stations`, `operators`, `source_id`, and the `stations` container.
- **Station:** `code`, `latitude`, `longitude`, `elevation`, `site`, `creation_date`, `termination_date`, `start_date`, `end_date`, `description`, and the `channels` container.
- **Channel:** `code`, `location_code`, `latitude`, `longitude`, `elevation`, `depth`, `azimuth`, `dip`, `sample_rate`, `sensor`, `data_logger`, `response`, `start_date`, `end_date`.

The four-level nesting exists because instruments move and get replaced over time: a `Channel`'s `start_date`/`end_date` scope a particular sensor at a particular orientation, and `response` carries the calibration needed by `Trace.remove_response()`.

### 5. Load Data Safely

The functions below wrap the `read_*` entry points with explicit typing, strict parameter validation, and defensive error handling. The validation is not ceremony: it is what stops untrusted input from escaping the data sandbox or reaching the network.

```python
from __future__ import annotations

from pathlib import Path
from typing import Final
from urllib.parse import urlparse

from obspy import Catalog, Inventory, Stream, read, read_events, read_inventory

# ObsPy can guess a format by trying every reader, but guessing on untrusted
# input is how you end up parsing the wrong thing or hitting a slow fallback.
# Pin the formats you actually expect so unknown input fails loudly and early.
SUPPORTED_WAVEFORM_FORMATS: Final[frozenset[str]] = frozenset(
    {"MSEED", "SAC", "GSE2", "SEISAN", "Q", "SH_ASC", "SLIST", "TSPAIR", "WAV"}
)

# read()/read_events()/read_inventory() all fetch URLs server-side. Without a
# scheme allow-list a caller-supplied string could reach file://, ftp://, or an
# internal http endpoint (SSRF), so only these schemes are treated as URLs.
ALLOWED_URL_SCHEMES: Final[frozenset[str]] = frozenset({"http", "https"})


def _looks_like_url(source: str) -> bool:
    """Return True only for genuine network URLs.

    A single-character "scheme" is really a Windows drive letter (for example
    ``C:\\data\\trace.mseed``), not a URL, so we require a multi-character
    scheme *and* a network location.
    Misclassifying a local path as a URL would skip the path-traversal check.
    """
    parsed = urlparse(source)
    return len(parsed.scheme) > 1 and bool(parsed.netloc)


def _resolve_local_path(source: str | Path, base_dir: Path) -> Path:
    """Resolve *source* and confirm it stays inside *base_dir*.

    ``resolve()`` collapses ``..`` segments and symlinks, and
    ``is_relative_to`` then rejects anything that escapes the sandbox. This is
    what prevents ``../../etc/passwd`` from reaching ObsPy's reader. ``base_dir``
    is resolved with ``strict=True`` so a missing sandbox fails fast and
    obviously rather than silently allowing every path.
    """
    base = base_dir.expanduser().resolve(strict=True)
    src = Path(source)
    candidate = (src if src.is_absolute() else base / src).resolve()
    if not candidate.is_relative_to(base):
        raise ValueError(f"Refusing to read {candidate}: escapes base_dir {base}")
    if not candidate.is_file():
        raise FileNotFoundError(f"No such file: {candidate}")
    return candidate


def _resolve_source(source: str | Path, base_dir: Path | None) -> str:
    """Validate *source* and return a target string for an ObsPy reader.

    Accepts an ``http(s)`` URL or a local path confined to *base_dir*. Raises
    early on the disallowed cases so the readers never see unvalidated input.
    """
    if not isinstance(source, (str, Path)):
        raise TypeError(f"source must be str or Path, got {type(source).__name__}")

    raw = str(source)
    if isinstance(source, str) and _looks_like_url(raw):
        scheme = urlparse(raw).scheme.lower()
        if scheme not in ALLOWED_URL_SCHEMES:
            raise ValueError(
                f"Disallowed URL scheme {scheme!r}; "
                f"allowed: {sorted(ALLOWED_URL_SCHEMES)}"
            )
        return raw

    if base_dir is None:
        raise ValueError("base_dir is required when reading local files")
    return str(_resolve_local_path(source, base_dir))


def load_waveform(
    source: str | Path,
    *,
    base_dir: Path | None = None,
    fmt: str | None = None,
) -> Stream:
    """Read a waveform file or URL into a validated, non-empty ``Stream``.

    Parameters
    ----------
    source:
        An ``http(s)`` URL or a filesystem path resolved against *base_dir*.
    base_dir:
        Directory that local paths must stay within. Required for local reads so
        untrusted *source* values cannot escape the data sandbox.
    fmt:
        Optional explicit format. When given it must be one of
        ``SUPPORTED_WAVEFORM_FORMATS``; passing it lets ObsPy skip
        auto-detection, which is both faster and less ambiguous.

    Returns
    -------
    Stream
        A stream guaranteed to contain at least one ``Trace``.

    Raises
    ------
    TypeError
        If *source* or *fmt* has the wrong type.
    ValueError
        If *fmt* is unsupported, the URL scheme is disallowed, a local path
        escapes *base_dir*, or the data cannot be parsed.
    FileNotFoundError
        If a local *source* does not exist.
    """
    if fmt is not None:
        if not isinstance(fmt, str):
            raise TypeError(f"fmt must be str or None, got {type(fmt).__name__}")
        fmt = fmt.upper()
        if fmt not in SUPPORTED_WAVEFORM_FORMATS:
            raise ValueError(
                f"Unsupported format {fmt!r}; expected one of "
                f"{sorted(SUPPORTED_WAVEFORM_FORMATS)}"
            )

    target = _resolve_source(source, base_dir)
    try:
        stream: Stream = read(target, format=fmt)
    except FileNotFoundError:
        # Preserve the precise "missing file" signal for callers to handle.
        raise
    except (TypeError, ValueError, OSError) as exc:
        # ObsPy raises TypeError("Unknown format for file <name>") for
        # undeterminable data and assorted OS/ValueErrors for corrupt input;
        # wrap them with context so callers get a single, actionable error type.
        raise ValueError(f"Could not parse waveform from {target!r}: {exc}") from exc

    if len(stream) == 0:
        raise ValueError(f"{target!r} contained no traces")
    return stream


def load_events(source: str | Path, *, base_dir: Path | None = None) -> Catalog:
    """Read an event file or URL into a ``Catalog`` (same validation as above)."""
    target = _resolve_source(source, base_dir)
    try:
        catalog: Catalog = read_events(target)
    except FileNotFoundError:
        raise
    except (TypeError, ValueError, OSError) as exc:
        raise ValueError(f"Could not parse events from {target!r}: {exc}") from exc
    return catalog


def load_inventory(source: str | Path, *, base_dir: Path | None = None) -> Inventory:
    """Read a station file or URL into an ``Inventory`` (same validation)."""
    target = _resolve_source(source, base_dir)
    try:
        inventory: Inventory = read_inventory(target)
    except FileNotFoundError:
        raise
    except (TypeError, ValueError, OSError) as exc:
        raise ValueError(f"Could not parse inventory from {target!r}: {exc}") from exc
    return inventory
```

### 6. Process Waveforms

Summaries and transforms should be explicitly typed and should never mutate the caller's data by surprise. The `TypedDict` gives downstream JSON/serialization code a precise shape, and `preprocess_trace` validates against the Nyquist frequency — a real constraint, since a band-pass edge at or above Nyquist is physically meaningless and will raise deep inside SciPy with a far less helpful message.

```python
from __future__ import annotations

from typing import TypedDict

from obspy import Stream, Trace


class TraceSummary(TypedDict):
    """A JSON-serialisable description of a single trace."""

    id: str
    starttime: str
    endtime: str
    sampling_rate: float
    npts: int


def describe_traces(stream: Stream) -> list[TraceSummary]:
    """Return one ``TraceSummary`` per trace in *stream*.

    Iterating a ``Stream`` yields its ``Trace`` objects in order.
    """
    if not isinstance(stream, Stream):
        raise TypeError(f"expected Stream, got {type(stream).__name__}")

    summaries: list[TraceSummary] = []
    for trace in stream:
        stats = trace.stats
        summaries.append(
            TraceSummary(
                id=trace.id,  # NET.STA.LOC.CHA, e.g. "BW.RJOB..EHZ"
                starttime=str(stats.starttime),
                endtime=str(stats.endtime),
                sampling_rate=float(stats.sampling_rate),
                npts=int(stats.npts),
            )
        )
    return summaries


def preprocess_trace(
    trace: Trace,
    *,
    freqmin: float,
    freqmax: float,
    taper_fraction: float = 0.05,
) -> Trace:
    """Return a detrended, tapered, band-pass-filtered *copy* of *trace*.

    A copy is returned because ``detrend``/``taper``/``filter`` all modify the
    trace in place; mutating the caller's object would corrupt any other code
    still holding the original samples.

    Raises
    ------
    TypeError
        If *trace* is not a ``Trace`` or the numeric arguments are not floats.
    ValueError
        If the frequency band is not ``0 < freqmin < freqmax < Nyquist`` or the
        taper fraction is outside ``[0, 0.5]``.
    """
    if not isinstance(trace, Trace):
        raise TypeError(f"expected Trace, got {type(trace).__name__}")
    for name, value in (("freqmin", freqmin), ("freqmax", freqmax),
                        ("taper_fraction", taper_fraction)):
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise TypeError(f"{name} must be a real number, got {value!r}")

    nyquist = 0.5 * float(trace.stats.sampling_rate)
    if not 0.0 < freqmin < freqmax < nyquist:
        raise ValueError(
            f"require 0 < freqmin ({freqmin}) < freqmax ({freqmax}) "
            f"< Nyquist ({nyquist})"
        )
    if not 0.0 <= taper_fraction <= 0.5:
        raise ValueError(f"taper_fraction must be in [0, 0.5], got {taper_fraction}")

    work: Trace = trace.copy()
    work.detrend("linear")
    work.taper(max_percentage=taper_fraction, type="hann")
    work.filter(
        "bandpass",
        freqmin=freqmin,
        freqmax=freqmax,
        corners=4,
        zerophase=True,
    )
    return work
```

## Examples

Calling `read()` with no arguments loads ObsPy's bundled three-component example seismogram, so the snippet below needs no files or network access. To read your own data, pass a path/URL to `load_waveform()` from above instead.

```python
from obspy import Stream, Trace, read

stream: Stream = read()
print(stream)
```

The output lists every trace with its SEED id, time span, sampling rate, and sample count:

```text
3 Trace(s) in Stream:
BW.RJOB..EHZ | 2009-08-24T00:20:03.000000Z - 2009-08-24T00:20:32.990000Z | 100.0 Hz, 3000 samples
BW.RJOB..EHN | 2009-08-24T00:20:03.000000Z - 2009-08-24T00:20:32.990000Z | 100.0 Hz, 3000 samples
BW.RJOB..EHE | 2009-08-24T00:20:03.000000Z - 2009-08-24T00:20:32.990000Z | 100.0 Hz, 3000 samples
```

Select a single `Trace` by index and inspect its metadata and samples:

```python
trace: Trace = stream[0]

# Identity and timing are deterministic for this bundled example.
print(trace.id)                   # -> BW.RJOB..EHZ
print(trace.stats.sampling_rate)  # -> 100.0
print(trace.stats.delta)          # -> 0.01
print(trace.stats.npts)           # -> 3000

# Samples live in a NumPy array. Inspect shape/dtype and slice explicitly
# rather than dumping 3000 numbers to the console.
print(trace.data.shape)           # -> (3000,)
print(trace.data.dtype)           # -> float64 (the in-memory example uses floats)
first_five = trace.data[:5]       # the first five samples, shown in full
last_five = trace.data[-5:]       # the last five samples, shown in full
print(first_five)
print(last_five)
```

Printing `trace.stats` shows the core metadata fields. The location code here is the empty string (an unset SEED location):

```text
         network: BW
         station: RJOB
        location:
         channel: EHZ
       starttime: 2009-08-24T00:20:03.000000Z
         endtime: 2009-08-24T00:20:32.990000Z
   sampling_rate: 100.0
           delta: 0.01
            npts: 3000
           calib: 1.0
```

`trace.stats.starttime` is a `UTCDateTime`, not a string, so it supports arithmetic and comparison:

```python
from obspy import UTCDateTime

start: UTCDateTime = trace.stats.starttime
print(repr(start))            # -> UTCDateTime(2009, 8, 24, 0, 20, 3)
print(start + 10)             # ten seconds later -> UTCDateTime(2009, 8, 24, 0, 20, 13)
print(trace.stats.endtime - start)  # span in seconds -> 29.99
```

**Note:** the in-memory default example does **not** set `trace.stats._format` (accessing it raises `KeyError`). When you instead read a real file, ObsPy adds a `_format` key (e.g. `"MSEED"`) plus a nested, format-specific `AttribDict` holding that format's header fields.

## Pitfalls

1. **Never pass unvalidated user input to `read()`, `read_events()`, or `read_inventory()`.** These functions accept URLs and local paths through the same argument. ObsPy fetches `http(s)`/`ftp` URLs server-side whenever `"://"` appears near the start of the string. An attacker can exploit this with `file:///etc/passwd`, `../` path traversal, or SSRF against internal services. Always use the `_resolve_source` helper with an allow-list of URL schemes (`http`, `https` only) and a `base_dir` sandbox for local reads.

2. **Never let `read()` auto-detect formats on untrusted input.** Auto-detection tries every registered reader in turn, producing confusing, slow-to-surface errors on unsupported formats. Always pass an explicit `fmt` from `SUPPORTED_WAVEFORM_FORMATS` so unknown input fails loudly and immediately.

3. **Windows drive letters are not URL schemes.** `C:\data\trace.mseed` has a single-character "scheme" (`C`) and no netloc. The `_looks_like_url` helper correctly rejects this as a URL by requiring `len(parsed.scheme) > 1 and bool(parsed.netloc)`. Without this check, a Windows path would be misclassified as a URL and skip the path-traversal guard.

4. **`Trace` methods mutate in place.** `detrend()`, `taper()`, `filter()`, `resample()`, `integrate()`, and `remove_response()` all modify the trace's `data` array directly. Always call `trace.copy()` first if the caller or any other code still holds a reference to the original.

5. **Do not index `origins[0]` for the authoritative solution.** An `Event` can have multiple competing origins from different agencies. Use `event.preferred_origin()`, `event.preferred_magnitude()`, and `event.preferred_focal_mechanism()` instead.

6. **`Event` depths are in meters, not kilometers.** QuakeML specifies depth in meters. Mixing this up introduces a factor-of-1000 error.

7. **Band-pass filter frequencies must satisfy `0 < freqmin < freqmax < Nyquist`.** A band-pass edge at or above Nyquist is physically meaningless. ObsPy/SciPy will raise, but with a far less helpful message than the explicit check in `preprocess_trace`.

8. **`taper_fraction` must be in `[0, 0.5]`.** Values outside this range are meaningless (you cannot taper more than half the signal on each side).

9. **`base_dir` must exist when using `_resolve_local_path`.** It is resolved with `strict=True`, so a missing sandbox directory fails fast rather than silently allowing every path.

10. **The bundled example does not set `trace.stats._format`.** Accessing it raises `KeyError`. Real files do set `_format` (e.g. `"MSEED"`) plus a nested, format-specific `AttribDict`.

## Verification

Confirm the API behaves as expected before relying on it. All three smoke tests run offline since the no-argument readers load ObsPy's packaged sample data.

**Run the test suite:**

```powershell
python -m pytest test_obspy_data_api.py -v
```

Or run directly:

```powershell
python test_obspy_data_api.py
```

**Expected output:** all three tests pass with `OK`:

```text
test_read_events_returns_catalog ... ok
test_read_inventory_returns_inventory ... ok
test_read_waveform_returns_non_empty_stream ... ok
----------------------------------------------------------------------
Ran 3 tests in 0.XXXs

OK
```

**Verification checklist:**

- [ ] Call `read()` and verify the `Stream` holds 3 traces of 3000 samples each at 100.0 Hz.
- [ ] Call `read_events()` and verify the `Catalog` is non-empty.
- [ ] Call `read_inventory()` and verify the `Inventory` exposes at least one network.
- [ ] Verify `trace.id` returns `BW.RJOB..EHZ` for the first trace.
- [ ] Verify `trace.stats.starttime + 10` returns `UTCDateTime(2009, 8, 24, 0, 20, 13)`.

**Full test file:**

```python
import unittest

from obspy import (
    Catalog,
    Inventory,
    Stream,
    read,
    read_events,
    read_inventory,
)


class TestObsPyDataAPI(unittest.TestCase):
    """Smoke tests over ObsPy's bundled example data (no network required)."""

    def test_read_waveform_returns_non_empty_stream(self) -> None:
        stream: Stream = read()
        self.assertIsInstance(stream, Stream)
        self.assertEqual(len(stream), 3)
        self.assertEqual(stream[0].stats.npts, 3000)
        self.assertAlmostEqual(float(stream[0].stats.sampling_rate), 100.0)

    def test_read_events_returns_catalog(self) -> None:
        catalog: Catalog = read_events()
        self.assertIsInstance(catalog, Catalog)
        self.assertGreater(len(catalog), 0)

    def test_read_inventory_returns_inventory(self) -> None:
        inventory: Inventory = read_inventory()
        self.assertIsInstance(inventory, Inventory)
        self.assertGreater(len(inventory.networks), 0)


if __name__ == "__main__":
    unittest.main()
```

## Classes & Functions

| Class/Function | Description |
|----------------|-------------|
| `read` | Read waveform files (or URLs) into an ObsPy `Stream` object. |
| `Stream` | List-like container of multiple ObsPy `Trace` objects. |
| `Trace` | A continuous time series (`data`) plus its metadata (`stats`). |
| `Stats` | Dict-like header container for a `Trace` (`obspy.core.trace.Stats`). |
| `UTCDateTime` | A UTC-based datetime supporting arithmetic and comparison. |
| `read_events` | Read event files (or URLs) into an ObsPy `Catalog` object. |
| `Catalog` | Container for `Event` objects. |
| `Event` | A seismic event (not necessarily a tectonic earthquake). |
| `read_inventory` | Read station metadata files (or URLs) into an `Inventory`. |
| `Inventory` | Root of the `Network` → `Station` → `Channel` hierarchy. |

## Modules

| Module | Description |
|--------|-------------|
| `obspy.core.trace` | Handles `Trace` and `Stats` objects. |
| `obspy.core.stream` | Handles `Stream` objects. |
| `obspy.core.utcdatetime` | Provides the UTC-based `UTCDateTime` class. |
| `obspy.core.event` | Handles event metadata (`Catalog`, `Event`, and friends). |
| `obspy.core.inventory` | Handles station metadata (`Inventory` and friends). |
| `obspy.core.util` | Various ObsPy utilities, including the format readers. |
| `obspy.core.preview` | Tools for creating and merging waveform previews. |

## Related skills

The ObsPy data API is the on-ramp to the rest of the seismology toolchain. Once data is in `Stream`/`Trace` form, it feeds ObsPy's own signal-processing routines (filtering, instrument-response removal, resampling) and machine-learning frameworks such as SeisBench, whose modeling API consumes `Stream` objects directly. The `Inventory` produced by `read_inventory()` supplies the instrument responses those processing steps require.
