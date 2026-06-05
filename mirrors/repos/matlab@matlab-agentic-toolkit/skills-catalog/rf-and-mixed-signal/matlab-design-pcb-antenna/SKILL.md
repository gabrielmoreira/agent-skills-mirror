---
name: matlab-design-pcb-antenna
description: Design PCB antennas using MATLAB Antenna Toolbox pcbStack. Builds multi-layer stackups with custom metal patterns (boolean shape operations), probe/edge/aperture feeds, via stitching, and Gerber export for fabrication. Use when the user wants to design, build, or fabricate a PCB antenna, printed antenna, microstrip antenna from scratch, or convert a catalog antenna to PCB.
license: MathWorks BSD-3-Clause
allowed-tools: mcp__matlab__evaluate_matlab_code mcp__matlab__check_matlab_code mcp__matlab__detect_matlab_toolboxes ReadMcpResourceTool
argument-hint: <antenna-type> <frequency>
metadata:
  author: MathWorks
  version: "1.0"
---

# PCB Antenna Design Skill

You are an expert RF and antenna engineer assisting a professional engineer with PCB antenna design. Use MATLAB Antenna Toolbox `pcbStack` to build multi-layer printed circuit board antennas with custom metal patterns, configure feeds and vias, analyze performance, and generate Gerber files for fabrication.

## When to Use

- User wants to design a PCB antenna or printed antenna from scratch
- User wants to build a multi-layer antenna stackup
- User wants to convert a catalog antenna (patchMicrostrip, pifa) to pcbStack
- User wants to add custom metal patterns, slots, or parasitic elements to a PCB
- User asks about probe feed, edge feed, or aperture-coupled feed on a PCB
- User wants to export Gerber files for antenna fabrication
- User wants to add via stitching or shorting vias

## When NOT to Use

- User wants a simple catalog antenna analysis — use `matlab-design-antenna`
- User wants a matching network — use `matlab-design-matching-network`
- User wants a reflectarray with unit cells — use `matlab-design-reflectarray`
- User wants to design a curved reflector — use `matlab-design-reflector-antenna`

## Core Workflow

1. **Parse the request** -- Identify the antenna type, operating frequency, substrate, number of layers, feed method, and any constraints (board size, connector type).

2. **Design the stackup** -- Create a `pcbStack` with the correct layer ordering: metal shapes and dielectric objects, top-to-bottom.

3. **Configure feeds and vias** -- Set `FeedLocations` with correct layer indices, add vias for grounding or stitching.

4. **Analyze** -- Compute impedance, S-parameters, radiation pattern, and bandwidth.

5. **Export** -- Generate Gerber fabrication files with connector footprints.

## Layer Stack Construction

This is the most error-prone step. The `Layers` property is a cell array specified **top-to-bottom**, alternating between metal shapes and dielectric objects.

```matlab
% 3-layer: patch on FR4 with ground plane
subHeight = 1.6e-3;
sub = dielectric("FR4");

p = pcbStack;
p.BoardShape = antenna.Rectangle(Length=60e-3, Width=60e-3);
p.BoardThickness = subHeight;       % MUST be set BEFORE Layers
p.Layers = {patch, sub, ground};    % {metal(1), diel(2), metal(3)}
```

### Critical Rules

1. **Set `BoardThickness` BEFORE `Layers`** -- Setting `Layers` always overwrites the dielectric thickness with the current `BoardThickness`. If you set Layers first, the dielectric gets the default 10 mm thickness, and setting BoardThickness afterwards does NOT fix it. To suppress the warning, also set `sub.Thickness` to the same value as `BoardThickness` before assigning Layers.

2. **Layer indices reference cell array positions** -- In `FeedLocations` and `ViaLocations`, layer numbers are cell array indices (1, 2, 3, ...), not metal-only indices. In `{metal, diel, metal}`, the metals are at indices 1 and 3.

3. **First and last entries are typically metal** -- but dielectric layers can also appear as the first or last entry when needed (e.g., radome above the top patch, or substrate beneath the bottom feed layer). Example: `{diel, patch, diel, slottedGround, diel, feedLine}`.

4. **`BoardThickness` = total dielectric below top metal** -- For multi-substrate stacks, this equals the sum of all dielectric thicknesses.

### 3-Layer Stack (Most Common)

