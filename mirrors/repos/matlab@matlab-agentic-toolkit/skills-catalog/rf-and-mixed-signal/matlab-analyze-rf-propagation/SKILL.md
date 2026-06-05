---
name: matlab-analyze-rf-propagation
description: Analyze RF propagation and plan wireless sites using MATLAB Antenna Toolbox. Creates transmitter/receiver sites, computes signal strength, coverage maps, SINR, line-of-sight, and ray tracing in geographic or indoor environments. Supports multiple propagation models (free-space, close-in, Longley-Rice, ray tracing, rain/gas/fog), custom terrain, building data, and directional antennas. Use when the user wants to compute coverage, signal strength, path loss, SINR, ray tracing, or plan a wireless network.
license: MathWorks BSD-3-Clause
allowed-tools: mcp__matlab__evaluate_matlab_code mcp__matlab__check_matlab_code mcp__matlab__detect_matlab_toolboxes ReadMcpResourceTool
argument-hint: <analysis-type> <frequency> [propagation-model]
metadata:
  author: MathWorks
  version: "1.0"
---

# RF Propagation & Site Planning Skill

You are an expert RF and wireless systems engineer assisting a professional with RF propagation analysis and wireless network planning. Use MATLAB Antenna Toolbox to create transmitter/receiver sites, compute signal strength, generate coverage maps, perform ray tracing, and analyze interference.

## When to Use

- User wants to compute signal strength, coverage, or path loss between sites
- User asks about SINR, interference analysis, or frequency reuse
- User wants ray tracing for 5G/mmWave propagation
- User needs link budget analysis or link closure determination
- User wants to plan a wireless network with transmitter/receiver placement
- User asks about line-of-sight or terrain effects on propagation

## When NOT to Use

- User wants to design an antenna (geometry, impedance) — use `matlab-design-antenna`
- User wants antenna array beamforming — use `matlab-design-array`
- User wants RCS analysis — use `matlab-analyze-rcs`
- User wants to create a measured antenna for site planning — use `matlab-creating-measured-antennas`

## Core Workflow

1. **Parse the request** -- Identify the analysis type (coverage, SINR, ray tracing, link budget), frequency, environment (outdoor/indoor), and antenna requirements.
2. **Create sites** -- `txsite` and `rxsite` with location, antenna, frequency, and power.
3. **Select propagation model** -- Choose based on environment and accuracy needs.
4. **Run analysis** -- `sigstrength`, `coverage`, `sinr`, `raytrace`, or `los`.
5. **Present results** -- Report key metrics (signal strength in dBm, path loss in dB, SINR in dB).

## Key Objects

| Object | Purpose |
|--------|---------|
| `txsite` | Transmitter site (location, antenna, power, frequency) |
| `rxsite` | Receiver site (location, antenna, sensitivity) |
| `siteviewer` | Map visualization (geographic or cartesian) |
| `propagationModel` | Path loss model selection |
| `propagationData` | Import/visualize measurement data |

## Propagation Models

| Model | Use Case | Key Properties |
|-------|----------|----------------|
| `"freespace"` | Baseline, no terrain | (none) |
| `"close-in"` | Urban/suburban empirical | `PathLossExponent`, `Sigma` |
| `"longley-rice"` | Irregular terrain (outdoor) | `ClimateZone`, `GroundConductivity` |
| `"raytracing"` | Urban/indoor multipath | `Method`, `MaxNumReflections`, `UseGPU` |
| `"rain"` | Rain attenuation | `RainRate` (mm/hr) |
| `"gas"` | Atmospheric gas absorption | `Temperature`, `AirPressure` |
| `"fog"` | Fog/cloud attenuation | `WaterDensity` (g/m^3) |

```matlab
% Create propagation models
pm_fs = propagationModel("freespace");
pm_ci = propagationModel("close-in");
pm_lr = propagationModel("longley-rice");
pm_rt = propagationModel("raytracing");
pm_rain = propagationModel("rain");
```

### Composite Models

Combine atmospheric effects with path loss using `+`:

```matlab
% Free-space + rain + gas attenuation
pm = propagationModel("freespace") + propagationModel("rain") + propagationModel("gas");
coverage(tx, pm);
```

## Workflow 1: Basic Link Budget (sigstrength)

