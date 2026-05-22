---
name: matlab-manage-sparameters
description: >
  Load, inspect, visualize, and export S-parameters using RF Toolbox. Use when working with
  Touchstone files (.s1p, .s2p, .s4p, .snp), the sparameters object, rfparam, rfplot, smithplot,
  group delay, rfinterp1, newref, rfwrite, ispassive, iscausal, or any task involving reading,
  plotting, quality-checking, or saving S-parameter data. Trigger on sparameters, Touchstone,
  .s2p, .s4p, rfplot, smithplot, rfparam, rfwrite, group delay, passivity, causality,
  makepassive, S-parameter visualization.
license: MathWorks BSD-3-Clause
metadata:
  author: MathWorks
  version: "1.0"
---

# S-Parameter I/O and Visualization

Load, inspect, visualize, and export S-parameters using the `sparameters` object and RF Toolbox plotting functions.

## When to Use

- Loading Touchstone files (.s1p, .s2p, .s4p, .snp) into MATLAB
- Extracting S-parameter values with `rfparam`
- Plotting S-parameters with `rfplot` or `smithplot`
- Computing group delay from S-parameter data
- Interpolating S-parameters to a new frequency grid with `rfinterp1`
- Changing reference impedance with `newref`
- Exporting S-parameters to Touchstone format with `rfwrite`

## When NOT to Use

- Converting between network parameter types (S, Z, Y, ABCD) -- use `matlab-convert-network-parameters`
- Cascading or de-embedding S-parameter networks -- use `matlab-deembed-rf-cascade`
- Fitting rational models to S-parameter data -- use `matlab-fit-rational-model`
- Amplifier stability or gain analysis -- use `matlab-analyze-rf-amplifier`

## Workflow

1. **Load** — Construct `sparameters` from Touchstone file, raw data, or circuit object
2. **Inspect** — Check ports, frequencies, impedance; extract parameters with `rfparam`
3. **Transform** — Interpolate with `rfinterp1`, re-reference with `newref`
4. **Visualize** — Plot with `rfplot`, `smithplot`, or compute group delay
5. **Export** — Write to Touchstone with `rfwrite`

## Core Object: `sparameters`

### Construction

```matlab
% From Touchstone file (most common)
s = sparameters('device.s2p');

% From raw complex data
s = sparameters(data, freq, Z0);       % data: N×N×K, freq: K×1 (Hz), Z0: scalar or vector

% From other network parameter objects
s = sparameters(yObj);                  % Y → S (uses yObj's impedance)
s = sparameters(zObj, 75);              % Z → S with explicit Z0

% From RF circuit objects
s = sparameters(circuitObj, freq);      % circuit, rffilter, nport, transmission line, RLC
```

### Properties

| Property | Description |
|----------|-------------|
| `Parameters` | N×N×K complex array — indexed as `(row, col, freqIdx)` |
| `Frequencies` | K×1 vector in Hz (ascending) |
| `Impedance` | Reference impedance — scalar or per-port vector |
| `NumPorts` | Number of ports (read-only) |

### Per-Port Reference Impedance (R2023a+)

```matlab
s = sparameters(data, freq, [50 75]);   % Port 1: 50 Ohm, Port 2: 75 Ohm
```

**Gotcha:** When `NumPorts == numel(Frequencies)`, MATLAB cannot distinguish per-port from per-frequency impedance. Use `reshape(z0, 1, 1, [])` to force frequency-dependent interpretation.

## Quality Checks

```matlab
ispassive(s)                            % true if max singular value of S <= 1 at all freqs
iscausal(s)                             % true if network is causal (no output before input)
p = passivity(s);                       % max singular value per frequency (passive where <= 1)
sp = makepassive(s);                    % enforce passivity by clipping singular values to <= 1
```

All four work directly on `sparameters` objects (no rational fit required). `passivity(s)` returns a vector showing *where* violations occur — useful for diagnostics before calling `makepassive`. `makepassive(s)` modifies data point-by-point — for optimization-based passivity enforcement on a fitted model, see `matlab-fit-rational-model`.

### IEEE P370 Quality Metrics (R2023b+)

