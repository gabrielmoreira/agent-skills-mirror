---
name: geospatial-analysis
version: 1.1.1
description: "Analyzes vector geospatial data with GeoPandas: load GeoJSON, spatial filter or join, and metric distances after projecting off EPSG:4326 (EPSG:4087 or UTM). Use when calculating distances between features, filtering points in polygons, or working with plate-boundary and earthquake-style datasets. Not for raster or satellite processing, or web map tiles. Do not calculate distances on raw lat/lon degrees."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

## Overview

When working with geographic data (earthquakes, plate boundaries, etc.), using `geopandas` with proper coordinate projections provides accurate distance calculations and efficient spatial operations. This guide covers best practices for geospatial analysis using modern Python standards.

**Critical Rule**: Never calculate distances directly in geographic coordinates (EPSG:4326). Always project to a metric coordinate system first.

## When to Use

- You need accurate distance calculations between geographic features.
- You are performing spatial filtering, joins, or overlays on plate boundaries, earthquake epicenters, or any other geospatial datasets.
- Your workflow requires projecting data to a metric CRS (e.g., EPSG:4087 or local UTM zones) before analysis.

## Prerequisites

- Python 3.8+ with `geopandas`, `shapely`, and `pyproj` installed.
- On Windows (PowerShell), ensure the conda or venv environment is activated before running scripts:

```powershell
# Activate environment (adjust path as needed)
conda activate geo-env
# or
.\.venv\Scripts\Activate.ps1
```

- Verify package availability:

```powershell
python -c "import geopandas; print(geopandas.__version__)"
```

## Procedure

### 1. Understand Coordinate Systems

| Coordinate System | Type | Units | Use Case |
|-------------------|------|-------|----------|
| EPSG:4326 (WGS84) | Geographic | Degrees (lat/lon) | Data storage, display, GPS coordinates |
| EPSG:4087 (World Equidistant Cylindrical) | Projected | Meters | Global distance calculations |
| UTM Zones (e.g., EPSG:32633) | Projected | Meters | High-precision local area analysis |

### 2. Load Geospatial Data

From GeoJSON files:

```python
import geopandas as gpd

gdf_plates = gpd.read_file("plates.json")
gdf_boundaries = gpd.read_file("boundaries.json")
```

From regular data with coordinates:

```python
from shapely.geometry import Point
import geopandas as gpd

data = [
    {"id": 1, "lat": 35.0, "lon": 140.0, "value": 5.5},
    {"id": 2, "lat": 36.0, "lon": 141.0, "value": 6.0},
]

# Use points_from_xy for better performance
gdf = gpd.GeoDataFrame(
    data,
    geometry=gpd.points_from_xy([row["lon"] for row in data], [row["lat"] for row in data]),
    crs="EPSG:4326"
)
```

### 3. Perform Spatial Filtering

Find points within a polygon:

```python
# Get the polygon of interest
target_poly = gdf_plates[gdf_plates["Name"] == "Pacific"].geometry.unary_union

# Filter points that fall within the polygon
points_inside = gdf_points[gdf_points.within(target_poly)]

print(f"Found {len(points_inside)} points inside the polygon")
```

Combine multiple boundary segments:

```python
# Combine multiple boundary segments into one geometry
all_boundaries = gdf_boundaries.geometry.unary_union

# Or filter first, then combine
pacific_boundaries = gdf_boundaries[
    gdf_boundaries["Name"].str.contains("PA")
].geometry.unary_union
```

### 4. Calculate Distances (Project to Metric CRS First)

```python
# 1. Load your data
gdf_points = gpd.read_file("points.json")
gdf_boundaries = gpd.read_file("boundaries.json")

# 2. Project to metric coordinate system
METRIC_CRS = "EPSG:4087"
points_proj = gdf_points.to_crs(METRIC_CRS)
boundaries_proj = gdf_boundaries.to_crs(METRIC_CRS)

# 3. Combine boundary segments if needed
boundary_geom = boundaries_proj.geometry.unary_union

# 4. Calculate distances (returns meters)
gdf_points["distance_m"] = points_proj.geometry.distance(boundary_geom)
gdf_points["distance_km"] = gdf_points["distance_m"] / 1000.0
```

Find the furthest point:

```python
furthest = gdf_points.nlargest(1, "distance_km").iloc[0]

print(f"Furthest point: {furthest['id']}")
print(f"Distance: {furthest['distance_km']:.2f} km")
```

### 5. Filter by Attributes

```python
# Filter by name or code
pacific_plate = gdf_plates[gdf_plates["PlateName"] == "Pacific"]
pacific_plate_alt = gdf_plates[gdf_plates["Code"] == "PA"]

# Filter boundaries involving a specific plate
pacific_bounds = gdf_boundaries[
    (gdf_boundaries["PlateA"] == "PA") |
    (gdf_boundaries["PlateB"] == "PA")
]

# String pattern matching
pa_related = gdf_boundaries[gdf_boundaries["Name"].str.contains("PA")]
```

