---
name: matlab-design-reflectarray
description: Design reflectarray antennas and reconfigurable intelligent surfaces (RIS) using MATLAB Antenna Toolbox. Builds unit cells with pcbStack, characterizes reflection phase (S-curve) via planeWaveExcitation + infiniteArray + EHfields, synthesizes aperture phase distributions, builds physical geometry with conformalArray, and verifies patterns via pattern multiplication. Use when the user wants to design a reflectarray, RIS, intelligent reflecting surface, or periodic surface with phase control.
license: MathWorks BSD-3-Clause
allowed-tools: mcp__matlab__evaluate_matlab_code mcp__matlab__check_matlab_code mcp__matlab__detect_matlab_toolboxes ReadMcpResourceTool
argument-hint: <frequency> [beam-direction] [array-size]
metadata:
  author: MathWorks
  version: "1.0"
---

# Reflectarray and RIS Design Skill

You are an expert RF and antenna engineer assisting a professional engineer with reflectarray and reconfigurable intelligent surface (RIS) design. Use MATLAB Antenna Toolbox (`pcbStack` + `infiniteArray` + `planeWaveExcitation`) to design unit cells, characterize phase response, synthesize aperture distributions, and verify beam patterns.

## When to Use

- User wants to design a reflectarray antenna
- User wants to design a reconfigurable intelligent surface (RIS)
- User wants to characterize unit cell reflection phase (S-curve)
- User wants to synthesize an aperture phase distribution for beam steering
- User asks about pattern multiplication for a periodic surface
- User wants to build a conformalArray with unique unit cell elements

## When NOT to Use

- User wants a curved reflector (parabolic, Cassegrain) — use `matlab-design-reflector-antenna`
- User wants a simple PCB antenna without periodic cells — use `matlab-design-pcb-antenna`
- User wants plane wave scattering analysis only — use `matlab-analyze-plane-wave`
- User wants an infinite array without reflectarray context — use `matlab-design-array`

## Core Workflow

1. **Parse the request** -- Identify the operating frequency, aperture size, beam direction, unit cell topology, substrate, f/D ratio, and whether it is a fixed reflectarray or reconfigurable RIS (with phase quantization bits).

2. **Design the unit cell** -- Build a parameterized `pcbStack` with a variable geometric parameter (patch size, slot length, rotation angle).

3. **Characterize the S-curve** -- Sweep the geometric parameter using `planeWaveExcitation` + `infiniteArray` + `EHfields` to extract reflection phase and magnitude at each step.

4. **Synthesize the aperture phase** -- Compute the required reflection phase at each element position given the feed location and desired beam direction.

5. **Map phase to geometry** -- Invert the S-curve to convert required phases to physical dimensions. For RIS, quantize to discrete states.

6. **Build the geometry** -- Construct a `conformalArray` with unique `pcbStack` elements at each position for visualization.

7. **Verify with pattern multiplication** -- Compute the element pattern from a representative unit cell, combine with the array factor, and display using `patternCustom`.

## Unit Cell Design with pcbStack

A reflectarray unit cell is a `pcbStack` with three layers: **patch (metal) + substrate (dielectric) + ground (metal)**.

```matlab
f0 = 5.8e9;
c0 = physconst("LightSpeed");
lambda = c0 / f0;
cellSize = 0.5 * lambda;
Lp = 8e-3;
subHeight = 1.524e-3;

sub = dielectric(Name="RO4003C", EpsilonR=3.55, LossTangent=0.0027, Thickness=subHeight);
boardGnd = antenna.Rectangle(Length=cellSize, Width=cellSize);
patch = antenna.Rectangle(Length=Lp, Width=Lp);

uc = pcbStack;
uc.BoardShape     = boardGnd;
uc.BoardThickness = subHeight;
uc.Layers         = {patch, sub, boardGnd};
uc.FeedLocations  = [Lp/4, 0, 1, 3];    % offset feed for proper excitation

figure;
show(uc);
```

