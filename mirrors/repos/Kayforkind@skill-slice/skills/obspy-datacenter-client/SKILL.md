---
name: obspy-datacenter-client
version: 1.1.1
description: "Retrieves MiniSEED waveforms, StationXML inventories, and QuakeML catalogs from FDSN web services via `obspy.clients.fdsn`, plus RoutingClient, mass downloader, SeedLink, or Syngine when FDSN is not enough. Use for EarthScope/IRIS, ORFEUS, or GFZ pulls while the archive still holds the data. Not a local MiniSEED/SAC/QuakeML file parser (obspy-data-api)."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

## When to Use

Use this skill when you need to **download earthquake research data** from seismological data centers. Trigger keywords and scenarios include:

- Downloading **waveforms** (MiniSEED) for a known station and time window
- Querying **event catalogs** (QuakeML) by magnitude, time, or region
- Retrieving **station metadata** (StationXML) including instrument response
- Fetching waveforms by **geographic region** when you do not know which data center holds the data
- **Bulk downloading** large campaigns spanning many stations or events
- Streaming **real-time waveform feeds** via SeedLink
- Downloading **synthetic seismograms** from IRIS Syngine

In almost all cases, reach for `obspy.clients.fdsn` — it is the default for a reason:

- **One interface, many archives.** FDSN web services are a published standard (`https://www.fdsn.org/webservices/`) that essentially every modern seismological data center implements. A single code path works against IRIS, ORFEUS, GFZ, INGV, RESIF, GEONET, and dozens of others.
- **Modern, portable formats.** FDSN returns canonical formats — MiniSEED for waveforms, StationXML for station metadata, QuakeML for events — so downstream processing stays portable.
- **Industry standard.** Tooling, tutorials, and colleagues all assume FDSN, keeping scripts readable and reviewable.

Use a data-center-specific client only when that center exposes something FDSN genuinely does not (real-time SeedLink feeds, synthetic seismograms, legacy SAC/RESP instrument response).

**Load the detailed reference** [obspy-clients-fdsn.md](obspy-clients-fdsn.md) when you need the full FDSN client API reference, including the complete list of provider shortcut names and routing client configuration details.

## Prerequisites

- Python 3.9+ with a virtual environment (`pip install obspy`)
- Network connectivity to the target data center (FDSN endpoints resolve and reachable)
- For restricted/embargoed datasets: credentials stored in environment variables or a credentials file **outside** the repository — never hardcoded
- For large jobs: register with the provider in advance where required

## Procedure

### 1. Choose the right client module

| Need | Module | When to choose over FDSN |
|------|--------|---------------------------|
| Waveforms, stations, or events (archived) | `obspy.clients.fdsn` | Default — always try this first |
| Waveforms by region, data center unknown | `obspy.clients.fdsn.RoutingClient` | When you do not know which center holds the data |
| Bulk download (many stations/events) | `obspy.clients.fdsn` + mass downloader | Campaign-scale acquisition with pacing and QC |
| Legacy instrument response (SAC PZ, RESP) | `obspy.clients.iris` | Only for formats FDSN StationXML does not cover |
| Real-time streaming feed | `obspy.clients.seedlink` | Live monitoring/alerting, not archived windows |
| Synthetic seismograms | `obspy.clients.syngine` | Modeled waveforms for source–receiver comparison |
| Earthworm Wave Server (local observatory) | `obspy.clients.earthworm` | Direct Earthworm protocol, not FDSN-standard |
| NEIC Continuous Waveform Buffer | `obspy.clients.neic` | Data from the NEIC "Edge" buffer specifically |

### 2. Install ObsPy in a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install obspy
```

### 3. Construct an FDSN client

```python
from obspy.clients.fdsn import Client

# Shortcut name — ObsPy maps to the base URL automatically
client = Client("IRIS")

# Or pass a full base URL for a provider without a shortcut
# client = Client("https://service.example.edu/fdsnws")
```

### 4. Download waveforms for a known station

```python
from obspy import UTCDateTime
from obspy.clients.fdsn import Client

