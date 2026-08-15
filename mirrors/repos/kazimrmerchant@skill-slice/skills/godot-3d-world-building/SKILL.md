---
name: godot-3d-world-building
description: "Builds Godot 4.7 3D levels with GridMap/MeshLibrary cell placement, CSGCombiner3D prototyping, WorldEnvironment sky/fog, chunk streaming, and LOD. Use when the user wants GridMap tiles, BSP-style CSG rooms, ProceduralSkyMaterial, or volumetric fog. Trigger: set_cell_item, map_to_local, CSGBox3D, PanoramaSkyMaterial. Not for StandardMaterial3D PBR or VoxelGI/SDFGI lighting. Never ship unbaked runtime CSG as final collision geometry."
version: 1.0.1
---

# 3D World Building

Expert guidance for level design with GridMaps, CSG, and environmental setup in Godot 4.7.

## When to Use

Activate this skill when the user requests any of the following:
- Building 3D levels with **GridMap** and **MeshLibrary** tilesets
- Creating **CSG** (Constructive Solid Geometry) for prototyping BSP-style rooms, corridors, and boolean geometry
- Setting up **WorldEnvironment**, **Sky**, **ProceduralSkyMaterial**, or **PanoramaSkyMaterial**
- Configuring **fog** (exponential, depth, or volumetric) and atmospheric effects
- Implementing **level streaming**, **LOD management**, or **occlusion culling** for large 3D scenes
- Procedural generation of dungeons or tile-based layouts
- Performance optimization for 3D worlds (MultiMesh partitioning, CSG baking, chunk loading)

Trigger keywords: `GridMap`, `MeshLibrary`, `set_cell_item`, `get_cell_item`, `map_to_local`, `local_to_map`, `CSGCombiner3D`, `CSGBox3D`, `CSGSphere3D`, `CSGPolygon3D`, `WorldEnvironment`, `Environment`, `Sky`, `ProceduralSkyMaterial`, `PanoramaSkyMaterial`, `fog_enabled`, `volumetric_fog_enabled`.

## Prerequisites

