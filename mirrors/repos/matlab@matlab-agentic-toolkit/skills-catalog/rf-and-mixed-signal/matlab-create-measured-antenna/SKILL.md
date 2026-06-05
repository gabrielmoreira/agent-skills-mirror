---
name: matlab-create-measured-antenna
description: Create measuredAntenna objects from simulated or measured data using MATLAB Antenna Toolbox. Converts catalog antennas and arrays into measuredAntenna for RF site planning (txsite/rxsite), satellite scenarios, beam steering, and pattern multiplication. Use when the user wants to create a measuredAntenna, convert an antenna to measured data, use an antenna with txsite/rxsite, build a satellite link budget, or steer an array beam with phase shifts.
license: MathWorks BSD-3-Clause
allowed-tools: mcp__matlab__evaluate_matlab_code mcp__matlab__check_matlab_code mcp__matlab__detect_matlab_toolboxes ReadMcpResourceTool
argument-hint: <source-antenna> <frequency> [workflow]
metadata:
  author: MathWorks
  version: "1.0"
---

# Measured Antenna Skill

You are an expert RF and antenna engineer assisting a professional antenna engineer or RF system designer. Use MATLAB Antenna Toolbox to create `measuredAntenna` objects from simulated or measured antenna data.

## When to Use

- User wants to create a `measuredAntenna` from pattern data or catalog antenna simulation
- User needs to use an antenna with `txsite`/`rxsite` for propagation or site planning
- User wants to steer a beam or apply pattern multiplication with measured data
- User asks about satellite link budget with a directional antenna
- User has measured data (directivity, gain) and wants to create an antenna object

## When NOT to Use

- User wants to design a new antenna from scratch — use `matlab-design-antenna`
- User wants RF propagation/coverage analysis — use `matlab-analyze-rf-propagation`
- User wants to build a custom antenna from shapes — use `matlab-create-custom-antenna`

## Core Workflow

1. **Parse the request** -- Identify the source antenna or array, operating frequency (or frequency band), the intended use case (general E-field capture, RF site planning, satellite link, array beam steering, or element-in-array), and any additional constraints (grid resolution, tilt, scan angle).

2. **Select the workflow** -- Choose the correct constructor variant based on the use case (see Workflow Selection table below).

3. **Generate the spherical grid** -- Create the evaluation grid with azimuth-fast ordering. Always transpose after `meshgrid`.

4. **Extract field or pattern data** -- Use `EHfields` for E-field workflows or `pattern` with `Type="directivity"` for directivity-only workflows. Transpose all outputs to the expected orientation.

5. **Build the measuredAntenna** -- Construct the object with the correct property combination for the selected workflow.

6. **Verify** -- Compare the `measuredAntenna` pattern against the original antenna or array pattern. Use `pattern` for E-field and EmbeddedE workflows, `patternMultiply` for element-in-array.

7. **Present results professionally** -- Summarize in a table including: workflow name, key functions used (e.g. `EHfields`, `pattern`), data sizes (e.g. P-by-3), ordering method (e.g. az-fast meshgrid transpose), and key constructor properties set (e.g. `E = []`, `CalculateTotalField = true`). Include peak gain/directivity with units.

## Workflow Selection

| Goal | Workflow | Key Property |
|------|----------|-------------|
| Preserve full E-field data for a single element | E-field | `E` = P-by-3-by-F |
| Use antenna with `txsite`/`rxsite`/`coverage` | Directivity-only | `Directivity` = P-by-F, `E = []` |
| Tilted antenna for satellite uplink | Directivity-only with tilt | `Directivity` = P-by-F, `E = []` |
| Array with per-element beam steering | EmbeddedE | `EmbeddedE` = P-by-3-by-N-by-F |
| Use measuredAntenna as element in a larger array | Element-in-array | `E` = P-by-3, use `patternMultiply` |

**Informal name mapping** -- When the user gives a common description, map to the correct workflow:
- "convert antenna to measured" / "create measuredAntenna" --> E-field workflow
- "use antenna with txsite" / "RF propagation" / "coverage map" --> Directivity-only workflow
- "satellite link" / "uplink" / "ground station antenna" --> Directivity-only with tilt
- "array beam steering" / "phase shift array" / "embedded element" --> EmbeddedE workflow
- "measured element in array" / "patternMultiply" --> Element-in-array workflow

## Critical: Azimuth-Fast Data Ordering

`measuredAntenna` expects data with **azimuth as the fast-varying index**. `meshgrid` produces el-fast by default because MATLAB flattens column-major. **Always transpose after meshgrid:**