client = Client("IRIS")
stream = client.get_waveforms(
    network="IU",
    station="ANMO",
    location="00",
    channel="LHZ",
    starttime=UTCDateTime("2010-02-27T06:45:00"),
    endtime=UTCDateTime("2010-02-27T07:45:00"),
)
stream.write("IU.ANMO.00.LHZ.mseed", format="MSEED")
```

### 5. Query an event catalog

```python
from obspy import UTCDateTime
from obspy.clients.fdsn import Client

client = Client("IRIS")
catalog = client.get_events(
    starttime=UTCDateTime("2002-01-01"),
    endtime=UTCDateTime("2002-01-02"),
    minmagnitude=6.0,
)
print(f"Retrieved {len(catalog)} event(s).")
```

### 6. Query station metadata

```python
from obspy import UTCDateTime
from obspy.clients.fdsn import Client

client = Client("IRIS")
inventory = client.get_stations(
    network="IU",
    station="A*",
    starttime=UTCDateTime("2002-01-01"),
    endtime=UTCDateTime("2002-01-02"),
    level="channel",  # one of: network, station, channel, response
)
inventory.write("IU_stations.xml", format="STATIONXML")
```

### 7. Fetch waveforms by region using a routing client

```python
from obspy import UTCDateTime
from obspy.clients.fdsn import RoutingClient

# iris-federator or eida-routing
client = RoutingClient("iris-federator")
stream = client.get_waveforms(
    channel="LHZ",
    starttime=UTCDateTime(2017, 1, 1, 0, 0, 0),
    endtime=UTCDateTime(2017, 1, 1, 0, 5, 0),
    latitude=10.0,
    longitude=10.0,
    maxradius=25.0,
)
```

### 8. Bulk download with the mass downloader

For campaigns spanning many stations or events, use the mass downloader. It handles pagination, retries, de-duplication, gap handling, request pacing, and downloads both waveforms and corresponding StationXML. Load [obspy-clients-fdsn.md](obspy-clients-fdsn.md) for the full mass downloader API and restrictions syntax.

```python
from obspy.clients.fdsn.mass_downloader import CircularDomain, Restrictions, MassDownloader

domain = CircularDomain(
    latitude=10.0,
    longitude=10.0,
    minradius=0.0,
    maxradius=25.0,
)
restrictions = Restrictions(
    starttime=UTCDateTime("2024-01-01T00:00:00"),
    endtime=UTCDateTime("2024-01-01T01:00:00"),
    channel="LHZ",
    location="",
)
mdl = MassDownloader()
mdl.download(domain, restrictions, mseed_storage="waveforms", stationxml_storage="stations")
```

## Do Not Use

- **Avoid `obspy.clients.neries`.** The NERIES web service was decommissioned years ago; the client survives only as a historical stub. Any call will fail with a connection error or HTTP 404. Use `obspy.clients.fdsn` with providers like EMSC, ORFEUS, or INGV instead.
- **Avoid IRIS calculation web services for local math.** `traveltime`, `distaz`, and `flinnengdahl` each require a network round trip per call, adding latency, a hard dependency on IRIS being reachable, and rate-limit exposure when looping over thousands of station pairs. Use `obspy.taup` and `obspy.geodetics` (offline, deterministic, CI-safe) instead. Reserve the web services only for the rare case where you need IRIS's exact reference tables.
- **Never hardcode API keys or credentials.** Restricted datasets and some routing services require HTTP Basic Auth or an EIDA authentication token. Hardcoding them means they get committed to version control, copied into shared notebooks, and printed in tracebacks and logs. Read credentials from environment variables or a credentials file outside the repository.
- **Respect each provider's Terms of Service and rate limits.** These are shared, often publicly funded services. Aggressive parallel requests can get your IP throttled or blocked, breaking not only your job but everyone behind the same network address. For large jobs use `get_waveforms_bulk()` or the mass downloader (both batch and pace requests), and register in advance where a provider requires it.

## Examples

### Example 1 — Download and save waveforms with defensive validation

```python
from __future__ import annotations

from pathlib import Path

from obspy import Stream, UTCDateTime
from obspy.clients.fdsn import Client
from obspy.clients.fdsn.header import FDSNException, FDSNNoDataException