- **Godot 4.7** project opened in the editor (Windows host, PowerShell primary)
- For GridMap workflows: a scene with a `GridMap` node
- For CSG workflows: understanding of boolean operations (Union, Subtraction, Intersection)
- For environment workflows: a `WorldEnvironment` node in the scene tree
- **MANDATORY**: Read the relevant script from `scripts/` before implementing the corresponding pattern (see [Available Scripts](#available-scripts) below)

## NEVER Do

- **NEVER forget to bake GridMap navigation** — GridMaps don't auto-generate navigation meshes. Use EditorPlugin or manual `NavigationRegion3D`.
- **NEVER use CSG for final game geometry** — CSG is for prototyping. Convert to static meshes for performance (use "Bake CSG Mesh" in editor).
- **NEVER scale GridMap cell size after placing tiles** — Changing `cell_size` doesn't update existing tiles, causing misalignment. Set it once at the start.
- **NEVER use MeshLibrary without collision shapes** — Items without collision spawn visual-only geometry that players fall through.
- **NEVER enable volumetric fog without DirectionalLight3D** — Volumetric fog requires at least one light to scatter. No lights = no visible fog.
- **NEVER animate CSG nodes during gameplay** — Moving a CSG node within another forces the CPU to recalculate the boolean geometry, causing significant performance drops.
- **NEVER place generic logic nodes in a GridMap** — GridMap is highly optimized only for meshes, navigation, and collision. It is not a general-purpose system for placing arbitrary node structures on a grid.
- **NEVER use non-manifold meshes in CSG** — If you import a custom mesh for `CSGMesh3D`, it must be manifold (closed, no self-intersections, no interior faces, no negative volume). Non-manifold meshes will break the CSG algorithm and are completely unsupported.

## Available Scripts

> **MANDATORY**: Read the appropriate script before implementing the corresponding pattern. All scripts are located in `scripts/` relative to this skill directory.

| Script | When to Load |
|---|---|
| `scripts/collision_gen.gd` | Load when importing models without collision or generating collision for procedural geometry. |
| `scripts/gridmap_runtime_builder.gd` | Load when implementing runtime GridMap tile placement with batch operations and auto-navigation baking. |
| `scripts/csg_bake_tool.gd` | Load when finalizing level prototypes — bakes CSG geometry to static meshes with proper materials and collision. |
| `scripts/safe_csg_baking.gd` | Load when implementing expert CSG baking — awaits end of frame before extracting baked meshes to avoid empty data. |
| `scripts/lod_manager.gd` | Load when implementing level-of-detail switching based on camera distance for large outdoor scenes. |
| `scripts/occlusion_setup.gd` | Load when configuring `OccluderInstance3D` for manual occlusion culling in indoor levels with many rooms. |

## Procedure

### 1. GridMap Fundamentals

#### 1.1 Setup Workflow

1. In the editor, create a MeshLibrary resource:
   - **Scene → New Inherits Scene → Create Grid-aligned meshes**
   - **Scene → Convert To → MeshLibrary...**
2. Assign the library to a GridMap node and set cell size:

```gdscript
# 1. Create MeshLibrary resource (editor)
# Scene → New Inherits Scene → Create Grid-aligned meshes
# Scene → Convert To → MeshLibrary...

# 2. Assign to GridMap
extends GridMap

func _ready() -> void:
    mesh_library = load("res://tilesets/dungeon_library.tres")
    cell_size = Vector3(2, 2, 2)  # Must match library cell size
```

#### 1.2 Cell Manipulation

```gdscript
# gridmap_builder.gd
extends GridMap

# Place cell
func place_tile(grid_pos: Vector3i, tile_index: int) -> void:
    set_cell_item(grid_pos, tile_index)

# Get cell
func get_tile(grid_pos: Vector3i) -> int:
    return get_cell_item(grid_pos)  # Returns index or INVALID_CELL_ITEM (-1)

# Remove cell
func remove_tile(grid_pos: Vector3i) -> void:
    set_cell_item(grid_pos, INVALID_CELL_ITEM)

# Rotate cell (0-23, see GridMap.ROTATION_* constants)
func place_rotated(grid_pos: Vector3i, tile_index: int, orientation: int) -> void:
    set_cell_item(grid_pos, tile_index, orientation)
```

#### 1.3 Coordinate Conversion (Click-to-Place)

```gdscript
# World position ↔ Grid coordinates
func _input(event: InputEvent) -> void:
    if event is InputEventMouseButton and event.pressed:
        var camera := get_viewport().get_camera_3d()
        var from := camera.project_ray_origin(event.position)
        var to := from + camera.project_ray_normal(event.position) * 1000
        
        var space := get_world_3d().direct_space_state
        var query := PhysicsRayQueryParameters3D.create(from, to)
        var result := space.intersect_ray(query)
        
        if result:
            var world_pos: Vector3 = result.position
            var grid_pos := local_to_map(to_local(world_pos))
            place_tile(grid_pos, 0)  # Place tile at clicked position

# Grid → World
func get_cell_center(grid_pos: Vector3i) -> Vector3:
    return to_global(map_to_local(grid_pos))
```

### 2. MeshLibrary Creation

#### 2.1 Collision Setup

1. Build the source scene with this hierarchy before converting to MeshLibrary:

```
# tile_scene.tscn (before converting to MeshLibrary)
# Root: Node3D
#   ├─ MeshInstance3D (visual)
#   └─ StaticBody3D (collision)
#       └─ CollisionShape3D
```

> **CRITICAL**: `StaticBody3D` must be sibling/child for GridMap to detect collision.

#### 2.2 Item Metadata

```gdscript
# Access MeshLibrary item data
func get_tile_name(tile_index: int) -> String:
    return mesh_library.get_item_name(tile_index)

# Custom metadata (stored in MeshLibrary resource)
# Use item_set_name() in editor script to organize
```

### 3. CSG (Constructive Solid Geometry)

#### 3.1 Boolean Operations

```
CSG Combiner3D
  ├─ CSGBox3D (Operation: Union)        # Base room
  ├─ CSGBox3D (Operation: Subtraction)  # Door cutout
  └─ CSGSphere3D (Operation: Intersection)  # Rounded corner
```

#### 3.2 CSG Brush Types

```gdscript
# CSGBox3D - Room primitives
var room := CSGBox3D.new()
room.size = Vector3(10, 5, 10)

# CSGCylinder3D - Pillars
var pillar := CSGCylinder3D.new()
pillar.radius = 0.5
pillar.height = 5.0

# CSGSphere3D - Domes
var dome := CSGSphere3D.new()
dome.radius = 3.0
dome.radial_segments = 16
dome.rings = 8

# CSGPolygon3D - Extruded 2D shapes
var arch := CSGPolygon3D.new()
arch.polygon = PackedVector2Array([
    Vector2(-1, 0), Vector2(-1, 2), Vector2(1, 2), Vector2(1, 0)
])
arch.depth = 0.5
```

#### 3.3 CSG Performance

```gdscript
# ❌ BAD: Use CSG at runtime (slow)
func _ready() -> void:
    var csg := CSGBox3D.new()
    add_child(csg)  # Recalculates mesh every frame

# ✅ GOOD: Bake to MeshInstance3D (editor only)
# Select CSG node → Mesh → Bake Mesh Instance
# Then delete CSG node

# ✅ ALSO GOOD: Use CSG for level editor, bake on export
```

### 4. WorldEnvironment Setup

#### 4.1 Sky Configuration

```gdscript
# world_env.gd
extends WorldEnvironment

func _ready() -> void:
    var env := Environment.new()
    environment = env
    
    # Procedural sky
    env.background_mode = Environment.BG_SKY
    var sky := Sky.new()
    var sky_mat := ProceduralSkyMaterial.new()
    
    sky_mat.sky_top_color = Color(0.4, 0.6, 1.0)  # Blue
    sky_mat.sky_horizon_color = Color(0.8, 0.9, 1.0)  # Lighter
    sky_mat.ground_bottom_color = Color(0.2, 0.2, 0.1)
    sky_mat.sun_angle_max = 30.0
    
    sky.sky_material = sky_mat
    env.sky = sky
```

#### 4.2 HDRI Skybox

```gdscript
# For realistic lighting
var env := environment
env.background_mode = Environment.BG_SKY

var sky := Sky.new()
var panorama := PanoramaSkyMaterial.new()
panorama.panorama = load("res://hdri/sunset.hdr")  # Equirectangular HDR image

sky.sky_material = panorama
env.sky = sky

# Sky contribution to ambient light
env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
env.ambient_light_sky_contribution = 1.0
```

### 5. Fog & Atmosphere

#### 5.1 Exponential Fog

```gdscript
extends WorldEnvironment

func _ready() -> void:
    var env := environment
    
    env.fog_enabled = true
    env.fog_mode = Environment.FOG_MODE_EXPONENTIAL
    env.fog_density = 0.01  # 0.0-1.0
    env.fog_light_color = Color(0.9, 0.95, 1.0)  # Blueish
    env.fog_light_energy = 1.0
```

#### 5.2 Depth Fog

```gdscript
# Distance-based fog
env.fog_enabled = true
env.fog_mode = Environment.FOG_MODE_DEPTH
env.fog_depth_begin = 50.0  # Start distance
env.fog_depth_end = 200.0   # End distance (fully opaque)
env.fog_depth_curve = 1.0   # Falloff curve
```

#### 5.3 Volumetric Fog

> **CRITICAL**: Requires at least one `DirectionalLight3D` for scattering. No lights = no visible fog.

```gdscript
env.volumetric_fog_enabled = true
env.volumetric_fog_density = 0.05
env.volumetric_fog_albedo = Color(0.9, 0.9, 1.0)
env.volumetric_fog_emission = Color.BLACK
env.volumetric_fog_gi_inject = 1.0  # How much GI affects fog

# Performance settings
env.volumetric_fog_temporal_reprojection_enabled = true
env.volumetric_fog_detail_spread = 2.0
```

### 6. Level Streaming / LOD

#### 6.1 GridMap Chunking

```gdscript
# level_streamer.gd - Load/unload GridMap chunks based on player position
extends Node3D

@export var chunk_size := 32  # Grid cells per chunk
@export var load_radius := 2  # Chunks to keep loaded

var loaded_chunks := {}  # Vector2i → GridMap

func _process(delta: float) -> void:
    var player_pos := get_player_position()
    var player_chunk := Vector2i(
        int(player_pos.x / (chunk_size * cell_size.x)),
        int(player_pos.z / (chunk_size * cell_size.z))
    )
    
    # Load nearby chunks
    for x in range(-load_radius, load_radius + 1):
        for z in range(-load_radius, load_radius + 1):
            var chunk_coord := player_chunk + Vector2i(x, z)
            if chunk_coord not in loaded_chunks:
                load_chunk(chunk_coord)
    
    # Unload distant chunks
    for chunk_coord in loaded_chunks.keys():
        var dist := chunk_coord.distance_to(player_chunk)
        if dist > load_radius:
            unload_chunk(chunk_coord)

func load_chunk(coord: Vector2i) -> void:
    var gridmap := GridMap.new()
    gridmap.mesh_library = preload("res://library.tres")
    add_child(gridmap)
    loaded_chunks[coord] = gridmap
    
    # TODO: Load chunk data from file/database
    # gridmap.set_cell_item(...)

func unload_chunk(coord: Vector2i) -> void:
    var gridmap: GridMap = loaded_chunks[coord]
    gridmap.queue_free()
    loaded_chunks.erase(coord)
```

#### 6.2 World-Streaming-Queue (Stutter-Free Loading)

```gdscript
class_name WorldStreamer extends Node

var load_queue: Array[String] = []

func request_chunk(path: String) -> void:
    # Begin background thread request
    var err = ResourceLoader.load_threaded_request(path)
    if err == OK:
        load_queue.append(path)

func _process(_delta: float) -> void:
    for i in range(load_queue.size() - 1, -1, -1):
        var path = load_queue[i]
        var status = ResourceLoader.load_threaded_get_status(path)
        
        if status == ResourceLoader.THREAD_LOAD_LOADED:
            # Resource ready! Instantiate and add to scene
            var chunk: PackedScene = ResourceLoader.load_threaded_get(path)
            add_child(chunk.instantiate())
            load_queue.remove_at(i)
```

### 7. Procedural Generation

#### 7.1 Random Dungeon with GridMap

```gdscript
# dungeon_generator.gd
extends GridMap

enum Tile { FLOOR, WALL, DOOR }

func generate_room(pos: Vector3i, size: Vector3i) -> void:
    # Fill with floor
    for x in range(size.x):
        for z in range(size.z):
            set_cell_item(pos + Vector3i(x, 0, z), Tile.FLOOR)
    
    # Add walls
    for x in range(size.x):
        set_cell_item(pos + Vector3i(x, 0, 0), Tile.WALL)  # North
        set_cell_item(pos + Vector3i(x, 0, size.z - 1), Tile.WALL)  # South
    
    for z in range(size.z):
        set_cell_item(pos + Vector3i(0, 0, z), Tile.WALL)  # West
        set_cell_item(pos + Vector3i(size.x - 1, 0, z), Tile.WALL)  # East

func _ready() -> void:
    generate_room(Vector3i(0, 0, 0), Vector3i(10, 1, 10))
```

### 8. Expert Patterns

#### 8.1 GridMap-Custom-Data (Logic Proxies)

Since `GridMap` is optimized for visuals/collision rather than logic, use "Proxy Tiles" to mark locations for spawn points, NPCs, or triggers during level design.

```gdscript
class_name GridMapLogicManager extends Node3D

@export var level_grid: GridMap
@export var spawn_point_scene: PackedScene

# The ID of the invisible cube in your MeshLibrary
const SPAWN_PROXY_ID: int = 5 

func _ready() -> void:
    _replace_proxies_with_logic()

func _replace_proxies_with_logic() -> void:
    # 1. Find all cells using the proxy tile
    var proxy_cells: Array[Vector3i] = level_grid.get_used_cells_by_item(SPAWN_PROXY_ID)
    
    for cell in proxy_cells:
        # 2. Convert grid pos to world pos
        var world_pos: Vector3 = level_grid.to_global(level_grid.map_to_local(cell))
        
        # 3. Instantiate actual gameplay logic
        var instance: Node3D = spawn_point_scene.instantiate()
        add_child(instance)
        instance.global_position = world_pos
        
        # 4. Clear the proxy tile to save performance
        level_grid.set_cell_item(cell, GridMap.INVALID_CELL_ITEM)
```

#### 8.2 Interior-Mapping (Fake Windows)

For massive cities, avoid rendering actual interiors. Use a Spatial shader to project the illusion of 3D depth onto a single 2D window plane.

```glsl
shader_type spatial;

uniform sampler2DArray room_textures; // Cubemap-like layers

void fragment() {
    // Project view vector into fake room depth
    vec3 view_dir = normalize(VIEW);
    
    // Intersection math to determine which wall/floor/ceiling pixel to sample
    // Note: Use 'VIEW' and 'INV_VIEW_MATRIX' for perspective calculations
    vec3 room_uv = view_dir; // Simplified placeholder
    
    ALBEDO = texture(room_textures, room_uv).rgb;
}
```

#### 8.3 Spatially Partitioning MultiMeshes

The major drawback of `MultiMesh` is that individual instances cannot be frustum or occlusion culled; the entire cluster is drawn based on the bounding box of the `MultiMeshInstance3D`. To solve this, partition your thousands of objects into several regional `MultiMeshInstance3D` nodes so the engine can cull entire regions at once.

## Pitfalls

1. **GridMap cells not colliding** — MeshLibrary items lack collision shapes. Ensure `StaticBody3D` + `CollisionShape3D` in the source scene before converting. Verify in code:

```gdscript
var item_shapes := mesh_library.get_item_shapes(tile_index)
if item_shapes.is_empty():
    push_error("Tile %d has no collision!" % tile_index)
```

2. **CSG mesh flickering (Z-fighting)** — Overlapping CSG operations cause exact-surface conflicts. Add a small offset (0.001) to prevent exact overlap:

```gdscript
var box := CSGBox3D.new()
box.size = Vector3(10, 5, 10)

var cutout := CSGBox3D.new()
cutout.operation = CSGShape3D.OPERATION_SUBTRACTION
cutout.size = Vector3(2, 3, 2.002)  # Slightly larger depth
```

3. **Empty CSG baked mesh data** — Baking CSG meshes synchronously can return empty geometry. Load and use `scripts/safe_csg_baking.gd` which awaits the end of the frame before extracting baked meshes.

4. **Cell size misalignment** — Changing `cell_size` after placing tiles does not retroactively update existing tile positions. Set `cell_size` once at the start and never change it.

5. **Volumetric fog invisible** — Volumetric fog requires at least one `DirectionalLight3D` to scatter. Without a light source, the fog will not be visible.

6. **CSG at runtime** — Creating or moving CSG nodes during gameplay forces CPU recalculation of boolean geometry every frame. Always bake CSG to static meshes before shipping.

7. **Non-manifold CSG meshes** — Custom meshes used in `CSGMesh3D` must be manifold (closed, no self-intersections, no interior faces, no negative volume). Non-manifold meshes break the CSG algorithm.

## Verification

1. **GridMap collision check** — Run this in a tool script or `_ready()`:

```gdscript
for item_index in range(mesh_library.get_item_count()):
    var shapes := mesh_library.get_item_shapes(item_index)
    if shapes.is_empty():
        push_warning("MeshLibrary item %d ('%s') has NO collision shapes!" % [item_index, mesh_library.get_item_name(item_index)])
```

2. **GridMap tile placement** — Verify a tile was placed correctly:

```gdscript
set_cell_item(Vector3i(0, 0, 0), 0)
assert(get_cell_item(Vector3i(0, 0, 0)) == 0, "Tile placement failed!")
assert(get_cell_item(Vector3i(1, 0, 0)) == GridMap.INVALID_CELL_ITEM, "Unexpected tile found!")
```

3. **WorldEnvironment active** — Confirm the environment is applied:

```gdscript
assert(get_viewport().find_world_3d().environment != null, "No Environment set on WorldEnvironment!")
```

4. **CSG bake result** — After baking, verify the resulting `MeshInstance3D` has valid geometry:

```gdscript
var baked_mesh := $MeshInstance3D.mesh
assert(baked_mesh != null, "Baked mesh is null!")
assert(baked_mesh.get_surface_count() > 0, "Baked mesh has no surfaces!")
```

5. **Volumetric fog visibility** — Ensure a `DirectionalLight3D` exists in the scene:

```gdscript
var lights := get_tree().get_nodes_in_group("directional_lights")
assert(not lights.is_empty(), "No DirectionalLight3D found — volumetric fog will be invisible!")
```

## Godot 4.7 Editor Notes

- **Path3D** supports snap-to-colliders for path point placement on geometry.
- **3D vertex snapping** with vertex/origin base setting (editor B key workflow).
- `EditorSceneFormatImporter` uses **ImportFlags** enum for import constants.

## Related skills

- Master Skill: [godot-master](../godot-master/SKILL.md)
