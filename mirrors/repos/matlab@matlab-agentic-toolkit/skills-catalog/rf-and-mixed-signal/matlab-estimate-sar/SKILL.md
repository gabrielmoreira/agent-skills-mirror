---
name: matlab-estimate-sar
description: Estimate Specific Absorption Rate (SAR) of electromagnetic fields inside dielectric tissue phantoms using MATLAB Antenna Toolbox. Supports three approaches -- birdcage coil with volumetric Phantom (full tissue properties), conformalArray with shape.Custom3D (antenna outside tissue), and direct EHfields for implantable antennas (antenna inside tissue). Computes internal E-fields, calculates point and mass-averaged SAR, and validates via power balance. Use when the user wants to compute SAR, tissue absorption, or RF exposure from antennas near or inside biological tissue.
license: MathWorks BSD-3-Clause
allowed-tools: mcp__matlab__evaluate_matlab_code mcp__matlab__check_matlab_code mcp__matlab__detect_matlab_toolboxes ReadMcpResourceTool
argument-hint: <antenna-type> <frequency> [phantom-type]
metadata:
  author: MathWorks
  version: "1.0"
---

# SAR Estimation Skill

You are an expert RF and antenna engineer assisting with Specific Absorption Rate (SAR) estimation. Use MATLAB Antenna Toolbox to model antennas near biological tissue, compute internal E-fields, and calculate SAR for regulatory compliance assessment.

## When to Use

- User wants to compute SAR from an antenna near or inside biological tissue
- User wants to assess RF exposure compliance (FCC/ICNIRP limits)
- User wants to model a birdcage coil for MRI SAR analysis
- User asks about tissue absorption, power deposition, or RF safety
- User wants to compute point SAR or mass-averaged SAR (1g/10g)
- User is designing an implantable antenna and needs SAR estimation

## When NOT to Use

- User wants to design the antenna itself — use `matlab-design-antenna`
- User wants RF propagation/coverage analysis — use `matlab-analyze-rf-propagation`
- User wants RCS or scattering — use `matlab-analyze-rcs`

## SAR Formula

$$\mathrm{SAR} = \frac{\sigma |E|^2}{2\rho} \quad [\mathrm{W/kg}]$$

where:
- $\sigma$ = tissue conductivity (S/m)
- $|E|$ = electric field magnitude inside tissue (V/m)
- $\rho$ = tissue mass density (kg/m^3)

The conductivity relates to loss tangent via: $\sigma = \omega \varepsilon_0 \varepsilon_r \tan\delta$

## Three Approaches

| Approach | Antenna | Tissue Model | Tissue Properties | Best For |
|----------|---------|--------------|-------------------|----------|
| `birdcage` + `Phantom` | Birdcage MRI coil only | Volumetric tetrahedral mesh (struct) | Arbitrary εr and LossTangent (no cap) | MRI SAR with realistic tissue |
| `conformalArray` + `shape.Custom3D` | Any antenna (dipole, PIFA, etc.) | Surface triangulation with catalog material | Limited to catalog (LossTangent ≤ 0.03) | Phone/device SAR (antenna outside tissue) |
| Direct `EHfields` + SAR formula | Any antenna (pcbStack, catalog) | Post-processing only (no tissue in solver) | Real values in formula (no cap) | Implantable antenna SAR |

**Key limitation:** The `dielectric` class enforces `LossTangent <= 0.03`. Real tissue (brain at 900 MHz: tanδ ≈ 0.36) exceeds this cap. Only `birdcage.Phantom` bypasses this limit using a custom struct format. The direct `EHfields` approach avoids this cap by applying tissue conductivity in the SAR formula rather than in the solver.

## Approach 1: birdcage + Phantom (Full Tissue Properties)

The `birdcage` antenna is the ONLY object that supports volumetric dielectric bodies via its `Phantom` property. The phantom is included directly in the MoM solver.

### Phantom Data Format

```matlab
phantom = struct( ...
    Points=vertices, ...      % N x 3 vertex coordinates (meters)
    Tetrahedra=elements, ...  % M x 4 tetrahedral element connectivity
    EpsilonR=epsR, ...        % Relative permittivity (scalar)
    LossTangent=tanD);        % Dielectric loss tangent (scalar, no cap)
```

### Shipped Phantoms

- `humanheadcoarse.mat` -- 584 vertices, 2818 tetrahedra (fast)
- `humanheadfine.mat` -- finer resolution (more accurate, slower)

Both provide variables `P` (vertices) and `T` (tetrahedra). Apply `scaleFactor = 0.003` to get physical dimensions.

### Workflow