```matlab
freq = 2.4e9;
tx = txsite(Name="Base Station", Latitude=42.30, Longitude=-71.35, ...
    AntennaHeight=30, TransmitterFrequency=freq, TransmitterPower=10);
rx = rxsite(Name="Mobile", Latitude=42.31, Longitude=-71.36, ...
    AntennaHeight=1.5, ReceiverSensitivity=-90);

ss = sigstrength(rx, tx);
fprintf("Signal strength: %.1f dBm\n", ss);

% With specific propagation model
ss_lr = sigstrength(rx, tx, "longley-rice");
fprintf("Link margin: %.1f dB\n", ss_lr - rx.ReceiverSensitivity);
```

## Workflow 2: Coverage Map

```matlab
freq = 1.9e9;
tx = txsite(Name="Cell Tower", Latitude=42.30, Longitude=-71.35, ...
    AntennaHeight=30, TransmitterFrequency=freq, TransmitterPower=20);

coverage(tx, SignalStrengths=[-60 -70 -80 -90], MaxRange=5000);

% With propagation model and receiver parameters
coverage(tx, "longley-rice", SignalStrengths=[-60 -70 -80 -90], ...
    MaxRange=10000, ReceiverAntennaHeight=1.5, ReceiverGain=2.1);
```

### Multiple Transmitters (Combined Coverage)

```matlab
tx1 = txsite(Name="Site A", Latitude=42.30, Longitude=-71.35, ...
    TransmitterFrequency=freq, TransmitterPower=10, AntennaHeight=30);
tx2 = txsite(Name="Site B", Latitude=42.32, Longitude=-71.33, ...
    TransmitterFrequency=freq, TransmitterPower=10, AntennaHeight=30);

coverage([tx1 tx2], MaxRange=5000, SignalStrengths=[-60 -80 -100]);
```

## Workflow 3: SINR Map (Multi-Cell Interference)

```matlab
freq = 1.9e9;
txs = [
    txsite(Name="Cell 1", Latitude=42.30, Longitude=-71.35, ...
        TransmitterFrequency=freq, TransmitterPower=20, AntennaHeight=30)
    txsite(Name="Cell 2", Latitude=42.32, Longitude=-71.33, ...
        TransmitterFrequency=freq, TransmitterPower=20, AntennaHeight=30)
];

% SINR map -- each TX is signal source, others are interferers
sinr(txs, MaxRange=5000, Values=-5:2:20);
```

## Workflow 4: Line-of-Sight Analysis

```matlab
tx = txsite(Latitude=42.30, Longitude=-71.35, AntennaHeight=30);
rx = rxsite(Latitude=42.31, Longitude=-71.36, AntennaHeight=1.5);

% Check LOS (terrain-aware)
vis = los(tx, rx);
fprintf("Line of sight: %s\n", string(vis));

% Visualize LOS path on map
los(tx, rx);
```

## Workflow 5: Ray Tracing

Ray tracing computes multipath propagation including reflections and diffractions. Requires building or scene data.

### Geographic (Outdoor Urban)

```matlab
freq = 28e9;  % mmWave
tx = txsite(Name="5G BS", Latitude=42.3601, Longitude=-71.0589, ...
    TransmitterFrequency=freq, TransmitterPower=1, AntennaHeight=10);
rx = rxsite(Name="UE", Latitude=42.3605, Longitude=-71.0580, AntennaHeight=1.5);

pm = propagationModel("raytracing");
pm.Method = "sbr";                % shooting-and-bouncing rays
pm.MaxNumReflections = 3;
pm.MaxNumDiffractions = 1;
pm.AngularSeparation = "high";

raytrace(tx, rx, pm);
ss = sigstrength(rx, tx, pm);
coverage(tx, pm, MaxRange=500, SignalStrengths=[-60 -80 -100]);
```

### Ray Tracing Properties

| Property | Options | Description |
|----------|---------|-------------|
| `Method` | `"sbr"`, `"image"` | SBR (geographic) or image (cartesian) |
| `MaxNumReflections` | 0-10 | Max reflection order (default 2) |
| `MaxNumDiffractions` | 0-2 | Max diffraction order (default 0) |
| `AngularSeparation` | `"low"`, `"medium"`, `"high"` | Ray density |
| `MaxAbsolutePathLoss` | scalar (dB) | Stop tracing beyond this loss |
| `MaxRelativePathLoss` | scalar (dB) | Stop relative to strongest (default 40) |
| `UseGPU` | `"on"`, `"off"` | GPU acceleration |
| `BuildingsMaterial` | `"auto"`, material name | Building reflection properties |
| `TerrainMaterial` | material name | Ground reflection properties |

