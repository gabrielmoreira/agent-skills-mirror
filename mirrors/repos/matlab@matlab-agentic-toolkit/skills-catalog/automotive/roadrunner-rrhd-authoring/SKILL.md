---
name: roadrunner-rrhd-authoring
description: >
  Build RoadRunner HD Map entities in MATLAB — lanes, boundaries, markings, junctions, signs,
  signals, barriers, parking. Use when creating driving scenes from scratch, authoring road
  networks for simulation and testing automated driving systems, or assembling RRHD maps
  from Lanelet2 or other HD map sources.
license: MathWorks BSD-3-Clause
metadata:
  author: MathWorks
  version: "1.0"
---

# RRHD Authoring Skill

Build RoadRunner HD Map (`.rrhd`) entities directly using the `roadrunnerHDMap` API in MATLAB. No external builder scripts required.

## When to Use

- Building RRHD maps from scratch (synthetic scenes, test roads)
- Assembling RRHD entities from converted map data (Lanelet2, OpenDRIVE)
- Adding lanes, boundaries, markings, junctions, signs, barriers, or parking to an HD Map
- Need verified `roadrunner.hdmap.*` class/property reference and construction patterns
- Debugging RRHD construction errors (wrong property names, alignment issues)

## When NOT to Use

- Converting Lanelet2 .osm files — use `roadrunner-convert-lanelet2-to-rrhd` (which invokes this skill)
- Looking up asset paths for markings/signs/barriers — use `roadrunner-asset-mapping`
- Importing finished .rrhd into RoadRunner — use `roadrunner-import-scene`
- Editing an existing RoadRunner scene interactively (this skill writes .rrhd files, not scene edits)

## Key Rules

- **Always write to .m files.** Never put multi-line MATLAB code directly in `evaluate_matlab_code`. Write to a `.m` file, run with `run_matlab_file`, edit on error.
- **Read references/apiReference.md** before writing any RRHD construction code.
- **Only build what the user asked for.** Do not add extra lanes, junctions, or objects unless explicitly requested.
- **`rrMap = roadrunnerHDMap;` must come first** — loads the namespace before any `roadrunner.hdmap.*` usage.
- **Create-then-assign pattern** — never pass constructor args (except `RelativeAssetPath` and `AlignedReference`).
- **Empty typed arrays** — use `ClassName.empty` not `[]`.
- **All geometry must be Nx3** — always include Z column (default 0 if flat).
- **Run enforcement gate before `write()`** — alignment, spatial, and geometry checks are mandatory.

## Critical API Rules

**You MUST create a `roadrunnerHDMap` object before using any `roadrunner.hdmap.*` classes** (lazy namespace loading):
```matlab
rrMap = roadrunnerHDMap;  % REQUIRED — loads the namespace
```

**Create-then-assign pattern** — never pass constructor args (except Name=Value for two classes):
```matlab
ref = roadrunner.hdmap.Reference;
ref.ID = "myID";  % assign after creation
```

**Name=Value constructors** — ONLY `RelativeAssetPath` and `AlignedReference` accept Name=Value:
```matlab
rap = roadrunner.hdmap.RelativeAssetPath(AssetPath="Assets/Markings/StopLine.rrlms");
ar = roadrunner.hdmap.AlignedReference(Reference=ref, Alignment="Forward");
% WRONG: positional args error with "A name is expected"
```

**Empty typed arrays** — never use `[]` for typed properties:
```matlab
lane.Predecessors = roadrunner.hdmap.AlignedReference.empty;  % CORRECT
lane.Predecessors = [];  % WRONG: "Value must be of type AlignedReference"
```

## Verified Property Names (R2025a+)

See [references/apiReference.md](references/apiReference.md) for the complete verified class/property table. Key gotchas:

| Common Mistake | Correct |
|---|---|
| `LeftBoundary` | `LeftLaneBoundary` |
| `RightBoundary` | `RightLaneBoundary` |
| `Speed` | `Value` (int32) |
| `Unit = "KPH"` | `VelocityUnit = "Kph"` |
| `ParametricAttrib` | `ParametricAttribution` |
| `pa.Value = mr` | `pa.MarkingReference = mr` |
| `pa.StartFraction/EndFraction` | `pa.Span = [0 1]` (double array) |
| `JunctionPhase` | `Phase` |
| `roadrunnerHDMap("file.rrhd")` | `rrMap = roadrunnerHDMap; read(rrMap, "file.rrhd")` |
| Nx2 geometry | Nx3 geometry (always include Z column) |
| `cm.CurveMarkingTypeID` | `cm.MarkingTypeReference` |
| `b.BarrierTypeID` | `b.BarrierTypeReference` |
| `s.SignTypeID` | `s.SignTypeReference` |
| `s.BoundingBox` | `s.Geometry` (takes GeoOrientedBoundingBox) |
| `bb.Position` | `bb.Center` (1x3 double) |
| `bb.Orientation` | `bb.GeoOrientation` ([h,p,r] double array) |
| `pg.OuterRing` | `pg.ExteriorRing` (Nx3 double) |
| `bt.AssetPath` | `bt.ExtrusionPath` (for BarrierType only) |
| `roadrunner.hdmap.GeoOrientation` | NOT a class — use `[h,p,r]` double array directly |
| `Lane.Predecessors = []` | `Lane.Predecessors = roadrunner.hdmap.AlignedReference.empty` |
| `lb.ParametricAttributes = []` | Cannot clear — skip assignment for no markings |
| `RelativeAssetPath("path")` | `RelativeAssetPath(AssetPath="path")` — Name=Value required |
| `AlignedReference(ref, "Fwd")` | `AlignedReference(Reference=ref, Alignment="Forward")` |
| `Junction.Geometry = polygon` | `Junction.Geometry = multiPolygon` (wrap in MultiPolygon) |
| `MarkingReference.MarkingID = 5` | `MarkingReference.MarkingID = ref` (Reference object, NOT numeric) |
| `SpeedLimit.Velocity` | `SpeedLimit.Value` (int32) + `.VelocityUnit = "Kph"` |

## Synthetic Scene Construction

### Lane Width and Geometry

Standard lane width: **3.7m** (US highway). Compute boundary positions by offsetting perpendicular to the lane center line direction.

### Shared Boundaries Between Adjacent Lanes

**Adjacent lanes MUST share boundary geometry.** The right boundary of lane N is the same object as the left boundary of lane N+1. For N lanes, create N+1 boundaries.

```
  LB_0 (left edge)
  ───────────────────
  │    Lane_1        │  left=LB_0(Fwd), right=LB_1(Fwd)
  ───────────────────
  LB_1 (shared)
  ───────────────────
  │    Lane_2        │  left=LB_1(Fwd), right=LB_2(Fwd)
  ───────────────────
  LB_2 (right edge)
```

### Alignment Rules

See [references/alignmentRules.md](references/alignmentRules.md) and [scripts/detectAlignment.m](scripts/detectAlignment.m) for complete rules, diagrams, and green-surface debugging.

Alignment specifies how boundary geometry direction relates to lane geometry direction:
- **Same direction → `"Forward"`**
- **Opposite direction → `"Backward"`**

**Two-step algorithm: proximity detection + spatial verification.**

A simple dot product is NOT sufficient — it misses cases where boundaries are spatially swapped (left boundary assigned to right side). The corrected algorithm:

```matlab
% Step 1: Proximity — are boundaries digitized same or opposite direction?
d_starts = norm(leftGeom(1,1:2) - rightGeom(1,1:2));
d_cross  = norm(leftGeom(1,1:2) - rightGeom(end,1:2));

if d_starts <= d_cross
    % Both boundaries go same direction — determine which direction
    laneDir = (leftGeom(end,1:2)+rightGeom(end,1:2))/2 ...
            - (leftGeom(1,1:2)+rightGeom(1,1:2))/2;
    laneDir = laneDir / norm(laneDir);
    leftNormal = [-laneDir(2), laneDir(1)];  % 90 deg CCW
    toLeft = mean(leftGeom(:,1:2)) - mean(rightGeom(:,1:2));
    if dot(toLeft, leftNormal) >= 0
        leftAlign = "Forward"; rightAlign = "Forward";
    else
        leftAlign = "Backward"; rightAlign = "Backward";
    end
else
    % Boundaries go opposite directions
    laneDirA = leftGeom(end,1:2) - leftGeom(1,1:2);
    laneDirA = laneDirA / norm(laneDirA);
    leftNormalA = [-laneDirA(2), laneDirA(1)];
    toLB = mean(leftGeom(:,1:2)) - mean(rightGeom(:,1:2));
    if dot(toLB, leftNormalA) >= 0
        leftAlign = "Forward"; rightAlign = "Backward";
    else
        leftAlign = "Backward"; rightAlign = "Forward";
    end
end
```