```matlab
freq = 128e6;  % 3T MRI Larmor frequency

% Tissue properties (gray matter at 128 MHz)
tissueEpsR = 77;
tissueSigma = 0.51;  % S/m
tissueRho = 1040;    % kg/m^3
omega = 2 * pi * freq;
eps0 = 8.854e-12;
tanD = tissueSigma / (omega * eps0 * tissueEpsR);

% Load phantom
load humanheadcoarse.mat
scaleFactor = 0.003;
phantom = struct( ...
    Points=scaleFactor * P, ...
    Tetrahedra=T, ...
    EpsilonR=tissueEpsR, ...
    LossTangent=tanD);

% Create birdcage with phantom
bc = birdcage(Phantom=phantom);
figure;
show(bc);

% Compute E-fields inside head
gridSpacing = 0.02;
[obsPoints, insideMask] = createObservationGrid(phantom.Points, gridSpacing);
[E, ~] = EHfields(bc, freq, obsPoints');

% Calculate SAR
E_mag_sq = abs(E(1,:)).^2 + abs(E(2,:)).^2 + abs(E(3,:)).^2;
SAR_point = tissueSigma * E_mag_sq / (2 * tissueRho);
```

## Approach 2: conformalArray + shape.Custom3D (Any Antenna)

Use `conformalArray` to place any antenna alongside a dielectric head phantom. The `shape.Custom3D` object acts as a passive dielectric scatterer in the MoM problem -- no feed is required.

### Key Insight

`shape` objects can be placed directly as elements in `conformalArray.Element` without wrapping in `customAntenna`. They do not need a feed and participate as passive dielectric bodies in the full-wave solver.

### Workflow

```matlab
freq = 2.4e9;
c = physconst("LightSpeed");
lambda = c / freq;

% Load and scale head phantom
load humanheadcoarse.mat
scaleFactor = 0.003;
pts = scaleFactor * P;
pts = pts * (0.18 / (max(pts(:,1)) - min(pts(:,1))));  % 180mm width

% Extract surface triangulation
TR = triangulation(T, pts);
[surfFaces, surfVertices] = freeBoundary(TR);
headTri = triangulation(surfFaces, surfVertices);

% Create dielectric shape
headShape = shape.Custom3D(headTri);
headShape.Dielectric = "TMM10";  % highest-permittivity catalog material

% Design antenna
d = design(dipole, freq);

% Build conformalArray
arr = conformalArray;
arr.Element = {d, headShape};
arr.ElementPosition = [0.10 0 0; 0 0 0];
arr.Reference = "origin";

figure;
show(arr);
figure;
pattern(arr, freq);

% Compute E-fields inside head
gridSpacing = 0.015;
[obsPoints, insideMask] = createObservationGrid(pts, gridSpacing);
[E, ~] = EHfields(arr, freq, obsPoints');

% SAR computation (using TMM10 properties)
epsR = 9.8; tanD_mat = 0.0022; rho = 2270;
omega = 2 * pi * freq; eps0 = 8.854e-12;
sigma = omega * eps0 * epsR * tanD_mat;
E_mag_sq = abs(E(1,:)).^2 + abs(E(2,:)).^2 + abs(E(3,:)).^2;
SAR_point = sigma * E_mag_sq / (2 * rho);
```

## Observation Grid Generation

Filter a 3D grid to only include points inside the head volume:

```matlab
function [obsPoints, insideMask] = createObservationGrid(pts, gridSpacing)
    margin = gridSpacing;
    xVec = (min(pts(:,1))+margin) : gridSpacing : (max(pts(:,1))-margin);
    yVec = (min(pts(:,2))+margin) : gridSpacing : (max(pts(:,2))-margin);
    zVec = (min(pts(:,3))+margin) : gridSpacing : (max(pts(:,3))-margin);
    [Xg, Yg, Zg] = meshgrid(xVec, yVec, zVec);
    allPts = [Xg(:), Yg(:), Zg(:)];

    DT = delaunayTriangulation(pts);
    insideMask = ~isnan(pointLocation(DT, allPts));
    obsPoints = allPts(insideMask, :);
end
```

**Note:** `EHfields` expects a 3-by-M matrix (columns are points), so pass `obsPoints'`.

## Power Normalization

Default feed voltage is 1V. Normalize SAR to a standard input power:

```matlab
Z_in = impedance(ant, freq);
% For birdcage (multiple ports), take first port:
Z_in = Z_in(1);
P_accepted = 0.5 * real(Z_in) / abs(Z_in)^2;  % power at 1V

% Scale to 1W accepted power
SAR_1W = SAR_point * (1.0 / P_accepted);
```

## Mass-Averaged SAR (10g / 1g)

Regulatory limits are mass-averaged. Simplified cube averaging:

```matlab
avgMass = 0.010;  % 10 grams (ICNIRP) or 0.001 for 1g (FCC)
avgCubeSide = (avgMass / tissueRho)^(1/3);
halfSide = avgCubeSide / 2;

SAR_avg = zeros(size(SAR_1W));
for i = 1:numel(SAR_1W)
    dx = abs(obsPoints(:,1) - obsPoints(i,1));
    dy = abs(obsPoints(:,2) - obsPoints(i,2));
    dz = abs(obsPoints(:,3) - obsPoints(i,3));
    mask = (dx <= halfSide) & (dy <= halfSide) & (dz <= halfSide);
    SAR_avg(i) = mean(SAR_1W(mask));
end
```

## Power Balance Validation

The most important validation step. Two independent methods must agree:

**Method 1 (Efficiency):** Uses far-field pattern integration.
```matlab
eta = efficiency(ant, freq);
P_absorbed_eff = P_accepted * (1 - eta);
```

**Method 2 (SAR Integral):** Uses near-field EHfields + volume integration.
```matlab
deltaV = gridSpacing^3;
P_absorbed_SAR = sum(SAR_point) * tissueRho * deltaV;
```

**Interpretation:**
```matlab
relError = abs(P_absorbed_SAR - P_absorbed_eff) / P_absorbed_eff * 100;
% < 20%: PASS (good agreement)
% 20-50%: MARGINAL (expected with coarse grids)
% > 50%: Refine grid or mesh
```

If both methods agree, the SAR values are validated by energy conservation.

## Visualization

```matlab
figure;
scatter3(obsPoints(:,1)*1e3, obsPoints(:,2)*1e3, obsPoints(:,3)*1e3, ...
    30, SAR_1W, "filled");
colormap(jet); colorbar;
xlabel("X (mm)"); ylabel("Y (mm)"); zlabel("Z (mm)");
title("Point SAR Distribution (Normalized to 1W Input)");
axis equal; grid on; view(30, 20);
```

## DielectricCatalog: Adding Custom Materials

Materials can be added to the catalog programmatically:

```matlab
catalog = DielectricCatalog;
add(catalog, "BrainTissue900MHz", 52, 0.36, 900e6);
```

**Limitation:** The catalog accepts any LossTangent value, and `shape.Dielectric` accepts the name string, but when the solver instantiates the material it calls `dielectric("name")` which enforces `LossTangent <= 0.03`. Custom materials above this cap cannot be used in analysis.

## Available Catalog Materials

| Material | εr | tan δ | Notes |
|----------|------|--------|-------|
| TMM10 | 9.8 | 0.0022 | Highest permittivity available |
| TMM6 | 6.3 | 0.0023 | |
| FR4 | 4.8 | 0.026 | Highest loss tangent available |
| Teflon | 2.1 | 0.0002 | Very low loss |

For SAR demonstrations, use **TMM10** (highest εr) to maximize tissue-like behavior within the cap.

## Tissue Properties Reference

| Tissue (freq) | εr | σ (S/m) | tan δ | ρ (kg/m³) |
|----------------|-----|---------|-------|-----------|
| Brain (128 MHz) | 77 | 0.51 | 0.93 | 1040 |
| Brain (900 MHz) | 52 | 0.94 | 0.36 | 1040 |
| Brain (2.4 GHz) | 48 | 1.8 | 0.28 | 1040 |
| Muscle (900 MHz) | 55 | 0.94 | 0.34 | 1040 |
| Skin (900 MHz) | 41 | 0.87 | 0.42 | 1100 |

Source: IT'IS Foundation tissue properties database.

## Regulatory SAR Limits

| Standard | Limit | Averaging Mass | Region |
|----------|-------|----------------|--------|
| FCC (USA) | 1.6 W/kg | 1 g | Head/body |
| ICNIRP (EU) | 2.0 W/kg | 10 g | Head/trunk |
| ICNIRP (EU) | 4.0 W/kg | 10 g | Limbs |
| IEC 60601-2-33 (MRI) | 3.2 W/kg | 10 g | Head |

## Approach 3: Implantable Antenna (Direct EHfields)

For antennas **embedded inside tissue** (implantable medical devices), `conformalArray` cannot be used because the solver rejects intersecting geometries. Use direct `EHfields` from the standalone antenna, then apply the SAR formula in post-processing.

### Limitation

The EM solver computes fields as if radiating into free space — **tissue loading on antenna impedance is not captured**. The tissue conductivity is applied only in the SAR formula. This underestimates detuning effects but correctly demonstrates the SAR workflow.

### Workflow

