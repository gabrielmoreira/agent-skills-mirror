---
name: matlab-design-reflector-antenna
description: Design and analyze curved reflector antennas using MATLAB Antenna Toolbox. Covers parabolic dishes (prime-focus, Cassegrain, Gregorian), offset dual-reflector configurations, corner reflectors, cylindrical and spherical reflectors, and custom dual-reflector surfaces. Includes exciter selection, f/D ratio design, solver selection (MoM-PO, PO, MoM, FMM), feed offset, and pattern analysis. Use when the user wants to design a dish antenna, parabolic reflector, Cassegrain, Gregorian, corner reflector, or any curved reflector structure.
license: MathWorks BSD-3-Clause
allowed-tools: mcp__matlab__evaluate_matlab_code mcp__matlab__check_matlab_code mcp__matlab__detect_matlab_toolboxes ReadMcpResourceTool
argument-hint: <reflector-type> <frequency> [exciter-type]
metadata:
  author: MathWorks
  version: "1.0"
---

# Reflector Antenna Design Skill

You are an expert RF and antenna engineer assisting a professional engineer with reflector antenna design. Use MATLAB Antenna Toolbox to design, analyze, and visualize curved reflector antennas including parabolic dishes, dual-reflector systems, corner reflectors, and custom reflector geometries.

**Scope:** This skill covers curved/shaped reflector structures. The flat `reflector` (backing structure for dipoles) is a catalog element covered by the general antenna design skill.

## When to Use

- User wants to design a parabolic dish, satellite dish, or prime-focus reflector
- User wants a Cassegrain or Gregorian dual-reflector system
- User wants an offset-fed reflector (no blockage)
- User wants a corner reflector antenna
- User wants to use reflectorCalculator for trade studies
- User asks about f/D ratio, aperture efficiency, or feed illumination taper

## When NOT to Use

- User wants a flat reflector backing a dipole — use `matlab-design-antenna` (catalog `reflector`)
- User wants a reflectarray with unit cells — use `matlab-design-reflectarray`
- User wants a PCB antenna — use `matlab-design-pcb-antenna`
- User wants to optimize reflector dimensions — use `matlab-optimize-antenna`

## Core Workflow

1. **Parse the request** -- Identify reflector type, operating frequency, exciter type, aperture size, f/D ratio, and constraints (offset feed, scan angle, polarization).
2. **Create the reflector** -- Set exciter first (if non-default), then call `design()`.
3. **Analyze** -- Pattern, gain, beamwidth, impedance, sidelobe level.
4. **Solver selection** -- Choose MoM-PO (default), PO, MoM, or FMM based on electrical size.
5. **Present results** -- Summarize key metrics with units.

## Reflector Types

| Type | Description | Default Exciter | Solver |
|------|-------------|-----------------|--------|
| `reflectorParabolic` | Prime-focus parabolic dish | `dipole` | MoM-PO |
| `cassegrain` | Symmetric dual-reflector (hyperbolic sub) | `hornConical` | MoM-PO |
| `gregorian` | Symmetric dual-reflector (ellipsoidal sub) | `hornConical` | MoM-PO |
| `cassegrainOffset` | Offset Cassegrain (no blockage) | `hornConical` | MoM-PO |
| `gregorianOffset` | Offset Gregorian (no blockage) | `hornConical` | MoM-PO |
| `reflectorCorner` | Corner reflector (directional) | `dipole` | MoM |
| `reflectorCylindrical` | Cylindrical reflector (fan beam) | `dipole` | MoM |
| `reflectorSpherical` | Spherical reflector (wide scan) | `dipole` | MoM-PO |
| `customDualReflectors` | Custom surface geometry | `hornConical` | MoM-PO |

**Name mapping:**
- "dish antenna" / "parabolic dish" / "satellite dish" --> `reflectorParabolic`
- "Cassegrain" / "dual reflector" --> `cassegrain` or `cassegrainOffset`
- "Gregorian" --> `gregorian` or `gregorianOffset`
- "corner reflector" --> `reflectorCorner`
- "offset feed" / "no blockage" --> `cassegrainOffset` or `gregorianOffset`
- "shaped reflector" / "custom surface" --> `customDualReflectors`

## Creating Reflector Antennas

### design() for Reflectors

Reflector antennas use `design(obj, freq)` with **two arguments only**. Set the exciter on the object before calling `design()`:

```matlab
freq = 10e9;

% Default exciter (dipole for parabolic)
rp = design(reflectorParabolic, freq);

% Custom exciter -- set BEFORE design
rp = reflectorParabolic;
rp.Exciter = hornConical;
rp = design(rp, freq);
```

**Important:** Unlike finite arrays, `design()` for reflectors does NOT accept a third element argument. Always set `Exciter` property first.

### Supported Exciters

| Exciter | Works With | Notes |
|---------|-----------|-------|
| `dipole` | All reflectors | Simple, linearly polarized |
| `horn` | Parabolic, dual-reflectors | Rectangular horn |
| `hornConical` | All except corner/cylindrical | Best for dishes (circular symmetry) |
| `helix` | Parabolic, spherical | Circular polarization |
| `spiralArchimedean` | Parabolic, spherical | Wideband CP |
| `vivaldi` | Parabolic | Wideband, linear pol |
| `patchMicrostrip` | Parabolic | Compact feed |
| `cavity` | **NOT supported** | Cannot be set as Exciter |

For dual-reflector systems (Cassegrain/Gregorian), `hornConical` is the standard choice -- it provides symmetric illumination with controlled beamwidth.

## Workflow 1: Prime-Focus Parabolic Dish

The most common reflector antenna. Key parameter is the f/D ratio.

```matlab
freq = 10e9;
c = physconst("LightSpeed");
lambda = c / freq;

% Design with default dipole exciter
rp = design(reflectorParabolic, freq);
figure; show(rp);
figure; pattern(rp, freq);

% Key dimensions
fprintf("Radius: %.4f m (%.1f lambda)\n", rp.Radius, rp.Radius/lambda);
fprintf("Focal length: %.4f m\n", rp.FocalLength);
fprintf("f/D ratio: %.2f\n", rp.FocalLength / (2*rp.Radius));
fprintf("Aperture diameter: %.4f m (%.1f lambda)\n", 2*rp.Radius, 2*rp.Radius/lambda);
```

### With Horn Exciter (Higher Gain)

```matlab
freq = 10e9;

rp = reflectorParabolic;
rp.Exciter = hornConical;
rp = design(rp, freq);

figure; show(rp);
figure; pattern(rp, freq);

% Beamwidth
[bw, angles] = beamwidth(rp, freq, 0, 1:360);
fprintf("3-dB beamwidth: %.1f deg\n", bw);
```

### Custom f/D Ratio

```matlab
freq = 12e9;
c = physconst("LightSpeed");
lambda = c / freq;

rp = reflectorParabolic;
rp.Exciter = hornConical;
rp.Radius = 10 * lambda;           % 10-lambda aperture radius
rp.FocalLength = 10 * lambda;      % f/D = 0.5
rp.FeedOffset = [0 0 0];

figure; show(rp);
figure; pattern(rp, freq);
```

## Workflow 2: Cassegrain and Gregorian (Symmetric Dual-Reflector)

```matlab
freq = 10e9;

% Cassegrain (hyperbolic subreflector) -- shorter, common for large dishes
cass = design(cassegrain, freq);
figure; show(cass);
figure; pattern(cass, freq);
fprintf("Main radius: %.4f m, Sub radius: %.4f m\n", cass.Radius(1), cass.Radius(2));

% Gregorian (ellipsoidal subreflector) -- lower cross-pol, slightly longer
greg = design(gregorian, freq);
figure; show(greg);
figure; pattern(greg, freq);
```

Both use `hornConical` as default exciter. Properties: `Radius` (1-by-2), `FocalLength` (1-by-2).

## Workflow 3: Offset Dual-Reflector (No Feed Blockage)

Offset configurations eliminate aperture blockage, improving efficiency and reducing sidelobes.

```matlab
freq = 10e9;

co = design(cassegrainOffset, freq);
figure; show(co);
figure; pattern(co, freq);
fprintf("Offset: %.4f m, InterAxialAngle: %.1f deg\n", co.MainReflectorOffset, co.InterAxialAngle);

% Offset Gregorian
go = design(gregorianOffset, freq);
figure; show(go);
```

**Offset-specific properties:** `MainReflectorOffset`, `InterAxialAngle`, `DualReflectorSpacing`, `ReflectorTilt` ([main, sub] angles).

## Workflow 4: Corner Reflector

Two conducting planes at an angle. Corner angle determines gain.