```matlab
% {topMetal(1), dielectric(2), bottomMetal(3)}
p.Layers = {patch, sub, ground};
p.FeedLocations = [x, y, 1, 3];    % sig=1(top), gnd=3(bottom)
```

### 2-Layer Stack (Air Dielectric)

When only two metal layers are specified with no dielectric object, the stack assumes air as the dielectric between them:

```matlab
% {topMetal(1), bottomMetal(2)} -- air dielectric assumed
p.Layers = {radiator, ground};
p.FeedLocations = [x, y, 1, 2];    % sig=1(top), gnd=2(bottom)
```

### 5-Layer Stack (Aperture-Coupled)

```matlab
% {radiator(1), upperSub(2), slottedGround(3), lowerSub(4), feedLine(5)}
p.BoardThickness = upperSubHeight + lowerSubHeight;
p.Layers = {radiator, upperSub, slottedGround, lowerSub, feedLine};
p.FeedLocations = [x, y, 5, 3];    % sig=5(feedLine), gnd=3(ground)
```

### Substrate Materials

| Material | EpsilonR | LossTangent | Use Case |
|----------|----------|-------------|----------|
| `"FR4"` | 4.8 | 0.026 | Prototyping, low cost |
| Custom `"RO4003C"` | 3.55 | 0.0027 | High-frequency, low loss |
| `"Teflon"` | 2.1 | 0.0002 | Very low loss |
| `"Air"` | 1.0 | 0 | 2-layer stacks with physical spacer |

For materials not in the built-in catalog, create a custom dielectric:

```matlab
sub = dielectric(Name="RO4003C", EpsilonR=3.55, LossTangent=0.0027, Thickness=h);
```

## Shape Operations for Metal Patterns

All shapes are in the `antenna` namespace. Build complex metal patterns using boolean operations.

### Available Shapes

| Shape | Key Properties |
|-------|---------------|
| `antenna.Rectangle` | `Length`, `Width`, `Center`, `NumPoints` |
| `antenna.Circle` | `Radius`, `Center`, `NumPoints` |
| `antenna.Ellipse` | `MajorAxis`, `MinorAxis`, `Center` |
| `antenna.Polygon` | `Vertices` (N-by-3 matrix) |
| `antenna.Triangle` | `InputType` ("SSS"/"SAS"/"ASA"), `Side`, `Angle` |

### Boolean Operations

```matlab
% Union: combine shapes
patchWithFeed = patch + feedLine;

% Subtraction: cut slots, notches, holes
gndWithSlot = ground - slot;
eNotch = patch - notch1 - notch2;

% Intersection: overlap region
overlap = shape1 & shape2;
```

### Geometric Transforms

```matlab
% Translate
shifted = translate(shape, [dx, dy, 0]);

% Rotate (requires axis definition, or use rotateZ convenience)
rotated = rotate(shape, angleDeg, [0 0 0], [0 0 1]);
rotated = rotateZ(shape, angleDeg);

% Mirror (for symmetric geometries — fractals, bowties, balanced structures)
mirrored = mirrorX(copy(shape));    % mirror across Y-axis
mirrored = mirrorY(copy(shape));    % mirror across X-axis

% Copy (duplicate before transforming to preserve original)
shapeCopy = copy(shape);

% Scale
bigger = scale(shape, factor);
```

### Common Patterns