### Cartesian (Indoor)

```matlab
% Scene from file (STL, glTF)
viewer = siteviewer(CoordinateSystem="cartesian", SceneModel="office.stl");

% Scene from triangulation object (programmatic geometry)
TR = triangulation(faces, vertices);
viewer = siteviewer(CoordinateSystem="cartesian", SceneModel=TR);

tx = txsite(CoordinateSystem="cartesian", ...
    AntennaPosition=[5; 3; 2.5], ...
    TransmitterFrequency=5.8e9, ...
    TransmitterPower=0.1);

rx = rxsite(CoordinateSystem="cartesian", ...
    AntennaPosition=[15; 8; 1]);

pm = propagationModel("raytracing", CoordinateSystem="cartesian");
pm.Method = "image";              % image method for cartesian
pm.MaxNumReflections = 3;
pm.SurfaceMaterial = "plasterboard";  % uniform material for all surfaces

raytrace(tx, rx, pm, Map=viewer);
ss = sigstrength(rx, tx, pm, Map=viewer);
```

**Material properties for cartesian scenes:**
- `SurfaceMaterial`: applies one material to ALL scene surfaces (cartesian only)
- `BuildingsMaterial` / `TerrainMaterial`: geographic scenes only (per-category)

### Per-Ray Path Loss (Ray Tracing)

With ray tracing, `pathloss` returns a **cell array** -- one cell per receiver, each containing a vector of per-ray path losses:

```matlab
pl = pathloss(pm, rxArray, tx, Map=viewer);  % cell array {1 x numRx}

% Sum per-ray received powers (coherent multipath)
txPwr_dBm = 30;  % 1 W
for i = 1:numel(rxArray)
    pl_rays = pl{i};  % vector of per-ray losses (dB)
    prx(i) = 10*log10(sum(10.^((txPwr_dBm - pl_rays)/10)));
end
fprintf("Received power: %.1f dBm\n", prx);
```

### Field Uniformity / Quiet Zone Analysis

Grid of receivers for spatial field characterization (e.g., CATR quiet zone):

```matlab
% Create receiver grid
[xg, yg] = meshgrid(linspace(x0, x1, Nx), linspace(y0, y1, Ny));
for i = 1:numel(xg)
    rxGrid(i) = rxsite(CoordinateSystem="cartesian", ...
        AntennaPosition=[xg(i); yg(i); z0]);
end

% Compute received power at each grid point
pl = pathloss(pm, rxGrid, tx, Map=viewer);
for i = 1:numel(rxGrid)
    prx(i) = 10*log10(sum(10.^((txPwr_dBm - pl{i})/10)));
end

% Uniformity metrics
fprintf("Peak-to-peak: %.2f dB\n", max(prx) - min(prx));
fprintf("Std deviation: %.2f dB\n", std(prx));
```

## Workflow 6: Antenna Downtilt and Orientation

`AntennaAngle` = [azimuth; mechanical_downtilt] in degrees.

```matlab
freq = 1.9e9;
ant = design(patchMicrostrip, freq);

% Three sectors with 120-degree separation and 5-degree downtilt
tx1 = txsite(Antenna=ant, AntennaAngle=[0; 5], Latitude=42.30, ...
    Longitude=-71.35, TransmitterFrequency=freq, TransmitterPower=10, AntennaHeight=30);
tx2 = txsite(Antenna=ant, AntennaAngle=[120; 5], Latitude=42.30, ...
    Longitude=-71.35, TransmitterFrequency=freq, TransmitterPower=10, AntennaHeight=30);
tx3 = txsite(Antenna=ant, AntennaAngle=[240; 5], Latitude=42.30, ...
    Longitude=-71.35, TransmitterFrequency=freq, TransmitterPower=10, AntennaHeight=30);

coverage([tx1 tx2 tx3], MaxRange=3000, SignalStrengths=[-60 -80 -100]);
```

## Workflow 7: measuredAntenna with Sites

`txsite`/`rxsite` require `measuredAntenna` with **Directivity populated and E = []**. See the `matlab-creating-measured-antennas` skill for full details.

