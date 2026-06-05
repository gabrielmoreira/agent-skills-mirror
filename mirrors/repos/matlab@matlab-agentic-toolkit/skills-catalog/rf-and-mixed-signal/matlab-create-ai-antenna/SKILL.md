---
name: matlab-create-ai-antenna
description: Use AI-based antenna design exploration and 3D pattern reconstruction in MATLAB Antenna Toolbox. AIAntenna provides instant parametric sweeps of catalog antennas via pretrained surrogate models. patternFromAI reconstructs full 3D radiation patterns from two orthogonal 2D slices using AI. Use when the user wants rapid antenna design exploration, instant parameter tuning, or 3D pattern reconstruction from 2D measured/imported data.
license: MathWorks BSD-3-Clause
allowed-tools: mcp__matlab__evaluate_matlab_code mcp__matlab__check_matlab_code mcp__matlab__detect_matlab_toolboxes ReadMcpResourceTool
argument-hint: <antenna-type-or-pattern-data> <frequency>
metadata:
  author: MathWorks
  version: "1.0"
---

# AI Antenna Workflows Skill

You are an expert RF and antenna engineer assisting with AI-accelerated antenna design and pattern reconstruction. Use MATLAB Antenna Toolbox `AIAntenna` for rapid design-space exploration and `patternFromAI` for 3D pattern reconstruction from 2D slices.

## When to Use

- User wants to quickly explore antenna design space without running full EM simulations
- User wants to sweep antenna parameters and instantly see performance (resonant frequency, bandwidth, beamwidth)
- User wants to reconstruct a full 3D radiation pattern from two measured 2D pattern cuts
- User has datasheet or chamber-measured 2D pattern slices and wants a 3D model
- User asks about AI-based antenna design or surrogate models
- User wants to tune antenna dimensions interactively and export the result

## When NOT to Use

- User wants full-wave EM simulation accuracy — use `matlab-design-antenna`
- User wants to design from scratch with `design()` — use `matlab-design-antenna`
- User wants PCB stackup or fabrication — use `matlab-design-pcb-antenna`
- User wants to optimize antenna dimensions with SADEA — use `matlab-optimize-antenna`

## AIAntenna Overview

`em.ai.AIAntenna` creates a pretrained surrogate model of a catalog antenna. Once created, you can instantly:
- Tune geometric parameters and get predicted resonant frequency, bandwidth, beamwidth, and peak radiation
- Explore the full design space without running MoM simulations (milliseconds vs. minutes)
- Export the tuned parameters to a real catalog antenna for full-wave validation

**Key advantage:** 1000x faster than full-wave simulation for parametric sweeps. The AI model predicts antenna performance from geometry in milliseconds.

**Limitation:** Predictions are approximate (surrogate model). Always validate final designs with `exportAntenna` + full-wave analysis.

### Requirements

- Antenna Toolbox
- Statistics and Machine Learning Toolbox

### Supported Antenna Types

| Type | Description |
|------|-------------|
| `"dipole"` | Half-wave dipole |
| `"patchMicrostrip"` | Rectangular microstrip patch |
| `"patchMicrostripCircular"` | Circular microstrip patch |
| `"patchMicrostripElliptical"` | Elliptical microstrip patch |
| `"patchMicrostripInsetfed"` | Inset-fed microstrip patch |
| `"patchMicrostripEnotch"` | E-notch microstrip patch |
| `"patchMicrostripHnotch"` | H-notch microstrip patch |
| `"patchMicrostripTriangular"` | Triangular microstrip patch |
| `"pifa"` | Planar inverted-F antenna |
| `"dipoleHelix"` | Helical dipole |
| `"waveguide"` | Open-ended waveguide |
| `"horn"` | Pyramidal horn |

### Creation

Create an AIAntenna using `design` with `ForAI=true`. **Only the 12 antenna types listed above are supported** — other catalog antennas (helix, yagiUda, vivaldi, monopole, etc.) do not have pretrained AI models.

```matlab
freq = 2.4e9;

% Create AI model from a supported catalog antenna
ant = patchMicrostrip;
antAI = design(ant, freq, ForAI=true);

% Or directly with the antenna constructor
antAI = design(horn, 10e9, ForAI=true);
```

