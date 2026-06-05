---
name: matlab-create-custom-antenna
description: Build custom antennas from geometric shapes using MATLAB Antenna Toolbox customAntenna. Creates arbitrary 2D and 3D antenna structures from shape primitives (shape.Rectangle, shape.Box, shape.Cylinder, etc.) with boolean operations, extrusion, substrate support, and feed creation. Use when the user wants to build a non-catalog antenna from scratch, create a custom geometry, import STL/CAD, or needs 3D structures like waveguides, horns, or cavities.
license: MathWorks BSD-3-Clause
allowed-tools: mcp__matlab__evaluate_matlab_code mcp__matlab__check_matlab_code mcp__matlab__detect_matlab_toolboxes ReadMcpResourceTool
argument-hint: <antenna-description> <frequency>
metadata:
  author: MathWorks
  version: "1.0"
---

# Custom Antenna Design Skill

You are an expert RF and antenna engineer assisting a professional engineer with custom antenna design. Use MATLAB Antenna Toolbox `customAntenna` to build arbitrary antenna structures from `shape.*` primitives, configure feeds, add substrates, and analyze performance.

## When to Use

- User wants to build a non-catalog antenna from scratch using geometric primitives
- User needs custom geometry (not available as a catalog antenna)
- User wants to import STL/CAD geometry and add feeds
- User needs 3D structures like waveguides, horns, or cavities built from shapes
- User asks about boolean operations on antenna geometry

## When NOT to Use

- User wants a standard catalog antenna (dipole, patch, horn, etc.) — use `matlab-design-antenna`
- User wants a PCB antenna with stackup layers — use `matlab-designing-pcb-antennas`
- User wants to optimize antenna parameters — use `matlab-optimizing-antennas`

## Core Workflow

1. **Build shapes** -- Create 2D or 3D primitives from the `shape.*` namespace.
2. **Transform** -- Position shapes with `translate`, `rotate`, `scale`.
3. **Combine** -- Boolean operations: `+` (union), `-` (subtraction), `&` (intersection).
4. **Modify 3D structures** -- `removeFaces` for openings, `imprintShape` for feed contact.
5. **Extrude** -- `extrudeLinear` or `extrudeRotate` to convert 2D into 3D. Assign output arguments when using extrude.
6. **Add substrate** -- `addSubstrate` for dielectric regions (requires air bounding box).
7. **Create antenna** -- `customAntenna(Shape=finalShape)`.
8. **Create feed** -- `createFeed(ant, [x y z], numEdges)`.
9. **Mesh** -- `mesh(ant, MaxEdgeLength=..., MinEdgeLength=...)`.
10. **Analyze** -- `impedance`, `sparameters`, `pattern`, etc.

## shape.* vs antenna.* -- Two Different Namespaces

**This is the #1 source of confusion.** MATLAB has two shape namespaces:

| Namespace | Used With | Examples |
|-----------|----------|---------|
| `shape.*` | `customAntenna` | `shape.Rectangle`, `shape.Box`, `shape.Cylinder` |
| `antenna.*` | `pcbStack` | `antenna.Rectangle`, `antenna.Circle`, `antenna.Polygon` |

They are **not interchangeable**. `customAntenna` requires `shape.*` objects. `pcbStack` requires `antenna.*` objects.

## 2D Shape Primitives

All 2D shapes live in the XY plane (z = 0). They can be used directly as flat metal structures or extruded into 3D.

| Shape | Key Properties |
|-------|---------------|
| `shape.Rectangle` | `Length`, `Width`, `Center`, `NumPoints`, `Metal` |
| `shape.Circle` | `Radius`, `Center`, `NumPoints`, `Metal` |
| `shape.Ellipse` | `MajorAxis`, `MinorAxis`, `Center`, `Metal` |
| `shape.Polygon` | `Vertices` (N-by-3, z must be 0), `Metal` |

```matlab
r = shape.Rectangle(Length=0.05, Width=0.03);
c = shape.Circle(Radius=0.02, Center=[0.04, 0]);
p = shape.Polygon(Vertices=[0 0 0; 0.03 0 0; 0.015 0.04 0]);
```

