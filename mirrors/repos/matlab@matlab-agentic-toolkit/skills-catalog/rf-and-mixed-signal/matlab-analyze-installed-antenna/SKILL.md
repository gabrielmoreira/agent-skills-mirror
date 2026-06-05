---
name: matlab-analyze-installed-antenna
description: Analyze antennas installed on electrically large conducting platforms using MATLAB Antenna Toolbox. Loads platform geometry from STL/STEP/IGES, installs antenna elements, selects electromagnetic solvers (MoM-PO, FMM, MoM), and computes patterns, impedance, coupling, and efficiency. Use when the user wants to model an antenna on a vehicle, aircraft, ship, satellite, or other large structure.
license: MathWorks BSD-3-Clause
allowed-tools: mcp__matlab__evaluate_matlab_code mcp__matlab__check_matlab_code mcp__matlab__detect_matlab_toolboxes ReadMcpResourceTool
argument-hint: <platform-file> <antenna-type> <frequency>
metadata:
  author: MathWorks
  version: "1.0"
---

# Installed Antenna Skill

You are an expert RF and antenna engineer assisting a professional antenna engineer or RF system designer. Use MATLAB Antenna Toolbox to model and analyze antennas installed on electrically large conducting platforms.

## When to Use

- User wants to mount an antenna on a vehicle, aircraft, ship, satellite, or other large platform
- User asks about installed antenna patterns, coupling, or efficiency on a structure
- User needs to select a solver (MoM-PO, FMM, MoM) for platform-antenna analysis
- User has a CAD file (STL/STEP/IGES) and wants to analyze antenna performance on it

## When NOT to Use

- User wants standalone antenna design (no platform) — use `matlab-design-antenna`
- User wants RCS of the platform — use `matlab-analyze-rcs`
- User wants plane wave excitation on a platform — use `matlab-analyzing-plane-wave-excitation`
- User wants a PCB antenna with stackup — use `matlab-designing-pcb-antennas`

## Core Workflow

1. **Parse the request** -- Identify the platform geometry (STL/STEP/IGES file or default plate), antenna element(s), operating frequency, element positions on the platform, and any solver preference or constraints.

2. **Create the platform** -- Load geometry from a CAD file:
   ```matlab
   plat = platform(FileName="aircraft.stl", Units="m");
   figure;
   show(plat);
   ```

3. **Install the antenna** -- Mount element(s) on the platform:
   ```matlab
   ant = installedAntenna;
   ant.Platform = plat;
   ant.Element = design(dipole, freq);
   ant.ElementPosition = [0 0 0.5];
   ```

4. **Select the solver** -- Choose based on platform electrical size and geometry (see Solver Selection Guide):
   ```matlab
   ant.SolverType = "MoM-PO";
   ```

5. **Mesh and display** -- Generate the mesh and show the installed geometry:
   ```matlab
   c = physconst("LightSpeed");
   lambda = c / freq;
   mesh(ant, MaxEdgeLength=lambda/10);
   figure;
   show(ant);
   ```

6. **Analyze and report** -- Compute pattern, impedance, and other metrics. Summarize key results in a table with units.

## Platform Creation

The `platform` object loads 3D geometry from CAD files for use as the conducting structure.

### Supported File Formats

| Format | Extensions | Units |
|--------|-----------|-------|
| STL | `.stl` | User-configurable via `Units` (default: `"mm"`) |
| STEP | `.step`, `.stp` | Read-only (embedded in file) |
| IGES | `.igs`, `.iges` | Read-only (embedded in file) |

### Platform Units

**The `platform` object defaults to millimeters (`"mm"`), but `ElementPosition` in `installedAntenna` is always in meters.** Mismatched units place the antenna in the wrong location or scale the platform incorrectly. Always set `Units` explicitly when loading STL files:

```matlab
% Correct -- explicit units
plat = platform(FileName="vehicle.stl", Units="m");

% Built-in plate geometry (ships with Antenna Toolbox)
plat = platform(FileName="plate.stl", Units="m");
```

**`platform` requires a `FileName`** -- calling `platform()` with no file and then `show()` or `mesh()` produces an error. Always provide a geometry file. The built-in `"plate.stl"` is available for quick tests.

STEP and IGES files carry their own units, so the `Units` property is read-only for those formats.

### Generating Platform STL Programmatically

When no CAD file exists, generate the platform geometry in MATLAB using `triangulation` + `stlwrite`:

```matlab
% Open-ended metal tube (cylinder without end caps)
radius = 0.05; height = 0.15; nPts = 24;
theta = linspace(0, 2*pi, nPts+1); theta(end) = [];
xBot = radius*cos(theta); yBot = radius*sin(theta);
zBot = -height/2 * ones(size(theta));
xTop = radius*cos(theta); yTop = radius*sin(theta);
zTop = height/2 * ones(size(theta));
verts = [xBot(:), yBot(:), zBot(:); xTop(:), yTop(:), zTop(:)];
faces = [];
for i = 1:nPts
    j = mod(i, nPts) + 1;
    faces = [faces; i, i+nPts, j; j, i+nPts, j+nPts];
end
TR = triangulation(faces, verts);
stlwrite(TR, fullfile(tempdir, "tube.stl"));
plat = platform(FileName=fullfile(tempdir, "tube.stl"), Units="m");
```

For plates, boxes, and mesh quality tips, see `references/programmatic-stl-generation.md`.

### Using the STL Mesh Directly

By default, `platform` remeshes the imported geometry. To skip remeshing and use the STL triangulation as-is (useful when the file comes from a dedicated mesh generator):

```matlab
plat = platform(FileName="premeshed_body.stl", Units="m");
plat.UseFileAsMesh = true;
```

### Platform Tilt

Rotate the platform orientation before installing antennas:

```matlab
plat.Tilt = 90;
plat.TiltAxis = "Y";
```

## Element Installation

### installedAntenna Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Platform` | `platform` object | rectangular plate | Conducting structure |
| `Element` | antenna, array, or cell array | `dipole` | Antenna element(s) to install |
| `ElementPosition` | N-by-3 matrix (meters) | `[0 0 0.075]` | [x, y, z] per element |
| `Reference` | `"feed"` or `"origin"` | `"feed"` | Position reference point |
| `FeedVoltage` | scalar or vector (V) | 1 | Excitation amplitude per element |
| `FeedPhase` | scalar or vector (deg) | 0 | Excitation phase per element |
| `Tilt` | scalar or vector (deg) | 0 | Element rotation angle |
| `TiltAxis` | vector, matrix, or string | `[1 0 0]` | Element rotation axis |
| `SolverType` | string | `"MoM-PO"` | `"MoM-PO"`, `"MoM"`, or `"FMM"` |

### Substrate Limitation

**`installedAntenna` only supports pure metal antennas.** Antennas with a dielectric substrate other than air are **not supported** as elements. This means you cannot install a `patchMicrostrip` with FR4 or Teflon substrate on a platform.

Use metal-only antenna types:
- Wire: `dipole`, `monopole`, `dipoleFolded`, `dipoleMeander`, `invertedF`, `invertedL`, etc.
- Horn: `horn`, `hornConical`, `hornCorrugated`, `hornPotter`, `hornScrimp`
- Spiral/helix: `spiralArchimedean`, `spiralEquiangular`, `helix`
- Slot: `slot`, `vivaldi`
- Loop: `loopCircular`, `loopRectangular`
- Cone: `bicone`, `discone`, `monocone`
- Waveguide: `waveguide`, `waveguideCircular`
- Arrays of the above: `linearArray`, `rectangularArray`, `circularArray`

If the user requests a substrate-based antenna on a platform, explain the limitation and suggest either a metal-only alternative or the `conformalArray` workaround below.

### Alternative for Substrate Elements: conformalArray

When you need to analyze a substrate-backed antenna (e.g., `pcbStack` with FR4) on a platform, use `conformalArray` instead of `installedAntenna`. Model the platform as a separate element and place both the antenna and platform geometry in a `conformalArray`:

```matlab
freq = 2.4e9;

% 1. Design the PCB antenna element (with substrate)
ant = design(patchMicrostrip, freq);

% 2. Model the phone chassis as a custom metal plate with a feed
chassis = customAntenna(Shape=shape.Rectangle(Length=0.14, Width=0.07));
createFeed(chassis, [0 0 0], 1);

% 3. Place both in a conformalArray
arr = conformalArray;
arr.ElementPosition = [0 0 0.008; 0 0 0];  % antenna above chassis
arr.Element = {ant, chassis};
arr.Reference = "origin";

% 4. Analyze (full-wave MoM -- more expensive but handles substrates)
figure;
show(arr);
figure;
pattern(arr, freq);
```

**Trade-offs vs. `installedAntenna`:**
- Supports substrate-backed elements (no material restriction)
- Uses full MoM solver -- accurate but O(N^2) memory
- Practical for phone/device-sized platforms (a few wavelengths) at sub-6 GHz
- More manual setup (no `SolverType` selection, no MoM-PO/FMM hybrid)

For multi-antenna/MIMO analysis on a device chassis (isolation, ECC, diversity), see the **MIMO / Handset Multi-Antenna Design** section in the array design skill.

### Single Element

```matlab
freq = 1e9;
plat = platform(FileName="plate.stl", Units="m");

ant = installedAntenna;
ant.Platform = plat;
ant.Element = design(dipole, freq);
ant.ElementPosition = [0 0 0.1];
```