def fetch_waveforms(
    data_center: str,
    network: str,
    station: str,
    location: str,
    channel: str,
    starttime: UTCDateTime,
    endtime: UTCDateTime,
) -> Stream:
    """Return a Stream for one SEED id and time window from an FDSN center."""
    for label, value in (
        ("data_center", data_center),
        ("network", network),
        ("station", station),
        ("channel", channel),
    ):
        if not value or not value.strip():
            raise ValueError(f"{label} must be a non-empty SEED code")

    if endtime <= starttime:
        raise ValueError(
            f"endtime ({endtime}) must be strictly after starttime ({starttime})"
        )

    client = Client(data_center)
    return client.get_waveforms(
        network, station, location, channel, starttime, endtime
    )


def save_waveforms(stream: Stream, output_path: Path) -> None:
    """Write a non-empty Stream to disk as MiniSEED."""
    if len(stream) == 0:
        raise ValueError("refusing to write an empty Stream")
    stream.write(str(output_path), format="MSEED")


if __name__ == "__main__":
    start_time: UTCDateTime = UTCDateTime("2010-02-27T06:45:00")
    end_time: UTCDateTime = start_time + 60 * 60  # one hour

    try:
        waveforms: Stream = fetch_waveforms(
            data_center="IRIS",
            network="IU",
            station="ANMO",
            location="00",
            channel="LHZ",
            starttime=start_time,
            endtime=end_time,
        )
    except FDSNNoDataException:
        print("No data available for IU.ANMO.00.LHZ in this window.")
    except FDSNException as exc:
        print(f"FDSN request failed: {exc}")
    else:
        save_waveforms(waveforms, Path("IU.ANMO.00.LHZ.mseed"))
        print(f"Saved {len(waveforms)} trace(s).")
```

### Example 2 — Query an event catalog with magnitude validation

```python
from __future__ import annotations

from obspy import Catalog, UTCDateTime
from obspy.clients.fdsn import Client
from obspy.clients.fdsn.header import FDSNException, FDSNNoDataException


def fetch_events(
    data_center: str,
    starttime: UTCDateTime,
    endtime: UTCDateTime,
    minmagnitude: float,
) -> Catalog:
    """Return a Catalog of events at or above a magnitude threshold."""
    if endtime <= starttime:
        raise ValueError(
            f"endtime ({endtime}) must be strictly after starttime ({starttime})"
        )
    if not -1.0 <= minmagnitude <= 10.0:
        raise ValueError(
            f"minmagnitude ({minmagnitude}) is outside the plausible range [-1, 10]"
        )

    client = Client(data_center)
    return client.get_events(
        starttime=starttime,
        endtime=endtime,
        minmagnitude=minmagnitude,
    )


if __name__ == "__main__":
    try:
        catalog: Catalog = fetch_events(
            data_center="IRIS",
            starttime=UTCDateTime("2002-01-01"),
            endtime=UTCDateTime("2002-01-02"),
            minmagnitude=6.0,
        )
    except FDSNNoDataException:
        print("No events matched the query.")
    except FDSNException as exc:
        print(f"Event query failed: {exc}")
    else:
        print(f"Retrieved {len(catalog)} event(s).")
        for event in catalog:
            origin = event.preferred_origin() or (
                event.origins[0] if event.origins else None
            )
            magnitude = event.preferred_magnitude() or (
                event.magnitudes[0] if event.magnitudes else None
            )
            if origin is None or magnitude is None:
                continue
            print(
                f"  {origin.time}  M{magnitude.mag:.1f}  "
                f"({origin.latitude}, {origin.longitude})"
            )
```

### Example 3 — Query station metadata with level validation

```python
from __future__ import annotations

from obspy import Inventory, UTCDateTime
from obspy.clients.fdsn import Client
from obspy.clients.fdsn.header import FDSNException, FDSNNoDataException

VALID_LEVELS: frozenset[str] = frozenset({"network", "station", "channel", "response"})