All shapes default to `Metal="PEC"`. Set `Metal="Copper"` for realistic conductor loss.

Available metals: `PEC`, `Copper`, `Aluminium`, `Gold`, `Silver`, `Zinc`, `Tungsten`, `Lead`, `Iron`, `Steel`, `Brass`.

## 3D Shape Primitives

| Shape | Key Properties | Notes |
|-------|---------------|-------|
| `shape.Box` | `Length`, `Width`, `Height`, `Center` | Closed box (6 faces) |
| `shape.OpenBox` | `Length`, `Width`, `Height`, `Center` | Box with one face removed |
| `shape.Cylinder` | `Radius`, `Height`, `Center`, `Cap` | `Cap=[1 1]` = both ends closed |
| `shape.OpenCylinder` | `Radius`, `Height`, `Center` | Open-ended cylinder |
| `shape.Sphere` | `Radius`, `Center` | Full sphere |
| `shape.Custom3D` | `Vertices` (from triangulation) | Arbitrary 3D mesh |

3D shapes have both `Metal` and `Dielectric` properties:

```matlab
wg = shape.Box(Length=0.023, Width=0.010, Height=0.030, Metal="PEC");
sub = shape.Box(Length=0.06, Width=0.06, Height=1.6e-3, Dielectric="FR4");
```

## Boolean Operations

```matlab
combined = shape1 + shape2;        % union (or add(shape1, shape2))
slotted = ground - slot;           % subtraction (or subtract(ground, slot))
overlap = shape1 & shape2;         % intersection (or intersect(shape1, shape2))
```

Use `RetainShape=true` in `add`/`subtract` to preserve internal boundaries for correct meshing at junctions.

### createHole (For Slots in 2D Shapes)

For cutting holes or slots in 2D shapes, use `createHole` instead of subtraction. Subtraction (`-`) on 2D `shape.*` objects can produce geometry that fails to mesh:

```matlab
ground = shape.Rectangle(Length=0.1, Width=0.1);
slot = shape.Rectangle(Length=0.05, Width=0.003);
slottedGround = createHole(ground, slot);    % use this, not ground - slot
```

**For overlapping holes** (e.g., a cross-shaped slot), union the hole shapes first, then cut once:

```matlab
hSlot = shape.Rectangle(Length=0.05, Width=0.003);
vSlot = shape.Rectangle(Length=0.003, Width=0.05);
crossSlot = hSlot + vSlot;                    % union first
slottedGround = createHole(ground, crossSlot); % single cut
```

### Alternative: Direct Polygon Definition

When boolean operations (`createHole`, `-`) fail or produce meshing issues, define the final shape directly as a `shape.Polygon` with the target outline vertices. This avoids boolean operations entirely and is often cleaner for simple truncations, chamfers, or notches.

```matlab
% Instead of: rect - triangle (boolean subtraction)
% Define the truncated rectangle directly as a polygon:
halfL = patchL/2;
cornerClip = 0.008;

% Two opposite corners truncated (e.g., for circular polarization)
verts = [
    -halfL, -halfL, 0;
     halfL-cornerClip, -halfL, 0;
     halfL, -halfL+cornerClip, 0;
     halfL, halfL, 0;
    -halfL+cornerClip, halfL, 0;
    -halfL, halfL-cornerClip, 0];

truncatedPatch = shape.Polygon(Vertices=verts);
```

This approach is preferred when the final outline is simple to describe — fewer operations, no boolean failure modes, and explicit geometry intent.

## Transforms

```matlab
translate(shape, [dx, dy, dz]);
rotate(shape, angleDeg, [x1 y1 z1], [x2 y2 z2]);
rotateX(shape, angleDeg);  rotateY(shape, angleDeg);  rotateZ(shape, angleDeg);
scale(shape, factor);
```

**Shapes are handle objects** -- transforms modify the original. Use `copy(shape)` to preserve the original before transforming.

**Vertical rectangles (walls, pins):** Always rotate at the origin first, then translate. Rotating a translated shape around a point causes the large dimension to "swing" into an unexpected axis.