```matlab
freq = 2.4e9;

% Build implantable antenna (patch between two substrates)
% Stack: {superstrate(1), patch(2), substrate(3), ground(4)}
subH = 1.27e-3;
supH = 0.5e-3;
sub = dielectric(Name="RO3010", EpsilonR=10.2, LossTangent=0.0023, Thickness=subH);
sup = dielectric(Name="RO3010_sup", EpsilonR=10.2, LossTangent=0.0023, Thickness=supH);

Lp = 12e-3; Wp = 12e-3; gndSize = 25e-3;
patch = antenna.Rectangle(Length=Lp, Width=Wp);
ground = antenna.Rectangle(Length=gndSize, Width=gndSize);

ant = pcbStack;
ant.BoardShape = antenna.Rectangle(Length=gndSize, Width=gndSize);
ant.BoardThickness = subH + supH;
ant.Layers = {sup, patch, sub, ground};
ant.FeedLocations = [Lp/4, 0, 2, 4];
ant.FeedDiameter = 0.6e-3;

% Define observation grid inside tissue (above superstrate)
tissueStart = supH + 1e-3;  % gap above antenna top
tissueEnd = tissueStart + 30e-3;
nx = 21; ny = 21; nz = 11;
xobs = linspace(-15e-3, 15e-3, nx);
yobs = linspace(-15e-3, 15e-3, ny);
zobs = linspace(tissueStart, tissueEnd, nz);
[X, Y, Z] = meshgrid(xobs, yobs, zobs);
obsPoints = [X(:), Y(:), Z(:)];

% Compute E-fields (3-by-M format)
[E, ~] = EHfields(ant, freq, obsPoints.');
E_mag_sq = abs(E(1,:)).^2 + abs(E(2,:)).^2 + abs(E(3,:)).^2;

% Power normalization
Z_in = impedance(ant, freq);
P_accepted = 0.5 * real(Z_in) / abs(Z_in)^2;
E_mag_sq_norm = E_mag_sq / P_accepted;

% SAR with real tissue properties (not limited by dielectric cap)
sigma_skin = 1.464;   % S/m (skin at 2.4 GHz)
rho_skin = 1100;      % kg/m^3
SAR = sigma_skin * E_mag_sq_norm / (2 * rho_skin);

fprintf("Peak point SAR: %.2f W/kg per 1W input\n", max(SAR));
```

### Why conformalArray Fails for Implantable

`conformalArray` calls `checkIntersection` during meshing. If the antenna geometry overlaps the `shape.Custom3D` tissue body, the solver throws: *"Intersection detected in specified geometry."* This is a hard constraint — the antenna must be geometrically outside the dielectric body for `conformalArray` to work.

## Choosing the Right Approach

Use **birdcage + Phantom** when:
- Modeling MRI coil SAR
- Realistic tissue properties are essential (high LossTangent)
- The antenna is a birdcage coil

Use **conformalArray + shape.Custom3D** when:
- Modeling phone/device SAR with any antenna type
- Antenna is **outside** the tissue body (not embedded)
- The LossTangent cap (0.03) is acceptable for the use case

Use **Direct EHfields** (Approach 3) when:
- Antenna is **implanted inside** tissue
- Any antenna type (pcbStack, catalog, array)
- Tissue conductivity applied in post-processing (real values, no cap)

## Frequency Interpretation

- Parse units: MHz, GHz, Hz. Default to Hz if no unit given.
- Common SAR frequencies: 128 MHz (3T MRI), 900 MHz (GSM), 1.8 GHz (LTE), 2.4 GHz (Wi-Fi)
- Use frequency-specific tissue properties from the reference table.

## MATLAB Coding Standards

- Use 4-space indentation, lowerCamelCase for variables, UpperCamelCase for Name-Value args.
- Use `"double quotes"` for strings.
- Do not add titles to Antenna Toolbox plots (`show`, `pattern`, `impedance`, `rfplot`).
- **Do** add titles to manual `plot()` and `scatter3()` figures.
- Use `fprintf` for formatted numerical output.
- Show all plots in separate figures.
- Include units in all output (meters, ohms, W/kg, dB).

## Guidelines

- **Always validate** SAR results with the power balance check.
- **Always normalize** to a known input power (typically 1W accepted).
- **Use `EHfields` with transposed points** -- expects 3-by-M, not M-by-3.
- **For birdcage,** take `Z_in(1)` since impedance returns a vector (multiple ports).
- **Grid spacing** affects accuracy: 20mm for quick demos, 5mm for publication quality.
- **Default to conformalArray approach** for phone/device SAR unless the user specifically wants birdcage/MRI SAR.
- **Warn about the LossTangent cap** when tissue properties are requested.
- **Explain the TMM10 limitation** -- it demonstrates the workflow but underestimates real tissue absorption.
- **Do not over-explain** electromagnetic theory. The user is a professional.

----

Copyright 2026 The MathWorks, Inc.