`design(..., ForAI=true)` initializes the AI model with appropriate default dimensions for the target frequency. The direct `em.ai.AIAntenna()` constructor is not supported — always use `design`. If the user requests an antenna type not in the supported list, recommend using `matlab-design-antenna` or `matlab-optimize-antenna` skills instead.

### Core Workflow

```matlab
freq = 1e9;
antAI = design(horn, freq, ForAI=true);

% View default tunable parameters
defaults = defaultTunableParameters(antAI);
disp(defaults)

% Check tunable ranges
ranges = tunableRanges(antAI);
disp(ranges)

% Visualize geometry
figure; show(antAI);

% Get performance predictions (instant)
fRes = resonantFrequency(antAI);
[bw, fL, fU, matching] = bandwidth(antAI);
fprintf("Resonant frequency: %.3f GHz\n", fRes/1e9);
fprintf("Bandwidth: %.1f MHz (%.3f - %.3f GHz)\n", bw/1e6, fL/1e9, fU/1e9);
fprintf("Matching: %s\n", matching);  % "Matched", "Almost", or "Not Matched"
```

### Tuning Parameters

After creation, the AIAntenna object exposes dynamic properties matching the catalog antenna's geometric dimensions. Set them directly:

```matlab
antAI = design(patchMicrostrip, 2.4e9, ForAI=true);

% Check what's tunable and its bounds
ranges = tunableRanges(antAI);
disp(ranges)

% Tune dimensions directly (property names match catalog antenna)
antAI.Length = 0.035;
antAI.Width = 0.045;
antAI.Height = 0.002;

% Instantly check new performance
fRes = resonantFrequency(antAI);
[bw, fL, fU, matching] = bandwidth(antAI);
fprintf("After tuning: fRes=%.3f GHz, BW=%.1f MHz, %s\n", fRes/1e9, bw/1e6, matching);

% Reset to defaults
reset(antAI);
```

### Tunable Ranges

`tunableRanges` returns a table with bounds for each tunable property:

```matlab
ranges = tunableRanges(antAI);           % default: "all" bounds
ranges = tunableRanges(antAI, "strict"); % tighter bounds (higher accuracy)
ranges = tunableRanges(antAI, "loose");  % wider bounds (may reduce accuracy)
```

Use `"strict"` bounds for best prediction accuracy. Parameters outside strict bounds may give unreliable results.

### Peak Radiation and Beamwidth

```matlab
freq = 5.8e9;
ai = design(horn, freq, ForAI=true);

% Peak radiation (gain and direction)
[peakGain, az, el] = peakRadiation(ai, freq);
fprintf("Peak gain: %.2f dBi at az=%.1f, el=%.1f deg\n", peakGain, az, el);

% Beamwidth
[hpbw, angles, plane] = beamwidth(ai, freq);
fprintf("HPBW: %.1f deg (E-plane), %.1f deg (H-plane)\n", hpbw(1), hpbw(2));
```

### Parametric Sweep (Design-Space Exploration)

The main use case — sweep a parameter and plot performance:

```matlab
freq = 2.4e9;
ai = design(patchMicrostrip, freq, ForAI=true);

ranges = tunableRanges(ai, "strict");

% Sweep patch length
lengthRange = linspace(ranges.Length(1), ranges.Length(2), 20);
fResVec = zeros(size(lengthRange));
bwVec = zeros(size(lengthRange));

for k = 1:numel(lengthRange)
    ai.Length = lengthRange(k);
    fResVec(k) = resonantFrequency(ai);
    bwVec(k) = bandwidth(ai);
end

figure;
yyaxis left;
plot(lengthRange*1e3, fResVec/1e9, "-o");
ylabel("Resonant Frequency (GHz)");
yyaxis right;
plot(lengthRange*1e3, bwVec/1e6, "-s");
ylabel("Bandwidth (MHz)");
xlabel("Patch Length (mm)");
grid on;
title("Design Space: Patch Length vs. Performance");
```

### Export to Catalog Antenna

Convert the AI model to a real antenna for full-wave validation:

```matlab
ai = design(patchMicrostrip, 2.4e9, ForAI=true);
ai.Length = 0.035;
ai.Width = 0.045;

% Export to catalog antenna
ant = exportAntenna(ai);
disp(ant)

% Now run full-wave analysis to validate
figure; impedance(ant, linspace(2e9, 3e9, 51));
figure; pattern(ant, 2.4e9);
```

### Design Iteration Workflow

1. Create AIAntenna at target frequency
2. Sweep parameters to understand sensitivities (instant)
3. Tune to desired performance (resonant frequency, bandwidth, matching)
4. Export to catalog antenna
5. Validate with full-wave simulation
6. Fine-tune if needed using full-wave results

```matlab
freq = 5.8e9;

% Step 1: Create AI model
ai = design(patchMicrostripInsetfed, freq, ForAI=true);

% Step 2: Check if initial design is matched
[bw, ~, ~, matching] = bandwidth(ai);
fprintf("Initial: BW=%.1f MHz, %s\n", bw/1e6, matching);

% Step 3: Tune for better performance
defaults = defaultTunableParameters(ai);
ai.NotchLength = defaults.NotchLength * 1.1;  % increase inset depth
fRes = resonantFrequency(ai);
[bw, ~, ~, matching] = bandwidth(ai);
fprintf("Tuned: fRes=%.3f GHz, BW=%.1f MHz, %s\n", fRes/1e9, bw/1e6, matching);

% Step 4: Export
ant = exportAntenna(ai);

% Step 5: Full-wave validation
freqRange = linspace(freq*0.8, freq*1.2, 51);
figure; impedance(ant, freqRange);
figure; pattern(ant, freq);
```

### Full-Factorial Sweep and Optimization

For multi-parameter exploration, use `combinations()` to generate a full-factorial grid and sweep all tunable parameters simultaneously. For targeted optimization, use `OptimizerTRSADEA` with a custom evaluation function.

**Full-factorial pattern:**
```matlab
a = 0.85:0.1:1.15;
kc = combinations(a, a, a, a, a);  % all permutations
k = table2array(kc);
% Loop: scale params by k(i,:), evaluate performance, filter results
```

**OptimizerTRSADEA pattern:**
```matlab
Bounds = [0.85*defaults; 1.15*defaults];  % 2-by-N
s = OptimizerTRSADEA(Bounds);
s.CustomEvaluationFunction = @myFitness;
s.GeometricConstraints = struct(A=[0 -1 0 0 1], b=0);
s.optimize(50);
bestData = s.getBestMemberData;
```

**Matching status check** — always verify before trusting `resonantFrequency`:
```matlab
[~, ~, ~, matching] = bandwidth(antAI);
switch string(matching)
    case "Matched"
        fRes = resonantFrequency(antAI);
    case {"Almost", "Not Matched"}
        fRes = NaN;
end
```

See `references/optimization-workflows.md` for complete examples including custom evaluation functions, geometric constraints, and result filtering.

## patternFromAI Overview

`patternFromAI` reconstructs a complete 3D radiation pattern from just two orthogonal 2D pattern slices using a trained neural network. This is useful when you only have measured data from an anechoic chamber (typically E-plane and H-plane cuts).

**Key advantage:** Traditional interpolation methods (`patternFromSlices`) use simple geometric algorithms that produce artifacts. `patternFromAI` uses a neural network trained on thousands of antenna patterns to produce physically realistic 3D reconstructions.

### Requirements

- Antenna Toolbox (R2024a or later)
- No additional toolbox required

### Syntax

```matlab
% Plot mode (no outputs)
patternFromAI(magVertSlice, angleVertSlice, magHorizSlice, angleHorizSlice)
patternFromAI(___, Name=Value)

% Data mode (capture 3D pattern)
[p3D, vertAngleOut, horizAngleOut] = patternFromAI(___)
```

### Input Format

| Argument | Size | Description |
|----------|------|-------------|
| `magVertSlice` | 1-by-360 or 1-by-361 | Vertical (elevation) plane pattern magnitude (dBi) |
| `angleVertSlice` | 1-by-360 or 1-by-361 | Vertical plane angles (degrees) |
| `magHorizSlice` | 1-by-360 or 1-by-361 | Horizontal (azimuth) plane pattern magnitude (dBi) |
| `angleHorizSlice` | 1-by-360 or 1-by-361 | Horizontal plane angles (degrees) |