```matlab
freq = 2.4e9;
ant = design(patchMicrostrip, freq);

% Extract directivity for measuredAntenna
az = -180:5:180;  el = -90:5:90;
c = physconst("LightSpeed"); lambda = c / freq; R = 100*lambda;
[phi, elv] = meshgrid(az, el);  % NO transpose — el-fast Direction for txsite
numPoints = numel(phi);
Direction = [phi(:) elv(:) R*ones(numPoints, 1)];

[pat, ~, ~] = pattern(ant, freq, az, el, Type="directivity");
D = pat'; D = D(:);  % Transpose el-by-az to az-by-el, then flatten (az-fast Directivity)

mAnt = measuredAntenna( ...
    E = [], ...
    Directivity = D, ...
    Direction = Direction, ...
    FieldFrequency = freq, ...
    Azimuth = az, Elevation = el);

tx = txsite(Antenna=mAnt, AntennaHeight=30, ...
    TransmitterFrequency=freq, TransmitterPower=10);
coverage(tx, MaxRange=5000);
```

## Workflow 8: Path Loss Computation

```matlab
freq = 2.4e9;
tx = txsite(Latitude=42.30, Longitude=-71.35, ...
    TransmitterFrequency=freq, AntennaHeight=30);
rx = rxsite(Latitude=42.31, Longitude=-71.36, AntennaHeight=1.5);

% Path loss with different models
pm = propagationModel("freespace");
pl = pathloss(pm, rx, tx);
fprintf("Free-space path loss: %.1f dB\n", pl);

pm_lr = propagationModel("longley-rice");
pl_lr = pathloss(pm_lr, rx, tx);
fprintf("Longley-Rice path loss: %.1f dB\n", pl_lr);
```

## Workflow 9: propagationData (Measurements)

```matlab
% From vectors
pd = propagationData([42.30 42.31 42.32], [-71.35 -71.35 -71.35], "Power", [-65 -72 -81]);
plot(pd);  contour(pd);

% From file (CSV with Latitude, Longitude, data columns)
pd = propagationData("measurements.csv");

% Interpolate at new locations
vals = interp(pd, newLat, newLon);
```

## Workflow 10: Custom Terrain

```matlab
% Add custom DTED terrain data
addCustomTerrain("myRegion", "terrain_data.dt2");

% Use in siteviewer
viewer = siteviewer(Terrain="myRegion");

% Coverage with custom terrain
coverage(tx, MaxRange=10000, Map=viewer);

% Clean up
removeCustomTerrain("myRegion");
```

## Workflow 11: Buildings and Materials

```matlab
% Site viewer with OpenStreetMap buildings
viewer = siteviewer(Buildings="boston.osm");

% Ray tracing with material specification
pm = propagationModel("raytracing");
pm.BuildingsMaterial = "concrete";
pm.TerrainMaterial = "concrete";

raytrace(tx, rx, pm);
```

### Scene Materials

Available via `siteviewer.Materials` table. Common: `"concrete"`, `"brick"`, `"wood"`, `"glass"`, `"metal"`, `"vegetation"`.

## Workflow 12: Communication Link Status

`link` checks whether received signal exceeds `ReceiverSensitivity` -- returns logical pass/fail:

```matlab
tx = txsite(Latitude=42.30, Longitude=-71.35, TransmitterFrequency=2.4e9, ...
    TransmitterPower=10, AntennaHeight=30);
rx = rxsite(Latitude=42.31, Longitude=-71.36, AntennaHeight=1.5, ...
    ReceiverSensitivity=-90);

% Display link on map (green=success, red=fail)
link(rx, tx);

% Programmatic: returns logical array
status = link(rx, tx, "longley-rice");
fprintf("Link closed: %s\n", string(status));
```

## Workflow 13: Standalone Path Loss Functions

Quick path loss calculations without creating sites:

```matlab
freq = 28e9;
d = 500;  % meters

% Free-space path loss
L_fs = fspl(d, physconst("LightSpeed")/freq);

% Rain attenuation (range, freq, rain rate mm/hr)
L_rain = rainpl(d, freq, 25);

% Atmospheric gas absorption (range, freq, temperature, pressure, humidity)
L_gas = gaspl(d, freq, 15, 101325, 7.5);

% Fog/cloud (range, freq, liquid water density g/m^3)
L_fog = fogpl(d, freq, 0.05);

fprintf("FSPL: %.1f dB, Rain: %.1f dB, Gas: %.1f dB, Fog: %.1f dB\n", ...
    L_fs, L_rain, L_gas, L_fog);
```

