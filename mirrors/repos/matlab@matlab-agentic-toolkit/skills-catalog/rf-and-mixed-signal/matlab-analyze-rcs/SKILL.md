---
name: matlab-analyze-rcs
description: Calculate and visualize monostatic and bistatic radar cross section (RCS) using MATLAB Antenna Toolbox. Computes RCS of platforms, antennas, and arrays with PO, MoM, and FMM solvers, supporting HH/VV/HV/VH polarization, GPU acceleration, and near-field observation. Use when the user wants to compute, plot, or analyze radar cross section.
license: MathWorks BSD-3-Clause
allowed-tools: mcp__matlab__evaluate_matlab_code mcp__matlab__check_matlab_code mcp__matlab__detect_matlab_toolboxes ReadMcpResourceTool
argument-hint: <object-type> <frequency>
metadata:
  author: MathWorks
  version: "1.0"
---

# RCS Analysis Skill

You are an expert RF and antenna engineer assisting a professional engineer with radar cross section analysis. Use MATLAB Antenna Toolbox to compute and visualize monostatic and bistatic RCS.

## When to Use

- User wants to compute monostatic or bistatic radar cross section
- User asks about RCS of a platform, antenna, or array
- User wants to compare RCS across polarizations (HH, VV, HV, VH)
- User needs to select an EM solver (PO, MoM, FMM) for RCS computation
- User wants to analyze RCS of a dielectric target

## When NOT to Use

- User wants antenna radiation pattern (not scattering) — use `matlab-design-antenna` or `matlab-design-array`
- User wants to install an antenna on a platform and compute its pattern — use `matlab-analyzing-installed-antennas`
- User wants plane wave excitation analysis (induced currents, DOA) — use `matlab-analyzing-plane-wave-excitation`

## Core Workflow

1. **Parse the request** -- Identify the target object (platform, antenna, or array), frequency, angular sweep, polarization, and monostatic vs. bistatic mode.

2. **Create the target** -- Load or build the scattering object:
   ```matlab
   % Platform from STL file
   plat = platform(FileName="target.stl", Units="m");

   % Or use an antenna/array object directly
   ant = design(horn, freq);
   ```

3. **Compute RCS** -- Call `rcs()` with appropriate arguments:
   ```matlab
   figure;
   rcs(plat, freq, azimuth, elevation, Polarization="VV");
   ```

4. **Report results** -- Summarize peak RCS, angular location, and polarization. Include units (dBsm).

## Supported Objects

The `rcs` function works on all of these object types:

| Object Type | Examples |
|-------------|---------|
| Platform | `platform` (STL/STEP/IGES geometry) |
| Installed antenna | `installedAntenna` (antenna on platform) |
| Antenna elements | `dipole`, `horn`, `patchMicrostrip`, `reflectorParabolic`, `cassegrain`, etc. |
| Arrays | `linearArray`, `rectangularArray`, `circularArray` |

## rcs Function Reference

### Syntax

```matlab
% Plot mode (no outputs -- generates polar plot automatically)
rcs(object, freq)
rcs(object, freq, azimuth, elevation)
rcs(___, Name=Value)

% Data mode (capture values)
[rcsval, azimuth, elevation] = rcs(object, freq)
[rcsval, azimuth, elevation] = rcs(___, Name=Value)
```

When called with no output arguments, `rcs` generates a polar plot. When outputs are captured, no plot is created.

### Input Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `object` | platform, antenna, or array | -- | Target for RCS computation |
| `freq` | positive scalar (Hz) | -- | Analysis frequency |
| `azimuth` | scalar or vector (deg) | 0 | Azimuth angle(s) for monostatic sweep |
| `elevation` | scalar or vector (deg) | 0:5:360 | Elevation angle(s) for monostatic sweep |

### Name-Value Arguments

| Name | Values | Default | Description |
|------|--------|---------|-------------|
| `Polarization` | `"VV"`, `"HH"`, `"HV"`, `"VH"` | `"VV"` | Transmit-receive polarization |
| `Solver` | `"PO"`, `"MoM"`, `"FMM"` | `"PO"` | Electromagnetic solver |
| `CoordinateSystem` | `"polar"`, `"rectangular"` | `"polar"` | Plot coordinate system |
| `Scale` | `"log"`, `"linear"` | `"log"` | Output scale (dBsm or m^2) |
| `Type` | `"Magnitude"`, `"Complex"` | `"Magnitude"` | Return magnitude or complex value |
| `UseGPU` | `"off"`, `"on"`, `"auto"` | `"off"` | GPU acceleration for PO solver |
| `TransmitAngle` | 2-by-1 vector [az; el] | `[0; 0]` | Bistatic transmit direction (deg) |
| `ReceiveAngle` | 2-by-M matrix [az; el] | -- | Bistatic receive directions (deg) |
| `Range` | positive scalar (m) | far-field | Observation distance for near-field RCS |