| Corner Angle | Image Sources | Approx. Gain |
|---|---|---|
| 90 | 3 (total 4) | ~10 dBi |
| 60 | 5 (total 6) | ~12 dBi |
| 45 | 7 (total 8) | ~13 dBi |

```matlab
freq = 1e9;
rc = design(reflectorCorner, freq);
rc.CornerAngle = 90;
figure; show(rc);
figure; pattern(rc, freq);
fprintf("Corner angle: %d deg, Spacing: %.4f m\n", rc.CornerAngle, rc.Spacing);
```

## Workflow 5: Cylindrical and Spherical Reflectors

```matlab
freq = 1e9;

% Cylindrical -- fan beam (narrow in one plane, wide in other)
% Properties: GroundPlaneLength, GroundPlaneWidth, Spacing, Depth, EnableProbeFeed, Conductor
rcyl = design(reflectorCylindrical, freq);
figure; show(rcyl);
figure; pattern(rcyl, freq);

% Spherical -- wide-angle scanning by moving the feed
% Properties: Radius, Depth, FeedOffset ([0 0 0.075] default), SolverType
rs = design(reflectorSpherical, freq);
figure; show(rs);
figure; pattern(rs, freq);
fprintf("Radius: %.4f m, Depth: %.4f m\n", rs.Radius, rs.Depth);
```

## Using an Array as Exciter

Any array object (`linearArray`, `circularArray`, etc.) can be assigned as the `Exciter` for a reflector. Design the array first, then assign it -- do NOT call `design()` on the reflector afterward.

```matlab
freq = 10e9;
c = physconst("LightSpeed");
lambda = c / freq;

% Design the array exciter first
arr = circularArray;
arr.NumElements = 4;
arr.Element = spiralArchimedean;
arr = design(arr, freq);

% Assign to reflector (set dimensions manually -- no design() on reflector)
rp = reflectorParabolic;
rp.Exciter = arr;
rp.Radius = 5*lambda;
rp.FocalLength = 5*lambda;   % f/D = 0.5

figure; show(rp);
figure; pattern(rp, freq);
```

Works with all reflector types:
```matlab
% Corner reflector with linear array of invertedF
rc = reflectorCorner;
rc.Exciter = design(linearArray, freq, invertedF);
rc.GroundPlaneWidth = 2*lambda;
rc.Spacing = 0.25*lambda;
figure; show(rc);
```

### EnableProbeFeed (Cylindrical Reflector)

`reflectorCylindrical` has an `EnableProbeFeed` property that changes the feed mechanism from a standalone exciter to a probe feed through the reflector surface:

```matlab
rcyl = design(reflectorCylindrical, freq);
rcyl.EnableProbeFeed = true;
figure; show(rcyl);
figure; pattern(rcyl, freq);
```

## Workflow 6: Custom Reflector Surfaces from STL Files

Import arbitrary reflector geometry from STL files using `stlread` and assign to `customDualReflectors`. This works for single-reflector setups (only `MainReflector` needed) or dual-reflector configurations.

### Single Custom Reflector from STL

```matlab
freq = 2e9;
c = physconst("LightSpeed");
lambda = c / freq;

% Load STL as triangulation object
tri = stlread("MyCustomReflector.stl");

% Create reflector with custom surface
cdr = customDualReflectors;
cdr.MainReflector = tri;
cdr.Exciter = dipole(Length=0.15, Width=0.015, Tilt=90, TiltAxis=[0 1 0]);
cdr.FeedOffset = [0 0 0.05];          % exciter position relative to reflector
cdr.RemeshReflectors = true;           % re-mesh imported surface for solver

figure; show(cdr);
figure; pattern(cdr, freq);
```

### Dual Custom Reflectors from STL

```matlab
freq = 10e9;

mainTri = stlread("main_reflector.stl");
subTri = stlread("sub_reflector.stl");

cdr = customDualReflectors;
cdr.MainReflector = mainTri;
cdr.SubReflector = subTri;
cdr.Exciter = hornConical;
cdr.ReflectorOffset = [0 0 0; 0 0 0.1];
cdr.FeedOffset = [0 0 0.15];

figure; show(cdr);
figure; pattern(cdr, freq);
```

### Optimizing Exciter Position on Custom Reflector

To optimize the exciter location on a custom STL reflector without moving the reflector itself, vary `FeedOffset` using SADEA optimization (see `matlab-optimize-antenna`):

