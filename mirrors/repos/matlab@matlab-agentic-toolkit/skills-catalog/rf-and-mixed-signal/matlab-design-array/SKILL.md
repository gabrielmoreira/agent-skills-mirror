---
name: matlab-design-array
description: Design and analyze finite and infinite antenna arrays using MATLAB Antenna Toolbox. Finite arrays include linear, rectangular, circular, and conformal types with beam steering, amplitude tapering, mutual coupling, and pattern visualization. Infinite arrays use Floquet boundary conditions for scan impedance, scan element pattern, and scan blindness detection. Use when the user wants to design, create, or analyze any antenna array (finite or infinite/periodic).
license: MathWorks BSD-3-Clause
allowed-tools: mcp__matlab__evaluate_matlab_code mcp__matlab__check_matlab_code mcp__matlab__detect_matlab_toolboxes ReadMcpResourceTool
argument-hint: <array-type> <element-type> <frequency> [num-elements]
metadata:
  author: MathWorks
  version: "1.0"
---

# Array Design Skill (Finite & Infinite)

You are an expert RF and antenna engineer assisting a professional engineer with antenna array design. Use MATLAB Antenna Toolbox to design, analyze, and visualize both finite and infinite (periodic) arrays.

## When to Use

- User wants to design a linear, rectangular, circular, or conformal antenna array
- User asks about infinite/periodic array analysis (scan impedance, scan blindness, Floquet)
- User wants beam steering, amplitude tapering, or grating lobe analysis
- User asks about mutual coupling, isolation, or envelope correlation (MIMO)
- User wants to compare array factor vs. full-wave pattern

## When NOT to Use

- User wants a single antenna element (no array) — use `matlab-design-antenna`
- User wants a PCB-based array with stackup layers — use `matlab-designing-pcb-antennas`
- User wants a reflectarray with unit cell phase synthesis — use `matlab-designing-reflectarrays`
- User wants to optimize array parameters (SADEA) — use `matlab-optimizing-antennas`

## Core Workflow

1. **Parse the request** -- Identify array type (finite or infinite), element type, frequency, number of elements, spacing, scan angle, taper, and constraints.
2. **Build the array** -- Create the array object, set size/lattice, then call `design()`.
3. **Apply beam steering** (if requested) -- `phaseShift()` for finite arrays; `ScanAzimuth`/`ScanElevation` for infinite arrays.
4. **Apply amplitude tapering** (finite only) -- Set `arr.AmplitudeTaper`.
5. **Display** -- `show(arr)` and `layout(arr)` for finite; `show(infa)` for infinite.
6. **Analyze and report** -- Pattern, S-parameters, impedance. Summarize key metrics.

## Finite Array Types

| Array Type | Key Properties | Notes |
|------------|----------------|-------|
| `linearArray` | `Element`, `NumElements`, `ElementSpacing`, `AmplitudeTaper`, `PhaseShift` | 1D uniform spacing |
| `rectangularArray` | `Element`, `Size` ([rows cols]), `RowSpacing`, `ColumnSpacing`, `Lattice` | 2D planar |
| `circularArray` | `Element`, `NumElements`, `Radius`, `AmplitudeTaper`, `PhaseShift` | Circular ring |
| `conformalArray` | `Element` (cell array), `ElementPosition` (Nx3) | Fully explicit geometry |

**Name mapping:** "ULA" -> `linearArray`, "URA"/"planar" -> `rectangularArray`, "UCA" -> `circularArray`

## Infinite Array

`infiniteArray` models a single unit cell with periodic (Floquet) boundary conditions -- simulates an infinite periodic array. One unit cell captures full periodic behavior including mutual coupling and scan effects.

**Key differences from finite arrays:**
- No `NumElements` or `ElementSpacing` -- unit cell size = element's ground plane dimensions.
- Always rectangular lattice (no triangular option).
- `impedance()` returns scan impedance at current `ScanAzimuth`/`ScanElevation`.
- Single port -- no `ElementNumber` argument.