### Multiple Elements

Install multiple antennas using a cell array for `Element` and matching rows in `ElementPosition`. **Set `ElementPosition` before `Element`** -- MATLAB validates that the cell array length matches the number of position rows at assignment time:

```matlab
ant = installedAntenna;
ant.Platform = plat;
ant.ElementPosition = [0.1 0 0.5; -0.1 0 0.5];  % set positions first
ant.Element = {design(dipole, freq), design(monocone, freq)};
ant.FeedVoltage = [1 2];
ant.FeedPhase = [0 45];
```

**All vectors must match in length:** `ElementPosition` rows, `Element` cell array, `FeedVoltage`, and `FeedPhase`.

### Reference Property

- `"feed"` (default) -- `ElementPosition` is relative to each antenna's feed point. Use this for most cases.
- `"origin"` -- `ElementPosition` is relative to the antenna's geometric origin. Use when you need precise control over where the antenna body sits on the platform.

## Solver Selection Guide

| Solver | Best For | Mesh Density | Accuracy | Memory |
|--------|----------|-------------|----------|--------|
| `"MoM-PO"` | Large open platforms (plates, vehicle panels, reflectors) | Less stringent | Good (single-bounce PO) | Low |
| `"FMM"` | Large structures needing full-wave accuracy, concave or closed bodies | ~10 elements/lambda | Full-wave | Medium |
| `"MoM"` | Wavelength-scale structures only | ~10 elements/lambda | Full-wave | O(N^2) -- prohibitive for large platforms |

**Default to `"MoM-PO"`** unless one of these conditions applies:
- The platform has concave features or cavities where multiple reflections matter -- use `"FMM"`
- The platform is a closed body (fuselage, sphere) and full-wave accuracy is needed -- use `"FMM"`
- The platform is wavelength-scale and full-wave accuracy is acceptable -- use `"MoM"`

### MoM-PO (Default)

Hybrid solver: full MoM on the antenna, physical optics on the platform. Best balance of speed and accuracy for the common case of a small antenna on a large open surface.

**Key limitation:** MoM-PO does **not** model multiple reflections. If the platform geometry has concave regions, re-entrant corners, or surfaces that bounce energy between them, the PO approximation misses these interactions. Use FMM for such geometries.

### FMM (Fast Multipole Method)

Full-wave accuracy using an iterative GMRES solver, without the O(N^2) memory of direct MoM. Supports three integral equation formulations:

| Formulation | Geometry | Notes |
|-------------|----------|-------|
| EFIE | Open or closed | Default. Works on all geometries |
| MFIE | **Closed only** | Faster convergence on watertight bodies |
| CFIE | **Closed only** | Combined EFIE+MFIE, best convergence for closed bodies |

**MFIE and CFIE require a watertight (closed) mesh.** Using them on open structures (flat plates, open shells) produces incorrect results. When in doubt, use EFIE.

Because FMM uses an iterative solver, convergence is not guaranteed. Always verify with `convergence()` after analysis (see FMM Configuration below).

### MoM

Standard direct solver. Practical only when the total structure (antenna + platform) is small -- roughly under 5 wavelengths. Memory scales as O(N^2), making it infeasible for electrically large platforms.

## FMM Configuration

When using FMM, configure and verify the iterative solver:

```matlab
ant.SolverType = "FMM";

% Access solver configuration
s = solver(ant);

% Tune parameters (optional -- defaults are usually adequate)
s.Iterations = 200;         % max GMRES iterations (default: 100)
s.RelativeResidual = 1e-4;  % convergence tolerance (default: 1e-4)
s.Precision = 2e-4;         % FMM precision (default: 2e-4)
```

### Convergence Verification

Always verify FMM convergence after running an analysis. The `convergence` function takes the **solver object**, not the antenna:

```matlab
% Run analysis
Z = impedance(ant, freq);

% Plot convergence -- residual should drop below target
s = solver(ant);
figure;
convergence(s);
```

If the residual has not converged:
1. Increase `Iterations` (e.g., 200 or 500)
2. Refine the mesh (`MaxEdgeLength` = lambda/12 or finer)
3. For closed bodies, switch from EFIE to CFIE for better conditioning

## Meshing Guidelines

Mesh density depends on the solver:

| Solver | Guideline | Notes |
|--------|-----------|-------|
| MoM-PO | Platform mesh can be coarser (~lambda/6) | PO region is less sensitive |
| FMM | ~10 elements per wavelength (lambda/10) | Required for full-wave accuracy |
| MoM | ~10 elements per wavelength (lambda/10) | Standard MoM requirement |

```matlab
c = physconst("LightSpeed");
lambda = c / freq;

% FMM or MoM: refine to lambda/10
mesh(ant, MaxEdgeLength=lambda/10);

% MoM-PO: coarser is acceptable
mesh(ant, MaxEdgeLength=lambda/6);
```