**Feed location:** Use `[Lp/4, 0, 1, 3]` -- the feed is offset from patch center by `Lp/4` in x, connecting layer 1 (patch) to layer 3 (ground). The offset ensures proper excitation of the dominant patch mode.

### Critical Constraint: 3-Layer Limit

**`infiniteArray` only supports pcbStack with exactly 3 layers** (metal-dielectric-metal). Multi-layer stacks throw: *"Multilayer Substrate is not supported for Infinite arrays."*

### Layer Numbering

Layer 1: patch (metal), Layer 2: substrate (dielectric), Layer 3: ground (metal). `FeedLocations = [x y sigLayer gndLayer]` references these indices.

### Shape Objects for Metal Patterns

All shapes are in the `antenna` namespace. Use boolean operations for complex geometries:

```matlab
% Cross-shaped patch
crossPatch = antenna.Rectangle(Length=armLen, Width=armWid) + ...
             antenna.Rectangle(Length=armWid, Width=armLen);

% Ring patch
ring = antenna.Circle(Radius=Ro) - antenna.Circle(Radius=Ri);

% Slotted patch
slotted = antenna.Rectangle(Length=Lp, Width=Wp) - antenna.Rectangle(Length=Ls, Width=Ws);
```

### Substrate Selection

| Material | EpsilonR | LossTangent | Use Case |
|----------|----------|-------------|----------|
| Custom `"RO4003C"` | 3.55 | 0.0027 | Recommended for reflectarrays |
| `"Teflon"` | 2.1 | 0.0002 | Low-loss, moderate phase range |
| `"TMM3"` | 3.45 | 0.002 | Higher permittivity, wider phase range |
| `"FR4"` | 4.8 | 0.026 | Prototyping only (high loss) |

Use `dielectric(Name="RO4003C", EpsilonR=3.55, LossTangent=0.0027, Thickness=h)` for custom materials not in the built-in catalog.

## Phase Characterization (S-Curve)

### Recommended: planeWaveExcitation + EHfields

This method uses `planeWaveExcitation` to illuminate the unit cell with a plane wave and `EHfields` to extract the patch-scattered field. The periodic Green's function in `infiniteArray` accounts for mutual coupling between elements.

**Important:** `EHfields` returns only the field scattered by the patch currents — the ground plane specular reflection is not included separately (it is part of the background medium). The magnitude therefore peaks at resonance (maximum patch re-radiation), which differs from a classical reflection coefficient that dips at resonance. However, the **relative phase variation** across patch sizes is correct for reflectarray design because the ground plane contribution is spatially constant and cancels when computing inter-element phase differences. The `AF` scaling factor (`4*pi*cellSize^2/lambda^2`) is a real scalar that does not affect phase; magnitude is normalized afterward.