**Left/Right spatial verification** (MANDATORY — catches swapped boundaries):
```matlab
laneDir2D = laneGeom(end,1:2) - laneGeom(1,1:2);
laneDir2D = laneDir2D / norm(laneDir2D);
leftNormal = [-laneDir2D(2), laneDir2D(1)];  % 90 deg CCW
centerToBnd = mean(leftBndGeom(:,1:2)) - mean(laneGeom(:,1:2));
assert(dot(centerToBnd, leftNormal) > 0, ...
    'Left boundary is spatially on the RIGHT — swap boundaries or fix assignment');
```

Wrong alignment or swapped left/right causes **green grass instead of road surface**.

### Standard Marking Assets

| Marking ID | Asset Path |
|---|---|
| `SolidSingleWhite` | `Assets/Markings/SolidSingleWhite.rrlms` |
| `DashedSingleWhite` | `Assets/Markings/DashedSingleWhite.rrlms` |
| `SolidDoubleYellow` | `Assets/Markings/SolidDoubleYellow.rrlms` |
| `DashedSolidYellow` | `Assets/Markings/DashedSolidYellow.rrlms` |
| `SolidDashedYellow` | `Assets/Markings/SolidDashedYellow.rrlms` |

### Multi-Lane Road Recipe

1. Compute N lane center lines (evenly spaced at `laneWidth` intervals)
2. Compute N+1 boundary lines (edges + between each lane pair)
3. Assign shared boundaries (lane i: `left=LB_(i-1)`, `right=LB_i`)
4. Detect alignment via dot product
5. Apply markings (edges: `SolidSingleWhite`, divider: `SolidDoubleYellow`, separators: `DashedSingleWhite`)
6. Wire topology (if multiple segments, connect with pred/succ)
7. Snap connected endpoints — see [scripts/snapConnectedEndpoints.m](scripts/snapConnectedEndpoints.m)
8. Resolve height conflicts — see [scripts/resolveHeightConflicts.m](scripts/resolveHeightConflicts.m)
9. Assemble map and write

### Complete 2-Lane Road Example

```matlab
rrMap = roadrunnerHDMap;
w = 3.7;

% Lane Markings
lm1 = roadrunner.hdmap.LaneMarking; lm1.ID = "SolidWhite";
rap1 = roadrunner.hdmap.RelativeAssetPath; rap1.AssetPath = "Assets/Markings/SolidSingleWhite.rrlms";
lm1.AssetPath = rap1;
lm2 = roadrunner.hdmap.LaneMarking; lm2.ID = "DashedWhite";
rap2 = roadrunner.hdmap.RelativeAssetPath; rap2.AssetPath = "Assets/Markings/DashedSingleWhite.rrlms";
lm2.AssetPath = rap2;

% Boundaries (3 for 2 lanes)
lb = roadrunner.hdmap.LaneBoundary;
lb(2) = roadrunner.hdmap.LaneBoundary;
lb(3) = roadrunner.hdmap.LaneBoundary;
lb(1).ID = "LB_0"; lb(1).Geometry = [0 w 0; 100 w 0];
lb(2).ID = "LB_1"; lb(2).Geometry = [0 0 0; 100 0 0];
lb(3).ID = "LB_2"; lb(3).Geometry = [0 -w 0; 100 -w 0];

% Markings on boundaries
for i = [1 3]  % solid on edges
    pa = roadrunner.hdmap.ParametricAttribution; pa.Span = [0 1];
    ref = roadrunner.hdmap.Reference; ref.ID = "SolidWhite";
    mr = roadrunner.hdmap.MarkingReference; mr.MarkingID = ref; mr.FlipLaterally = false;
    pa.MarkingReference = mr;
    lb(i).ParametricAttributes = pa;
end
pa = roadrunner.hdmap.ParametricAttribution; pa.Span = [0 1];
ref = roadrunner.hdmap.Reference; ref.ID = "DashedWhite";
mr = roadrunner.hdmap.MarkingReference; mr.MarkingID = ref; mr.FlipLaterally = false;
pa.MarkingReference = mr;
lb(2).ParametricAttributes = pa;

% Lanes
ln = roadrunner.hdmap.Lane;
ln(2) = roadrunner.hdmap.Lane;
ln(1).ID = "Lane_1"; ln(1).Geometry = [0 w/2 0; 100 w/2 0];
ln(1).TravelDirection = "Forward"; ln(1).LaneType = "Driving";
ln(2).ID = "Lane_2"; ln(2).Geometry = [0 -w/2 0; 100 -w/2 0];
ln(2).TravelDirection = "Forward"; ln(2).LaneType = "Driving";

% Assign boundaries with alignment
bndIDs = ["LB_0","LB_1","LB_2"];
for i = 1:2
    arL = roadrunner.hdmap.AlignedReference;
    refL = roadrunner.hdmap.Reference; refL.ID = bndIDs(i);
    arL.Reference = refL; arL.Alignment = "Forward";
    ln(i).LeftLaneBoundary = arL;

    arR = roadrunner.hdmap.AlignedReference;
    refR = roadrunner.hdmap.Reference; refR.ID = bndIDs(i+1);
    arR.Reference = refR; arR.Alignment = "Forward";
    ln(i).RightLaneBoundary = arR;
end

% Assemble and write
rrMap.Lanes = ln;
rrMap.LaneBoundaries = lb;
rrMap.LaneMarkings = [lm1 lm2];
write(rrMap, "two_lane_road.rrhd");
```