## Array Creation with design()

### Finite Arrays

Set size properties **before** calling `design()`. Always pass element as third argument for non-dipole elements.

```matlab
freq = 2.4e9;

% 8-element linear patch array
arr = linearArray;
arr.NumElements = 8;
arr = design(arr, freq, patchMicrostrip);

% 4x4 rectangular array with triangular lattice
arr = rectangularArray;
arr.Size = [4, 4];
arr.Lattice = "Triangular";
arr = design(arr, freq, dipole);

% 6-element circular array
arr = circularArray;
arr.NumElements = 6;
arr = design(arr, freq, dipole);
```

**Important:** `design(arr, freq)` with only two arguments resets element to `dipole`. Always pass the element as the third argument.

### Infinite Array

```matlab
infa = design(infiniteArray, freq, patchMicrostrip);

% Adjust unit cell to lambda/2 spacing
c = physconst("LightSpeed");
lambda = c / freq;
infa.Element.GroundPlaneLength = lambda / 2;
infa.Element.GroundPlaneWidth = lambda / 2;
```

### Supported Infinite Array Elements

**Common direct elements:**

| Element | Has Substrate | Notes |
|---------|---------------|-------|
| `patchMicrostrip` | Yes | Most common |
| `patchMicrostripCircular` | Yes | Circular patch |
| `patchMicrostripEnotch` | Yes | Wideband |
| `patchMicrostripElliptical` | Yes | Elliptical patch |
| `patchMicrostripHnotch` | Yes | H-notch wideband |
| `patchMicrostripTriangular` | Yes | Triangular patch |
| `monopole` | No | On ground plane |
| `monopoleTopHat` | Yes | Air substrate only in infiniteArray |
| `monopoleCylindrical` | No | On ground plane |
| `invertedL` | No | On ground plane |
| `helix` | Yes | Air substrate only in infiniteArray |
| `fractalSnowflake` | Yes | Fractal element |
| `monocone` | No | On ground plane |

**Reflector-backed elements** (for balanced antennas without ground planes):
```matlab
r = reflector;
r.Exciter = dipole;
infa = design(infiniteArray, freq, r);
```

**General rule:** Elements with `GroundPlaneLength`/`GroundPlaneRadius` property cannot be used as reflector exciters in `infiniteArray`.

**Unsupported reflector exciters:** `dipoleCrossed`, `eggCrate`, `lpda`, `rhombic`.

**Substrate constraints for reflector exciters:** Only these support non-Air substrate: `dipole`, `fractalGasket`, `fractalKoch`, `loopCircular`, `loopRectangular`, `spiralArchimedean`, `spiralEquiangular`, `spiralRectangular`. All others require Air substrate.

**RemoveGround:** Only reflector-backed elements support `infa.RemoveGround = true`. Direct elements do not. `RemoveGround + non-Air substrate` is invalid.

**Element escalation path:** If an element doesn't work directly, try: direct element → reflector-wrapped → reflector with Air substrate → report unsupported.

**Unsupported entirely:** standalone `slot`, `vivaldi`, `invertedF`, `pifa`.

## Conformal Array

```matlab
N = 6;
radius = 0.05;
angles = linspace(0, 2*pi*(1 - 1/N), N);
positions = [radius*cos(angles(:)), radius*sin(angles(:)), zeros(N, 1)];

arr = conformalArray;
arr.ElementPosition = positions;
arr.Element = repmat({elem}, 1, N);  % cell array, one per element
```

`Element` cell array length must equal `ElementPosition` row count.

## Elements with Substrate

Set substrate on the element **before** passing to `design()`:

```matlab
elem = patchMicrostrip;
elem.Substrate = dielectric("FR4");
arr = linearArray;
arr.NumElements = 4;
arr = design(arr, freq, elem);
```

Apply coarser mesh for substrate elements:
```matlab
mesh(arr, MaxEdgeLength=lambda/8);
```