```matlab
[cm, rm, pm] = ieee370QualityCheckFrequencyDomain(s);
% cm = causality metric (0-100, higher is better)
% rm = reciprocity metric (0-100)
% pm = passivity metric (0-100)
```

Returns percentage scores per the IEEE 370 standard — quantitative grades beyond pass/fail booleans. Accepts a `sparameters` object, filename, or raw 3-D array.

## Extracting Parameters

```matlab
s21 = rfparam(s, 2, 1);                % Complex S21 across all frequencies
s21_dB = 20*log10(abs(s21));            % Convert to dB magnitude
s21_phase = angle(s21)*180/pi;          % Phase in degrees
```

**Gotcha:** `rfparam` returns complex values, NOT dB. Always use `20*log10(abs(...))` for dB magnitude.

## Interpolation

```matlab
fNew = linspace(1e9, 6e9, 500);
sInterp = rfinterp1(s, fNew);          % Interpolate to new frequency grid
sExtrap = rfinterp1(s, fNew, 'extrap'); % Allow extrapolation outside original range
```

**Gotcha:** `rfinterp1` interpolates the **real and imaginary parts** of each S-parameter independently (like `interp1`), not magnitude and angle. This can produce artifacts near sharp resonances or rapid phase transitions.

## Change Reference Impedance

```matlab
s75 = newref(s, 75);                   % Re-reference from 50 to 75 Ohm
```

**Gotcha:** `sparameters(filename, Z0)` is not a valid call signature — it errors with "Too many input arguments." Always load first, then use `newref` to change impedance.

## Export to Touchstone

```matlab
rfwrite(s, 'output.s2p');
rfwrite(s, 'output.s2p', 'FrequencyUnit', 'GHz', 'Format', 'RI', 'ForceOverwrite', true);
```

`Format` options: `'MA'` (magnitude/angle, default), `'DB'` (dB/angle), `'RI'` (real/imaginary).

**Gotcha:** `'DB'` format writes `-Inf` for any zero-valued S-parameter (e.g., S12=0 in an isolator), producing a file that `sparameters` cannot re-read. Use `'RI'` for lossless round-trip fidelity.

## Visualization

### `rfplot` — Rectangular Plots

```matlab
rfplot(s);                              % All S-parameters, magnitude in dB
rfplot(s, 2, 1);                        % S21 only
rfplot(s, [1 2], [1 2]);               % S11, S12, S21, S22
rfplot(s, {[2 1]; [1 1]});             % S21 and S11 specifically
rfplot(s, 'diag');                      % Diagonal only (S11, S22, ...) — reflection coefficients
rfplot(s, 'triu');                      % Upper triangular portion
```

Plot types via the `plotflag` argument:
```matlab
rfplot(s, 2, 1, 'db');                 % Magnitude in dB (default)
rfplot(s, 2, 1, 'angle');              % Phase in degrees
rfplot(s, 2, 1, 'abs');                % Linear magnitude
rfplot(s, 2, 1, 'real');               % Real part
rfplot(s, 2, 1, 'imag');               % Imaginary part
```

Multi-panel layout with `tiledlayout`:
```matlab
figure;
tiledlayout(2, 2);
nexttile; rfplot(s, 1, 1);       title('S11 (dB)');
nexttile; rfplot(s, 2, 1);       title('S21 (dB)');
nexttile; rfplot(s, 1, 1, 'angle'); title('S11 Phase');
nexttile; rfplot(s, 2, 1, 'angle'); title('S21 Phase');
```

### `smithplot` — Smith Chart (R2017b+)

Prefer `smithplot` over the legacy `smith` function.

```matlab
smithplot(s, 1, 1);                    % S11 on Smith chart
smithplot(s, [1,1; 2,2]);             % S11 and S22 together
```

With name-value customization:
```matlab
sp = smithplot(s, 1, 1, ...
    'TitleTop', 'Input Match', ...
    'LegendLabels', {'S_{11}'});
```

**Gotcha:** Use `smithplot` for modern workflows with name-value customization. The legacy `smith` function lacks these capabilities.

### Group Delay

```matlab
gd = groupdelay(s);                    % S21 group delay for 2-port (default)
gd = groupdelay(s, 2, 1);             % Explicit S21
% gd is in seconds — multiply by 1e9 for nanoseconds

figure;
plot(s.Frequencies/1e9, gd*1e9);
xlabel('Frequency (GHz)'); ylabel('Group Delay (ns)');
title('S21 Group Delay');
```