## Enforcement Gate (MANDATORY before `write()`)

Run this validation block before writing any multi-lane map. Do NOT skip.

```matlab
%% --- ENFORCEMENT: Alignment computed (not all Forward) ---
lanes = rrMap.Lanes;
if numel(lanes) > 2
    nFwd = 0; nBwd = 0;
    for i = 1:numel(lanes)
        if lanes(i).LeftLaneBoundary.Alignment == "Forward", nFwd = nFwd+1;
        else, nBwd = nBwd+1; end
        if lanes(i).RightLaneBoundary.Alignment == "Forward", nFwd = nFwd+1;
        else, nBwd = nBwd+1; end
    end
    assert(nBwd > 0 || numel(lanes) <= 2, ...
        'ALIGNMENT ERROR: All boundaries Forward for %d lanes — compute dot product per lane.', numel(lanes));
    fprintf('Alignment: %d Forward, %d Backward — OK\n', nFwd, nBwd);
end

%% --- ENFORCEMENT: Left boundary spatially on left ---
bnds = rrMap.LaneBoundaries;
bndMap = containers.Map;
for i = 1:numel(bnds), bndMap(bnds(i).ID) = bnds(i).Geometry; end
nBadSide = 0;
for i = 1:numel(lanes)
    lGeom = lanes(i).Geometry;
    lDir = lGeom(end,1:2) - lGeom(1,1:2);
    lDir = lDir / norm(lDir);
    leftN = [-lDir(2), lDir(1)];
    leftBndID = lanes(i).LeftLaneBoundary.Reference.ID;
    if bndMap.isKey(leftBndID)
        leftBndGeom = bndMap(leftBndID);
        toBnd = mean(leftBndGeom(:,1:2)) - mean(lGeom(:,1:2));
        if dot(toBnd, leftN) < 0, nBadSide = nBadSide + 1; end
    end
end
assert(nBadSide == 0, ...
    'SPATIAL ERROR: %d lanes have left boundary on wrong side — fix alignment algorithm.', nBadSide);
fprintf('Spatial left-side check: PASS\n');

%% --- ENFORCEMENT: Geometry is Nx3 ---
bnds = rrMap.LaneBoundaries;
for i = 1:numel(bnds)
    assert(size(bnds(i).Geometry, 2) == 3, ...
        'Boundary %s geometry must be Nx3 (got Nx%d)', bnds(i).ID, size(bnds(i).Geometry,2));
end
fprintf('Geometry dimensions: PASS\n');

%% --- ENFORCEMENT: GeoReference set ---
assert(any(rrMap.GeoReference ~= 0), 'GeoReference is [0,0] — set lat/lon origin');
fprintf('GeoReference: PASS\n');
```

## Post-Processing

### Endpoint Snapping

For connected lanes (pred/succ), snap successor start to predecessor end. See [scripts/snapConnectedEndpoints.m](scripts/snapConnectedEndpoints.m) and [references/snapEndpoints.md](references/snapEndpoints.md).

### Height Conflict Resolution

Overlapping unconnected lanes at the same Z cause grass artifacts. Use graph coloring to assign Z-levels. See [scripts/resolveHeightConflicts.m](scripts/resolveHeightConflicts.m) and [references/resolveHeights.md](references/resolveHeights.md).

## Additional Entity Types