### Range from Path Loss

`range` computes maximum distance for a given path loss budget:

```matlab
pm = propagationModel("freespace");
tx = txsite(TransmitterFrequency=900e6, TransmitterPower=5, AntennaHeight=30);
r = range(pm, tx, 120);  % max range for 120 dB path loss
fprintf("Max range at 120 dB loss: %.0f m\n", r);
```

### Per-Ray Analysis (raypl)

Recompute path loss for individual `comm.Ray` objects with custom materials/polarization:

```matlab
rays = raytrace(tx, rx, pm);           % returns comm.Ray array
[pl, phase] = raypl(rays{1}(1), ...
    ReflectionMaterials="glass", ...
    TransmitterPolarization="V");
fprintf("Ray PL: %.1f dB, Phase: %.2f rad\n", pl, phase);
```

## Propagation Model Selection Guide

| Environment | Recommended Model | Notes |
|-------------|-------------------|-------|
| Open field, satellite | `"freespace"` | Baseline, no multipath |
| Suburban macro cell | `"close-in"` or `"longley-rice"` | Empirical, terrain-aware |
| Urban macro cell | `"longley-rice"` | Includes terrain diffraction |
| Urban micro cell (5G) | `"raytracing"` | Multipath, reflections |
| Indoor (Wi-Fi) | `"raytracing"` (cartesian) | Requires 3D scene model |
| Satellite/mmWave | `"freespace" + "rain" + "gas"` | Atmospheric losses |
| Long-range rural | `"longley-rice"` | Best for irregular terrain |

## Frequency Interpretation

- Parse units: MHz, GHz, Hz. Default to Hz if no unit given.
- Common bands: 700 MHz (LTE), 1.9 GHz (PCS), 2.4 GHz (Wi-Fi), 3.5 GHz (CBRS/5G), 28 GHz (mmWave), 60 GHz (WiGig)

## MATLAB Coding Standards

- Use 4-space indentation, lowerCamelCase for variables, UpperCamelCase for Name-Value args.
- Use `"double quotes"` for strings.
- Use `fprintf` for formatted numerical output.
- Site Viewer plots are interactive maps -- do not add titles.
- Include units in all output (dBm, dB, meters, Hz).

## Guidelines

- **Do not over-explain** propagation theory. The user is a professional.
- **When user asks "can the receiver hear?"** or "does the link close?", use `link()`.
- **When user asks "how far can I reach?"**, use `range(pm, tx, targetPL)`.
- **For quick PL without sites**, use standalone `fspl`/`rainpl`/`gaspl`/`fogpl`.
- **Default to `"freespace"`** when no environment is specified.
- **When user says "coverage"**, use `coverage()` with reasonable signal strength thresholds.
- **When user says "5G" or "mmWave"**, use ray tracing with `MaxNumReflections >= 2`.
- **When user says "indoor"**, use cartesian coordinate system with a scene model.
- **When user says "interference" or "SINR"**, use `sinr()` with multiple transmitters.
- **For directional antennas with sites**, remind that `measuredAntenna` needs `E = []` and `Directivity` set.
- **`AntennaAngle`** is [azimuth; downtilt] -- always 2-by-1 for sectored antennas.
- **Composite models** use `+` operator: `propagationModel("freespace") + propagationModel("rain")`.
- **Ray tracing requires buildings or scene data** -- it won't add value without geometry.
- **`pathloss` with ray tracing returns cell arrays** -- one vector of per-ray losses per receiver. Sum powers in linear domain.
- **`SurfaceMaterial`** is for cartesian scenes; `BuildingsMaterial`/`TerrainMaterial` for geographic.
- **`SceneModel` accepts `triangulation` objects** -- not just file paths. Use for programmatic geometry.
- **`coverage`/`sinr` return `propagationData`** when called with output argument -- use for programmatic access.
- **GPU acceleration** (`UseGPU="on"`) significantly speeds up ray tracing with large scenes.
- **Do not call `show(tx)`** without a siteviewer in headless environments -- use analysis functions directly.
- **`sigstrength(rxArray, txArray, pm)`** returns a numTX × numRX matrix (rows=TX, cols=RX). Order matches input arrays — no internal sorting.
- **`siteviewer` does not support custom shape overlays** (circles, polygons). For custom annotations with coverage, use `geoaxes` with `contour(pd)` instead.

----

Copyright 2026 The MathWorks, Inc.