```matlab
f0 = 5.8e9;
c0 = physconst("LightSpeed");
lambda = c0 / f0;
k0 = 2*pi / lambda;
cellSize = 0.5 * lambda;
subHeight = 1.524e-3;
epsR = 3.55;
tanD = 0.0027;

sub = dielectric(Name="RO4003C", EpsilonR=epsR, LossTangent=tanD, Thickness=subHeight);
boardGnd = antenna.Rectangle(Length=cellSize, Width=cellSize);

% Nominal resonant patch size (starting point for sweep range)
patchSize0 = lambda / (2*sqrt(epsR));
patchSizes = linspace(0.3*patchSize0, 1.4*patchSize0, 20);

% Scaling and observation point
AF = 4*pi*cellSize^2 / lambda^2;         % real scalar, does not affect phase
obsRadius = 100 * lambda;                 % far-field observation distance

reflMag   = zeros(size(patchSizes));
reflPhase = zeros(size(patchSizes));

for idx = 1:numel(patchSizes)
    ps = patchSizes(idx);
    patch = antenna.Rectangle(Length=ps, Width=ps);

    uc = pcbStack;
    uc.BoardShape     = boardGnd;
    uc.BoardThickness = subHeight;
    uc.Layers         = {patch, sub, boardGnd};
    uc.FeedLocations  = [ps/4, 0, 1, 3];

    ia = infiniteArray(Element=uc);
    ia.ScanAzimuth   = 0;
    ia.ScanElevation = 90;
    numSummationTerms(ia, 15);

    % Plane wave excitation: -z direction, x-polarized
    pw = planeWaveExcitation;
    pw.Element      = ia;
    pw.Direction    = [0 0 -1];
    pw.Polarization = [1 0 0];

    % Extract reflected field at far-field observation point
    obsLoc = [0; 0; obsRadius];
    [Eo, ~] = EHfields(pw, f0, obsLoc);
    Eo = Eo * AF;
    Eco = dot(Eo, [1; 0; 0]);            % co-pol component

    reflMag(idx)   = abs(Eco);
    reflPhase(idx) = angle(Eco);
end

% Normalize magnitude (peak = 1, represents relative patch re-radiation)
reflMag = reflMag / max(reflMag);

% Unwrap phase for monotonic mapping
reflPhaseUnwrap = unwrap(reflPhase);

% Plot S-curve
figure;
subplot(2,1,1);
plot(patchSizes*1e3, reflMag, "b-o", LineWidth=1.5, MarkerSize=4);
ylabel("Reflection Magnitude |R|");
title(sprintf("Unit Cell S-Curve (%.1f GHz)", f0/1e9));
grid on;

subplot(2,1,2);
plot(patchSizes*1e3, rad2deg(reflPhaseUnwrap), "r-o", LineWidth=1.5, MarkerSize=4);
xlabel("Patch Side Length (mm)");
ylabel("Reflection Phase (deg)");
grid on;

phaseRange = max(reflPhaseUnwrap) - min(reflPhaseUnwrap);
fprintf("Phase range: %.0f degrees\n", rad2deg(phaseRange));
```

### S-Curve Quality Criteria

- **Phase range >= 300 degrees** (ideally 360). If less, increase substrate thickness or use a higher-permittivity material.
- **Smooth, monotonic variation** -- no abrupt jumps or flat regions.
- **Normalized magnitude near unity across most sizes** -- a sharp peak with rapid roll-off indicates the usable phase range is narrow; consider a thicker substrate.

### Sweep Range Guidance

Start with `0.3 * patchSize0` to `1.4 * patchSize0` where `patchSize0 = lambda / (2*sqrt(epsR))` is the nominal resonant size. This range captures the full phase transition through resonance.

## Aperture Phase Synthesis

### Required Phase Formula

The required reflection phase has two components:
- **Path delay**: `phiPath = k0 * Rmn` compensates for the spherical feed wavefront.
- **Beam steering**: `phiBeam = k0 * (x*u0 + y*v0)` adds a progressive gradient.

```matlab
% Element positions (centered grid)
xIdx = (-(Nx-1)/2 : (Nx-1)/2);
yIdx = (-(Ny-1)/2 : (Ny-1)/2);
[Xgrid, Ygrid] = meshgrid(xIdx * cellSize, yIdx * cellSize);

% Optional circular aperture mask
apertureRadius = max(Nx, Ny)/2 * cellSize;
mask = sqrt(Xgrid.^2 + Ygrid.^2) <= apertureRadius;
elemX = Xgrid(mask);
elemY = Ygrid(mask);

% Feed-to-element distances
dx = elemX - feedPos(1);
dy = elemY - feedPos(2);
dz = 0 - feedPos(3);
Rmn = sqrt(dx.^2 + dy.^2 + dz.^2);
phiPath = k0 * Rmn;

% Beam steering phase
u0 = sin(deg2rad(theta0)) * cos(deg2rad(phi0));
v0 = sin(deg2rad(theta0)) * sin(deg2rad(phi0));
phiBeam = k0 * (elemX * u0 + elemY * v0);

% Required reflection phase
phiReq = mod(phiPath - phiBeam, 2*pi);
```

### S-Curve Inversion (Phase to Patch Size)