```matlab
% CORRECT: rotate at origin, then translate
wall = shape.Rectangle(Length=wallHeight, Width=wallSpan);
rotate(wall, 90, [0, 0, 0], [0, 1, 0]);  % tip into YZ plane
translate(wall, [x, y, wallHeight/2]);     % z spans 0 to wallHeight

% ERROR-PRONE: translate first, rotate around a point
wall = shape.Rectangle(Length=wallSpan, Width=wallHeight);
translate(wall, [x, y, wallHeight/2]);
rotate(wall, 90, [x, y, wallHeight/2], [x, y+1, wallHeight/2]);  % wallSpan swings into Z
```

## Extrusion: 2D to 3D

### extrudeLinear

Extrudes a 2D shape along the z-axis. The 2D shape **must be in the XY plane**.

```matlab
rect = shape.Rectangle(Length=0.023, Width=0.010);
box = extrudeLinear(rect, 0.030);    % height = 0.030 m

% Tapered extrusion (horn flare)
rect = shape.Rectangle(Length=0.023, Width=0.010);
horn = extrudeLinear(rect, 0.050, Scale=[2.5 2.0], NumSegments=1, Caps=false);
```

| Argument | Default | Description |
|----------|---------|-------------|
| `height` | -- | Extrusion height along z (m) |
| `Scale` | `1` | `[sx sy]` scale factor at the far end (creates taper) |
| `NumSegments` | `1` | Mesh segments along extrusion |
| `Caps` | `false` | Close both ends |
| `Direction` | `[0 0 1]` | Extrusion direction |
| `Twist` | `0` | Twist angle (degrees) |

**Critical:** The 2D shape must be in the XY plane. Extrude first, then `rotate` into position.

### extrudeRotate

Revolves a 2D shape around the z-axis. Creates bodies of revolution.

```matlab
profile = shape.Polygon(Vertices=[0.005 0 0; 0.01 0 0; 0.02 0.05 0; 0.015 0.05 0]);
hornRev = extrudeRotate(profile, 360, NumSegments=16);
```

| Argument | Default | Description |
|----------|---------|-------------|
| `angle` | -- | Revolution angle (degrees, 360 = full) |
| `NumSegments` | `3` | Segments around the revolution |
| `Caps` | `false` | Close the ends |
| `Pitch` | `0` | Z-advance per revolution (helical) |

## Modifying 3D Structures

### removeFaces

Opens a face on a closed 3D shape (e.g., waveguide aperture). Face numbering varies across shapes and MATLAB versions -- never hardcode face indices. To determine the correct face:

1. Run `removeFaces(sh)` with no face index via MATLAB evaluation -- this opens an interactive GUI displaying all face numbers. Identify the correct face from the GUI output. Do not include this exploratory call in the final code.
2. Use the resolved face number directly: `removeFaces(sh, faceIdx)`.

### imprintShape

Cuts a 2D shape outline into a 3D surface for clean feed contact:

```matlab
imprintCirc = shape.Circle(Radius=0.005);
translate(imprintCirc, [feedX 0 0]);
wgWithImprint = imprintShape(wg, imprintCirc);
```

## Feed Configuration

### Delta-Gap Feed Model

Antenna Toolbox uses a **delta-gap feed model**. The feed edge must be at a **geometric discontinuity** where current is forced *through* the edge, not *around* it:

| Feed Location | Why It Works |
|---|---|
| **Dipole gap** | Feed edge bridges the physical gap between two arms |
| **Slot edge** | Feed edge is at metal/air boundary |
| **Shape junction** (`shape1 + shape2`) | Boolean union creates shared edges |
| **Probe-to-wall junction** (FeedShape) | Probe creates new edges perpendicular to wall |
| **Circular gap** (large NumEdges) | Multiple RWG edges ring the circumference |

**A feed in the middle of a continuous flat plate gives ~0 ohm impedance.** Always place feeds at geometric boundaries.

### createFeed Syntax

**`FeedLocation` is read-only.** You must use `createFeed()` to define feeds.