def fetch_stations(
    data_center: str,
    network: str,
    station: str,
    starttime: UTCDateTime,
    endtime: UTCDateTime,
    level: str = "station",
) -> Inventory:
    """Return an Inventory describing matching stations."""
    if level not in VALID_LEVELS:
        raise ValueError(
            f"level must be one of {sorted(VALID_LEVELS)}, got {level!r}"
        )
    if endtime <= starttime:
        raise ValueError(
            f"endtime ({endtime}) must be strictly after starttime ({starttime})"
        )

    client = Client(data_center)
    return client.get_stations(
        network=network,
        station=station,
        starttime=starttime,
        endtime=endtime,
        level=level,
    )


if __name__ == "__main__":
    try:
        inventory: Inventory = fetch_stations(
            data_center="IRIS",
            network="IU",
            station="A*",
            starttime=UTCDateTime("2002-01-01"),
            endtime=UTCDateTime("2002-01-02"),
            level="channel",
        )
    except FDSNNoDataException:
        print("No stations matched the query.")
    except FDSNException as exc:
        print(f"Station query failed: {exc}")
    else:
        station_count = sum(len(net.stations) for net in inventory.networks)
        print(
            f"Retrieved {station_count} station(s) "
            f"across {len(inventory.networks)} network(s)."
        )
        inventory.write("IU_stations.xml", format="STATIONXML")
```

### Example 4 — Fetch waveforms by region with coordinate validation

```python
from __future__ import annotations

from obspy import Stream, UTCDateTime
from obspy.clients.fdsn import RoutingClient
from obspy.clients.fdsn.header import FDSNException, FDSNNoDataException


def fetch_waveforms_by_region(
    channel: str,
    starttime: UTCDateTime,
    endtime: UTCDateTime,
    latitude: float,
    longitude: float,
    maxradius_degrees: float,
    router: str = "iris-federator",
) -> Stream:
    """Return waveforms near a point without naming a data center."""
    if not -90.0 <= latitude <= 90.0:
        raise ValueError(f"latitude ({latitude}) must be within [-90, 90]")
    if not -180.0 <= longitude <= 180.0:
        raise ValueError(f"longitude ({longitude}) must be within [-180, 180]")
    if not 0.0 < maxradius_degrees <= 180.0:
        raise ValueError(
            f"maxradius_degrees ({maxradius_degrees}) must be within (0, 180]"
        )
    if endtime <= starttime:
        raise ValueError(
            f"endtime ({endtime}) must be strictly after starttime ({starttime})"
        )

    client = RoutingClient(router)
    return client.get_waveforms(
        channel=channel,
        starttime=starttime,
        endtime=endtime,
        latitude=latitude,
        longitude=longitude,
        maxradius=maxradius_degrees,
    )


if __name__ == "__main__":
    try:
        stream: Stream = fetch_waveforms_by_region(
            channel="LHZ",
            starttime=UTCDateTime(2017, 1, 1, 0, 0, 0),
            endtime=UTCDateTime(2017, 1, 1, 0, 5, 0),
            latitude=10.0,
            longitude=10.0,
            maxradius_degrees=25.0,
        )
    except FDSNNoDataException:
        print("No data center reported data for this region and window.")
    except FDSNException as exc:
        print(f"Routed waveform request failed: {exc}")
    else:
        networks = {trace.stats.network for trace in stream}
        print(f"Retrieved {len(stream)} trace(s) from {len(networks)} network(s).")
