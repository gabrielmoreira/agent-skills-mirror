---
name: roadrunner-asset-mapping
description: >
  RoadRunner asset path lookup tables for map format conversions in MATLAB. Maps lane markings,
  signs, signals, barriers, objects, and lane types to RoadRunner asset paths. Use when converting
  map formats to RRHD, resolving asset paths, or assigning visual assets to HD Map objects.
license: MathWorks BSD-3-Clause
user-invocable: false
metadata:
  author: MathWorks
  version: "1.0"
---

# RoadRunner Asset Mapping

Consolidated lookup tables for mapping source map format elements to RoadRunner project asset paths. All paths are relative to the project `Assets/` folder.

## When to Use

- Resolving lane marking subtypes to RoadRunner `.rrlms` asset paths
- Mapping sign codes (US MUTCD, German StVO, Japanese) to sign asset SVGs
- Looking up barrier/extrusion asset paths for fence, guard rail, jersey barrier, wall
- Finding prop/static object asset paths for placement in RRHD
- Determining region-specific sign paths based on geoReference coordinates
- Assigning lane type enums from source format lane classifications

## When NOT to Use

- Building RRHD objects from scratch — use `roadrunner-rrhd-authoring`
- Performing the full Lanelet2 conversion pipeline — use `roadrunner-convert-lanelet2-to-rrhd`
- Importing maps into RoadRunner — use `roadrunner-import-scene`

## Key Rules

- **All asset paths start with `Assets/`** — always prefix when constructing `RelativeAssetPath` objects.
- **Extension matters.** `.rrlms` = lane marking style, `.rrcws` = crosswalk style, `.rrpms` = polygon marking style. Using wrong extension causes "Asset file is missing" on import.
- **Region detection from geoReference.** Use lat/lon to determine Japan/Germany/US for sign paths.
- **Sign naming convention.** All signs use `Sign_<code>.svg` format based on national regulatory numbering.
- **Japan speed signs have a space.** `Sign_323 (30).svg` — note space before parenthesis.

## Source Data

Asset mappings are derived from the official RoadRunner project configuration XMLs:
- `DefaultAssets.xml` — default materials and markings
- `ApolloAssetData.xml` — Apollo/Baidu HD Map format
- `OpenDriveAssetData.xml` — OpenDRIVE format
- `HEREAssetData_NA.xml` / `HEREAssetData_WE.xml` — HERE HD Map (NA/EU)
- `TomTomAssetData.xml` — TomTom HD Map format

These XML files are located in the RoadRunner project's configuration directory (typically `<RoadRunner Project>/Configuration/`).

## Lane Markings

See [references/laneMarkings.md](references/laneMarkings.md) for full mapping table.

**Key patterns:**
- All marking assets are in `Assets/Markings/` with `.rrlms` extension
- Markings are keyed by **type** (solid/dashed/double) + **color** (white/yellow)
- Default road center marking: `SolidDoubleYellow.rrlms`
- Default outer boundary: `SolidSingleWhite.rrlms`

## Signs

See [references/signs.md](references/signs.md) for full mapping table.

**Key patterns:**
- US signs: `Assets/Signs/US/Regulatory Signs/` or `Assets/Signs/US/Warning Signs/`
- German signs: `Assets/Signs/Germany/Regulatory Signs/`
- Japan signs: `Assets/Signs/Japan/Regulatory Signs/` or `Assets/Signs/Japan/Warning Signs/`
- Speed limit signs use regulatory numbering: `Sign_R2-1(30).svg` (US), `Sign_274(30).svg` (DE), `Sign_323 (30).svg` (JP)
- Fallbacks: `Sign_R2-1(Blank).svg` (US), `Sign_101.svg` (DE warning), `Sign_215.svg` (JP warning)
- Sign geometry uses `GeoOrientedBoundingBox` (Center + Dimension + GeoOrientation)

**Region detection from geoReference:**
```matlab
lat = geoRef(1); lon = geoRef(2);
if lat >= 24 && lat <= 46 && lon >= 122 && lon <= 154
    region = "Japan";
elseif lat >= 35 && lat <= 72 && lon >= -10 && lon <= 25
    region = "Germany";
else
    region = "US";
end
```

**Region-specific sign paths (verified R2026a):**

| Sign | Japan | US | Germany |
|---|---|---|---|
| Stop | `Assets/Signs/Japan/Regulatory Signs/Sign_330-A.svg` | `Assets/Signs/US/Regulatory Signs/Sign_R1-1.svg` | `Assets/Signs/Germany/Regulatory Signs/Sign_206.svg` |
| Speed N | `Assets/Signs/Japan/Regulatory Signs/Sign_323 (<N>).svg` | `Assets/Signs/US/Regulatory Signs/Sign_R2-1(<N>).svg` | `Assets/Signs/Germany/Regulatory Signs/Sign_274(<N>).svg` |
| Fallback | `Assets/Signs/Japan/Warning Signs/Sign_215.svg` | `Assets/Signs/US/Regulatory Signs/Sign_R2-1(Blank).svg` | `Assets/Signs/Germany/Warning Signs/Sign_101.svg` |

**Naming convention:** All signs use `Sign_<code>.svg` format based on national regulatory numbering (MUTCD for US, StVO for Germany, Japanese road sign numbers). Note: Japan speed signs have a space before the parenthesis: `Sign_323 (30).svg`.