```matlab
ant = customAntenna(Shape=antShape);
createFeed(ant, [x y z], numEdges);
createFeed(ant, [x y z], numEdges, FeedShape=probeShape);  % for 3D structures
```

| Argument | Description |
|----------|-------------|
| `[x y z]` | Feed point coordinates (N-by-3 for multi-feed). Must be on the metal surface. |
| `numEdges` | Number of mesh edges per feed. Must be `1` or `>= 3`. |
| `FeedShape` | Optional. A 2D `shape.*` object defining a physical feed probe. |

### Choosing the Right Feed Approach

| Antenna Type | Feed Approach | Example |
|---|---|---|
| **2D planar** (slot, dipole, patch at z=0) | Bare `createFeed(ant, loc, 1)` | Feed at slot edge or shape junction |
| **Probe-fed patch on substrate** (ground + raised patch) | Imprint on ground + `FeedShape=probeRect` | See "Probe-Fed Patch" below |
| **3D waveguide** (horn, slotted WG) | `FeedShape=probeRect` -- physical probe | Thin rectangle rotated into waveguide |
| **Body of revolution** (biconical, conical) | Bare `createFeed(ant, loc, N)` with large `NumEdges` | `NumEdges=20` for circular feed gap |

**Probe-fed patch warning:** For antennas where the feed bridges two parallel planes (ground to raised patch through a substrate), bare `createFeed(ant, loc, 1)` produces a feed edge as wide as the local mesh element. This gives unrealistically low impedance (typically 5-15 ohm instead of 50 ohm). Always use the imprint + FeedShape combination for these structures.

### 3D Waveguide Feeds (FeedShape)

Standard probe pattern for waveguide-based structures:

```matlab
probeH = narrowWall * 0.65;    % 50-70% of narrow wall height
probeW = 5.2e-5;               % very thin (0.052 mm)
feedrect = shape.Rectangle(Length=probeH, Width=probeW);
feedX = -wgLength/2 + lambda/4;     % lambda/4 from back wall
wallZ = -narrowWall/2;
translate(feedrect, [feedX, 0, wallZ + probeH/2]);
rotate(feedrect, 90, [feedX, 0, wallZ + probeH/2], [feedX, 1, wallZ + probeH/2]);
createFeed(ant, [feedX, 0, wallZ], 1, FeedShape=feedrect);
```

### Feed Width Control (Imprint Technique)

For probe-fed patches on substrate, use the imprint technique to control feed edge width. Without it, the feed edge width is determined by the mesh and gives unrealistically low impedance.

1. Create a rectangle with `Length = feedWidth/sqrt(2)` and `Width = feedWidth/sqrt(2)`.
2. Rotate 45 deg with `rotateZ(imprintRect, 45)`.
3. Translate to feed location.
4. `imprintShape(groundPlane, imprintRect)` to imprint the feed edge on the ground.
5. Combine the imprinted ground with other metal shapes.
6. Call `createFeed(ant, loc, 1, FeedShape=probeRect)` with a probe spanning ground to patch.

### Probe-Fed Patch on Substrate (Complete Pattern)

```matlab
% Ground with imprint at feed point
ground = shape.Rectangle(Length=gndL, Width=gndW);
feedWidth = 1.3e-3;  % SMA pin diameter (1.3 mm)
imprintRect = shape.Rectangle(Length=feedWidth/sqrt(2), Width=feedWidth/sqrt(2));
rotateZ(imprintRect, 45);
translate(imprintRect, [feedOffset, 0, 0]);
groundImprinted = imprintShape(ground, imprintRect);

% Patch raised to substrate height
patch = shape.Rectangle(Length=patchL, Width=patchW);
translate(patch, [0, 0, subH]);
metalShape = groundImprinted + patch;

% Substrate + air bounding box
substrate = shape.Box(Length=gndL, Width=gndW, Height=subH, ...
    Center=[0, 0, subH/2], Dielectric="FR4");
bbox = shape.Box(Length=0.2, Width=0.2, Height=0.1, ...
    Center=[0, 0, 0.05], Dielectric="Air", Transparency=0.1);
antShape = addSubstrate(metalShape, substrate + bbox);
ant = customAntenna(Shape=antShape);

% FeedShape: thin vertical probe from ground to patch
feedProbe = shape.Rectangle(Length=feedWidth, Width=subH);
translate(feedProbe, [feedOffset, 0, subH/2]);
rotate(feedProbe, 90, [feedOffset, 0, subH/2], [feedOffset+1, 0, subH/2]);
createFeed(ant, [feedOffset, 0, 0], 1, FeedShape=feedProbe);
```