## Gotchas

1. **`rfparam` returns complex, not dB** -- Always use `20*log10(abs(rfparam(...)))` for dB magnitude. `rfparam` itself returns raw complex values.
2. **`sparameters(filename, Z0)` is invalid** -- Cannot pass reference impedance at load time. Load first, then use `newref(s, Z0)`.
3. **`rfinterp1` interpolates real/imag independently** -- Not magnitude and angle. Can produce artifacts near sharp resonances or rapid phase transitions.
4. **`'DB'` format in `rfwrite` writes `-Inf` for zeros** -- Zero-valued S-parameters (e.g., S12=0) produce `-Inf` in DB format, which `sparameters` cannot re-read. Use `'RI'` for lossless round-trip fidelity.
5. **Per-port vs per-frequency impedance ambiguity** -- When `NumPorts == numel(Frequencies)`, MATLAB cannot distinguish per-port from per-frequency impedance. Use `reshape(z0, 1, 1, [])` to force frequency-dependent interpretation.
6. **Use `smithplot`, not `smith`** -- The legacy `smith` function lacks name-value customization. `smithplot` is the modern replacement (R2017b+).
7. **Non-ASCII characters in Touchstone comments cause read errors** -- Degree symbols, em-dashes, or other non-ASCII characters in comment lines (starting with `!`) cause `sparameters` to error. Fix with `setTouchstoneReader('IgnoreComments', false)` before reading (R2024b+). The second argument is a persistence flag -- use `false` to avoid the setting persisting across MATLAB sessions. Restore default behavior with `setTouchstoneReader('ParseComments', false)`.
8. **File extension does not need to be `.snp`** -- The Touchstone 2.0 reader (used by `sparameters`) accepts any file extension, not just `.s2p`/`.s4p`/`.snp`. Non-standard extensions (`.txt`, `.dat`, etc.) produce a warning ("The extension .xxx is unrecognized. Attempting to read the file using the Touchstone format.") but succeed if the file content is valid Touchstone. This is a Touchstone 2.0 relaxation -- Touchstone 1.0 required `.snp` extensions.
9. **`.amp` files not supported by `sparameters`** -- AMP files (bundling S-params, noise, power data) are not readable by `sparameters` or `nport`. Use the legacy `rfckt.amplifier` with `read(rfckt.amplifier, 'file.amp')` to access AMP data.

## Legacy `extract` Function

The `extract` function belongs to the legacy `rfckt`/`rfdata` API. It returned S-parameter data (and other quantities like noise figure, group delay) from legacy objects. Common issue: it returns **cached data** and may appear to give identical results for different inputs if the object was not re-analyzed after property changes.

**Modern equivalent:** Use `rfparam(s, i, j)` for complex S-parameter extraction and `s.Frequencies` for the frequency vector. Other quantities have dedicated functions: `groupdelay(s)`, `noisefigure(...)`, etc.

## Scope Note

RF Toolbox handles **circuit-level** S-parameter analysis (loading, plotting, cascading, de-embedding, fitting). It does NOT provide RF propagation modeling (path loss, fading channels, ray tracing). Propagation is in Communications Toolbox (`propagationModel`), Phased Array System Toolbox (`fspl`, `gaspl`), and Antenna Toolbox (`txsite`, `coverage`, `raytrace`).

## Conventions

- Use `tiledlayout`/`nexttile` for multi-panel figures (not `subplot`)
- Always label axes with units (GHz, dB, ns) and include figure titles
- Use `rfparam` to extract parameters — not `squeeze(s.Parameters(i,j,:))`

## Quick Reference: Sample Touchstone Files

RF Toolbox ships with example files for testing:

| File | Description |
|------|-------------|
| `default.s2p` | Active 2-port (amplifier-like, non-passive) |
| `passive.s2p` | Passive 2-port network |
| `default.s4p` | 4-port for differential/mixed-mode analysis |
| `lnadata.s2p` | Low-noise amplifier data |
| `measured.s2p` | Measured device data |

----

Copyright 2026 The MathWorks, Inc.

----