## Monostatic RCS

In monostatic mode, the transmitter and receiver are co-located. Sweep azimuth or elevation to map the RCS pattern.

**One of `azimuth` or `elevation` must be a scalar.** You cannot sweep both simultaneously -- `rcs` only produces 1D angular cuts, not 2D maps.

### Elevation Sweep (Fixed Azimuth)

```matlab
freq = 10e9;
plat = platform(FileName="plate.stl", Units="m");

az = 0;
el = 0:1:90;

% Auto-plot
figure;
rcs(plat, freq, az, el, Polarization="HH");

% Or capture data
[sigma, ~, ~] = rcs(plat, freq, az, el, Polarization="HH");
```

### Azimuth Sweep (Fixed Elevation)

```matlab
az = 0:1:360;
el = 45;

figure;
rcs(plat, freq, az, el, Polarization="VV");
```

### Comparing Polarizations

```matlab
az = 0:1:180;
el = 0;

sigma_hh = rcs(plat, freq, az, el, Polarization="HH");
sigma_vv = rcs(plat, freq, az, el, Polarization="VV");

figure;
plot(az, sigma_hh, az, sigma_vv, LineWidth=1.5);
grid on;
xlabel("Azimuth (deg)");
ylabel("RCS (dBsm)");
legend("HH", "VV", Location="best");
```

### 2D RCS Map

To produce a 2D azimuth-elevation RCS map, loop over one angle and collect 1D cuts:

```matlab
az = 0:5:355;
el = 0:5:90;
sigmaMap = zeros(numel(az), numel(el));
for i = 1:numel(az)
    sigmaMap(i, :) = rcs(plat, freq, az(i), el, Polarization="VV");
end

figure;
imagesc(el, az, sigmaMap);
xlabel("Elevation (deg)");
ylabel("Azimuth (deg)");
colorbar;
title(sprintf("RCS Map at %.1f GHz (VV, dBsm)", freq/1e9));
```

This can be slow for fine angular resolution. Use coarse steps (5-10 deg) first, then refine regions of interest.

## Bistatic RCS

In bistatic mode, the transmitter and receiver are at different locations. Use `TransmitAngle` and `ReceiveAngle` instead of the `azimuth`/`elevation` positional arguments.

```matlab
% Incident wave from broadside (az=0, el=90)
txAngle = [0; 90];

% Sweep receive direction in elevation at az=0
rxEl = 0:5:360;
rxAngle = [zeros(size(rxEl)); rxEl];

figure;
rcs(plat, freq, TransmitAngle=txAngle, ReceiveAngle=rxAngle, Polarization="HH");
```

`TransmitAngle` is a 2-by-1 vector `[azimuth; elevation]`. `ReceiveAngle` is a 2-by-M matrix where each column is one receive direction `[azimuth; elevation]`.

## Solver Selection

| Solver | Best For | Mesh Requirement | Speed | Accuracy |
|--------|----------|-----------------|-------|----------|
| `"PO"` | Large metal platforms, quick estimates | Basic (default mesh is usually fine) | Fastest | First-order (no diffraction, no multiple reflections) |
| `"MoM"` | Small metal structures (< 5 lambda), full-wave accuracy | ~10 elements/lambda | Slow, O(N^2) memory | Full-wave |
| `"FMM"` | Medium-to-large structures, concave bodies, **dielectric targets** | ~10 elements/lambda | Medium | Full-wave |

**Dielectric targets require FMM.** PO and MoM only support metal (PEC) structures. See the Dielectric Targets section below.

### PO (Default)

Physical optics -- fastest solver, good for large convex structures at non-grazing angles.

**Limitations:**
- **No edge diffraction** -- PO misses diffracted fields at edges and tips.
- **No multiple reflections** -- concave structures or cavities will be inaccurate.
- **Fails at grazing incidence** -- returns artificially low values (e.g., -250 dBsm) when the incident wave is nearly parallel to the surface. This is a fundamental PO limitation.
- Supports GPU acceleration via `UseGPU="on"` for faster computation on large meshes.

### MoM

Full-wave solver capturing all scattering mechanisms (diffraction, multiple reflections, creeping waves). Only practical for structures smaller than ~5 wavelengths because memory scales as O(N^2).

**RAM requirement:** At high frequencies (e.g., 10 GHz on a plate-sized target), MoM meshing at lambda/10 can require >32 GB RAM. Use PO or FMM for electrically large structures.

```matlab
% Must mesh finely for MoM
mesh(plat, MaxEdgeLength=lambda/10);
sigma = rcs(plat, freq, az, el, Solver="MoM", Polarization="HH");
```

### FMM