All inputs must be **row vectors**. Angles must be integer-valued with 1-degree spacing.

### Name-Value Arguments

| Name | Values | Default | Description |
|------|--------|---------|-------------|
| `AngleConvention` | `"phi-theta"`, `"az-el"` | `"phi-theta"` | Coordinate system of input angles |
| `MinMaxMagnitude` | 2-element vector | auto | `[min max]` for normalization |
| `PatternOptions` | `PatternPlotOptions` | default | Plot display options |

### Output Format

| Output | Size | Description |
|--------|------|-------------|
| `p3D` | 361-by-181 | Reconstructed 3D pattern (dBi) |
| `vertAngleOut` | 181-by-1 | Elevation angles (-90:90 for az-el) |
| `horizAngleOut` | 361-by-1 | Azimuth angles (0:360 for az-el) |

### Workflow 1: From Simulated Antenna

Extract 2D cuts from a simulated antenna and reconstruct the full 3D pattern:

```matlab
freq = 2.4e9;
ant = design(dipole, freq);

% Extract orthogonal cuts (az-el convention)
magVert = patternElevation(ant, freq, 0).';     % el cut at az=0 (row vector)
angVert = -180:1:180;                            % elevation angles
magHoriz = patternAzimuth(ant, freq, 0).';      % az cut at el=0 (row vector)
angHoriz = -180:1:180;                           % azimuth angles

% Reconstruct 3D pattern
figure;
patternFromAI(magVert, angVert, magHoriz, angHoriz, AngleConvention="az-el");

% Capture data for post-processing
[p3D, elOut, azOut] = patternFromAI(magVert, angVert, magHoriz, angHoriz, AngleConvention="az-el");
fprintf("Reconstructed pattern: %d x %d (az x el)\n", size(p3D));
fprintf("Peak gain: %.2f dBi\n", max(p3D(:)));
```

### Workflow 2: From Imported Measured Data

```matlab
% Import from CSV with columns [angle_deg, gain_dBi]
dataVert = readmatrix("elevation_cut.csv");
dataHoriz = readmatrix("azimuth_cut.csv");
magVert = dataVert(:,2).';       % transpose to row vector
angVert = dataVert(:,1).';
magHoriz = dataHoriz(:,2).';
angHoriz = dataHoriz(:,1).';

% Force intersection consistency (el=0 must match az=0 within 3 dB)
idx_el0 = find(angVert == 0);
idx_az0 = find(angHoriz == 0);
magHoriz(idx_az0) = magVert(idx_el0);

figure;
patternFromAI(magVert, angVert, magHoriz, angHoriz, AngleConvention="az-el");
```

### Workflow 3: Visualize with patternCustom

```matlab
[p3D, elOut, azOut] = patternFromAI(magVert, angVert, magHoriz, angHoriz, AngleConvention="az-el");

% Convert az-el output to phi-theta for patternCustom
theta = 90 - elOut';   % theta = 90 - elevation
phi = azOut';           % phi = azimuth
figure; patternCustom(p3D, theta, phi);
```

### Intersection Consistency (Data Quality)

**`patternFromAI` (az-el):** Vertical slice at el=0 should agree with horizontal slice at az=0. `patternFromAI` does NOT throw an error on mismatch, but large discrepancies degrade reconstruction quality. Aim for intersection agreement within 3 dB for best results.

**`patternFromSlices` (phi-theta):** Vertical slice at theta=90 must match horizontal slice at phi=0. `patternFromSlices` throws an error if the value at theta=90 is more than 3 dB below the peak of the vertical slice.

**Fix for poor intersection consistency:** Adjust one slice to match the other at the intersection, or average the two values.

## patternFromSlices Overview

`patternFromSlices` reconstructs a 3D pattern from two orthogonal 2D slices using geometric interpolation (introduced R2019a). Use this when `patternFromAI` is unavailable (pre-R2024a) or when you need a user-specified output grid.

### Syntax

