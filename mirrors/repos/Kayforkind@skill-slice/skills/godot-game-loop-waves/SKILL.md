---
name: godot-game-loop-waves
version: 1.1.1
description: "Runs Godot 4 wave combat as data-driven WaveResource encounters plus a WaveManager timeline, weighted Marker3D spawners, object pools, MultiMesh swarms, and async NavigationServer pathing. Trigger on horde nights, TD lanes, or designer-owned encounter Resources in Godot 4. Not for writing a single enemy's behavior tree or non-Godot engines."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# Wave Loop: Combat Pacing

> [!NOTE]
> **Resource Context**: This module provides expert patterns for **Wave Loops**. Accessed via Godot Master.

## When to Use

- Building wave-based shooters, tower defense, or arena games in Godot 4.x (optimized for 4.3+).
- Need scalable patterns for managing combat waves, dynamic difficulty scaling, and automated enemy spawning.
- Require data-driven "Encounters" using `Resource` files to allow designers to rebalance without touching code.
- Implementing survival modes, endless modes, or scripted RPG encounters with triggered waves.

**Trigger keywords**: wave, spawn, enemy, difficulty scaling, arena, tower defense, survival, endless, encounter, MultiMesh, object pool, NavigationServer, WaveManager, WaveResource.

## Prerequisites

