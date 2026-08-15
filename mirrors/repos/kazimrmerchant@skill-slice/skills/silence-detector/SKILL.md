---
name: silence-detector
version: 1.1.1
description: "Finds the first silence-to-content crossing in a precomputed energy series (opening-window baseline times a multiplier). Use when trimming title-card, waiting-room, or pre-roll dead air at the start of a lecture or screencast. Do not use for interior pauses, live streaming VAD, or any job that still needs to decode the audio file."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

## Overview

Detects the initial silence segment of a recording by analyzing a pre-computed energy series. It finds the single transition point where low-energy silence gives way to higher-energy content (someone starts talking, music begins, the screen-share goes live).

The whole design rests on one observation: the *start* of many recordings is predictably quiet. Lectures open on a title slide, webinars wait for attendees to join, screencasts begin with mic and screen setup. That quiet lead-in has measurably lower energy than the content that follows, so a cheap threshold test is enough to find where it ends — no voice-activity model or full audio-decode pass required.

## When to Use

- **Finding initial silence in recordings.** The opening seconds are assumed silent and used as the baseline, so detection is most reliable here. Trigger keywords: *initial silence, pre-roll, trim silence, title card, setup period, dead air, leading silence, silence detection, energy threshold*.
- **Trimming pre-roll silence before content.** Useful for auto-generating a start offset so playback or transcription can skip dead air.
- **Identifying setup/title-card periods.** A title slide or "waiting room" screen produces a long, flat, low-energy run that this skill isolates as a single segment.

Reach for this skill when the cost of a full voice-activity-detection (VAD) pipeline is not justified and you only need the *first* silence→content boundary.

### When NOT to use

- **No energy data available.** This skill consumes the JSON emitted by the `energy-calculator` skill; it never decodes audio itself. Without that input there is nothing to analyze.
- **Silence in the middle or end of a recording.** The algorithm scans for the *first* rise above the threshold and then stops. It models exactly one leading silence, so any later gaps are invisible by design. For interior pauses, use a pause-detector that scans the full series.
- **The opening is not distinctly quieter than the rest.** The baseline is the mean energy of the opening window, *assuming it is silent*. If the recording opens on loud content, the baseline is already high and the threshold becomes meaningless — you will get a near-zero or false boundary.
- **Real-time / streaming detection.** Detection needs the complete energy series plus a baseline window computed up front. A live stream would require an online algorithm with a rolling baseline, which this skill does not implement.

## Prerequisites

- **Python 3.12+** — the implementation uses built-in generic types (`list[float]`, `tuple[int, ...]`) and `numpy.typing` annotations.
- **numpy 1.26.0** — provides the vectorized mean, convolution (smoothing), and `flatnonzero` crossing search. These run in C, so even long recordings analyze near-instantly.
- **pandas 2.1.0** — listed for environment parity with the rest of the skill toolchain; the core detection path relies only on numpy.
- **Input file from `energy-calculator`** — you must run `energy-calculator` first to produce the `energies` + `total_seconds` JSON this skill requires.

Pin these versions when reproducibility matters. If you upgrade numpy, re-run the verification checklist, since `np.convolve` edge behavior and dtype promotion are the parts most sensitive to version changes.

## Procedure

### Step 1 — Ensure prerequisites are met

```powershell
python --version    # Must be 3.12+
python -c "import numpy; print(numpy.__version__)"    # Must be 1.26.0
python -c "import pandas; print(pandas.__version__)"  # Must be 2.1.0
```

If any dependency is missing or mismatched, install the pinned versions:

```powershell
pip install numpy==1.26.0 pandas==2.1.0
```

### Step 2 — Confirm the input energy JSON exists

The input file must be a JSON object with a non-empty `energies` array and a numeric `total_seconds` field, as produced by `energy-calculator`:

```json
{
  "energies": [0.001, 0.002, 0.001, ...],
  "total_seconds": 3600
}
```

### Step 3 — Run the silence detector