```matlab
[phi, elv] = meshgrid(az, el);
phi = phi';   % Transpose: now az-by-el
elv = elv';   % Transpose: now az-by-el
% phi(:) and elv(:) are now az-fast column vectors
```

Failing to transpose produces silently wrong patterns -- the data maps to incorrect angular positions.

### pattern() output is also el-fast

`pattern(ant, freq, az, el)` returns an **el-by-az** matrix. Transpose before flattening:

```matlab
[pat, ~, ~] = pattern(ant, freq, az, el, Type="directivity");
pat1 = pat';       % Transpose to az-by-el
D = pat1(:);       % Flatten az-fast
```

### EHfields output is 3-by-P

`EHfields` returns 3-by-P. Transpose to P-by-3 for `measuredAntenna`:

```matlab
[e, ~] = EHfields(ant, freq, points);
E = e.';  % P-by-3
```

## FieldCoordinate: Rectangular vs Polar

`measuredAntenna` supports two field coordinate systems:

| FieldCoordinate | E columns (P-by-3) | Source |
|---|---|---|
| `"rectangular"` (default) | [Ex, Ey, Ez] | `EHfields(ant, freq, points)` |
| `"polar"` | [Ephi, Etheta, Er] | `EHfields(ant, freq, points, Coordinate="spherical")` |

### When to use `"polar"`

- Importing measured data from an anechoic chamber (which outputs Etheta/Ephi)
- Importing from external EM tools (HFSS .ffd files, CST, FEKO)
- When source data is already in spherical components

### Extracting polar data from Antenna Toolbox

`EHfields` with `Coordinate="spherical"` returns rows [Ephi; Etheta; Er]. Transpose gives exactly what `measuredAntenna` expects:

```matlab
[e, ~] = EHfields(ant, freq, points, Coordinate="spherical");
E_polar = e.';  % P-by-3: [Ephi, Etheta, Er]

mAnt = measuredAntenna( ...
    E = E_polar, ...
    Direction = Direction, ...
    FieldFrequency = freq, ...
    FieldCoordinate = "polar", ...
    Azimuth = az, ...
    Elevation = el);
```

### Importing external chamber measurements

Measurement systems typically output Etheta and Ephi directly. Er is zero in the far field:

```matlab
% From chamber data (Etheta_meas and Ephi_meas are P-by-1 complex vectors)
E_polar = [Ephi_meas, Etheta_meas, zeros(numPoints, 1)];

mAnt = measuredAntenna( ...
    E = E_polar, ...
    Direction = Direction, ...
    FieldFrequency = measuredFreq, ...
    FieldCoordinate = "polar", ...
    Azimuth = az, ...
    Elevation = el);
```

**Column order is [Ephi, Etheta, Er]** -- not [Etheta, Ephi, Er]. This matches the HFSS .ffd import convention.

## Common Setup: Spherical Grid (All Workflows)

Used by all workflows. The az-fast ordering after meshgrid is universal.

```matlab
freq = 2.4e9;
c = physconst("LightSpeed");
lambda = c / freq;
ant = design(patchMicrostrip, freq);

az = -180:5:180;
el = -90:5:90;
R = 100*lambda;

[phi, elv] = meshgrid(az, el);
phi = phi';    % Transpose for az-fast
elv = elv';
numPoints = numel(phi);

% Cartesian points for EHfields (3-by-P)
[x, y, z] = sph2cart(deg2rad(phi(:)), deg2rad(elv(:)), R);
points = [x, y, z].';

% Direction matrix for measuredAntenna (P-by-3: [az, el, R])
Direction = [phi(:) elv(:) R*ones(numPoints, 1)];
```

## Workflow 1: Single-Element E-Field (Multi-Frequency)

Creates a `measuredAntenna` preserving full E-field data. Supports multiple frequencies via P-by-3-by-F array.

```matlab
fieldFreqs = [2.2e9, 2.4e9, 2.6e9];
numFreqs = numel(fieldFreqs);

E_data = zeros(numPoints, 3, numFreqs);
for k = 1:numFreqs
    [e, ~] = EHfields(ant, fieldFreqs(k), points);
    E_data(:, :, k) = e.';  % Transpose 3-by-P to P-by-3
end

sParams = sparameters(ant, fieldFreqs);

mAnt = measuredAntenna( ...
    E = E_data, ...
    Direction = Direction, ...
    FieldFrequency = fieldFreqs(:), ...
    FieldCoordinate = "rectangular", ...
    Azimuth = az, ...
    Elevation = el, ...
    Sparameters = sParams);
```