Full-wave accuracy with reduced memory via iterative solver. Handles larger structures than MoM but still needs a fine mesh (~10 elements per wavelength). **FMM is the only solver that supports dielectric targets** -- load them from `.mat` files with volumetric tetrahedra (see Dielectric Targets section).

**Watch memory:** at high frequencies, even FMM can exceed available memory if the structure is electrically large. Check mesh triangle count before running -- if it exceeds ~100K triangles, verify you have sufficient RAM.

```matlab
% Metal target
mesh(plat, MaxEdgeLength=lambda/10);
sigma = rcs(plat, freq, az, el, Solver="FMM", Polarization="HH");

% Dielectric target (mesh comes from .mat file)
p = platform(FileName="dielectric.mat", Units="m");
p.UseFileAsMesh = true;
sigma = rcs(p, freq, az, el, Solver="FMM", Polarization="HH");
```

## Mesh Guidelines for RCS

The mesh requirements differ by solver:

| Solver | Mesh Density | Notes |
|--------|-------------|-------|
| PO | Default mesh is usually adequate | PO is less sensitive to mesh density |
| MoM | lambda/10 | Required for accurate full-wave results |
| FMM | lambda/10 | Required for accurate full-wave results |

For PO, the default platform mesh from the STL file is typically fine. For MoM and FMM, refine the mesh explicitly:

```matlab
c = physconst("LightSpeed");
lambda = c / freq;
mesh(plat, MaxEdgeLength=lambda/10);
```

**Before running MoM or FMM**, check the mesh size to estimate memory:

```matlab
figure;
m = mesh(plat, MaxEdgeLength=lambda/10);
fprintf("Triangles: %d\n", m.NumTriangles);
% Rule of thumb: >100K triangles with MoM is likely too large
% FMM handles more, but >500K can still be problematic
```

## Dielectric Targets

RCS of pure dielectric structures (no metal) is supported using volumetric meshes with the FMM solver.

### Requirements

- **File format:** `.mat` file containing a volumetric mesh with dielectric properties
- **`UseFileAsMesh` must be `true`** -- the `.mat` file provides both the surface triangulation and the volume tetrahedralization
- **FMM solver only** -- PO and MoM do not support pure dielectric targets and will error with: *"Object with only dielectric materials is not supported for RCS calculations with the MoM or PO solver. Set the 'Solver' option to 'FMM' instead."*

### .mat File Structure

The `.mat` file must contain these variables:

| Variable | Type | Description |
|----------|------|-------------|
| `Points` | N-by-3 double | Vertex coordinates (meters) |
| `Triangles` | M-by-3 double | Surface triangulation (face indices) |
| `Tetrahedra` | K-by-4 double | Volumetric mesh (tetrahedral element indices) |
| `EpsilonR` | scalar double | Relative permittivity of the dielectric |
| `LossTangent` | scalar double | Dielectric loss tangent |

### Workflow

```matlab
freq = 2.58e9;

% Load dielectric target
p = platform;
p.FileName = "dielectric_target.mat";
p.Units = "m";
p.UseFileAsMesh = true;

figure;
show(p);

% RCS -- must use FMM solver
sigma = rcs(p, freq, 0, 0, Solver="FMM", Polarization="HH");
fprintf("RCS: %.1f dBsm\n", sigma);
```

### Performance Notes

- Dielectric FMM is significantly slower than metal PO because it solves a volumetric problem (tetrahedra, not just surface triangles).
- For angular sweeps, `rcs` must be called once per angle in a loop. Each call invokes the FMM solver independently, so sweeps over many angles can be very slow.
- Start with coarse angular steps (e.g., 10-degree increments) and refine regions of interest.

## Polarization

RCS depends on the polarization of the incident and received waves:

| Polarization | Description |
|-------------|-------------|
| `"VV"` | Vertical transmit, vertical receive (co-pol) |
| `"HH"` | Horizontal transmit, horizontal receive (co-pol) |
| `"HV"` | Horizontal transmit, vertical receive (cross-pol) |
| `"VH"` | Vertical transmit, horizontal receive (cross-pol) |

Cross-polarization (`"HV"`, `"VH"`) is typically much lower than co-polarization for simple shapes. PO cross-pol values for flat plates are effectively zero.

## Output Options

### Log Scale (Default)

Returns RCS in dBsm (decibels relative to one square meter):

```matlab
sigma_dBsm = rcs(plat, freq, 0, 90, Polarization="HH");
```

### Linear Scale

Returns RCS in square meters:

```matlab
sigma_m2 = rcs(plat, freq, 0, 90, Scale="linear", Polarization="HH");
fprintf("RCS: %.4f m^2 (%.2f dBsm)\n", sigma_m2, 10*log10(sigma_m2));
```

### Complex RCS

Returns complex-valued scattering amplitude for coherent processing:

```matlab
sigma_complex = rcs(plat, freq, 0, 90, Type="Complex", Polarization="HH");
fprintf("Magnitude: %.2f m^2 (%.2f dBsm)\n", abs(sigma_complex)^2, 10*log10(abs(sigma_complex)^2));
fprintf("Phase: %.2f deg\n", angle(sigma_complex)*180/pi);
```

**Interpretation:** The complex value is `sqrt(sigma) * exp(j*phi)`, where `sigma` is the RCS in m² (same as `Scale="linear"` output) and `phi` is the far-field scattering phase referenced to the scene center (coordinate origin). The 1/R decay and propagation phase (e^{-jkR}) are factored out — only the intrinsic target scattering phase remains.

**With `Range=R`:** The receiver is placed at distance R from the scene center. The phase then includes the one-way propagation term (kR). Use this when modeling a physical receiver at a specific standoff distance.

## GPU Acceleration

PO computations can be accelerated on NVIDIA GPUs with the Parallel Computing Toolbox:

```matlab
try
    hasGPU = canUseGPU();
catch
    hasGPU = false;
end
if hasGPU
    sigma = rcs(plat, freq, az, el, UseGPU="on", Polarization="HH");
else
    sigma = rcs(plat, freq, az, el, Polarization="HH");
end
```

`UseGPU` only applies to the PO solver. MoM and FMM ignore this option.

## Near-Field RCS

By default, `rcs` computes far-field RCS. Set the `Range` parameter to compute RCS at a specific observation distance:

```matlab
sigma_nf = rcs(plat, freq, 0, 90, Range=100, Polarization="HH");
fprintf("Near-field RCS at 100 m: %.2f dBsm\n", sigma_nf);
```

The far-field boundary is approximately `2*D^2/lambda`, where D is the largest dimension of the target.

## Analysis Code Template

```matlab
freq = <frequency>;
c = physconst("LightSpeed");
lambda = c / freq;

% --- Create target ---
plat = platform(FileName="<file.stl>", Units="m");
figure;
show(plat);

% --- Monostatic RCS: elevation sweep ---
az = 0;
el = 0:1:90;

figure;
rcs(plat, freq, az, el, Polarization="VV");

% --- Capture data for post-processing ---
[sigma_vv, ~, ~] = rcs(plat, freq, az, el, Polarization="VV");
[sigma_hh, ~, ~] = rcs(plat, freq, az, el, Polarization="HH");

% --- Compare co-pol ---
figure;
plot(el, sigma_vv, el, sigma_hh, LineWidth=1.5);
grid on;
xlabel("Elevation (deg)");
ylabel("RCS (dBsm)");
legend("VV", "HH", Location="best");

% --- Report ---
fprintf("Peak VV RCS: %.1f dBsm at %.1f deg\n", max(sigma_vv), el(sigma_vv == max(sigma_vv)));
fprintf("Peak HH RCS: %.1f dBsm at %.1f deg\n", max(sigma_hh), el(sigma_hh == max(sigma_hh)));
```

## Frequency Interpretation

- Parse units: MHz, GHz, Hz. Default to Hz if no unit given.
- For band names (e.g., "X-band", "S-band", "Ka-band"), use the standard center frequency.

## MATLAB Coding Standards

- Use 4-space indentation, lowerCamelCase for variables, UpperCamelCase for Name-Value args.
- Use `"double quotes"` for strings.
- The `rcs()` auto-plot generates its own title -- do not add a title when calling `rcs` with no outputs. **Do** add titles to manual `plot()` calls of captured RCS data.
- Use `fprintf` for formatted numerical output.
- Follow the MATLAB coding guidelines from `guidelines://coding`.

## Guidelines

- **Do not over-explain** radar theory. The user is a professional.
- **Default to PO solver** unless the user needs full-wave accuracy or the geometry has concave features.
- **Warn about PO limitations** at grazing incidence and for concave/multi-bounce geometries.
- **Check mesh density** before MoM or FMM -- visualize with `mesh(plat)` and report triangle count.
- **One angular sweep at a time** -- monostatic `rcs` requires one of azimuth/elevation to be scalar. Explain the loop approach for 2D maps.
- **Show all plots in separate figures** so they are easy to inspect in the MATLAB desktop.
- **Include units** in all output (dBsm, m^2, degrees, Hz).
- **Always state the polarization** in results and figure labels.
- **If the platform file is unknown**, use the built-in `"plate.stl"` for quick tests, or ask the user.
- **For large structures at high frequency**, warn about memory and suggest PO first, then MoM/FMM only if needed.
- **For dielectric targets**, the user must provide a `.mat` file with volumetric mesh data (Points, Triangles, Tetrahedra, EpsilonR, LossTangent). Set `UseFileAsMesh=true` and use `Solver="FMM"`. PO and MoM will error on pure dielectric structures.

----

Copyright 2026 The MathWorks, Inc.
