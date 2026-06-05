---
name: matlab-import-tracking-data
description: "Import raw ground truth data (CSV, XLSX, TXT, or MATLAB tables) into formats used by Sensor Fusion and Tracking Toolbox: trackingScenarioRecording, tuning data timetable, truthlog struct array, or a clean converted table. Use when the user has recorded position/trajectory data and wants to: replay a tracking scenario from real data, tune tracking filters (EKF, UKF, IMM) with recorded truth, or assess tracker accuracy (GOSPA, OSPA, assignment metrics) against ground truth. Also use when the user mentions trackingDataImporter, importing flight logs, GPS logs, ADS-B data, AIS ship tracks, radar recordings, driving logs, or converting raw position data for use with trackers."
license: MathWorks BSD-3-Clause
metadata:
  author: MathWorks
  version: "1.0"
---

# Tracking Data Import

Import raw ground truth data into MATLAB for use with Sensor Fusion and Tracking Toolbox. This skill drives an agent workflow that writes plain MATLAB code — no App or internal APIs needed.

## When to Use

- User has recorded trajectory/position data (CSV, XLSX, TXT, or MATLAB table) and wants to bring it into MATLAB for tracking workflows
- User wants to replay a real-world scenario with `trackingScenarioRecording`
- User wants to tune tracking filters (EKF, UKF, IMM) using `trackingFilterTuner` and needs truth data in the right format
- User wants to evaluate tracker accuracy (GOSPA, OSPA, assignment metrics) and needs a truth log
- User mentions flight logs, GPS logs, ADS-B data, AIS ship tracks, radar recordings, or driving logs in the context of tracking
- User asks about `trackingDataImporter` or importing ground truth for trackers

## When NOT to Use

- User is generating synthetic scenarios from scratch (use `trackingScenario` directly)
- User already has data in the correct SFTT format and just needs to run a tracker
- User needs to import sensor detections (not truth/ground-truth data)
- User is working with image/video data rather than position/trajectory data

## Output Formats

| Output | Type | Use With |
|---|---|---|
| **Scenario Recording** | `trackingScenarioRecording` | `play`, scenario replay |
| **Tuning Data** | timetable / cell of timetables | `trackingFilterTuner` |
| **Truth Log** | cell array of struct arrays | `trackGOSPAMetric`, `trackAssignmentMetrics` |
| **Converted Table** | `table` | General inspection |

## Agent Workflow

### Step 1: Ask the User (2 questions only)

1. **What output do you need?** (recording / tuning data / truth log / converted table)
2. **Where is the data?** (file path or workspace variable name)

### Step 2: Inspect the Data

Read the data and display column names + sample rows. From this, **infer** the data model — do not ask the user yet:

- **Geo vs Cartesian**: lat/lon columns → geodetic; x/y/z → Cartesian
- **Category**: Flight log, GPS log, driving log, or custom (see `references/interpreter-categories.md`)
- **Time column & format**: name pattern + value magnitude (large → epoch, small → elapsed)
- **Platform/Class ID columns**: name patterns like "id", "pid", "object_id"
- **Position, velocity, orientation, dimension columns**: match by name
- **Units**: default to degrees/meters/m-per-s; adjust if names hint otherwise ("alt_ft", "speed_kts")

### Step 3: Propose Mapping — Let User Confirm/Edit

Present a table of inferred mappings:

> | State Element | Column | Unit |
> |---|---|---|
> | Time (DateTime) | `"timestamp"` | sec (posix epoch) |
> | Platform ID | `"aircraft_id"` | — |
> | Latitude | `"lat"` | degree |
> | ... | ... | ... |
>
> **Unmapped columns** (ignored): `"signal_strength"`, `"battery"`
>
> Does this look right? Edit anything that's wrong.

Iterate until the user confirms.

### Step 4: Ask About Output Frame (geo data only)

Requires Mapping Toolbox or Aerospace Toolbox for coordinate transforms (`wgs84Ellipsoid`, `geodetic2ecef`, `ned2ecefv`). If geodetic data is detected and neither toolbox is available, suggest that the user install one of these toolboxes.

Only for geodetic/earth-referenced data. Options:
- Cartesian ECEF
- Cartesian Fixed NED / ENU (requires origin lat/lon/alt)
- Geodetic Local NED / ENU

Default: same as input. Skip for Cartesian Scenario or Driving data.

### Step 5: Generate and Run Code

Write MATLAB code following the patterns in `references/code-patterns.md`. Key steps:
1. Read data → extract columns → convert units → parse time
2. Remap platform IDs to sequential integers (1, 2, 3, ...)
3. Transform coordinates if needed (see `references/coordinate-transforms.md`)
4. Build the output structure (see `references/output-formats.md`)
5. Sort by time before building output

### Step 6: Visualize

After conversion, offer to visualize. See `references/visualization.md`.
- **Geo data** → `trackingGlobeViewer` (globe with trajectories)
- **Non-geo data** → `theaterPlot` (3D axes with trajectories)

Offer interactive follow-ups: highlight a platform, show a time step, zoom in.

---

## Reference Documents

Read these on-demand when you need the details:

- `references/output-formats.md` — Exact struct/table schemas for all four output types
- `references/code-patterns.md` — Complete end-to-end code examples (flight log, driving log, GPS log)
- `references/coordinate-transforms.md` — When and how to transform between frames
- `references/visualization.md` — trackingGlobeViewer and theaterPlot usage
- `references/interpreter-categories.md` — Data model categories, state elements, and units
- `references/time-and-units.md` — Time parsing and unit conversion reference

----

Copyright 2026 The MathWorks, Inc.