## Signals (Traffic Lights)

| Configuration | Asset Path |
|---|---|
| 3-light vertical (post) | `Props/Signals/Signal_3Light_Post01.fbx` |
| 3-light vertical (bare) | `Props/Signals/Signal_3Light_Bare01.fbx_rrx` |

**Authoring vs Import limitation:** You CAN author `SignalType` objects in MATLAB, add them to `rrMap.Signals`, and write the map to `.rrhd` — signal data IS written to the file. However, RoadRunner does NOT import signals from `.rrhd` maps. Signal data in the file is silently ignored on import. Show the asset paths and authoring code, but warn the user that signals will not appear in the RoadRunner scene after import.

## Barriers & Extrusions

See [references/barriers.md](references/barriers.md) for full mapping table.

**Key patterns:**
- All extrusions in `Assets/Extrusions/` with `.rrext` or `.rrext.rrmeta` extension
- Barriers use `roadrunner.hdmap.BarrierType` with `ExtrusionPath`

## Props & Static Objects

See [references/staticObjects.md](references/staticObjects.md) for full mapping table.

**Key patterns:**
- Props in `Assets/Props/` subdirectories (Trees, Signals, TrafficControl, etc.)
- Static objects use `roadrunner.hdmap.StaticObjectType` with `AssetPath`
- Objects use `GeoOrientedBoundingBox` for placement

## Lane Types

See [references/laneTypes.md](references/laneTypes.md) for full mapping table.

## Crosswalks & Curve Markings

**Extension rules** (commonly confused):
- `.rrcws` = crosswalk style (only for actual crosswalks)
- `.rrlms` = lane marking style (stop lines, bike markings, zig-zag)
- `.rrpms` = polygon marking style (striped regions, chevrons)

| Type | Asset Path | Extension |
|---|---|---|
| Simple crosswalk | `Assets/Markings/SimpleCrosswalk.rrcws` | `.rrcws` |
| Continental crosswalk | `Assets/Markings/ContinentalCrosswalk.rrcws` | `.rrcws` |
| Ladder crosswalk | `Assets/Markings/LadderCrosswalk.rrcws` | `.rrcws` |
| Stop line | `Assets/Markings/StopLine.rrlms` | `.rrlms` |
| Striped region | `Assets/Markings/StripedRegion.rrpms` | `.rrpms` |

## Stencils (Road Surface Markings)

| Type | Asset Path |
|---|---|
| Arrow left | `Assets/Stencils/Stencil_ArrowType4L.svg` |
| Arrow right | `Assets/Stencils/Stencil_ArrowType4R.svg` |
| STOP text | `Assets/Stencils/Stencil_STOP.svg` |

## Materials

| Purpose | Asset Path |
|---|---|
| Road surface | `Assets/Materials/Asphalt1.rrmtl` |
| Sidewalk / concrete | `Assets/Materials/Concrete1.rrmtl` |
| Ground / grass | `Assets/Materials/Grass1.rrmtl` |

## Default Assets

These are the project-wide defaults (from `DefaultAssets.xml`):

| Name | Path |
|---|---|
| Island Curb Material | `Assets/Materials/Concrete1.rrmtl` |
| Blank Sign | `Assets/Signs/US/Sign_BlankWhite.rrsign` |
| Blank Warning Sign | `Assets/Signs/US/Yellow_Blank_US.svg` |
| Surface Material | `Assets/Materials/Grass1.rrmtl` |
| Crosswalk | `Assets/Markings/SimpleCrosswalk.rrcws` |
| Stop Line | `Assets/Markings/StopLine.rrlms` |
| Parking Space Marking | `Assets/Markings/SolidSingleWhite.rrlms` |
| Road Surface Material | `Assets/Materials/Asphalt1.rrmtl` |
| Road Center Marking | `Assets/Markings/SolidDoubleYellow.rrlms` |
| Dashed Road Marking | `Assets/Markings/DashedSingleWhite.rrlms` |
| Road Outer Boundary | `Assets/Markings/SolidSingleWhite.rrlms` |
| Road Inner Boundary | `Assets/Markings/SolidSingleYellow.rrlms` |
| One Way Passing | `Assets/Markings/DashedSolidYellow.rrlms` |
| Vehicle | `Assets/Vehicles/Sedan.fbx` |

## Usage Pattern (MATLAB)

```matlab
% Example: resolve marking asset path
function assetPath = resolveMarkingAsset(type, color)
    % type: "solid", "dashed", "solid_solid", etc.
    % color: "white", "yellow" (default: white)
    if nargin < 2, color = "white"; end
    % Use lookup from references/laneMarkings.md
end
```

All asset paths are prefixed with `Assets/` when used in RRHD `RelativeAssetPath` objects.

## Conventions

- All marking assets: `Assets/Markings/<Name>.<ext>` — extension determines type
- All sign assets: `Assets/Signs/<Region>/<Category>/Sign_<code>.svg`
- All extrusion assets: `Assets/Extrusions/<Name>.rrext`
- All prop assets: `Assets/Props/<Category>/<Name>.fbx`
- Use `RelativeAssetPath(AssetPath="...")` for RRHD construction (Name=Value syntax)
- Default road center: `SolidDoubleYellow.rrlms`; default outer boundary: `SolidSingleWhite.rrlms`

----

Copyright 2026 The MathWorks, Inc.
