---
name: matlab-extract-battery-features
description: >
  Extract battery features in MATLAB from voltage, current, and temperature
  measurements: multi-cycle cycling tests, HPPC / pulse tests, EIS impedance
  sweeps, or a single in-field charge or discharge segment. Use when the user
  asks for battery features, or for SOH, RUL, degradation, internal-resistance,
  or impedance analysis that needs them. Output is a feature table; does not
  train SOH / RUL models. Do not trigger only because battery data is present.
  Triggers on battery* functions such as batteryTestDataParser,
  batteryTestFeatureExtractor, batteryPulseFeatures, batteryEISFeatures.
license: https://www.mathworks.com/content/dam/mathworks/license/pmrl/license.md
metadata:
  author: MathWorks
  version: "2.0"
---

# Battery Feature Extraction

Router for MATLAB's Predictive Maintenance Toolbox battery feature extraction functions. Detailed workflows live in `references/*.md` — load only the file that matches the inspected data type.

## When to Use

Trigger on the domain questions asked about battery voltage / current / temperature measurements — from bench cycler / HPPC / EIS tests **or** from in-field / in-use operational data logged by a BMS or captured during a drive or charge event. The skill produces the feature table that feeds each question's downstream analysis. Concretely:

- **Degradation, SOH, RUL, capacity/energy fade.** *"How much has this cell degraded over 1000 cycles?" · "Track SOH." · "Estimate remaining useful life." · "Which cell is fading fastest?"*
- **Aging mechanism from differential curves.** *"How are the dQ/dV peaks shifting?" · "Loss of lithium inventory vs. active-material loss?" · "Plot IC curves at cycles 1, 250, 500, 1000." · "What's the DV signature of aging?"*
- **Internal resistance from HPPC / pulse tests.** *"What's R0 at 50% SOC?" · "How has DCR grown?" · "Get polarization resistance and recovery rate per pulse."*
- **EIS / impedance analysis.** *"Fit the Nyquist plot." · "What's the charge-transfer resistance?" · "How has R0 grown from EIS?" · "Extract arc widths and Warburg tail."*
- **Segmentation of cycling data.** *"Split this into charge / discharge / rest." · "Separate CC and CV portions of each cycle." · "Give me only the discharge segments."* (With or without downstream feature extraction.)
- **In-field / operational condition monitoring.** Features from a single measured segment that has no multi-cycle test structure — a partial charge or discharge logged by a BMS, one CC segment, or a drive/charge event. *"Extract features from this field charge segment." · "Summarize this discharge from the vehicle log." · "What condition-monitoring features can I get from this partial charge?"* (Served by `batteryMeasurementFeatures`, which works stats-only when no cycle/time structure is present.)
- **Fast-charging stress / plating indicators.** *"Is CV duration growing?" · "Any thermal signature of plating (DT)?" · "Recovery slowdown at high SOC?"*
- **Cell screening / cell-to-cell comparison.** *"Compare these 10 cells." · "Rank by fade rate." · "Which cells are outliers?"*
- **Feature engineering for ML.** *"Give me a feature table for SOH modeling." · "Which features best correlate with capacity fade?"*
- **Batch processing** of multiple test files through any of the above.

## When NOT to Use

- **First-look / data classification / orientation** questions on battery data: *"What kind of test is this?" · "Describe this data." · "Tell me about this file." · "Analyze cycling.csv and tell me what it contains."* These are inspection; the skill fires later when the user asks one of the analyses above.
- **Role-framing without a specific analysis in the current turn.** A system prompt setting a "battery reliability agent" persona, a filename containing "battery" / "cycling" / "SOH", or a bare *"analyze this"* verb is not enough — the current user turn must name one of the specific analyses.
- **Data import** or **vendor-format conversion** (Arbin `.res`, Neware `.nda`, Maccor, BioLogic → MATLAB table).
- **Plotting** raw voltage / current / temperature vs time or capacity **without** first segmenting or computing an IC/DV/DT curve — that's a plain plotting task.
- **Cleaning, resampling, interpolating,** or filtering time-series that does not feed into segmentation, differential curves, or feature extraction.
- **SOH / RUL model training or prediction** — or any ML training — on an already-extracted feature table. This skill is the upstream feature step; modeling and prediction are downstream.
- Battery **simulation**, **equivalent-circuit modeling**, or **Simulink** battery plant models.
- Non-electrochemical data (fuel cells, supercapacitors, generic sensor streams).