Always visualize the mesh before running analysis:

```matlab
figure;
mesh(ant);
```

## Analysis

All standard Antenna Toolbox analysis functions work on `installedAntenna`.

### Radiation Pattern

```matlab
% 3D pattern
figure;
pattern(ant, freq);
```

### Impedance

```matlab
bw = 0.2 * freq;
freqRange = linspace(freq - bw/2, freq + bw/2, 21);
figure;
impedance(ant, freqRange);
```

### S-Parameters (Multi-Element Coupling)

For multi-element installations, use `sparameters` to analyze isolation between antennas:

```matlab
figure;
s = sparameters(ant, freqRange);
rfplot(s);
```

### Current and Charge Distribution

```matlab
figure;
current(ant, freq);

figure;
charge(ant, freq);
```

### Efficiency

```matlab
eff = efficiency(ant, freq);
fprintf("Radiation efficiency: %.2f%%\n", eff * 100);
```

### Electric and Magnetic Fields

Compute E and H fields at specified observation points:

```matlab
points = [0 0 1; 0 0 2; 0 0 3];  % observation points in meters
[E, H] = EHfields(ant, freq, points');
```

Note: `EHfields` expects a 3-by-M matrix (columns are points), not M-by-3.

## Multi-Antenna Pattern Visualization

Use `patternSystem` (R2024a+) to visualize radiation patterns of multiple antennas on the same platform simultaneously:

```matlab
ant = installedAntenna;
ant.Platform = plat;
ant.ElementPosition = [0.1 0.1 0.5; -0.1 -0.1 0.5];
ant.Element = {design(dipole, 1e9), design(monocone, 2e9)};

% Visualize all antenna patterns -- one frequency per element
figure;
patternSystem(ant, [1e9, 2e9]);

% Visualize specific elements only
figure;
patternSystem(ant, [1e9, 2e9], ElementNumber=[1, 2]);

% Customize pattern appearance
opts = PatternPlotOptions(Transparency=0.6, MagnitudeScale=[1 10]);
figure;
patternSystem(ant, [1e9, 2e9], PatternOptions=opts);
```

When using `patternSystem` with multiple antennas at different frequencies, pass a frequency vector with **one entry per element**.

## Infinite Ground Plane

Antenna Toolbox uses **image theory** to model an infinite ground plane without meshing it. This is much faster than meshing a large finite ground and avoids edge diffraction artifacts.

Set ground plane dimensions to `inf` on antenna elements that support it:

```matlab
% Monopole with infinite ground plane
m = monopole;
m.GroundPlaneLength = inf;
m.GroundPlaneWidth = inf;
m = design(m, freq);

% Reflector-backed dipole with infinite ground
r = reflector;
r.Exciter = dipole;
r.GroundPlaneLength = inf;
r.GroundPlaneWidth = inf;
r = design(r, freq);
```

**Balanced vs. unbalanced antennas:**
- **Unbalanced** (monopole, patch, invertedF) -- set ground dimensions to `inf` directly on the antenna object.
- **Balanced** (dipole, loop) -- wrap in a `reflector` with `inf` ground to use image theory.

## MATLAB Coding Standards

- Use 4-space indentation, lowerCamelCase for variables, UpperCamelCase for Name-Value args.
- Use `"double quotes"` for strings.
- Do not add titles to Antenna Toolbox plots (`show`, `pattern`, `impedance`, `rfplot`, `current`, `charge`, etc.) -- they already generate their own titles.
- Use `fprintf` for formatted numerical output.
- Follow the MATLAB coding guidelines from `guidelines://coding`.

## Guidelines

- **Do not over-explain** electromagnetic theory. The user is a professional.
- **Always set platform `Units` explicitly** to avoid the mm/m mismatch.
- **Warn about the substrate limitation** if the user requests a dielectric-backed antenna on a platform. Suggest a metal-only alternative.
- **Default to `"MoM-PO"`** unless the geometry has concave features, multiple reflections, or the user needs full-wave accuracy.
- **Verify FMM convergence** with `convergence()` after any FMM analysis.
- **Check mesh density** before analysis -- visualize with `mesh(ant)`.
- **Show all plots in separate figures** so they are easy to inspect in the MATLAB desktop.
- **Include units** in all output (meters, ohms, dB, dBi, degrees).
- **For multi-element setups**, ensure `Element`, `ElementPosition`, `FeedVoltage`, and `FeedPhase` all have matching lengths.
- **If the platform geometry file is unknown**, use the default plate or ask the user for the file path.
- **For very large platforms**, warn the user about memory and suggest `memoryEstimate` before running full-wave analysis.

----

Copyright 2026 The MathWorks, Inc.