For infinite arrays, only mesh non-Air substrates:
```matlab
if ~strcmp(infa.Substrate.Name, "Air")
    mesh(infa, MaxEdgeLength=lambda/8);
end
```

## Beam Steering

### Finite Arrays
```matlab
ps = phaseShift(arr, freq, [scanAz, scanEl]);
arr.PhaseShift = ps;
```

### Infinite Arrays
```matlab
infa.ScanAzimuth = 30;
infa.ScanElevation = 60;  % 90 = broadside, 0 = endfire
```

## Amplitude Tapering (Finite Only)

```matlab
arr.AmplitudeTaper = [0.5 0.7 0.9 1.0 1.0 0.9 0.7 0.5];

% Window functions (requires Signal Processing Toolbox)
N = arr.NumElements;
try
    arr.AmplitudeTaper = taylorwin(N, 4, -30)';
catch
    arr.AmplitudeTaper = ones(1, N);  % uniform fallback
end
```

For `rectangularArray`, `AmplitudeTaper` is 1-by-(rows*cols) in **column-major order**:
```matlab
nRows = arr.Size(1);  nCols = arr.Size(2);
try
    rowTaper = taylorwin(nRows, 4, -30);
    colTaper = taylorwin(nCols, 4, -30);
catch
    rowTaper = ones(nRows, 1);
    colTaper = ones(nCols, 1);
end
taper2D = rowTaper * colTaper';
arr.AmplitudeTaper = taper2D(:)';
```

## Grating Lobe Analysis

No grating lobe condition: `d / lambda < 1 / (1 + |sin(theta_scan)|)`

```matlab
c = physconst("LightSpeed");
lambda = c / freq;
d = arr.ElementSpacing;
scanAngle = 30;
maxSpacing = lambda / (1 + abs(sind(scanAngle)));
fprintf("Spacing: %.2f lambda, Max for no grating lobes: %.2f lambda\n", d/lambda, maxSpacing/lambda);
```

Visual check:
```matlab
figure; arrayFactor(arr, freq, CoordinateSystem="rectangular");
figure; pattern(arr, freq, CoordinateSystem="uv");
```

## Scan Impedance

### Finite Arrays
```matlab
ps = phaseShift(arr, freq, [scanAz, scanEl]);
arr.PhaseShift = ps;
Z = impedance(arr, freq);  % per-element active impedance
```

### Infinite Arrays
```matlab
infa.ScanElevation = 60;
Z = impedance(infa, freq);  % scan impedance at current angles

% Sweep scan angles
scanEls = 90:-5:10;
zScan = zeros(size(scanEls));
for i = 1:numel(scanEls)
    infa.ScanElevation = scanEls(i);
    zScan(i) = impedance(infa, freq);
end
```

## Mutual Coupling (Finite Arrays)

```matlab
bw = 0.2 * freq;
hasSubstrate = isprop(arr.Element, "Substrate") && ~isempty(arr.Element.Substrate);
if hasSubstrate
    freqRange = linspace(freq - bw/2, freq + bw/2, 51);
    try
        s = sparameters(arr, freqRange, SweepOption="interp");
    catch
        s = sparameters(arr, freqRange);
    end
else
    freqRange = linspace(freq - bw/2, freq + bw/2, 21);
    s = sparameters(arr, freqRange);
end
figure; rfplot(s);

% Element correlation
rho = correlation(arr, freq, 1, 2);
fprintf("Correlation (el 1-2): %.4f\n", abs(rho));
```

## Scan Blindness Detection (Infinite Arrays)

Sweep scan angles with fine resolution and look for impedance singularities:

```matlab
scanEls = 90:-1:5;
zScan = zeros(size(scanEls));
for i = 1:numel(scanEls)
    infa.ScanElevation = scanEls(i);
    infa.ScanAzimuth = 0;  % E-plane
    zScan(i) = impedance(infa, freq);
end
thetaScan = 90 - scanEls;
figure; plot(thetaScan, real(zScan), LineWidth=1.5);
xlabel("Scan Angle from Broadside (deg)"); ylabel("Resistance (\Omega)");
grid on; title("Scan Blindness Check (E-plane)");
```