**Feed offset controls impedance:** Moving the feed further from center increases the real part. Typical range: 15-35% of patch length for 20-120 ohm.

**Imprint + FeedShape conflict:** Do not place the imprint diamond too close to shape edges or vertices -- this can cause geometry errors. Keep a margin of at least 2x the imprint size from any edge.

### Circular Feed (extrude technique)

Use `extrude` to grow a circular cross-section out of a surface, creating shared edges at the junction:

```matlab
feed_circ = shape.Circle(Radius=radius, NumPoints=20);
translate(feed_circ, feed_loc);
sh = extrude(groundPlane, feed_circ, Height=height);
createFeed(ant, feed_loc, 20);   % numEdges matches NumPoints
```

### Strip Feed

After imprinting the feed edge, create a rectangle with strip dimensions perpendicular to the surface. The bottom edge must touch (not penetrate) the surface. Use `show()` to verify contact.

### Multi-Feed Excitation (R2026a+)

```matlab
createFeed(ant, [x1 y1 z1; x2 y2 z2], [1, 1]);
ant.FeedVoltage = [1, 1];     % amplitude per feed
ant.FeedPhase = [0, 90];      % phase per feed (degrees)
```

For detailed feed examples (dipole, cylindrical monopole, strip, biconical), see `references/Feed.md`.

## Dielectric Support (addSubstrate)

```matlab
gnd = shape.Rectangle(Length=0.06, Width=0.06);
patch = shape.Rectangle(Length=0.03, Width=0.03);
translate(patch, [0 0 subH]);
metalShape = gnd + patch;

substrate = shape.Box(Length=0.06, Width=0.06, Height=subH, ...
    Center=[0 0 subH/2], Dielectric="FR4");
bbox = shape.Box(Length=0.2, Width=0.2, Height=0.1, ...
    Center=[0 0 0.05], Dielectric="Air", Transparency=0.1);
subShape = substrate + bbox;

antShape = addSubstrate(metalShape, subShape);
```

**The air bounding box is required.** Make it several wavelengths larger than the antenna. It must extend slightly below the ground plane (e.g., 5 mm) to fully enclose the antenna volume.

## Meshing

**Always mesh explicitly** before analyzing custom antennas.

```matlab
c = physconst("LightSpeed");
lambda = c / freq;
mesh(ant, MaxEdgeLength=lambda/6, MinEdgeLength=lambda/20);
mem = memoryEstimate(ant, freq);
fprintf("Memory estimate: %s\n", mem);
```

## Analysis

```matlab
freq = 10e9;
freqRange = linspace(freq*0.8, freq*1.2, 31);

Z = impedance(ant, freq);
fprintf("Z = %.2f + j%.2f ohm\n", real(Z), imag(Z));

hasSubstrate = isprop(ant, "Substrate") && ~isempty(ant.Substrate);
if hasSubstrate
    try
        s = sparameters(ant, freqRange, SweepOption="interp");
    catch
        s = sparameters(ant, freqRange);
    end
else
    s = sparameters(ant, freqRange);
end
figure; rfplot(s);
figure; pattern(ant, freq);
figure; current(ant, freq);
```

**Feed coupling diagnostic:** If impedance seems unrealistically low, use `current(ant, freq, Scale="log")` to verify the feed is physically coupling. Log-scale current reveals whether current flows into the antenna structure even when the impedance number is unreliable due to feed/mesh mismatch. If current IS flowing on the radiating elements, the antenna is working -- the impedance accuracy can be improved separately with the imprint technique.