```matlab
% Plot mode
patternFromSlices(vertSlice, theta, horizSlice, phi)

% Data mode
[p3D, thetaOut, phiOut] = patternFromSlices(vertSlice, theta, horizSlice, phi)

% Vertical slice only (assumes omnidirectional in azimuth)
[p3D, thetaOut, phiOut] = patternFromSlices(vertSlice, theta)
```

### Input Format (phi-theta convention only)

| Argument | Description |
|----------|-------------|
| `vertSlice` | Vertical (elevation) pattern magnitude (dBi), vector of length matching `theta` |
| `theta` | Polar angles (degrees), 0 to 180 |
| `horizSlice` | Horizontal (azimuth) pattern magnitude (dBi), vector of length matching `phi` |
| `phi` | Azimuth angles (degrees), 0 to 360 |

### Methods

| Method | Description |
|--------|-------------|
| `"Summing"` (default) | Adds vertical and horizontal contributions |
| `"CrossWeighted"` | Cross-weighted sum with configurable normalization |

### Workflow

```matlab
freq = 2.4e9;
ant = design(patchMicrostrip, freq);

% Extract slices in phi-theta convention
theta = 0:1:180;
phi = 0:1:360;
magVert = pattern(ant, freq, 0, theta);    % phi=0 cut
magHoriz = pattern(ant, freq, phi, 90);    % theta=90 cut

% Reconstruct (default: Summing method)
[p3D, thetaOut, phiOut] = patternFromSlices(magVert, theta, magHoriz, phi);
fprintf("Peak gain: %.2f dBi\n", max(p3D(:)));

% Visualize, or use CrossWeighted method
figure; patternFromSlices(magVert, theta, magHoriz, phi, Method="CrossWeighted");
```

## Training Custom Surrogate Models (fitrauto)

For antennas **not** in the AIAntenna catalog (custom pcbStack designs, modified geometries), train your own surrogate model using `fitrauto` from the Statistics and Machine Learning Toolbox.

**Workflow:** `lhsdesign` for sampling → parametric `sparameters` loop → `fitrauto` for model training → `predict` for instant evaluation.

```matlab
% 1. Sample design space with Latin hypercube
params = lhsdesign(200, 4);
% 2. Run full-wave for each sample (slow, use parfor)
for k = 1:N
    ant = buildAntenna(params(k,:));
    fRes(k) = findResonance(ant, freqRange);
end
% 3. Train surrogate (auto-selects GP, SVM, or neural net)
mdl = fitrauto(data, "fRes", Learners=["gp","svm","net"]);
% 4. Predict instantly
fPred = predict(mdl, newParams);
```

See `references/custom-surrogate-training.md` for the complete workflow with parameterized antenna definition, data generation, and model validation.

## MATLAB Coding Standards

- Use 4-space indentation, lowerCamelCase for variables, UpperCamelCase for Name-Value args.
- Use `"double quotes"` for strings.
- Do not add titles to Antenna Toolbox plots (`show`, `pattern`, `patternFromAI` auto-plot).
- **Do** add titles to manual `plot()` and `patternCustom()` figures.
- Use `fprintf` for formatted numerical output.
- Show all plots in separate figures.

## Guidelines

- **Check toolbox availability** before using AIAntenna — requires Statistics and Machine Learning Toolbox.
- **Use `"strict"` bounds** from `tunableRanges` for reliable predictions.
- **Always validate** AIAntenna results with `exportAntenna` + full-wave simulation before fabrication.
- **Input slices must be row vectors** with 1-degree integer spacing for `patternFromAI`.
- **Intersection consistency** — ensure the two slices agree within 3 dB at their shared point.
- **Default to az-el convention** for `patternFromAI` when working with measured data (more intuitive).
- **patternFromAI does not require any extra license** — only AIAntenna requires Stats & ML Toolbox.
- **Do not over-explain** AI/ML theory. The user is a professional engineer.
- **For parametric sweeps**, AIAntenna is 1000x faster than `impedance()` loops — recommend it for design exploration.
- **`reset(ai)` restores defaults** — useful after exploring parameter space.
- **Export early, export often** — validate AI predictions with full-wave at key design points.

----

Copyright 2026 The MathWorks, Inc.
