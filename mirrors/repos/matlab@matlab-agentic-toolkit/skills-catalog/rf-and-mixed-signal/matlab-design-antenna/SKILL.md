---
name: matlab-design-antenna
description: Design and analyze antennas using MATLAB Antenna Toolbox. Creates antenna geometry, computes key parameters (impedance, gain, pattern), and generates plots. Includes radiation pattern visualization with 2D/3D cuts, polarization analysis, beamwidth, sidelobe analysis, and pattern comparison. Use when the user wants to design, create, model, or analyze the radiation pattern of an antenna at a given frequency.
license: MathWorks BSD-3-Clause
allowed-tools: mcp__matlab__evaluate_matlab_code mcp__matlab__check_matlab_code mcp__matlab__detect_matlab_toolboxes ReadMcpResourceTool
argument-hint: <antenna-type> <frequency>
metadata:
  author: MathWorks
  version: "1.0"
---

# Antenna Design & Pattern Analysis Skill

You are an expert RF and antenna engineer assisting a professional antenna engineer or RF system designer. Use MATLAB Antenna Toolbox to design, analyze, and visualize antennas and their radiation patterns.

## When to Use

- User wants to design, create, or model an antenna at a specific frequency
- User asks for radiation pattern analysis (3D pattern, azimuth/elevation cuts)
- User wants impedance, S-parameters, or return loss of an antenna
- User asks to compare radiation patterns of multiple antennas or frequencies
- User needs polarization analysis (axial ratio, RHCP/LHCP patterns)
- User asks about beamwidth, sidelobe level, or peak directivity
- User wants to set a substrate material on an antenna before design

## When NOT to Use

- User wants to build a custom antenna from geometric shapes — use `matlab-creating-custom-antennas`
- User wants to design a PCB antenna with multi-layer stackups — use `matlab-designing-pcb-antennas`
- User wants to design antenna arrays (linear, rectangular, conformal) — use `matlab-designing-arrays`
- User wants to analyze antennas installed on platforms — use `matlab-analyzing-installed-antennas`
- User wants to design reflector antennas (parabolic, Cassegrain) — use `matlab-designing-reflector-antennas`
- User wants to design impedance matching networks — use `matlab-designing-matching-networks`
- User wants to optimize antenna parameters — use `matlab-optimizing-antennas`
- User wants RCS analysis — use `matlab-analyzing-rcs`

## Core Workflow

1. **Parse the request** -- Identify the antenna type, operating frequency (or band), and any constraints (substrate, ground plane, impedance target, polarization, pattern requirements).

2. **Create and scale the antenna** -- Always use `design()`:
   ```matlab
   ant = design(<antennaObject>, freq);
   ```
   Do NOT manually compute dimensions from wavelength unless the user specifically asks.

3. **Display the geometry**:
   ```matlab
   figure;
   show(ant);
   ```

4. **Compute and report key parameters** -- Provide:
   - Input impedance over bandwidth
   - S11 / return loss
   - 3D radiation pattern at design frequency

5. **Present results professionally** -- Summarize key metrics in a table with units.

## Supported Antenna Types

| Category | Types |
|----------|-------|
| Dipole | `dipole`, `dipoleFolded`, `dipoleMeander`, `dipoleVee`, `dipoleBlade`, `dipoleCycloid`, `dipoleCylindrical`, `dipoleJ`, `sectorInvertedAmos`, `bowtieTriangular`, `bowtieRounded`, `biquad`, `rhombic` |
| Monopole | `monopole`, `monopoleTopHat`, `monopoleCylindrical`, `monopoleRadial`, `monopoleCustom`\*, `invertedF`, `invertedL`, `invertedFcoplanar`, `invertedLcoplanar` |
| Loop | `loopCircular`, `loopRectangular` |
| Patch | `patchMicrostrip`, `patchMicrostripCircular`, `patchMicrostripEnotch`, `patchMicrostripElliptical`, `patchMicrostripHnotch`, `patchMicrostripInsetfed`, `patchMicrostripTriangular`, `pifa` |
| Slot | `slot`, `vivaldi`, `vivaldiAntipodal`, `vivaldiOffsetCavity` |
| Spiral | `spiralArchimedean`, `spiralRectangular`, `spiralEquiangular` |
| Helix | `helix`, `helixMultifilar`, `dipoleHelix`, `dipoleHelixMultifilar` |
| Horn | `horn` (rectangular), `hornConical`, `hornCorrugated`, `hornConicalCorrugated`, `hornPotter`, `hornScrimp`, `hornRidge` |
| Waveguide | `waveguide` (rectangular), `waveguideCircular`, `waveguideSlotted`, `waveguideRidge` |
| Cone | `bicone`, `biconeStrip`, `discone`, `disconeStrip`, `monocone` |
| Fractal | `fractalKoch`, `fractalIsland`, `fractalCarpet`, `fractalSnowflake`, `fractalGasket` |
| Dielectric Resonator | `draRectangular`, `draCylindrical` |
| Multi-Element | `yagiUda`, `lpda`\*, `dipoleCrossed`, `quadCustom` |
| Cloverleaf | `cloverleaf` |
| MRI | `birdcage`\* |
| Custom | `customAntenna`\* |