- Godot 4.3 or newer (4.x supported, 4.3+ optimized).
- A project with a 3D scene containing at least one `Marker3D` for spawn points.
- `NavigationRegion3D` baked in your arena if using pathfinding.
- Scripts directory present at `res://addons/godot_game_loop_waves/scripts/` (or your project's scripts folder).

## Procedure

### Architectural Thinking: The "Wave-State" Pattern

A professional implementation treats waves as **Data-Driven Transitions**. Instead of hardcoding spawn counts, use a `WaveResource` to define "Encounters" that the `WaveManager` processes as a state machine.

#### Core Responsibilities
- **WaveManager**: The orchestrator. Manages the timeline, handles inter-wave delays, and evaluates "Victory" conditions.
- **Spawner**: Decoupled spatial nodes that provide the "where" (Marker3D) and the "how" (spawn logic).
- **WaveResource**: Immutable data containers (Custom Resources) that define enemy types, counts, and difficulty modifiers.

### Step 1: Define the WaveResource Data Container

1. Create a new script `wave_resource.gd` extending `Resource` with `class_name WaveResource`.
2. Export a `Dictionary` for compositions mapping scene paths to counts.
3. Export a `difficulty_multiplier: float` defaulting to `1.0`.
4. Export spawn interval and pre-wave delay floats for pacing control.

```gdscript
# wave_resource.gd
extends Resource
class_name WaveResource

@export var compositions: Dictionary = {
    "res://Enemies/Goblin.tscn": 10,
    "res://Enemies/Orc.tscn": 2
}
@export var difficulty_multiplier: float = 1.0
@export var spawn_interval: float = 0.5
@export var pre_wave_delay: float = 3.0
```

> **MANDATORY**: Read `scripts/wave_resource.gd` before implementing this step. It contains the full data container with spawn rates and difficulty settings.

### Step 2: Implement the WaveManager Orchestrator

1. Create `wave_manager.gd` as an `Autoload` or scene-level `Node`.
2. Maintain an `Array[WaveResource]` for linear progression or generate procedurally for endless mode.
3. Use `await get_tree().create_timer(pre_delay, true).timeout` for inter-wave pacing.
4. Emit a `wave_started` signal before invoking spawn logic.
5. Track active enemy count via a signal-based counter (`enemy_died` signal), **never** by polling `get_children()`.

```gdscript
# wave_manager.gd snippet
func start_next_wave(pre_delay: float):
    # Provide "Juice" and preparation time
    await get_tree().create_timer(pre_delay, true).timeout 
    wave_started.emit()
    _spawn_logic()
```

> **MANDATORY**: Read `scripts/wave_manager.gd` before implementing. It orchestrates the timeline, manages delays between waves, and tracks "Victory" conditions.

### Step 3: Set Up Weighted Spawners at Marker3D Nodes

1. Place `Marker3D` nodes in your arena at desired spawn locations.
2. Attach a spawner script that reads from `WaveResource.compositions`.
3. Use weighted random selection for enemy variety and distribution.
4. Spawn via `call_deferred(&"add_child", enemy)` — never synchronously inside physics callbacks.

> **MANDATORY**: Read `scripts/wave_weighted_spawner.gd` before implementing. It provides spatial spawning using weighted random selection for enemy variety and distribution.

### Step 4: Implement Object Pooling for High-Frequency Entities

1. Pre-instantiate a pool of enemy nodes at scene load (e.g., 50–200 depending on expected concurrency).
2. On spawn, pull from the pool and reposition; on death, return to pool and disable collision.
3. Use `set_deferred("disabled", true)` on `CollisionShape` immediately upon death.
4. Never `instantiate()` and `queue_free()` high-frequency entities.

### Step 5: Optimize Swarms with MultiMeshInstance3D

1. For trivial enemies (no individual logic), use `MultiMeshInstance3D` to batch thousands of instances into a single draw call.
2. Update per-instance transforms via `multimesh.set_instance_transform(i, transform)`.
3. Pair with `OccluderInstance3D` baked in the arena for occlusion culling of hidden enemies.

> **MANDATORY**: Read `scripts/wave_loop_patterns.gd` before implementing advanced patterns. It contains 10 expert patterns: MultiMesh swarms, async pathfinding, background preloading, and server-side physics mobs.

### Step 6: Configure Async Pathfinding

1. Enable `use_async_iterations` on `NavigationAgent3D` nodes attached to enemies.
2. For large crowds, use `NavigationServer3D` async queries (`map_get_path` with `callback`).
3. Use separate `NavigationMap` instances for flying vs walking enemies to prevent pathing errors.

### Step 7: Build Wave UI with Signal-Bus Pattern

1. Add a `CanvasLayer` for wave counter and health bars.
2. Display `current_wave / total_waves` updated via signal from `WaveManager`.
3. Use `TextureProgressBar` on `CanvasLayer` for boss health, or `Sprite3D` with `SubViewport` texture for world-space bars.
4. Always provide a UI countdown or "Wave Incoming" warning before auto-starting waves.

### Master Decision Matrix: Progression

| Pattern | Best For | Logic |
| :--- | :--- | :--- |
| **Linear** | Story missions | A sequential `Array[WaveResource]` processed in order. |
| **Endless** | Survival modes | Procedurally generated `WaveResource` using exponential growth math. |
| **Triggered** | RPG Encounters | Wave starts only when player enters a specific `Area3D` trigger. |

## Pitfalls

### HARD RULES — Never Violate

- **NEVER iterate through `get_children()` to find all enemies** — This is $O(n)$ and slow. Always use `get_tree().get_nodes_in_group(&"enemies")` or maintain a dedicated `Array` of active entities.
- **NEVER `instantiate()` and `queue_free()` high-frequency entities** — This triggers frequent garbage collection and memory fragmentation. Use an **Object Pool** pattern to reuse nodes.
- **NEVER use `MeshInstance3D` for swarms** — Individual draw calls will tank performance. Use `MultiMeshInstance3D` to batch thousands of instances into a single draw call.
- **NEVER calculate complex pathfinding on the main thread** — This causes frame spikes. Use `NavigationServer3D` async queries or enable `use_async_iterations` in the NavigationAgent.
- **NEVER `add_child()` without verifying `is_inside_tree()`** — If the spawner is being freed, this will crash. Always verify the parent's state or use `call_deferred`.
- **NEVER assign a shared `.tres` resource directly to mobs** — Modifying a shared resource changes it for all enemies. Always call `.duplicate()` or `.duplicate(true)` (deep copy) for unique stats.
- **NEVER use standard `String` for high-frequency calls** — Use `StringName` (e.g., `&"enemies"`) to utilize Godot's internal string pooling and avoid repeated hashing.
- **NEVER spawn entities synchronously inside physics callbacks** — Modifying the scene tree during `_physics_process` or collision callbacks can corrupt the physics state. Always use `call_deferred(&"add_child", enemy)`.
- **NEVER leave `CollisionShape` active on dead enemies** — Dead bodies will block navigation and other entities. Use `set_deferred("disabled", true)` immediately upon death.
- **NEVER synchronize complex Objects via `MultiplayerSynchronizer`** — It is designed for primitive types. Sync a `uint` or `StringName` ID and resolve the object reference locally on the client.
- **NEVER auto-start waves without player feedback** — This creates a poor UX. Always provide a UI countdown, a "Wave Incoming" warning, or a manual start button.
- **NEVER hardcode spawn coordinates** — Use `Marker3D` nodes. This allows level designers to move spawn points visually in the editor without editing scripts.
- **NEVER poll for wave completion in `_process`** — Counting children every frame is expensive. Use a signal-based counter (e.g., `enemy_died` signal) to track active counts.
- **NEVER use a single navigation map for all entity types** — Flying and walking enemies require different navigation constraints. Use separate `NavigationMap` instances to prevent pathing errors.
- **NEVER scale `CollisionShape` non-uniformly** — Non-uniform scaling breaks collision detection math and physics stability. Adjust the shape's internal size/radius properties instead.

### Common Runtime Issues

- **Frame spikes during wave start**: Caused by synchronous instantiation. Fix by spreading spawns across frames using a timer or `call_deferred` queue.
- **Stutter during high-volume spawning**: Caused by GC from `queue_free()`. Fix by implementing object pooling.
- **Pathing errors for mixed enemy types**: Caused by shared navigation map. Fix by creating separate maps via `NavigationServer3D.map_create()`.
- **Shared stat mutation across enemies**: Caused by assigning the same `.tres` resource. Fix by calling `.duplicate(true)` before assigning.

## Verification

Run through this checklist after implementing:

- [ ] Verify `WaveManager` correctly sequences `WaveResources` with proper delays.
- [ ] Confirm `WaveResource` compositions use `.duplicate()` for unique enemy stats.
- [ ] Test that object pooling prevents GC stutters during high-volume spawning.
- [ ] Validate `MultiMeshInstance3D` batching reduces draw calls for swarms.
- [ ] Check async pathfinding (`use_async_iterations`) prevents main thread freezes.
- [ ] Ensure `StringName` (`&"name"`) is used for all high-frequency group operations.
- [ ] Verify `call_deferred` is used for all physics-callback spawns.
- [ ] Confirm dead enemies have `CollisionShapes` disabled via `set_deferred`.
- [ ] Test occlusion culling with `OccluderInstance3D` baked arena.
- [ ] Validate separate navigation maps for flying vs walking enemies.
- [ ] Check wave completion uses signal-based counters, not frame polling.
- [ ] Verify UI countdown/feedback is present before wave auto-starts.
- [ ] Test `Marker3D` spawn points are adjustable in editor without code changes.
- [ ] Confirm `MultiplayerSynchronizer` only syncs primitive UIDs/IDs.

### Quick Runtime Checks (PowerShell)

```powershell
# Check Godot project file exists
Test-Path "project.godot"

# Run the project headless to validate scene loading (adjust path to your Godot binary)
& "C:\Godot\Godot_v4.3-stable_win64.exe" --path . --quit-after 5

# Search for forbidden patterns in your scripts
Select-String -Path "res://scripts/*.gd" -Pattern "get_children\(\)" 
Select-String -Path "res://scripts/*.gd" -Pattern "queue_free\(\)"
Select-String -Path "res://scripts/*.gd" -Pattern "MeshInstance3D"
```

> Replace `C:\Godot\Godot_v4.3-stable_win64.exe` with your actual Godot executable path.

## Examples

### Available Scripts

> **MANDATORY**: Read the appropriate script before implementing the corresponding pattern.

| Script | When to Load | Contents |
| :--- | :--- | :--- |
| `scripts/wave_loop_patterns.gd` | Before implementing advanced optimization patterns | 10 Expert patterns: MultiMesh swarms, async pathfinding, background preloading, and server-side physics mobs. |
| `scripts/wave_manager.gd` | Before building the wave timeline orchestrator | Orchestrates the timeline, manages delays between waves, and tracks "Victory" conditions. |
| `scripts/wave_resource.gd` | Before defining wave data containers | Data containers for wave compositions, spawn rates, and difficulty settings. |
| `scripts/wave_weighted_spawner.gd` | Before implementing spatial spawn logic | Spatial spawner using weighted random selection for enemy variety and distribution. |

## Related skills

- Master Skill: [godot-master](../godot-master/SKILL.md)