```matlab
% Slot in ground plane
gnd = antenna.Rectangle(Length=60e-3, Width=60e-3);
slot = antenna.Rectangle(Length=30e-3, Width=2e-3);
slottedGround = gnd - slot;

% Cross-shaped patch
arm1 = antenna.Rectangle(Length=20e-3, Width=4e-3);
arm2 = antenna.Rectangle(Length=4e-3, Width=20e-3);
crossPatch = arm1 + arm2;

% Ring patch
ring = antenna.Circle(Radius=15e-3) - antenna.Circle(Radius=10e-3);

% Microstrip feed line (offset from center)
feedLine = antenna.Rectangle(Length=traceW, Width=traceL, Center=[0, -offset]);
topMetal = patch + feedLine;

% Corner-truncated patch for circular polarization
patch = antenna.Rectangle(Length=Lp, Width=Lp);
tri1 = antenna.Polygon(Vertices=[Lp/2, Lp/2, 0; Lp/2-tc, Lp/2, 0; Lp/2, Lp/2-tc, 0]);
tri2 = antenna.Polygon(Vertices=[-Lp/2, -Lp/2, 0; -Lp/2+tc, -Lp/2, 0; -Lp/2, -Lp/2+tc, 0]);
cpPatch = patch - tri1 - tri2;

% Parasitic patch (driven element + parasitic elements on same layer)
driven = antenna.Rectangle(Length=L, Width=W);
parasitic1 = antenna.Rectangle(Center=[L/2+gap+stripL/2, 0], Length=stripL, Width=W);
parasitic2 = antenna.Rectangle(Center=[-L/2-gap-stripL/2, 0], Length=stripL, Width=W);
topMetal = driven + parasitic1 + parasitic2;

% Series-fed coupled patches (patches joined by microstrip strips)
p1 = antenna.Rectangle(Length=L, Width=W);
p2 = antenna.Rectangle(Length=L, Width=W, Center=[spacing, 0]);
p3 = antenna.Rectangle(Length=L, Width=W, Center=[-spacing, 0]);
strip1 = antenna.Rectangle(Length=stripLen, Width=stripW, Center=[spacing/2, 0]);
strip2 = antenna.Rectangle(Length=stripLen, Width=stripW, Center=[-spacing/2, 0]);
seriesFed = p1 + p2 + p3 + strip1 + strip2;
```

## Feed Configuration

### Delta-Gap Feed Model

`pcbStack` uses the same **delta-gap feed model** as all Antenna Toolbox antennas. The excitation voltage is applied across RWG mesh edges at the feed point — peak voltage at the feed edge, zero everywhere else.

For a probe feed (unbalanced), the delta-gap acts across the edge connecting the feed pin to the ground plane. **Feed offset from the patch center controls impedance** because it determines where on the patch's standing-wave current distribution the probe taps in:

- **Center of patch**: current antinode (high current, low voltage) → near-zero impedance
- **Edge of patch**: current node (low current, high voltage) → high impedance (~200+ ohm)
- **Offset ~1/4 to 1/3 from center**: intermediate impedance → tune for ~50 ohm match

This is why `design()` returns a non-zero `FeedOffset` — it places the probe where the impedance is closest to 50 ohm.

### Unbalanced Feed (Most Common)

Format: `[x, y, sigLayer, gndLayer]` -- 4 columns. Connects signal metal to ground metal through the substrate.

```matlab
% Probe feed: offset from patch center for impedance matching
p.FeedLocations = [patchL/4, 0, 1, 3];
p.FeedDiameter = 1e-3;    % coaxial pin diameter
```

### Edge Feed

Place the feed at the board edge for edge-launch connectors:

```matlab
% Feed at south edge of 60x60 mm board
p.FeedLocations = [0, -30e-3, 1, 3];
```

### Multi-Feed (Dual Polarization / CP)

Stack rows in `FeedLocations`. Use `FeedVoltage` and `FeedPhase` to control excitation:

```matlab
p.FeedLocations = [7e-3, 0, 1, 3;     % feed 1: x-polarized
                   0, 9e-3, 1, 3];     % feed 2: y-polarized
p.FeedVoltage = [1, 1];
p.FeedPhase = [0, 90];                 % 90 deg offset for CP
```

### Balanced Feed

Format: `[x, y, layer]` -- 3 columns. For dipole-like structures on a single layer:

```matlab
p.FeedLocations = [0, 0, 1];    % balanced feed on layer 1
```

### FeedViaModel

Controls the mesh approximation of the cylindrical feed probe:

| Model | Sides | Mesh Size | When to Use |
|-------|-------|-----------|-------------|
| `"strip"` | 2 (flat) | Smallest | Default, fast analysis |
| `"square"` | 4 | Small | Better probe modeling |
| `"hexagon"` | 6 | Medium | More accurate |
| `"octagon"` | 8 | Largest | Most accurate probe shape |

Use `"strip"` (default) unless you need accurate probe radiation modeling.

## Via Configuration

Vias are electrical shorts between metal layers. Format: `[x, y, sigLayer, gndLayer]`.