This skill covers the 7 PMT battery feature extraction functions. These functions work natively with MATLAB tables and vectors, handle segmentation and peak detection internally, and are performance-optimized. Prefer these PMT functions over manual feature computation (e.g., hand-coded `cumtrapz` loops, manual peak finding). Override only if the user explicitly requests otherwise.

---

## API Overview

The Predictive Maintenance Toolbox provides **7 public functions** for battery feature extraction, organized by the kind of measurement they consume:

```
                                Battery Data
                                     │
      ┌────────────────┬─────────────┴────────┬────────────────────┐
      │                │                      │                    │
 Multi-cycle     Single measured          Pulse tests          EIS tests
 cycling test    segment                  (HPPC / GITT)        (impedance)
      │          (bench or in-field)           │                    │
      ▼                │                        ▼                    ▼
 batteryTest-          │                  batteryPulseFeatures  batteryEISFeatures
 DataParser            │                        │                    │
     +                 │                        ▼                    ▼
 batteryTest-          │                  Pulse feature         EIS feature
 FeatureExtractor      │                  table                 table
      │                │
      ▼                ├── batteryMeasurementFeatures        → Measurement feature table
 Full-pipeline         │
 feature table         ├── batteryDifferentialCurves         → IC / DV / DT curves
                       │
                       └── batteryDifferentialCurveFeatures  → Curve peak feature table
```

The **single measured segment** branch is the in-field / operational path: its functions take raw V / I / T / t from one charge or discharge segment and need no multi-cycle test structure, so they serve BMS-logged or drive/charge-event data as well as a segment pulled from a bench test.

| Function | Input | Output | Use When | Available From |
|----------|-------|--------|----------|----------------|
| `batteryTestDataParser` | Raw cycling table | Parser object (segmented data) | Multi-cycle data needing segmentation | R2024b |
| `batteryTestFeatureExtractor` | Options | Extractor object | Full pipeline: parser → all cycling features | R2024b |
| `batteryMeasurementFeatures` | V, I, T, t vectors | Statistical + cumulative feature table | Any single-phase segment (partial or full charge/discharge) | R2026a |
| `batteryDifferentialCurves` | V, I, T, t vectors | dQ/dV, dV/dQ, dT/dV tables | Constant-current segment only (CC charge or CC discharge) | R2026a |
| `batteryDifferentialCurveFeatures` | Curve + x-axis | Peak feature table | Extracting features from differential curves | R2026a |
| `batteryPulseFeatures` | V, I, t (or table) | Pulse feature table + pulse data | HPPC/pulse test resistance features | R2026b |
| `batteryEISFeatures` | Zr, Zi, F vectors | EIS feature table | Impedance spectroscopy analysis | R2026b |

---

## Load the Right Reference Before Proceeding

**Step 1 — inspect the data shape.** Load the file directly from the exact path the user gave, resolved against the current working folder. Do not recursively search temp, home, or system directories to locate it — a recursive `dir(..., '**', ...)` over such a tree can stall for over a minute. Then read the file and answer two questions:

1. **Granularity.** Is each row a **per-sample raw record** (many rows per cycle: voltage / current sampled at 1 Hz or faster), or is each row a **per-cycle / per-cell summary** (one row per cycle per cell, with columns like `Capacity`, `SOH`, `CV_hold_duration`)?
2. **Multi-cell.** Is there a `CellID` / `Cell` / `SerialNumber` column identifying multiple cells in the same file?

**Step 2 — route by shape:**