```powershell
python scripts/detect_silence.py `
    --energies /path/to/energies.json `
    --output /path/to/silence.json
```

> **Windows note:** On PowerShell, use backtick (`` ` ``) for line continuation instead of backslash (`\`). On bash/zsh, use backslash (`\`).

### Step 4 — Inspect the output

The script writes a JSON result to the `--output` path:

```json
{
  "method": "energy_threshold",
  "segments": [
    {"start": 0, "end": 120, "duration": 120}
  ],
  "total_segments": 1,
  "total_duration_seconds": 120,
  "parameters": {
    "threshold_multiplier": 1.5,
    "initial_window": 60,
    "smoothing_window": 30
  },
  "analysis": {
    "initial_avg": 0.012,
    "threshold": 0.018
  }
}
```

`segments` is empty (and `total_segments`/`total_duration_seconds` are `0`) when no clear transition is found — for example, when the whole recording is quiet or when it opens loud. The `analysis` block reports the computed baseline and threshold so you can sanity-check why a boundary was or was not detected.

### Parameters

| Parameter | Default | Constraint | Purpose |
|-----------|---------|------------|---------|
| `--energies` | *(required)* | Valid path | Path to the energy JSON file produced by `energy-calculator` |
| `--output` | *(required)* | Valid path | Path to write the result JSON |
| `--threshold-multiplier` | `1.5` | Must be > 0 | How far above the baseline energy must rise before a sample counts as "content" |
| `--initial-window` | `60` | Must be > 0 | Number of opening seconds averaged to form the silent baseline |
| `--smoothing-window` | `30` | Must be > 0 | Width of the moving-average window applied before thresholding |

### How the algorithm works

1. **Load and validate the energy data.** The loader rejects non-objects, empty `energies` arrays, non-numeric `total_seconds`, and non-finite values (NaN/inf) up front with a clear `SystemExit` message.
2. **Compute the baseline from the first N seconds.** The mean of the first `initial_window` samples stands in for "what silence looks like" in this particular recording, which makes the threshold adapt to each file's noise floor instead of a hard-coded constant.
3. **Smooth with a moving average.** A single loud spike (a cough, a click) should not end the silence. Averaging over `smoothing_window` samples suppresses transient blips so only a *sustained* rise crosses the threshold.
4. **Find the first crossing.** The end of silence is the first smoothed sample that exceeds `baseline × threshold_multiplier`. Because we want only the leading silence, the scan stops at that first crossing.

### When to load `scripts/detect_silence.py`

- **Read the script** when you need to understand the exact detection logic, modify the algorithm, or debug unexpected output.
- **Do not modify the script** unless you have a specific tuning requirement; the defaults are calibrated for typical lecture/webinar/screencast recordings.

## Examples

Detect initial silence with the defaults:

```powershell
python scripts/detect_silence.py `
    --energies energies.json `
    --threshold-multiplier 1.5 `
    --output silence.json
# -> Initial silence detected: 120s (2.00 min); results saved to silence.json
```

Be more conservative (require a larger jump before declaring content) for a recording with a noisy title card:

```powershell
python scripts/detect_silence.py `
    --energies energies.json `
    --threshold-multiplier 2.5 `
    --initial-window 90 `
    --smoothing-window 45 `
    --output silence.json
```

### Parameter tuning guide

| Parameter | Lower value | Higher value | Tune when |
|-----------|-------------|--------------|-----------|
| `threshold_multiplier` | More sensitive — ends silence on a smaller rise; risks cutting off early | More conservative — needs a bigger jump; risks keeping quiet speech inside "silence" | The detected boundary lands too early (raise it) or too late (lower it) |
| `initial_window` | Shorter baseline — faster to react, but noisier and easier to skew | Longer baseline — steadier estimate, but assumes a longer silent opening | The opening silence is shorter/longer than ~60s |
| `smoothing_window` | Less smoothing — reacts to brief sounds, more false early endings | More smoothing — ignores transients, but blurs the exact boundary | Single clicks/coughs are ending silence too soon (raise it) |

## Pitfalls

- **No energy data — skill cannot run.** This skill never decodes audio. It consumes the JSON emitted by `energy-calculator`. Without that input there is nothing to analyze. Always run `energy-calculator` first.
- **Recording opens loud — false or near-zero boundary.** The baseline is computed from the opening window *assuming it is silent*. If the recording opens on loud content, the baseline is already high and the threshold becomes meaningless. You will get `segments: []` with `total_segments: 0`.
- **Interior silence is invisible.** The algorithm scans for the *first* rise above the threshold and then stops. It models exactly one leading silence. Any later gaps are invisible by design. Use a pause-detector for interior pauses.
- **Single transient ends silence too early.** A cough, click, or door slam in the opening seconds can cross the threshold if smoothing is insufficient. Raise `--smoothing-window` to suppress brief transients.
- **Malformed input causes `SystemExit`, not a traceback.** The loader validates structure (object shape, non-empty `energies` array, numeric `total_seconds`, finite values) and surfaces a clear error. If you wire this into an automated pipeline, validate or sandbox the paths upstream before they reach the script.
- **NaN or inf in energy data is rejected.** The script explicitly checks `np.isfinite` on all samples. If `energy-calculator` emits non-finite values, fix the upstream calculation.
- **numpy version sensitivity.** `np.convolve` edge behavior and dtype promotion can change across numpy versions. Re-run the verification checklist after any numpy upgrade.
- **PowerShell line continuation.** On Windows PowerShell, use backtick (`` ` ``) for multi-line commands, not backslash (`\`). Using `\` will cause a syntax error.

## Verification

Run through this checklist after any change to the script, dependencies, or input pipeline:

- [ ] **Basic run exits 0.** Run the script against a sample `energies.json` and confirm it exits `0`:
  ```powershell
  python scripts/detect_silence.py `
      --energies energies.json `
      --output silence.json
  echo $LASTEXITCODE  # Should print 0
  ```
- [ ] **Output schema matches documentation.** Confirm the output JSON has keys `method`, `segments`, `total_segments`, `total_duration_seconds`, `parameters`, `analysis` with correct types.
- [ ] **Threshold sweep behaves correctly.** Sweep `--threshold-multiplier` (e.g. `1.2`, `1.5`, `2.5`) and check the detected boundary moves *later* as the multiplier rises:
  ```powershell
  python scripts/detect_silence.py `
      --energies energies.json --threshold-multiplier 1.2 --output silence_12.json
  python scripts/detect_silence.py `
      --energies energies.json --threshold-multiplier 2.5 --output silence_25.json
  # silence_25.json total_duration_seconds should be >= silence_12.json
  ```
- [ ] **No-quiet-opening returns empty segments.** Feed a recording with no quiet opening and confirm `segments` comes back empty with `total_segments: 0`.
- [ ] **Round-trip through `segment-combiner`.** Pass the `segments` array through `segment-combiner` to confirm format compatibility (same `start`/`end`/`duration` shape).
- [ ] **Malformed input produces clean error.** Pass a malformed energy file (missing `energies`, non-numeric entries, invalid JSON) and confirm a clear `SystemExit` message instead of a traceback:
  ```powershell
  echo '{"foo": "bar"}' | Out-File -Encoding utf8 bad.json
  python scripts/detect_silence.py `
      --energies bad.json --output out.json
  # Should print: "Energy file 'bad.json' must contain a non-empty 'energies' array"
  ```
- [ ] **Dependency version regression check.** Re-run on the pinned numpy/pandas versions after any dependency upgrade to catch convolution or dtype regressions.

## Related skills

- **energy-calculator** — produces the `energies` + `total_seconds` JSON this skill requires as input. Run it first.
- **segment-combiner** — consumes the `segments` array emitted here (same `start`/`end`/`duration` shape), so the two compose without a translation step.