```matlab
% Four corner vias connecting patch layer to ground
p.ViaLocations = [25e-3, 25e-3, 1, 3;
                  25e-3, -25e-3, 1, 3;
                  -25e-3, 25e-3, 1, 3;
                  -25e-3, -25e-3, 1, 3];
p.ViaDiameter = 0.8e-3;    % scalar: same for all vias
```

**Via fencing** -- place vias along the board perimeter to suppress surface waves and improve isolation. Generate positions programmatically:

```matlab
% Via fence along board perimeter
nVias = 20;
theta = linspace(0, 2*pi, nVias+1);
theta = theta(1:end-1);
viaRadius = 28e-3;  % slightly inside board edge
vx = viaRadius * cos(theta);
vy = viaRadius * sin(theta);
p.ViaLocations = [vx(:), vy(:), ones(nVias,1), 3*ones(nVias,1)];
p.ViaDiameter = 0.5e-3;
```

## Conductor Material

Default is PEC (perfect electric conductor). For realistic loss modeling:

```matlab
p.Conductor = metal("Copper");    % 1 oz copper (35.56 um thick)
```

Available metals: `PEC`, `Copper`, `Aluminium`, `Gold`, `Silver`. View full catalog with `openMetalCatalog`.

## Analysis

All standard Antenna Toolbox analysis functions work on `pcbStack`:

```matlab
freq = 2.4e9;
freqRange = linspace(2e9, 3e9, 21);

% Impedance
Z = impedance(p, freq);
fprintf("Z = %.2f + j%.2f ohm\n", real(Z), imag(Z));

% S-parameters (use interpolating sweep for faster analysis)
try
    s = sparameters(p, freqRange, SweepOption="interp");
catch
    s = sparameters(p, freqRange);
end
figure;
rfplot(s);

% Radiation pattern
figure;
pattern(p, freq);

% Pattern types: directivity (lossless), gain (material losses), realizedgain (material + mismatch)
pattern(p, freq, Type="directivity");
pattern(p, freq, Type="gain");
pattern(p, freq, Type="realizedgain");

% Active element pattern (multi-feed): excite one port, terminate others
p.FeedVoltage = [1 0];   % port 1 active, port 2 terminated
pattern(p, freq);

% Bandwidth (requires a frequency vector, not a scalar)
freqSweep = linspace(freq*0.8, freq*1.2, 31);
bw = bandwidth(p, freqSweep);
fprintf("Bandwidth (-10 dB): %.2f MHz\n", bw/1e6);

% Efficiency
eff = efficiency(p, freq);
fprintf("Efficiency: %.1f%%\n", eff*100);
```

### Interpolating S-Parameter Sweep

With the RF Toolbox, `SweepOption="interp"` uses rational fitting to interpolate S-parameters from fewer EM solves. This is significantly faster for wideband sweeps on substrate-backed antennas and produces smoother curves. Always use it when available.

### Mesh Control

```matlab
c = physconst("LightSpeed");
lambda = c / freq;

% Refine mesh for better accuracy (slower)
mesh(p, MaxEdgeLength=lambda/15);

% Check memory before heavy analysis
mem = memoryEstimate(p, freq);
fprintf("Memory estimate: %s\n", mem);

% For antennas with fine slots/notches next to large patches, control
% mesh transition with MinEdgeLength and GrowthRate
mesh(p, MaxEdgeLength=0.01, MinEdgeLength=0.001, GrowthRate=0.7);
% GrowthRate (0-1): lower = smoother size transition from fine to coarse.
% Use when fine features (narrow slots, thin arms) sit near large metal areas.

% Fallback: if MaxEdgeLength alone doesn't resolve narrow features,
% force mesh points along specific shape edges
feed = antenna.Rectangle(Length=traceW, Width=traceL, NumPoints=[2 40 2 40]);
```

### Visualization

```matlab
figure; show(p);       % 3D structure with layer colors
figure; layout(p);     % 2D PCB layout view (top-down)
figure; mesh(p, MaxEdgeLength=lambda/10);    % mesh visualization
```

## Catalog Antenna Conversion

Convert any supported catalog antenna to `pcbStack` for Gerber export or further customization:

```matlab
ant = design(patchMicrostrip, 2.4e9);
pb = pcbStack(ant);

% Now customize: change conductor, add vias, export Gerber
pb.Conductor = metal("Copper");
pb.FeedDiameter = 1.27e-3;
```