```

## Pitfalls

- **"No data" is a coverage gap, not a bug.** Not all providers offer all three data types (waveforms, stations, events). A request that works against IRIS may return "no data" against a provider that simply does not host that data type. Check the provider's catalog coverage before assuming your code is wrong.
- **Empty Stream is a silent trap.** A zero-trace MiniSEED file lets later processing steps "succeed" on no data. Always check `len(stream) == 0` before writing to disk.
- **`level` parameter typos.** The FDSN station service accepts only `network`, `station`, `channel`, `response`. A typo like `channels` produces a generic HTTP 400 that is hard to trace. Validate locally first.
- **`preferred_origin()` / `preferred_magnitude()` can return `None`.** Always fall back to `event.origins[0]` / `event.magnitudes[0]` and skip the event if neither is populated.
- **Backwards time windows.** `endtime <= starttime` silently returns empty results or an opaque error. Validate `endtime > starttime` before any network call.
- **Out-of-range geographic queries return nothing silently.** Latitude outside `[-90, 90]`, longitude outside `[-180, 180]`, or radius outside `(0, 180]` tend to return empty results instead of raising. Range-check locally.
- **Rate limiting and IP blocking.** Aggressive parallel requests against shared services can get your IP throttled or blocked, affecting everyone behind the same network address. Use `get_waveforms_bulk()` or the mass downloader for large jobs — they batch and pace requests.
- **Credentials in version control.** Never hardcode API keys, Basic Auth, or EIDA tokens. They end up in git history, shared notebooks, and tracebacks. Read from environment variables or a credentials file outside the repository.
- **NERIES client is dead.** `obspy.clients.neries` will always fail — the service was decommissioned. Use FDSN providers (EMSC, ORFEUS, INGV) instead.
- **IRIS calc web services add unnecessary network dependency.** `traveltime`, `distaz`, `flinnengdahl` require a round trip per call. Use `obspy.taup` and `obspy.geodetics` for offline, deterministic, CI-safe computation.

## Verification

Run through this checklist to confirm the client works end to end. Each item maps to a distinct failure mode:

- [ ] Install `obspy` in a virtual environment (`pip install obspy`) — isolates dependencies and avoids version clashes with the system Python.
- [ ] Confirm network connectivity to the chosen data center — rules out firewall/DNS issues before blaming the code.
- [ ] Run a small test request — proves the client can reach the service and authenticate where relevant.
- [ ] Check that the returned object is an ObsPy `Stream` (or `Inventory`/`Catalog`) — confirms parsing succeeded, not just the HTTP call.
- [ ] Confirm the data is written in the expected format (`.mseed` for waveforms) — confirms the full round trip to disk.

The script below performs all checks and returns exit code 0 on success, 1 on any handled failure — usable as a CI gate. It separates "no data" from "request failed" from "empty stream" because each points at a different fix: pick another station, check connectivity/credentials, or widen the time window.

```python
from __future__ import annotations

import sys
from pathlib import Path

from obspy import Stream, UTCDateTime
from obspy.clients.fdsn import Client
from obspy.clients.fdsn.header import FDSNException, FDSNNoDataException


def verify_fdsn_client(
    data_center: str = "IRIS",
    network: str = "IU",
    station: str = "ANMO",
    location: str = "00",
    channel: str = "BH*",
    output_path: Path = Path("verification_data.mseed"),
) -> int:
    """Download a short waveform window and confirm it round-trips to disk.

    IU.ANMO (Albuquerque, New Mexico) is a long-running Global Seismograph
    Network site, making it a reliable smoke-test target.
    """
    start_time: UTCDateTime = UTCDateTime("2024-01-01T00:00:00")
    end_time: UTCDateTime = UTCDateTime("2024-01-01T00:10:00")
    if end_time <= start_time:
        print("Verification failed: invalid time window (end <= start).")
        return 1

    try:
        client = Client(data_center)
        stream: Stream = client.get_waveforms(
            network, station, location, channel, start_time, end_time
        )
    except FDSNNoDataException:
        print(
            "Verification failed: the data center returned no data. "
            "Try a different station or time window."
        )
        return 1
    except FDSNException as exc:
        print(
            "Verification failed: the FDSN request errored "
            f"(check connectivity and credentials): {exc}"
        )
        return 1

    if len(stream) == 0:
        print("Verification failed: an empty Stream was returned.")
        return 1

    stream.write(str(output_path), format="MSEED")
    print(
        f"Verification successful: downloaded {len(stream)} trace(s) "
        f"and saved them to {output_path.resolve()}."
    )
    return 0


if __name__ == "__main__":
    sys.exit(verify_fdsn_client())
```

## Related Skills

This skill produces the three core ObsPy containers — `Stream` (waveforms), `Inventory` (station metadata), and `Catalog` (events) — so it pairs naturally with skills that consume them:

- **Waveform-processing skills** (filtering, instrument-response removal, resampling) operate on the `Stream`
- **Travel-time skills** built on `obspy.taup` take coordinates from `Inventory` and `Catalog`
- **Geodetic skills** built on `obspy.geodetics` take coordinates from `Inventory` and `Catalog`

Think of this skill as the data-acquisition front door and those skills as the processing steps that follow.