```matlab
% Sort and deduplicate S-curve for interpolation
[phaseSorted, sortIdx] = sort(scurve.reflPhase);
patchSorted = scurve.patchSizes(sortIdx);
magSorted   = scurve.reflMag(sortIdx);
[phaseSorted, uniqIdx] = unique(phaseSorted);
patchSorted = patchSorted(uniqIdx);
magSorted   = magSorted(uniqIdx);

% Wrap required phase into S-curve range
phaseMin = min(phaseSorted);
phaseMax = max(phaseSorted);
phaseRange = phaseMax - phaseMin;
phiReqWrap = phaseMin + mod(phiReq - phaseMin, phaseRange);

% Interpolate patch sizes and actual reflected phase/magnitude
elemPatchSize = interp1(phaseSorted, patchSorted, phiReqWrap, "pchip", "extrap");
elemPatchSize = max(min(elemPatchSize, max(scurve.patchSizes)), min(scurve.patchSizes));
elemReflPhase = interp1(patchSorted, phaseSorted, elemPatchSize, "pchip", "extrap");
elemReflMag   = interp1(patchSorted, magSorted,   elemPatchSize, "pchip", "extrap");
```

## Feed Illumination Model

Model the feed as `cos^q(theta)` with `1/R` spatial attenuation:

```matlab
thetaFeed = atan2(sqrt(dx.^2 + dy.^2), abs(dz));
feedIllum = (cos(thetaFeed).^qFeed) ./ Rmn;
elemAmp   = feedIllum .* elemReflMag;
elemAmp   = elemAmp / max(elemAmp);

% Total excitation phase = element reflection phase - feed path delay
elemTotalPhase = elemReflPhase - phiPath;
```

## Reflectarray Geometry Visualization

Use `conformalArray` with a unique `pcbStack` at each element position:

```matlab
elements = cell(1, nElem);
for ii = 1:nElem
    ps = elemPatchSize(ii);
    patch = antenna.Rectangle(Length=ps, Width=ps);
    uc = pcbStack;
    uc.BoardShape     = boardGnd;
    uc.BoardThickness = subHeight;
    uc.Layers         = {patch, sub, boardGnd};
    uc.FeedLocations  = [ps/4, 0, 1, 3];
    elements{ii} = uc;
end

elemPositions = [elemX, elemY, zeros(nElem, 1)];
raGeom = conformalArray(Element=elements, ElementPosition=elemPositions, Reference="origin");

figure;
show(raGeom);
figure;
layout(raGeom);
```

## Pattern Verification (Pattern Multiplication)

Combine a representative element pattern with the array factor for the total radiation pattern.

**Angle convention:** Use theta (0:180, measured from z-axis) throughout this section. `patternCustom` expects theta convention (theta=0 is broadside). The `pattern()` function uses elevation (el=90 is broadside), so convert with `el = 90 - theta`.

### Element Pattern

```matlab
thetaGrid = 0:1:180;
phiGrid   = 0:1:360;
elGrid    = 90 - thetaGrid;           % convert theta to elevation for pattern()
dElem = pattern(unitCell, f0, phiGrid, elGrid);
dElem = dElem.';    % transpose to phi-rows x theta-cols
```

### Array Factor (Full 2D Grid)

```matlab
[THG, PHG] = meshgrid(deg2rad(thetaGrid), deg2rad(phiGrid));
AF = zeros(size(THG));
for ii = 1:numel(THG)
    u = sin(THG(ii)) * cos(PHG(ii));
    v = sin(THG(ii)) * sin(PHG(ii));
    phaseProg = k0 * (elemX * u + elemY * v);
    AF(ii) = abs(sum(elemAmp .* exp(1j * (elemTotalPhase + phaseProg))));
end
AF_dB = 20*log10(AF / max(AF(:)));
AF_dB(AF_dB < -60) = -60;
```

### Pattern Multiplication and Display