```matlab
freq = 2e9;
tri = stlread("MyCustomReflector.stl");

% Define evaluation function that sweeps FeedOffset
evalFcn = @(params) evaluateReflector(params, tri, freq);

% Use SADEA to optimize exciter position
% Optimization variables: FeedOffset [x, y, z]
% See matlab-optimize-antenna skill for full SADEA setup
```

**Properties:**
- `MainReflector`: N-by-3 matrix or triangulation object (from `stlread`)
- `SubReflector`: N-by-3 matrix or triangulation object (optional for single-reflector)
- `ReflectorOffset`: 2-by-3 matrix [main offset; sub offset] — additive translation applied on top of existing coordinates
- `FeedOffset`: 1-by-3 vector — controls exciter position independently of reflector
- `ReflectorTilt`: [main, sub] tilt angles
- `RemeshReflectors`: true/false (re-mesh imported surfaces for better solver accuracy)

### Coordinate System Behavior

`customDualReflectors` **preserves** the coordinate system of the data you assign. If your surfaces are already positioned in a shared global frame, they will display correctly without any offset.

If both reflectors appear overlapping, the issue is in the source data — each surface was likely generated in its own local frame (both centered at origin). In that case, use `ReflectorOffset` to apply the correct relative positioning:

```matlab
% Surfaces generated independently (both at local origin)
cdr = customDualReflectors;
cdr.MainReflector = mainPoints;
cdr.SubReflector = subPoints;

% ReflectorOffset is ADDITIVE — shifts each surface from its current position
cdr.ReflectorOffset = [0 0 0; 0 0 0.3];   % shift sub 0.3m above main
```

If surfaces are already in global coordinates (correct relative positions), do NOT apply `ReflectorOffset` — coordinates are used as-is.

### Alternative: installedAntenna (Non-Reflector Structures)

If your custom geometry is an electrically large scattering structure (e.g., vehicle body, aircraft fuselage) rather than a traditional reflector, use `installedAntenna` instead (see `matlab-analyze-installed-antenna`):

```matlab
ant = installedAntenna;
ant.Platform = platform(FileName="vehicle_body.stl", Units="m");
ant.Element = dipole(Length=0.15, Width=0.015);
ant.ElementPosition = [x y z];    % meters — controls antenna placement
figure; show(ant);
figure; pattern(ant, freq);
```

Use `installedAntenna` when:
- The structure is not shaped to focus energy (not a dish/reflector)
- You need to study antenna placement on a large platform
- You want MoM-PO or FMM solvers for installed performance

## Workflow 7: Reflector Calculator (Gaussian-Beam Analysis)

`reflectorCalculator` (R2026a) provides fast analytical design using Gaussian-beam methods -- no full-wave solve required. Computes efficiency, gain, beamwidth, and sidelobe level instantly.

**See `references/reflectorCalculator.md` for full details** (feed types, single-fed/array-fed/pattern-fed examples, solve output metrics, and bridge to full-wave via `createAntenna`).

Quick usage:

```matlab
freq = 12e9;
rc = reflectorCalculator;
rc.Diameter = 1;
rc.FocalLength = 0.9;
rc.ClearanceHeight = 0.1;
rc.FeedType = "singlefed";
rc.RadiatingElement = "horn";
s = solve(rc, freq);           % returns 18-metric table instantly
ant = createAntenna(rc, freq); % bridge to customDualReflectors for full-wave
```

**When to use:** Trade studies, sizing, feed selection. Then `createAntenna` for full-wave validation with `customDualReflectors`.

## Solver Selection

| Solver | Speed | Accuracy | Best For |
|--------|-------|----------|----------|
| `"MoM-PO"` | Fast | Good | Default for dishes > 5lambda (hybrid full-wave + PO) |
| `"PO"` | Fastest | Approximate | Very large dishes (> 50lambda), quick estimates |
| `"MoM"` | Slowest | Best | Small reflectors (< 5lambda), corner/cylindrical |
| `"FMM"` | Moderate | Good | Large structures where MoM-PO is insufficient |

```matlab
rp.SolverType = "MoM-PO";      % Hybrid (default for parabolic)
rp.SolverType = "PO";          % Physical optics only (fastest)
rp.SolverType = "FMM";         % Fast multipole method
```

**Note:** `reflectorCorner` and `reflectorCylindrical` do NOT have a `SolverType` property -- they always use MoM.