### 6. Common Workflow Pattern (Earthquakes and Plate Boundaries)

```python
import geopandas as gpd
from shapely.geometry import Point

# 1. Load data
earthquakes_data = [
    {"latitude": 35.652834, "longitude": 139.839478, "magnitude": 4.5},
    {"latitude": 36.204824, "longitude": 138.252924, "magnitude": 5.2}
]
gdf_plates = gpd.read_file("plates.json")
gdf_boundaries = gpd.read_file("boundaries.json")

# 2. Create earthquake GeoDataFrame
gdf_eq = gpd.GeoDataFrame(
    earthquakes_data,
    geometry=gpd.points_from_xy(
        [eq["longitude"] for eq in earthquakes_data],
        [eq["latitude"] for eq in earthquakes_data]
    ),
    crs="EPSG:4326"
)

# 3. Spatial filtering - find earthquakes in specific plate
target_plate = gdf_plates[gdf_plates["Code"] == "PA"].geometry.unary_union
earthquakes_in_plate = gdf_eq[gdf_eq.within(target_plate)].copy()

# 4. Calculate distances (project to metric CRS)
METRIC_CRS = "EPSG:4087"
eq_proj = earthquakes_in_plate.to_crs(METRIC_CRS)

# Filter and combine relevant boundaries
plate_boundaries = gdf_boundaries[
    gdf_boundaries["Name"].str.contains("PA")
].to_crs(METRIC_CRS).geometry.unary_union

# Calculate distances
earthquakes_in_plate["distance_km"] = eq_proj.geometry.distance(plate_boundaries) / 1000.0

# 5. Find the furthest earthquake
furthest_eq = earthquakes_in_plate.nlargest(1, "distance_km").iloc[0]
```

### 7. Performance Tips

1. **Filter before projecting**: Reduce data size before expensive operations.
2. **Project once**: Convert to metric CRS once, not in loops.
3. **Use `.unary_union`**: Combine geometries before distance calculations to avoid O(N x M) complexity.
4. **Copy when modifying**: Use `.copy()` when creating filtered DataFrames to avoid `SettingWithCopyWarning`.
5. **Use `points_from_xy`**: Use `gpd.points_from_xy()` instead of list comprehensions with `Point()` for significantly faster GeoDataFrame creation.

```python
# Good: Filter first, then project
small_subset = gdf_large[gdf_large["region"] == "Pacific"]
small_projected = small_subset.to_crs(METRIC_CRS)

# Avoid: Projecting large dataset just to filter
# gdf_projected = gdf_large.to_crs(METRIC_CRS)
# small_subset = gdf_projected[gdf_projected["region"] == "Pacific"]
```

## Pitfalls

| Issue | Problem | Solution |
|-------|---------|----------|
| Distance in degrees | Using EPSG:4326 for distance calculations | Project to EPSG:4087 or similar metric CRS |
| Antimeridian issues | Manual longitude adjustments (+/-360) | Use `geopandas` spatial operations; for complex wraps, use `shapely`'s `orient` or specialized libraries |
| Slow performance | Calculating distance to each boundary point separately | Use `.unary_union` + single `.distance()` call |
| Missing geometries | Some features have no geometry | Filter with `gdf[gdf.geometry.notna()]` |
| CRS Mismatch | Attempting spatial join on different CRS | Ensure both GDFs have the same CRS using `.to_crs()` |
| Outdated syntax | Using `gdf.set_crs` when transformation is needed | Use `gdf.to_crs()` for transformation; `set_crs` only assigns, does not transform |
| Manual haversine | Writing custom haversine formulas | Use `geopandas` vectorized API with projected CRS instead |

**Do NOT**:
- Use manual haversine formulas or custom point-in-polygon code.
- Calculate distances directly on geographic coordinates (EPSG:4326).
- Iterate over individual boundary vertices for distance checks.
- Use `pyproj` for basic distance calculations when `geopandas` provides a vectorized API.
- Use outdated `geopandas` syntax (e.g., using `gdf.set_crs` when `gdf.to_crs` is required for transformation).

## Verification

- [ ] Run the provided workflow on a sample earthquake and plate boundary dataset to ensure distances are returned in meters/kilometers.
- [ ] Verify that filtering before projection reduces processing time compared to projecting first.
- [ ] Confirm that `gdf.crs` is correctly set to `EPSG:4326` before calling `.to_crs()`.
- [ ] Validate that `unary_union` is used for boundary distance calculations to ensure O(N) performance.

Quick check command:

```powershell
python -c "import geopandas as gpd; gdf = gpd.GeoDataFrame({'x':[0],'y':[0]}, geometry=gpd.points_from_xy([0],[0]), crs='EPSG:4326'); p = gdf.to_crs('EPSG:4087'); print('CRS OK:', p.crs)"
```

Expected output:

```
CRS OK: EPSG:4087
```

## Related Skills

- raster-analysis
- spatial-joins
- time-series-geospatial