```matlab
dElemNorm = dElem - max(dElem(:));
totalPattern_dB = dElemNorm + AF_dB;
totalPattern_dB = totalPattern_dB - max(totalPattern_dB(:));

figure;
patternCustom(totalPattern_dB, thetaGrid, phiGrid);

% E-plane cut with antenna metrics
[~, phiIdx0] = min(abs(phiGrid - 0));
eplaneCut = totalPattern_dB(phiIdx0, :);
figure;
pp = polarpattern(thetaGrid, eplaneCut);
pp.AntennaMetrics = true;
pp.TitleTop = sprintf("E-plane (phi = 0°) at %.1f GHz", f0/1e9);
```

## RIS Phase Quantization

```matlab
Nbits = 2;
Nstates = 2^Nbits;
phaseStep = 2*pi / Nstates;
phiQuantized = round(phiReq / phaseStep) * phaseStep;

% Quantization efficiency: sinc^2(1/2^N)
% Inline sinc to avoid Signal Processing Toolbox dependency
sincVal = sin(pi/Nstates) / (pi/Nstates);
quantEff = sincVal^2;
fprintf("Quantization loss: %.1f dB\n", 10*log10(quantEff));
```

| Bits | States | Efficiency | Loss |
|------|--------|------------|------|
| 1 | 2 | 0.405 | -3.9 dB |
| 2 | 4 | 0.811 | -0.9 dB |
| 3 | 8 | 0.950 | -0.2 dB |

## Design Parameters

- **Unit cell size:** `lambda/2` (default). Range: 0.3-0.6 lambda. Grating lobe limit: `cellSize < lambda/(1 + sin(theta_max))`.
- **f/D ratio:** 0.8 (default). Range: 0.5-1.5. Higher f/D = more uniform illumination but taller profile.
- **Feed exponent q:** Choose for -10 dB edge taper: `q = -10 / (20*log10(cos(atan(D/(2*F)))))`.
- **Patch sweep range:** `0.3*patchSize0` to `1.4*patchSize0` where `patchSize0 = lambda/(2*sqrt(epsR))`.

## MATLAB Coding Standards

- Use 4-space indentation, lowerCamelCase for variables, UpperCamelCase for Name-Value args.
- Use `"double quotes"` for strings.
- Do not add titles to Antenna Toolbox plots (`show`, `pattern`, `patternCustom`, etc.) -- they generate their own.
- **Do** add titles to manual `plot`, `imagesc`, `subplot` figures and `TitleTop` to `polarpattern`.
- Use `fprintf` for formatted numerical output.

## Guidelines

- **Do not over-explain** reflectarray theory. The user is a professional.
- **Use `planeWaveExcitation` + `EHfields`** for S-curve characterization -- this is more accurate than `sparameters` for reflectarray unit cells.
- **Always use `pcbStack` with exactly 3 layers** for `infiniteArray`. Warn about the multilayer limitation.
- **Set `BoardThickness` before `Layers`** on `pcbStack` -- setting Layers first causes MATLAB to silently overwrite dielectric thickness with BoardThickness, producing incorrect substrate dimensions.
- **Feed offset:** Use `[Lp/4, 0, 1, 3]` for proper patch excitation -- not `[0 0 1 3]`.
- **`BoardShape` must match the ground plane** -- this defines the unit cell boundary.
- **Always unwrap the phase** with `unwrap()` and normalize magnitude (peak = 1).
- **Magnitude represents patch re-radiation, not |Gamma|** -- it peaks at resonance. The ground plane reflection is constant and does not affect relative phase between elements.
- **Use `conformalArray`** to visualize the full reflectarray with unique elements at each position.
- **Use pattern multiplication** (`patternCustom` with element pattern + array factor in dB) for total pattern.
- **Theta is measured from broadside (z-axis)** in array factor sweeps.
- **For RIS designs**, report quantization efficiency and compare quantized vs. continuous patterns.
- **If S-curve phase range < 300°**, suggest increasing substrate thickness or permittivity.

----

Copyright 2026 The MathWorks, Inc.