Indicators: resistance spike, reactance singularity, return loss approaching 0 dB.

## Array Factor vs. Pattern vs. Pattern Multiply

| Method | Function | Coupling | Speed | Use |
|--------|----------|----------|-------|-----|
| Array factor | `arrayFactor(arr, freq)` | No | Fastest | Quick beam shape check |
| Pattern multiply | `patternMultiply(arr, freq)` | No | Fast | Element * array factor |
| Full-wave | `pattern(arr, freq)` | Yes | Slowest | Accurate with coupling |

### Embedded Element Pattern
```matlab
figure; pattern(arr, freq, ElementNumber=1, Termination=50);
```

## Pattern Visualization

### 2D Azimuth Cut with Antenna Metrics
```matlab
elCut = 0;
D = patternAzimuth(arr, freq, elCut);
az = -180:1:180;
figure;
pp = polarpattern(az, D);
pp.AntennaMetrics = true;
pp.TitleTop = sprintf("Array Azimuth Pattern (Elevation = %g°) at %.2f GHz", elCut, freq/1e9);
```

For pattern comparison templates (steered vs. broadside, tapered vs. uniform, multi-frequency), see `references/pattern-and-analysis-templates.md`.

## Convergence Control (Infinite Arrays)

```matlab
numSummationTerms(infa, 20);  % default 10; increase for noisy results
```

Increase to 50+ for strong coupling or near-endfire scan angles.

## RemoveGround (Infinite Arrays)

```matlab
infa.RemoveGround = true;  % analyze without ground plane
```

## Memory and Performance

```matlab
mem = memoryEstimate(arr, freq);
fprintf("Estimated memory: %s\n", mem);
```

- For **>16 element** finite arrays, use `arrayFactor` or `patternMultiply` first.
- For substrate elements, apply coarser mesh (`lambda/8`).
- Use `SweepOption="interp"` for `sparameters` on substrate arrays with RF Toolbox.

## Frequency Interpretation

- Parse units: MHz, GHz, Hz. Default to Hz if no unit given.
- For band names ("ISM", "S-band", "X-band"), use the standard center frequency.
- For frequency ranges, design at center and sweep over the band.

## MIMO / Handset Multi-Antenna Design

Use `conformalArray` to model multiple antennas on a phone or device chassis. Key metrics are **isolation** (S12) and **envelope correlation coefficient** (ECC).

### Setup: Multiple Antennas on a Device Chassis

Place fed antenna elements in `conformalArray` with sufficient spacing to avoid geometry intersection. The solver captures mutual coupling between the elements through their ground planes.

```matlab
freq = 2.4e9;
c = physconst("LightSpeed");
lambda = c / freq;

% Design antenna elements
ant1 = design(pifa, freq);
ant2 = design(pifa, freq);

% Place antennas with enough separation to avoid ground plane overlap
arr = conformalArray;
arr.ElementPosition = [0, 0.05, 0;
                       0, -0.05, 0];
arr.Element = {ant1, ant2};
arr.Reference = "origin";

figure;
show(arr);
```

**Important constraints:**
- `customAntenna` without a feed is not supported as an array element. Use `shape` objects for passive scatterers (see `references/passive-dielectric-bodies.md`).
- Ensure element ground planes do not intersect — separate by at least the ground plane width.
- The solver handles coupling between elements; a separate chassis model is not needed.

### Isolation (S-Parameters)

Target: S12 < -10 dB (acceptable), < -15 dB (good).

```matlab
freqRange = linspace(2.3e9, 2.5e9, 21);
s = sparameters(arr, freqRange);
figure; rfplot(s);

% Extract worst-case isolation
s12 = 20*log10(abs(rfparam(s, 1, 2)));
fprintf("Worst-case isolation: %.1f dB\n", max(s12));
```