### Verification

```matlab
% Compare simulated vs measuredAntenna pattern
figure; pattern(ant, freq, "Type", "efield");
figure; pattern(mAnt, freq);
```

### Properties Used

| Property | Size | Description |
|---|---|---|
| `E` | P-by-3-by-F | E-field in rectangular coordinates |
| `Direction` | P-by-3 | [az, el, R] for each point |
| `FieldFrequency` | F-by-1 | Frequencies in Hz |
| `FieldCoordinate` | string | `"rectangular"` for Ex/Ey/Ez |
| `Azimuth` | 1-by-Naz | Azimuth values in degrees |
| `Elevation` | 1-by-Nel | Elevation values in degrees |
| `Sparameters` | sparameters | S-parameter object |

## Workflow 2: Directivity-Only for RF Site Planning

`txsite` and `rxsite` require `measuredAntenna` with **non-empty Directivity** and **empty E and EmbeddedE**.

Direction and Directivity must use the **same az-fast ordering** — transpose after meshgrid, same as E-field workflows.

```matlab
% Direction: az-fast (transpose after meshgrid)
[phi, elv] = meshgrid(az, el);
phi = phi';
elv = elv';
numPoints = numel(phi);
Direction = [phi(:) elv(:) R*ones(numPoints, 1)];

D_data = zeros(numPoints, numFreqs);
for k = 1:numFreqs
    [pat, ~, ~] = pattern(ant, fieldFreqs(k), az, el, Type="directivity");
    pat1 = pat';           % Transpose el-by-az to az-by-el
    D_data(:, k) = pat1(:);  % Flatten az-fast
end

mAntSite = measuredAntenna( ...
    E = [], ...
    Directivity = D_data, ...
    Direction = Direction, ...
    FieldFrequency = fieldFreqs(:), ...
    Azimuth = az, ...
    Elevation = el);
```

### Using with txsite/rxsite

```matlab
tx = txsite( ...
    Name = "Patch TX", ...
    Antenna = mAntSite, ...
    AntennaHeight = 30, ...
    TransmitterFrequency = freq, ...
    TransmitterPower = 10);

rx = rxsite( ...
    Name = "Receiver", ...
    Latitude = 42.30, Longitude = -71.35, ...
    AntennaHeight = 1.5, ...
    ReceiverSensitivity = -90);

ss = sigstrength(rx, tx);
coverage(tx, SignalStrengths=[-60 -70 -80 -90], MaxRange=5000);
```

### Properties Used

| Property | Size | Description |
|---|---|---|
| `E` | `[]` | Must be empty for txsite/rxsite |
| `Directivity` | P-by-F | Directivity in dBi |
| `Direction` | P-by-3 | [az, el, R] for each point |

## Workflow 3: Tilted Antenna for Satellite Communication

Tilt the antenna beam toward zenith for ground-to-satellite uplink. Uses Directivity-only (same constructor as Workflow 2) with a tilted simulated antenna. Same az-fast ordering for Direction and Directivity.

```matlab
antTilted = design(patchMicrostrip, freq);
antTilted.Tilt = 90;
antTilted.TiltAxis = [0 1 0];

% Direction: az-fast (same as Workflow 2)
[phi, elv] = meshgrid(az, el);
phi = phi';
elv = elv';
numPoints = numel(phi);
Direction = [phi(:) elv(:) R*ones(numPoints, 1)];

D_data_tilted = zeros(numPoints, numFreqs);
for k = 1:numFreqs
    [pat, ~, ~] = pattern(antTilted, fieldFreqs(k), az, el, Type="directivity");
    pat1 = pat';
    D_data_tilted(:, k) = pat1(:);
end

mAntSat = measuredAntenna( ...
    E = [], ...
    Directivity = D_data_tilted, ...
    Direction = Direction, ...
    FieldFrequency = fieldFreqs(:), ...
    Azimuth = az, ...
    Elevation = el);
```

### Satellite Scenario Usage

```matlab
sc = satelliteScenario(startTime, stopTime, sampleTime);
sat = satellite(sc, semiMajorAxis, eccentricity, inclination, ...
    RAAN, argPeriapsis, trueAnomaly);
gs = groundStation(sc, lat, lon, MaskElevationAngle=10);

% Gimbal on ground station to track satellite
gimGS = gimbal(gs);
pointAt(gimGS, sat);

% Mount transmitter on gimbal with measuredAntenna
gsTx = transmitter(gimGS, ...
    Antenna = mAntSat, ...
    Frequency = freq, ...
    Power = 100, ...
    BitRate = 1, ...
    SystemLoss = 3);

% Gimbal on satellite pointing at ground station
gimSat = gimbal(sat);
pointAt(gimSat, gs);
satRx = receiver(gimSat, SystemLoss=3, RequiredEbNo=5);
gaussianAntenna(satRx, DishDiameter=0.5);

lnk = link(gsTx, satRx);
lnkIntervals = linkIntervals(lnk);
```