Supported catalog antennas: `patchMicrostrip`, `patchMicrostripCircular`, `patchMicrostripEnotch`, `patchMicrostripInsetfed`, `dipole`, `bowtieTriangular`, `vivaldi`, `spiralArchimedean`, `lpda`, `slot`, and others. Arrays (`linearArray`, `rectangularArray`, `circularArray`) also convert if homogeneous.

**Note:** `design()` does not work directly on `pcbStack`. Design the catalog antenna first, then convert.

For post-conversion layer manipulation, Tilt/TiltAxis for exciter use, STL export, PCB array fabrication (`array()`), and Gerber import (`gerberRead`), see `references/advanced-workflows.md`.

## Gerber Export for Fabrication

### Basic Export

```matlab
[A, g] = gerberWrite(p);    % returns PCBWriter object and output folder path
```

**Requirement:** The `Layers` cell array must include at least one dielectric layer.

### With Connector and Manufacturing Service

```matlab
W = PCBServices.OSHParkWriter;
W.Filename = 'my_antenna';        % MUST be char, not "string"

C = PCBConnectors.SMA_Cinch;      % through-hole SMA

A = PCBWriter(p, W, C);
gerberWrite(A);
```

**Filename gotcha:** `Writer.Filename` requires a char vector (`'single quotes'`). Using a double-quoted string throws an error.

### Edge-Launch Connector

```matlab
C = PCBConnectors.SMAEdge_Samtec;
C.EdgeLocation = 'south';           % 'north', 'south', 'east', 'west'
C.ExtendBoardProfile = true;        % extend board outline for connector

% Feed must be at the matching board edge
p.FeedLocations = [0, -boardW/2, 1, 3];
```

### No Connector

```matlab
A = PCBWriter(p);
A.UseDefaultConnector = false;
gerberWrite(A);
```

### Available Connectors

| Type | Examples |
|------|---------|
| Through-hole SMA | `SMA_Cinch`, `SMA_Multicomp` |
| Edge-launch SMA | `SMAEdge_Samtec`, `SMAEdge_Amphenol`, `SMAEdge_Cinch` |
| Coaxial | `Coax_RG58`, `Coax_RG174` |
| U.FL / IPX | `UFL_Hirose`, `IPX_Jack_LightHorse` |
| MMCX | `MMCX_Cinch`, `MMCX_Samtec` |

### Available Manufacturing Services

`OSHParkWriter`, `PCBWayWriter`, `SeeedWriter`, `MayhewWriter`, `EuroCircuitsWriter`, `AdvancedCircuitsWriter`, and others.

## Topology Templates

For complete code templates of common PCB antenna designs (probe-fed patch, microstrip-fed slot, aperture-coupled patch, corner-truncated CP patch, parasitic patch, series-fed array, stacked patch), see `references/topologies.md`.

## MATLAB Coding Standards

- Use 4-space indentation, lowerCamelCase for variables, UpperCamelCase for Name-Value args.
- Use `"double quotes"` for strings -- except `Writer.Filename` which requires `'char'`.
- Do not add titles to Antenna Toolbox plots (`show`, `pattern`, `rfplot`, `impedance`, etc.).
- **Do** add titles to manual `plot()` figures.
- Use `fprintf` for formatted numerical output.

## Guidelines

- **Do not over-explain** PCB antenna theory. The user is a professional.
- **Always set `BoardThickness` before `Layers`** -- this is the #1 source of silent errors.
- **Layer indices are cell array positions** -- remind the user that in `{M, D, M}`, the ground is index 3, not index 2.
- **Use `design()` on catalog antennas first**, then convert with `pcbStack(ant)`. `design()` does not work directly on pcbStack.
- **Use boolean operations** (`+`, `-`) for custom metal patterns -- not manual vertex arithmetic.
- **Start from physical reasoning** for feed placement: offset from center for probe feeds, board edge for edge-launch.
- **Recommend `show()` and `layout()`** after construction so the user can visually verify the stackup.
- **For Gerber export**, always specify a dielectric layer and use char for `Filename`.
- **Check `memoryEstimate`** before analyzing electrically large or multi-layer structures.
- **Default to MoM solver** -- FEM requires RF PCB Toolbox and has significant restrictions (PEC only, fixed excitation, limited analysis).

----

Copyright 2026 The MathWorks, Inc.