## f/D Ratio Design Guide

The focal-length-to-diameter ratio controls the tradeoff between spillover and illumination efficiency.

| f/D | Subtended Half-Angle | Characteristics |
|-----|---------------------|-----------------|
| 0.25 | 90 | Deep dish, wide feed beamwidth needed, compact |
| 0.35 | 69 | Common compromise |
| 0.50 | 53 | Shallow dish, narrow feed beamwidth, less spillover |
| 0.75 | 37 | Very shallow, minimal spillover, lower illumination |

**Optimal f/D:** Match feed -10 dB beamwidth to dish subtended angle. Use `thetaEdge = 2*atand(1/(4*fOverD))`.

## Feed Offset and Tilt

```matlab
% Beam squint via feed offset (small offsets only -- large offsets cause coma)
rp.FeedOffset = [0.02 0 0];   % 20mm lateral offset
figure; pattern(rp, freq);

% Mechanical steering via tilt
rp.Tilt = 30;
rp.TiltAxis = [0 1 0];   % 30 deg about Y-axis
figure; pattern(rp, freq);
```

For significant beam steering, use offset reflector configurations (`cassegrainOffset`/`gregorianOffset`) rather than feed offset.

## Analysis Functions

All standard Antenna Toolbox analysis functions work on reflector objects: `pattern`, `patternAzimuth`, `patternElevation`, `beamwidth`, `impedance`, `sparameters`, `axialRatio`, `rfplot`. Use `memoryEstimate(rp, freq)` before running large analyses.

**Mesh coarsening for substrate-backed exciters:** After `design()`, apply explicit mesh before analysis:
```matlab
mesh(ant, MaxEdgeLength=lambda/8);
```

**Interpolation sweep for faster frequency sweeps:** When RF Toolbox is available and the exciter has a substrate, use:
```matlab
try
    spar = sparameters(rp, freqRange, SweepOption="interp");
catch
    spar = sparameters(rp, freqRange);
end
```

## Memory and Performance

- **< 5 lambda:** MoM feasible. **5-50 lambda:** MoM-PO (default). **> 50 lambda:** PO or FMM.
- Dual-reflector systems require more memory than single-dish.

## Design Rules of Thumb

| Parameter | Typical Range | Notes |
|-----------|---------------|-------|
| f/D ratio | 0.25 - 0.75 | 0.35-0.5 most common |
| Aperture (D/lambda) | 5 - 100+ | Higher = narrower beam, higher gain |
| Aperture efficiency | 50-70% | Includes spillover + illumination + blockage |
| Feed taper at edge | -10 to -12 dB | Good spillover/illumination compromise |
| Gain (dBi) | ~20*log10(D/lambda) + 8 | Rough estimate for eta=55% |
| Beamwidth (deg) | ~70*lambda/D | Half-power beamwidth estimate |

## MATLAB Coding Standards

- Use 4-space indentation, lowerCamelCase for variables, UpperCamelCase for Name-Value args.
- Use `"double quotes"` for strings. Use `fprintf` for formatted numerical output.
- Do not add titles to Antenna Toolbox plots (`show`, `pattern`, `impedance`, `returnLoss`, `rfplot`). **Do** add titles to manual `plot()` figures.
- Show all plots in separate figures. Include units in all output.

## Guidelines

- **Always set Exciter before design()** -- `design()` only takes two arguments for reflectors.
- **Default feeds:** `hornConical` for parabolic/dual-reflector; `dipole` for corner/cylindrical. `cavity` is NOT valid -- it will error.
- **Keyword mapping:** "dish"/"satellite" → `reflectorParabolic`; "no blockage"/"offset" → `cassegrainOffset`/`gregorianOffset`; "corner reflector" → `reflectorCorner` (90 deg default).
- **Use MoM-PO** as default solver for parabolic/spherical. `reflectorCorner` and `reflectorCylindrical` always use MoM (no `SolverType`).
- **Report f/D ratio** and aperture size in wavelengths. Warn about memory for dishes > 50 lambda.
- **For trade studies**, use `reflectorCalculator` first, then `createAntenna` for full-wave.
- **For custom STL reflectors**, use `stlread` + `customDualReflectors` (only `MainReflector` required). To optimize feed position, vary `FeedOffset` with SADEA. If the STL is a scattering platform, use `installedAntenna` instead.

----

Copyright 2026 The MathWorks, Inc.