Key notes:
- Mount transmitter/receiver on a `gimbal` (not directly on station/satellite); use `pointAt(gimbal, target)` for tracking on both ends.
- `Tilt=90` with `TiltAxis=[0 1 0]` rotates beam from broadside to zenith.

## Workflow 4: Array with EmbeddedE (Beam Steering)

Extract per-element embedded E-fields from an array. Enables beam steering via `PhaseShift` and `AmplitudeTaper`.

```matlab
arr = linearArray( ...
    Element = design(patchMicrostrip, freq), ...
    NumElements = 4, ...
    ElementSpacing = lambda/2);

sParamsArr = sparameters(arr, fieldFreqs);
numElements = arr.NumElements;

% Extract embedded E-field per element: P-by-3-by-N-by-F
EmbE = zeros(numPoints, 3, numElements, numFreqs);
for k = 1:numFreqs
    for n = 1:numElements
        [e, ~] = EHfields(arr, fieldFreqs(k), points, ElementNumber=n);
        EmbE(:, :, n, k) = e.';
    end
end

mAntArray = measuredAntenna( ...
    E = [], ...
    EmbeddedE = EmbE, ...
    Direction = Direction, ...
    NumPorts = numElements, ...
    FieldFrequency = fieldFreqs(:), ...
    FieldCoordinate = "rectangular", ...
    Azimuth = az, ...
    Elevation = el, ...
    Sparameters = sParamsArr, ...
    CalculateTotalField = true);
```

### Beam Steering

```matlab
steerAz = 30;
ps = phaseShift(arr, freq, [steerAz, 0]);
mAntArray.PhaseShift = ps;
figure;
pattern(mAntArray, freq);
```

### Verification

```matlab
% Compare total pattern
figure; pattern(arr, freq, "Type", "efield");
figure; pattern(mAntArray, freq);

% Compare per-element embedded patterns
figure; pattern(arr, freq, az, el, ElementNumber=1, Type="efield");
figure; pattern(mAntArray, freq, az, el, ElementNumber=1);
```

### Properties Used

| Property | Size | Description |
|---|---|---|
| `E` | `[]` | Must be empty when using EmbeddedE |
| `EmbeddedE` | P-by-3-by-N-by-F | Per-element E-field |
| `NumPorts` | scalar | Number of array elements |
| `CalculateTotalField` | logical | `true` to sum element contributions |
| `PhaseShift` | 1-by-N | Phase weights per element (degrees) |
| `AmplitudeTaper` | 1-by-N | Amplitude weights per element |

## Workflow 5: measuredAntenna as Element in Array

Create a `measuredAntenna` from a single element, then assign it as the `Element` of an array. **Only `patternMultiply` is supported** when `measuredAntenna` is used as an array element -- not `pattern`.

```matlab
ant2 = design(patchMicrostrip, freq);

% Single-frequency E-field extraction
E0 = EHfields(ant2, freq, points);

mesAnt = measuredAntenna( ...
    E = E0.', ...
    Direction = Direction, ...
    NumPorts = 1, ...
    Azimuth = az, ...
    Elevation = el, ...
    FieldCoordinate = "rectangular", ...
    FieldFrequency = freq);

% Use as element in a rectangular array
rectArray = design(rectangularArray, freq, ant2);
rectArrayMes = copy(rectArray);
rectArrayMes.Element = mesAnt;

% Compare using patternMultiply (NOT pattern)
figure; patternMultiply(rectArray, freq);
figure; patternMultiply(rectArrayMes, freq);
```

## Performance

- Start with 5-degree grid steps; use 1-degree only when high accuracy is needed.
- Limit multi-frequency extraction to 3--5 frequencies unless dense sweeps are required.
- For EmbeddedE with >8 elements, warn about computation time before proceeding.

## MATLAB Coding Standards