\* Does not support `design()` — see "Antennas Without design() Support" below.

**Informal name mapping:**
- "patch antenna" / "microstrip patch" -> `patchMicrostrip`
- "circular patch" -> `patchMicrostripCircular`
- "inset-fed patch" -> `patchMicrostripInsetfed`
- "triangular patch" -> `patchMicrostripTriangular`
- "elliptical patch" -> `patchMicrostripElliptical`
- "Yagi" / "Yagi-Uda" -> `yagiUda`
- "LPDA" / "log-periodic" -> `lpda`
- "horn" / "rectangular horn" -> `horn`
- "conical horn" -> `hornConical`
- "ridged horn" -> `hornRidge`
- "folded dipole" -> `dipoleFolded`
- "meander dipole" / "meander line" -> `dipoleMeander`
- "crossed dipole" -> `dipoleCrossed`
- "J-pole" / "J antenna" -> `dipoleJ`
- "IFA" / "inverted-F" -> `invertedF`
- "ILA" / "inverted-L" -> `invertedL`
- "PIFA" -> `pifa`
- "bowtie" -> `bowtieTriangular`
- "Vivaldi" / "TSA" -> `vivaldi`
- "antipodal Vivaldi" -> `vivaldiAntipodal`
- "multifilar helix" -> `helixMultifilar`
- "bicone strip" -> `biconeStrip`
- "discone strip" -> `disconeStrip`
- "ridged waveguide" -> `waveguideRidge`
- "Koch antenna" -> `fractalKoch`
- "Koch island" / "Minkowski" -> `fractalIsland`
- "Koch snowflake" -> `fractalSnowflake`
- "Sierpinski carpet" -> `fractalCarpet`
- "Sierpinski gasket" -> `fractalGasket`
- "DRA" -> `draRectangular` (or `draCylindrical` if cylindrical)
- "birdcage coil" -> `birdcage`

## Antenna Systems (Structures with Exciters)

Structures combine a backing structure with an antenna element via the `Exciter` property.

### Cavity Structures
| Structure | Default Exciter | Substrate | `design()` |
|-----------|-----------------|-----------|------------|
| `cavity` | `dipole` | Yes | Yes |
| `cavityCircular` | `dipole` | Yes | Yes |

### Planar Reflectors
| Structure | Default Exciter | Substrate | `design()` |
|-----------|-----------------|-----------|------------|
| `reflector` | `dipole` | Yes | Yes |
| `reflectorCircular` | `dipole` | Yes | Yes |
| `reflectorCorner` | `dipole` | No | Yes |
| `reflectorGrid` | `dipole` | No | Yes |
| `reflectorCylindrical` | `dipole` | No | Yes |

### Curved Reflectors
| Structure | Default Exciter | `design()` |
|-----------|-----------------|------------|
| `reflectorParabolic` | `dipole` | Yes |
| `reflectorSpherical` | `dipole` | Yes |
| `cassegrain` | `hornConical` | Yes |
| `cassegrainOffset` | `hornConical` | Yes |
| `gregorian` | `hornConical` | Yes |
| `gregorianOffset` | `hornConical` | Yes |
| `customDualReflectors` | `hornConical` | **No** -- set dimensions manually |

### Dielectric Lens
| Structure | `design()` |
|-----------|------------|
| `dielectricLens` | **No** -- set manually. No `Exciter` property. |

### Workflow
```matlab
ant = cavity;
ant.Exciter = dipole;
ant = design(ant, freq);

ant = reflectorParabolic;
ant.Exciter = helix;
ant = design(ant, freq);
```

### Probe Feed (EnableProbeFeed)

Some antenna structures (e.g., `cavity`, `cavityCircular`, `reflector`) have an `EnableProbeFeed` property. When the user requests a probe feed, set `EnableProbeFeed = 1` after calling `design()`:

```matlab
ant = cavity;
ant.Substrate = dielectric("FR4");
ant.Exciter = dipole;
ant = design(ant, freq);
ant.EnableProbeFeed = 1;

% Ensure Height > Spacing (required constraint when substrate is specified)
if ant.Height <= ant.Spacing
    ant.Height = ant.Spacing + 0.005;
end
```

**Important:** When a substrate is specified, the cavity `Height` must be greater than `Spacing`.

## Antennas Without `design()` Support

The following catalog items do not support `design()`. Using `design()` on them will error.

| Antenna | Category |
|---------|----------|
| `birdcage` | MRI |
| `customAntenna` | Custom |
| `lpda` | Multi-Element |
| `monopoleCustom` | Monopole |

**Fallback workflow** for these antennas:
```matlab
ant = birdcage;       % or lpda, customAntenna, monopoleCustom
disp(ant);            % Inspect available properties and defaults
% Set dimensions manually based on wavelength or user-provided values
c = physconst("LightSpeed");
lambda = c / freq;
% Adjust properties as needed, then proceed with analysis
```

## Substrate Support

Set substrate on the antenna **before** calling `design()`:

```matlab
ant = patchMicrostrip;
ant.Substrate = dielectric("FR4");
ant = design(ant, freq);
```

**Elements with Substrate:** `patchMicrostrip`, `patchMicrostripCircular`, `patchMicrostripEnotch`, `pifa`, `monopoleTopHat`, `vivaldiAntipodal`, `draRectangular`, `draCylindrical`, `fractalIsland`, `fractalCarpet`, `fractalSnowflake`

**Built-in materials:** `"FR4"` (er=4.8), `"Teflon"` (er=2.1), `"Air"` (er=1.0). Use `openDielectricCatalog` for more.

**Custom substrates:**
```matlab
sub = dielectric(Name="MySubstrate", EpsilonR=2.2, LossTangent=0.0009, Thickness=0.787e-3);
ant.Substrate = sub;
```

**Note:** `design()` may adjust the substrate `Thickness` as part of the optimization. Always display the final substrate properties after calling `design()`.

**Meshing for substrate antennas** -- default mesh is ~lambda/40, which is slow. Apply coarser mesh after `design()`:
```matlab
c = physconst("LightSpeed");
lambda = c / freq;
mesh(ant, MaxEdgeLength=lambda/8);
```

## S-Parameter Interpolation Sweep

Use `SweepOption="interp"` only when **both** conditions are met:
1. RF Toolbox available and licensed
2. Antenna has a `Substrate` property

```matlab
if isprop(ant, "Substrate") && ~isempty(ant.Substrate)
    try
        s = sparameters(ant, freqRange, SweepOption="interp");
    catch
        s = sparameters(ant, freqRange);
    end
else
    s = sparameters(ant, freqRange);
end
```

**Note:** `SweepOption` is only supported by `sparameters`, not by `impedance` or other analysis functions.

## Pattern Analysis

### 3D Radiation Pattern
```matlab
figure;
pattern(ant, freq);
```

### 2D Cuts with Antenna Metrics

Always use `polarpattern` with `AntennaMetrics = true` for 2D cuts:

```matlab
% Azimuth cut at elevation = 0 degrees
elCut = 0;
D = patternAzimuth(ant, freq, elCut);
az = -180:1:180;
figure;
pp = polarpattern(az, D);
pp.AntennaMetrics = true;
pp.TitleTop = sprintf("Azimuth Pattern (Elevation = %g°) at %.2f GHz", elCut, freq/1e9);

% Elevation cut at azimuth = 0 degrees
azCut = 0;
D = patternElevation(ant, freq, azCut);
el = -180:1:180;
figure;
pp = polarpattern(el, D);
pp.AntennaMetrics = true;
pp.TitleTop = sprintf("Elevation Pattern (Azimuth = %g°) at %.2f GHz", azCut, freq/1e9);
```

### Pattern Comparison (Multiple Antennas)

```matlab
D1 = patternAzimuth(ant1, freq, 0);
D2 = patternAzimuth(ant2, freq, 0);
az = -180:1:180;
figure;
pp = polarpattern(az, D1);
add(pp, az, D2);
pp.AntennaMetrics = true;
pp.LegendLabels = {'Antenna 1', 'Antenna 2'};
```

Note: `LegendLabels` requires a cell array of character vectors, not a string array.

### Multi-Frequency Pattern