- **Lanes** — See [references/lanes.md](references/lanes.md)
- **Speed Limits** — See [references/speedLimits.md](references/speedLimits.md)
- **Lane Boundaries** — See [references/laneBoundaries.md](references/laneBoundaries.md)
- **Lane Groups** — See [references/laneGroups.md](references/laneGroups.md)
- **Lane Markings** — See [references/laneMarkings.md](references/laneMarkings.md)
- **Junctions** — See [references/junctions.md](references/junctions.md) and [references/junctionPolygon.md](references/junctionPolygon.md) for polygon construction
- **Barriers** — See [references/barriers.md](references/barriers.md)
- **Signs & Signals** — See [references/signs.md](references/signs.md), [references/signals.md](references/signals.md)
- **Static Objects** — See [references/staticObjects.md](references/staticObjects.md)
- **Stencil Markings** — See [references/stencilMarkings.md](references/stencilMarkings.md)
- **Curve Markings** — See [references/curveMarkings.md](references/curveMarkings.md)
- **Parking Spaces** — See [references/parkingSpaces.md](references/parkingSpaces.md)
- **Assemble Map** — See [references/assembleMap.md](references/assembleMap.md)
- **Validate Map** — See [references/validateMap.md](references/validateMap.md) and [scripts/validateRRHD.m](scripts/validateRRHD.m)
- **Arc Length to Parametric** — See [references/arcLengthToParametric.md](references/arcLengthToParametric.md)
- **Compute Bounds** — See [references/computeBounds.md](references/computeBounds.md)
- **Make Aligned Reference** — See [references/makeAlignedRef.md](references/makeAlignedRef.md)
- **Make Bounding Box** — See [references/makeBoundingBox.md](references/makeBoundingBox.md)
- **Make Marking Attribution** — See [references/makeMarkingAttrib.md](references/makeMarkingAttrib.md)
- **Make Reference** — See [references/makeRef.md](references/makeRef.md)
- **Make Signal Attribution** — See [references/makeSignalAttrib.md](references/makeSignalAttrib.md)
- **Make Speed Limit Attribution** — See [references/makeSpeedLimitAttrib.md](references/makeSpeedLimitAttrib.md)
- **Split Closed Geometry** — See [references/splitClosedGeometry.md](references/splitClosedGeometry.md)
- **N-Way Orthogonal Split** — See [references/orthogonalSplit.md](references/orthogonalSplit.md) — Generic algorithm to split closed-loop lanes into N segments with perfectly orthogonal joints. Use for tracks, ovals, circuits.
- **Synthesize Center Line** — See [references/synthesizeCenterLine.md](references/synthesizeCenterLine.md)

## Key Functions

| Function | Purpose |
|----------|---------|
| `roadrunnerHDMap` | Create HD Map object (loads namespace) |
| `read(rrMap, file)` | Read existing `.rrhd` file |
| `write(rrMap, file)` | Write HD Map to `.rrhd` file |
| `roadrunner.hdmap.Lane` | Lane entity (Geometry, TravelDirection, LaneType) |
| `roadrunner.hdmap.LaneBoundary` | Boundary entity (Geometry, ParametricAttributes) |
| `roadrunner.hdmap.LaneMarking` | Marking definition (ID, AssetPath) |
| `roadrunner.hdmap.Junction` | Junction area (Geometry as MultiPolygon) |
| `roadrunner.hdmap.AlignedReference` | Reference with alignment (Name=Value constructor) |
| `roadrunner.hdmap.RelativeAssetPath` | Asset path wrapper (Name=Value constructor) |
| `roadrunner.hdmap.ParametricAttribution` | Marking placement (Span, MarkingReference) |

## Known Limitations

- SignalTypes/Signals lost on RRHD write/read cycle — signals import not yet supported
- RoadRunner cannot render self-closing lanes — split using N-way orthogonal algorithm (see [references/orthogonalSplit.md](references/orthogonalSplit.md))
- Geometry must always be Nx3 (include Z=0 if flat)
- For track maps (closed-loop ovals): omit topology, Z bumps, and marking attributes — see orthogonalSplit.md Track-Specific Guidance

## Conventions

- Always use create-then-assign pattern for `roadrunner.hdmap.*` objects
- Use `RelativeAssetPath(AssetPath="...")` and `AlignedReference(Reference=ref, Alignment="...")` — Name=Value only
- Use `ClassName.empty` for empty typed arrays, never `[]`
- All geometry is Nx3 with Z column (default 0 for flat terrain)
- Shared boundaries: one object per way, multiple lanes reference with different alignments
- Use `tiledlayout`/`nexttile` for multi-panel figures (not `subplot`)

----

Copyright 2026 The MathWorks, Inc.