- Use 4-space indentation, lowerCamelCase for variables, UpperCamelCase for Name-Value args.
- Use `"double quotes"` for strings. Parse frequency units (MHz, GHz, Hz); default to Hz if unspecified.
- Do not add titles to Antenna Toolbox plots (`show`, `pattern`, `patternMultiply`, etc.) -- they already generate their own titles.
- Use `fprintf` for formatted numerical output.
- Follow the MATLAB coding guidelines from `guidelines://coding`.

## Gotchas

1. **Forgot to transpose meshgrid** -- All workflows: always `phi = phi'; elv = elv';` after `meshgrid`. This ensures az-fast ordering for both Direction and data (E, Directivity, EmbeddedE).
2. **Mismatched Direction and Directivity ordering** -- Direction and Directivity must use the same az-fast flattening. If you transpose one but not the other, each index maps to a different angular position, producing silently wrong patterns.
3. **Forgot to transpose pattern() output** -- `pattern` returns el-by-az. Do `pat'` then `(:)`.
4. **Forgot to transpose EHfields output** -- Returns 3-by-P, need P-by-3 for `measuredAntenna`.
5. **Using E-field measuredAntenna with txsite** -- `txsite` requires `Directivity` populated and `E = []`. Set `E = []` explicitly.
6. **Using `pattern` instead of `patternMultiply`** -- When `measuredAntenna` is the `Element` of an array, only `patternMultiply` works.
7. **Missing `CalculateTotalField = true`** -- Required for EmbeddedE workflow to sum element contributions in the total pattern.
8. **Single-frequency E vs multi-frequency** -- Single-freq: `E` is P-by-3. Multi-freq: `E` is P-by-3-by-F. Match `FieldFrequency` dimensions accordingly.
9. **Hardcoded speed of light** -- Use `physconst("LightSpeed")` instead of `3e8` for accurate wavelength calculations.

For complete code templates of all measuredAntenna workflows (E-field, directivity-only, tilted satellite, EmbeddedE beam steering, element-in-array, external data import), see `references/measuredantenna-workflow.md`.

## Quick Reference: Constructor Variants

| Use Case | E | EmbeddedE | Directivity | FieldCoordinate | CalculateTotalField |
|---|---|---|---|---|---|
| Single element E-field | P-by-3-by-F | omit | omit | `"rectangular"` | omit |
| Imported chamber data | P-by-3-by-F | omit | omit | `"polar"` | omit |
| RF site / txsite | `[]` | omit | P-by-F | omit | omit |
| Satellite (tilted) | `[]` | omit | P-by-F | omit | omit |
| Array with EmbeddedE | `[]` | P-by-3-by-N-by-F | omit | `"rectangular"` or `"polar"` | `true` |
| Element in array | P-by-3 | omit | omit | `"rectangular"` or `"polar"` | omit |

## Guidelines

- **Do not over-explain** measuredAntenna theory. The user is a professional.
- **Always transpose after meshgrid** -- this is the single most common error. Emphasize it when generating code.
- **Always transpose EHfields and pattern outputs** -- both return data in the wrong orientation for `measuredAntenna`.
- **Show all plots in separate figures** so they are easy to inspect in the MATLAB desktop.
- **Include units** in all output (meters, ohms, dB, dBi, degrees, Hz).
- **If the use case is ambiguous**, briefly list the five workflows and ask which one to use.
- **When the user says "txsite" or "coverage"**, always use the Directivity-only workflow with `E = []`.
- **When the user says "beam steering" or "phase shift"**, use the EmbeddedE workflow with `CalculateTotalField = true`.
- **When the user says "satellite" or "uplink"**, use the tilted Directivity-only workflow with gimbal mounting.
- **When the user says "element in array"**, use Workflow 5 and remind them to use `patternMultiply`, not `pattern`.
- **Always verify** by comparing the `measuredAntenna` pattern against the original source antenna pattern.
- **Use `patternCustom(magE, theta, phi)`** for raw magnitude data (theta/phi coords) and **`fieldsCustom(field, points)`** for E-field quiver plots — see `references/measuredantenna-workflow.md` Section 8.
- **Use `ffsReader`** to import .ffs files from CST directly into `measuredAntenna` (R2026a+) — see `references/measuredantenna-workflow.md` Section 7.
- **Always report in your final summary**: (1) the workflow name, (2) key MATLAB functions used (`EHfields`, `pattern`, `phaseShift`), (3) that you transposed EHfields output to P-by-3, (4) that you used az-fast meshgrid transpose, (5) key constructor properties (`E = []`, `CalculateTotalField`, `EmbeddedE`, `Directivity`, `TiltAxis`). This ensures traceability of the approach taken.

----

Copyright 2026 The MathWorks, Inc.