| Data shape inspected | Route |
|----------------------|-------|
| Raw per-sample **multi-cycle** cycling table with cycle **and** step index columns (one cell, or multi-cell — see note below) | `references/cycling-pipeline.md` |
| Raw per-sample cycling table with **step index but no cycle index** — either multiple cycles the parser can synthesize a cycle index for, or a single full charge-discharge cycle (see reference for the multi- vs single-cycle rule) | `references/cycling-pipeline.md` |
| Raw per-sample **single-phase** cycling segment (partial charge, one discharge, CC segment) with no cycle index and no full charge-discharge boundary | `references/individual-cycling-functions.md` |
| Raw **short current pulses** separated by rest periods (HPPC / GITT) | `references/pulse-features.md` |
| Raw **impedance sweep** with `Frequency`, `Zreal`, `Zimag` | `references/eis-features.md` |
| **Already-aggregated per-cell / per-cycle summary** — one row per (cell, cycle) with pre-computed `Capacity`, `SOH`, `CV_hold_duration`, `RPT_capacity`, temperature summaries, etc. (no per-sample V/I/t traces) | **No reference loads.** See § Data Is Already Aggregated below. |
| Additionally, when tuning `Tolerance`, `WindowSize`, IC/DV/DT smoothing, or diagnosing "not CC data" errors | Also load `references/parameter-tuning.md` |

**Multi-battery-cell data.** When the data covers more than one battery cell, see the loaded reference's § Preprocessing: Data Layout for detection and combine/iterate rules, and § Postprocessing: Feature Table Organization for the `featuresPerCell{k}` output convention.

### Data Is Already Aggregated — Skill Does Not Apply

If each row is already a per-cycle or per-cell summary (e.g., a CSV with columns `CellID, Cycle, Capacity_Ah, SOH, CV_hold_s, Temp_max_C`), the PMT `battery*` functions covered by this skill have **nothing to add** — they compute those very features from raw traces, and you already have them. Tell the user this, then handle the cell-ranking / degradation-comparison task with plain table operations:

- **Rank cells** by fade rate: fit a slope of `Capacity` vs `Cycle` per `CellID`, sort ascending.
- **Compare mechanisms** by trending `CV_hold_s`, temperature statistics, or resistance summaries per cell.
- **Visualize** with `tiledlayout`: capacity-vs-cycle families, SOH trajectories, CV-hold growth.

This is standard MATLAB table wrangling — no PMT function is required. If a downstream skill fits better (e.g. `matlab-analyze-data` for the ranking workflow), route there instead of loading a reference from this skill.

**Application × data shape.** When the user names an application (SOH, RUL, Fast Charging, Cell Screening) that could be served by multiple data types, still route by inspected shape first — application alone doesn't pick a workflow. Then read the matching reference's **"Feature Selection for Common Applications"** section for the recipe.

---

## Workflow Skeleton

Every reference in this skill follows the same phase template. Load the matching reference for the phase-by-phase details; the skeleton is:

| # | Phase | What it does |
|---|-------|--------------|
| 1 | **Identify inputs** | Map data columns to the function's parameters. Workflow-specific vocabulary table lives at the top of each reference. General rules (vocabulary-first, datetime > numeric, unit conversion) below. |
| 2 | **Data layout** | Detect single-file vs multi-file, single-cell vs multi-cell, single-sweep vs multi-sweep; combine or split accordingly. |
| 3 | **Call functions** | Issue the primary computation call(s). |
| 4 | **Verify results** | Cross-check outputs against independent evidence. Cycling uses `verifySegmentation` + `checkCyclingProtocol`; individual-cycling uses `verifySingleSegment`. **Pulse and EIS skip this phase — no verifier helper exists.** |
| 5 | **Tune parameters** | Only if Phase 4 flagged an issue (or the caller reports symptoms of a wrong setting). Sweep tuning parameters and re-call. |
| 6 | **Postprocess / organize** | Attach tag columns (`CellID`, `ExperimentIndex`), keep per-cell tables in a cell array, etc. |
| 7 | **Report + next steps** | Present the feature table with the key-decisions summary and the Next Steps offer (§ Stop After Extraction rule below). |

Reference-to-phase map:

| Reference | Phases | Verify helper | Tuning reference |
|-----------|--------|---------------|------------------|
| `cycling-pipeline.md` (+ `cycling/*.md` on demand) | 1-7 | `verifySegmentation` or `verifyAgainstSchedule`, + `checkCyclingProtocol` | `cycling/tolerance-tuning.md` or `cycling/schedule-verification.md`; `parameter-tuning.md` (IC/DV/DT smoothing) |
| `individual-cycling-functions.md` | 1-7 | `verifySingleSegment` | `parameter-tuning.md` (IC/DV/DT smoothing, `NoiseTolerance`) |
| `pulse-features.md` | 1-3, 5-7 (no Verify) | — | inline (`ValidPulseDurationRange`, `MinCurrentChange`) |
| `eis-features.md` | 1-3, 5-7 (no Verify) | — | inline (`NumArcs`, multi-sweep splitting) |

## Interaction Rules

Cross-cutting rules that apply to every workflow — do not skip regardless of which reference you loaded.

### Interaction Model: Stop or Proceed

Do not stop and ask before every extraction. Most decisions have a deterministic rule — apply it, extract, and **report what you did** so the user can correct it. Only stop when a decision is genuinely ambiguous *and* guessing it wrong would fail silently (plausible-but-wrong features). The rule applies to every workflow — cycling pipeline, individual cycling functions, pulse, and EIS.

**STOP and ask the user first** — but only when one of these is true:

*General (all workflows):*

1. **Two or more candidate columns of the same type for one variable** (e.g. two numeric elapsed-time columns, two current-like columns) — no rule can choose between them.
2. **Raw unnamed numeric matrix** — column roles must be inferred, not read from names.
3. **A required variable cannot be mapped** — a needed column is missing or its role is unclear.

*Cycling pipeline only:*

4. **`checkCyclingProtocol` finds neither phase consistent** — no phase can be recommended.
5. **Anomalous cycles detected** — never silently exclude them.

**Otherwise PROCEED, then REPORT.** Apply the deterministic rules — datetime/duration beats numeric time; set `DT=true` iff temperature is present; set `CC=true` whenever IC/DV/DT is requested; for cycling, use `checkCyclingProtocol`'s `RecommendedPhase` — write and run the extraction, then present in a single after-extraction turn:

- the column mappings used (noting any alternatives considered and why the chosen one won),
- any workflow-specific decisions — cycling: `CyclingPhase` and its consistency reason; pulse: pulse-detection thresholds if adjusted; EIS: frequency range or sweep selected if the file had multiple,
- any data-quality findings (time-gap indices, invalid-point count, negative Zreal, missing rests, etc.) as a report line — not a gate,
- any goal-vs-data tension, if present (see the loaded reference — e.g. cycling-pipeline.md Phase 4),
- the resulting feature table, followed by the "what next?" offer.

Close the report with an explicit undo invitation, e.g. *"If any mapping or the phase choice looks wrong, tell me and I'll re-run."* This preserves the safety net without a blocking question.

### Stop After Extraction — Offer Next Steps

Once the feature table is extracted and displayed, **stop and present available next steps** to the user. Do not autonomously proceed to visualization, feature ranking, or script saving. The stopping turn must have three parts:

1. **Feature-table summary** — M features across N rows / cycles / pulses / sweeps.
2. **Key decisions + undo invitation** — the autonomous choices you made, each stated so the user can override it, because these were decisions the user never explicitly approved:
   - Column mappings used (with any alternatives considered) and any unit conversion applied.
   - The workflow-specific settings the loaded reference tells you to report (cycling: CyclingPhase + consistency reason + feature categories; pulse: pulse-detection settings; EIS: frequency range / sweep selection; individual cycling: segment identified). The full workflow-specific template lives in each reference's § Report to the user after extraction.
   - **Undo invitation, pointed at those choices** — e.g. *"I chose the time column, CyclingPhase, and feature categories automatically — tell me and I'll re-run with different ones."* Do not use a generic *"if anything looks wrong, let me know."*
   - **When Phase 4 flagged a concern, this is required and must name the finding** — e.g. `verifySegmentation` returned `TuningRecommended`, `checkCyclingProtocol` reported anomalous cycles, or pulse/EIS detection returned empty/failed. State the flag and the concrete re-run it implies (*"3 cycles segmented inconsistently — I can re-run with a tighter Tolerance, or exclude them"*).