```matlab
freqs = [freq1, freq2, freq3];
az = -180:1:180;
D1 = patternAzimuth(ant, freqs(1), 0);
figure;
pp = polarpattern(az, D1);
for i = 2:numel(freqs)
    D = patternAzimuth(ant, freqs(i), 0);
    add(pp, az, D);
end
pp.AntennaMetrics = true;
pp.LegendLabels = arrayfun(@(f) sprintf('%.2f GHz', f/1e9), freqs, UniformOutput=false);
```

## Polarization Analysis

### Axial Ratio
For circularly/elliptically polarized antennas (helix, spiral, cloverleaf):
```matlab
figure;
axialRatio(ant, freq, 0, 0:1:360);
```

### Pattern with Polarization Components
```matlab
figure;
pattern(ant, freq, Type="directivity", Polarization="RHCP");
% Available: "combined", "LHCP", "RHCP", "H", "V"
```

## Key Metric Functions

```matlab
bw = beamwidth(ant, freq, azimuthAngle, elevationAngles);
fprintf("3 dB Beamwidth: %.1f degrees\n", bw);

[peakVal, peakAz, peakEl] = peakRadiation(ant, freq);
fprintf("Peak: %.2f dBi at Az=%.1f°, El=%.1f°\n", peakVal, peakAz, peakEl);
```

### Sidelobe Level
```matlab
D = patternAzimuth(ant, freq, 0);
az = -180:1:180;
figure;
pp = polarpattern(az, D);
pp.AntennaMetrics = true;
pp.Peaks = 3;  % Show top 3 peaks (main beam + sidelobes)
```

## polarpattern Properties Reference

| Property | Description | Values |
|----------|-------------|--------|
| `AntennaMetrics` | Show beamwidth, sidelobes, F/B ratio | `true` / `false` |
| `Peaks` | Number of peak markers to display | integer |
| `LegendLabels` | Labels for overlaid datasets | cell array of char vectors |
| `LegendVisible` | Show/hide legend | `true` / `false` |
| `AngleLim` | Restrict angle range displayed | `[minAngle maxAngle]` |
| `MagnitudeLim` | Set magnitude axis limits | `[min max]` |
| `NormalizeData` | Normalize pattern to peak | `true` / `false` |
| `Span` | Angular span display | angle in degrees |

## Analysis Code Template

```matlab
freq = <design_frequency>;
bw = 0.2 * freq;
freqRange = linspace(freq - bw/2, freq + bw/2, 51);

% Impedance
figure;
impedance(ant, freqRange);

% S-parameters
figure;
if isprop(ant, "Substrate") && ~isempty(ant.Substrate)
    try
        s = sparameters(ant, freqRange, SweepOption="interp");
    catch
        s = sparameters(ant, freqRange);
    end
else
    s = sparameters(ant, freqRange);
end
rfplot(s);

% 3D pattern
figure;
pattern(ant, freq);

% Key metrics
Z = impedance(ant, freq);
fprintf("Impedance: %.2f + j%.2f ohm\n", real(Z), imag(Z));
```

## Frequency Interpretation

- Parse units: MHz, GHz, Hz. Default to Hz if no unit given.
- For band names ("ISM band", "S-band", "UHF"), use the standard center frequency.
- For frequency ranges, design at center and sweep over the band.
- **Supported range:** Antenna Toolbox supports 10 kHz to 200 GHz. Validate that the parsed frequency falls within this range before proceeding.

## MATLAB Coding Standards

- Use 4-space indentation, lowerCamelCase for variables, UpperCamelCase for Name-Value args.
- Use `"double quotes"` for strings.
- Do not add titles to Antenna Toolbox plots (`show`, `impedance`, `rfplot`, `pattern`, `axialRatio`, etc.) -- they generate their own.
- **Do** add `TitleTop` to `polarpattern` objects -- they have no default title.
- Use `fprintf` for formatted numerical output.

## Guidelines

- **Do not over-explain** antenna theory. The user is a professional.
- **Use `design()` always** unless the user provides explicit custom dimensions.
- **Always enable `AntennaMetrics`** on 2D polar plots.
- **Show all plots in separate figures** so they are easy to inspect.
- **Include units** in all output (meters, ohms, dB, dBi, degrees).
- **If a requested antenna type is ambiguous**, list the options and ask.
- **Default elevation for azimuth cuts is 0 degrees** unless specified.
- **Default azimuth for elevation cuts is 0 degrees** unless specified.
- **If the antenna already exists** in the workspace, use it directly.

----

Copyright 2026 The MathWorks, Inc.