## STL/CAD Import via customAntennaStl

```matlab
ant = customAntennaStl;
ant.FileName = "horn.stl";
ant.Units = "mm";
createFeed(ant, [0 0 0], 1);
figure; show(ant);
mesh(ant, MaxEdgeLength=lambda/6);
```

Supported formats: `.stl`, `.step`, `.iges`. Set `UseFileAsMesh = true` if the STL mesh is already fine enough.

## Topology Templates

For complete code templates (horn, conical horn, patch on substrate, slot antenna, STL import), see `references/topologies.md`.

## MATLAB Coding Standards

- Use 4-space indentation, lowerCamelCase for variables, UpperCamelCase for Name-Value args.
- Use `"double quotes"` for strings.
- Do not add titles to Antenna Toolbox plots (`show`, `pattern`, `rfplot`, `impedance`, etc.).
- **Do** add titles to manual `plot()` figures.
- Use `fprintf` for formatted numerical output.
- Use `tiledlayout`/`nexttile` for multi-panel figures (never `subplot`).

## Must-Follow Rules

- **All dimensions in meters** -- shape properties are in meters, not mm or cm.
- **All frequencies in Hz** -- `impedance`, `pattern`, `design` expect Hz, not GHz.
- **Use `show()` to verify geometry before EM analysis** -- catches modeling errors early.
- **Always define a feed** -- `customAntenna` without `createFeed` cannot be analyzed.
- **Use `physconst('LightSpeed')`** -- never hardcode `3e8`.
- **Check mesh quality** -- use `mesh(ant, MaxEdgeLength=lambda/10)` before trusting results.

## Common Mistakes

```matlab
% WRONG -- dimensions in mm (30 m x 20 m!)
rect = shape.Rectangle(Length=30, Width=20);
% CORRECT
rect = shape.Rectangle(Length=0.03, Width=0.02);

% WRONG -- frequency in GHz (2.4 Hz!)
impedance(ant, 2.4);
% CORRECT
impedance(ant, 2.4e9);

% WRONG -- no feed defined
ant = customAntenna(Shape=myShape);
impedance(ant, 1e9);  % Error
% CORRECT
ant = customAntenna(Shape=myShape);
createFeed(ant, [0 0 0], 1);
impedance(ant, 1e9);

% WRONG -- internal boundary lost in CSG union
combined = add(waveguide, flare);
% CORRECT -- RetainShape preserves internal boundary
combined = add(waveguide, flare, RetainShape=1);
```

## Guidelines

- **Do not over-explain** antenna theory. The user is a professional.
- **Use `shape.*` classes** with `customAntenna`, never `antenna.*` classes.
- **Shapes are handle objects** -- transforms modify in-place. Use `copy()` if you need the original.
- **`extrudeLinear` requires XY-plane shapes** -- extrude first, then rotate into position.
- **`FeedLocation` is read-only** -- always use `createFeed()`.
- **Feed must be at a geometric discontinuity** -- place feeds at gaps, slot edges, shape junctions, or probe contact points.
- **Match the feed method to the topology** -- bare `createFeed` for 2D planar, `FeedShape` for waveguide, large `NumEdges` for body-of-revolution.
- **Use `FeedShape` for waveguide feeds** -- probe height controls coupling strength (50-70% of narrow wall). Section must be at least 3 lambda; use `design(waveguide, freq)` for dimensions.
- **Always mesh explicitly** before analysis. Use `imprintShape` when a feed probe meets a 3D surface.
- **`addSubstrate` requires an air bounding box** -- extend it below the ground plane.
- **`removeFaces` for openings** -- resolve face index interactively first, never hardcode.
- **`Polygon` vertices must have z=0** -- strictly 2D. Use extrusion for 3D.
- **Recommend `show()` after construction** to verify geometry before expensive analysis.
- **Check `memoryEstimate`** before analyzing electrically large structures.
- **Use `removeSlivers`** if boolean operations produce missing geometry artifacts.

----

Copyright 2026 The MathWorks, Inc.