3. **Next-steps offer** — the four standing options:
   > - **Visualize:** plots appropriate to the workflow (see the loaded reference's Phase 7 Visualize hints; cycling loads `references/cycling/postprocess.md`)
   > - **Rank features:** identify most discriminative features for your analysis goal
   > - **Export:** save the feature table to a .mat or .csv file
   > - **Refine:** adjust feature categories, phase, or smoothing parameters

Only execute a next step when the user explicitly requests it. This applies even if the original prompt contains phrasing like "show me" or "plot" — extract first, present the table with the key decisions, then offer to visualize.

### Column Mapping: General Rules

Workflow-specific column vocabularies live in the loaded reference's Phase 1 (Identify inputs). The rules below apply regardless of which vocabulary you're consulting.

**Vocabulary first — try common vendor names before declaring a column missing.** The 4 mainstream cyclers (Arbin, Neware, Maccor, BioLogic) and typical EIS/potentiostat exports each use different conventions. Match case-insensitively; strip units suffixes (`_V`, `_A`, `/mA`, `/V`, `/Hz`, `/Ohm`); a match on any name in the reference's Phase 1 vocabulary is sufficient — no need to stop-and-ask.

**Unit conversion when the column name carries units.** If the current column is `I/mA` (milliamps), convert to Amps *before* passing to the function (`data.I_A = data.("I/mA") / 1000`); same for `mV` → `V`. Report the conversion in the after-extraction summary.

1. **Prefer datetime/duration over numeric elapsed time.** If one candidate is `datetime`/`duration` type and another is numeric seconds, the datetime column wins — this is a rule, not a judgment call. Apply it and **report it** rather than asking. Note the alternative you considered in the after-extraction report (e.g., *"I found both `Test_Time` (numeric) and `DateTime` (datetime type) — used `DateTime` as it is a proper datetime column"*).
2. **Stop only when the rule can't decide.** If two candidates share the same type (e.g. two numeric elapsed-time columns) so no rule can pick, ask. Likewise if a required variable has no clear column.
3. **Report the mappings after extracting** — with any workflow-specific decisions, data-quality findings, and an undo invitation. See § Stop After Extraction above and the loaded reference's Phase 7 for the workflow-specific template.

### Unnamed Data (Matrices Without Column Names)

When data is a raw numeric matrix (no column names), infer column roles from value characteristics, then confirm with the user before proceeding:

- **EIS data:** Frequency spans orders of magnitude (all positive), Zreal is non-negative with narrow range, Zimag can be negative with similar magnitude to Zreal
- **Pulse data:** Current has distinct pulse/rest pattern, voltage shows step responses, time is monotonically increasing
- **Otherwise:** If the data does not clearly match EIS or pulse patterns, ask the user what type of data it is rather than guessing

Present the inferred mapping and ask the user to confirm. Example:

> Your data is a 641×3 matrix with no column names. Based on value ranges:
> - Column 1: spans 0.05 to 10000 (likely Frequency)
> - Column 2: all positive, range 13–22 (likely Zreal)
> - Column 3: range -14 to 6, mixed sign (likely Zimag)
>
> Does this mapping look correct?

---

## Cross-Function Pitfalls

Only two pitfalls are truly cross-cutting. Workflow-specific pitfalls (time format, phase mixing, DT requirements, feature-count overfitting, CC data requirements, EIS sign conventions, pulse-detection thresholds, etc.) live in the loaded reference's own § Pitfalls section — consult it before extracting.

- **Manual loops when a PMT function exists.** If the user asks for capacity fade, IC peaks, pulse R0, EIS Rct, etc., use the PMT function — do not hand-code `cumtrapz`, `findpeaks`, or manual segmentation loops.
- **Wrong units.** Current in Amps (not mA), voltage in Volts. Convert unit-suffixed columns before passing them to any PMT function.

----

Copyright 2026 The MathWorks, Inc.

----