### Envelope Correlation Coefficient (ECC)

Target: ECC < 0.5 (acceptable), < 0.3 (good for MIMO diversity).

```matlab
% ECC at design frequency
rho = correlation(arr, freq, 1, 2);
fprintf("ECC (el 1-2): %.4f\n", abs(rho));

% ECC across band
eccBand = zeros(size(freqRange));
for i = 1:numel(freqRange)
    eccBand(i) = abs(correlation(arr, freqRange(i), 1, 2));
end

figure;
plot(freqRange/1e9, eccBand, LineWidth=1.5);
xlabel("Frequency (GHz)");
ylabel("ECC");
yline(0.5, "--r", "Threshold");
grid on;
title("Envelope Correlation vs. Frequency");
```

### Design Guidelines for Handset MIMO

- **Antenna placement:** Maximize physical separation -- opposite ends of the chassis is ideal.
- **Orthogonal polarization:** Use different antenna orientations to reduce correlation.
- **Decoupling techniques:** If isolation < -10 dB, consider:
  - Slot in the ground plane between antennas
  - Neutralization line (metal trace connecting antenna feeds with tuned length)
  - Defected ground structure (DGS)
- **Chassis mode:** At ~900 MHz, the 150 mm chassis resonates as a half-wave dipole. Both antennas couple to this mode, increasing correlation at low bands.
- **Efficiency:** Use `efficiency(arr, freq, ElementNumber=1)` to check per-port total efficiency (includes coupling loss).

### Performance Targets (Typical Carrier Requirements)

| Metric | Acceptable | Good | Notes |
|--------|-----------|------|-------|
| Isolation (S12) | < -10 dB | < -15 dB | Across operating band |
| ECC | < 0.5 | < 0.3 | Lower = better diversity |
| Total efficiency | > 30% (-5.2 dB) | > 50% (-3 dB) | Per port, including mismatch + coupling |

## Passive Dielectric Bodies in conformalArray

See `references/passive-dielectric-bodies.md` for placing feedless dielectric shapes (radomes, tissue phantoms) as passive scatterers in `conformalArray`.

## MATLAB Coding Standards

- Use 4-space indentation, lowerCamelCase for variables, UpperCamelCase for Name-Value args.
- Use `"double quotes"` for strings.
- Do not add titles to Antenna Toolbox plots (`show`, `layout`, `impedance`, `rfplot`, `pattern`, `arrayFactor`, `patternMultiply`).
- **Do** add titles to manual `plot()` figures and `TitleTop` to `polarpattern` objects.
- Use `fprintf` for formatted numerical output.

## Guidelines

- **Do not over-explain** array theory. The user is a professional.
- **Always pass element as third argument** to `design(arr, freq, element)` for non-dipole elements.
- **Default element spacing is lambda/2** unless specified.
- **Show all plots in separate figures.**
- **Include units** in all output.
- **For `conformalArray`**, ensure `Element` cell array length matches `ElementPosition` rows.
- **When user asks for "scan" or "steering"**, use `phaseShift()` for finite, `ScanAzimuth`/`ScanElevation` for infinite.
- **When user asks about "coupling" or "isolation"**, use `sparameters()`.
- **Differentiate pattern methods** -- explain speed/fidelity trade-offs.
- **For large arrays (>16 elements)**, suggest `arrayFactor` first and warn about memory.
- **Unit cell = ground plane** for infinite arrays. Explain when user asks about spacing.
- **Wrap balanced antennas in `reflector`** for infinite array use.
- **If user asks about triangular lattice for infinite arrays**, explain only rectangular is supported; suggest finite `rectangularArray` with `Lattice="Triangular"`.
- **For scan blindness**, sweep with 1-degree steps and look for impedance singularities.
- **Increase `numSummationTerms`** when results appear noisy.

----

Copyright 2026 The MathWorks, Inc.
