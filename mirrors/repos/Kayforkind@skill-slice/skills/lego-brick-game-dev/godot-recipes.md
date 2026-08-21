# Godot 4 Recipes — Brick Building

Concrete Godot 4.x implementations for the systems in `SKILL.md`. Data shapes come from `brick-data-model.md`; algorithms from `reference.md`. Snippets are minimal-but-runnable patterns — adapt names to your project. Godot 4.3+ assumed.

## 1. Scene architecture

```
Main (Node3D)
├── BuildWorld (Node3D)
│   ├── BrickSystem (Node)            # autoload-able: grid + graph + ops (pure data)
│   ├── ChunkRenderer (Node3D)        # MultiMesh chunks, dirty-rebake
│   ├── ChunkColliders (Node3D)       # StaticBody3D per chunk
│   └── DebrisPool (Node3D)           # pooled RigidBody3D + stud pickups
├── BuildController (Node3D)          # input → ops; owns ghost + tool state
│   ├── Ghost (MeshInstance3D)
│   └── OrbitCamera (Node3D → Camera3D)
└── UI (CanvasLayer)                  # catalog hotbar, palette, undo buttons
```

Rule: `BrickSystem` is pure data + signals (`piece_placed`, `piece_removed`, `islands_changed`). Renderer, colliders, audio, and VFX all *subscribe*. Nothing renders from inside the data layer — this is what keeps multiplayer/replays/undo sane.

## 2. Constants and grid math

```gdscript
# grid_space.gd
class_name GridSpace

const CELL := 1.0            # world units per stud pitch
const PLATE := 0.4           # plate height, in cells
const CHUNK := 16            # studs per chunk side

static func to_world(g: Vector3i) -> Vector3:
    return Vector3(g.x * CELL, g.y * CELL * PLATE, g.z * CELL)

static func to_grid(w: Vector3) -> Vector3i:
    return Vector3i(floori(w.x / CELL), floori(w.y / (CELL * PLATE)), floori(w.z / CELL))

static func rotate_offset(o: Vector3i, rot: int) -> Vector3i:
    var p := o
    for i in rot % 4:
        p = Vector3i(p.z, p.y, -p.x)     # 90° CCW about +Y
    return p

# Rotate a whole footprint and renormalize so min corner = (0,0,0).
static func rotated_footprint(cells: Array[Vector3i], rot: int) -> Array[Vector3i]:
    var out: Array[Vector3i] = []
    var mn := Vector3i(1 << 30, 1 << 30, 1 << 30)
    for c in cells:
        var r := rotate_offset(c, rot)
        out.append(r)
        mn = Vector3i(mini(mn.x, r.x), mini(mn.y, r.y), mini(mn.z, r.z))
    for i in out.size():
        out[i] -= mn
    return out

static func chunk_key(g: Vector3i) -> Vector2i:
    return Vector2i(floori(float(g.x) / CHUNK), floori(float(g.z) / CHUNK))
```

## 3. PieceDef as a Resource

```gdscript
# piece_def.gd
class_name PieceDef
extends Resource

@export var id: StringName
@export var family: StringName
@export var footprint: Array[Vector3i] = []       # local cells, min corner (0,0,0)
@export var stud_cells: Array[Vector3i] = []      # cells exposing a top stud
@export var socket_cells: Array[Vector3i] = []    # cells exposing a bottom socket
@export var mesh: Mesh
@export var mass := 0.25
@export var cost_studs := 1
@export var paintable := true
```

Author one `.tres` per piece; load the catalog with `ResourceLoader` or a preloaded `Array[PieceDef]`. Side connectors (clips/pins/hinges) get their own exported arrays when you add those families — same pattern.

## 4. BrickSystem: occupancy, placement, removal

```gdscript
# brick_system.gd
class_name BrickSystem
extends Node

signal piece_placed(id: int, def: PieceDef, pos: Vector3i, rot: int, color: int)
signal piece_removed(id: int)
signal island_detached(piece_ids: Array[int])

var occupancy: Dictionary = {}   # Vector3i -> piece id
var pieces: Dictionary = {}      # id -> {def, pos, rot, color}
var adjacency: Dictionary = {}   # id -> Array[int]  (rigid edges)
var _next_id := 1

func world_cells(def: PieceDef, pos: Vector3i, rot: int) -> Array[Vector3i]:
    var out: Array[Vector3i] = []
    for c in GridSpace.rotated_footprint(def.footprint, rot):
        out.append(pos + c)
    return out

func can_place(def: PieceDef, pos: Vector3i, rot: int) -> Dictionary:
    var cells := world_cells(def, pos, rot)
    for c in cells:
        if c.y < 0:
            return {ok = false, reason = "below_ground"}
        if occupancy.has(c):
            return {ok = false, reason = "overlaps"}
    var links := _find_connections(def, pos, rot)
    var grounded := cells.any(func(c: Vector3i) -> bool: return c.y == 0)
    if links.is_empty() and not grounded:
        return {ok = false, reason = "no_support"}
    return {ok = true, links = links}

func place(def: PieceDef, pos: Vector3i, rot: int, color: int) -> int:
    var check := can_place(def, pos, rot)
    if not check.ok:
        return -1
    var id := _next_id; _next_id += 1
    pieces[id] = {def = def, pos = pos, rot = rot, color = color}
    for c in world_cells(def, pos, rot):
        occupancy[c] = id
    adjacency[id] = []
    for other in check.links:
        adjacency[id].append(other)
        adjacency[other].append(id)
    piece_placed.emit(id, def, pos, rot, color)
    return id

func remove(id: int) -> void:
    var p: Dictionary = pieces[id]
    var neighbors: Array = adjacency[id].duplicate()
    for c in world_cells(p.def, p.pos, p.rot):
        occupancy.erase(c)
    for n in neighbors:
        adjacency[n].erase(id)
    adjacency.erase(id)
    pieces.erase(id)
    piece_removed.emit(id)
    _check_detachment(neighbors)   # reference.md §1.3 — local re-flood

# Rigid mating rule: my socket cell c mates a stud whose cell is c + (0,-1,0);
# my stud cell c mates a socket at c + (0,+1,0).
func _find_connections(def: PieceDef, pos: Vector3i, rot: int) -> Array[int]:
    var found := {}
    for c in GridSpace.rotated_footprint(def.socket_cells, rot):
        var below: Vector3i = pos + c + Vector3i(0, -1, 0)
        if occupancy.has(below) and _has_stud_at(occupancy[below], below):
            found[occupancy[below]] = true
    for c in GridSpace.rotated_footprint(def.stud_cells, rot):
        var above: Vector3i = pos + c + Vector3i(0, 1, 0)
        if occupancy.has(above) and _has_socket_at(occupancy[above], above):
            found[occupancy[above]] = true
    return found.keys()
```

`_has_stud_at`/`_has_socket_at` check the neighbor's rotated stud/socket arrays — required so tiles (no studs) and slopes (partial studs) behave honestly. `_check_detachment` is a bounded BFS from each ex-neighbor toward ground; islands that can't reach ground emit `island_detached` (algorithm: `reference.md` §1.3).

## 5. Ghost preview and raycast targeting

```gdscript
# Inside BuildController — runs every frame while a piece is selected.
func _update_ghost() -> void:
    var cam := get_viewport().get_camera_3d()
    var mouse := get_viewport().get_mouse_position()
    var from := cam.project_ray_origin(mouse)
    var to := from + cam.project_ray_normal(mouse) * 200.0
    var q := PhysicsRayQueryParameters3D.create(from, to)
    q.collision_mask = LAYER_BRICKS | LAYER_GROUND
    var hit := get_world_3d().direct_space_state.intersect_ray(q)
    if hit.is_empty():
        ghost.visible = false
        return
    # Nudge into the cell the surface faces, so we target the space ON the face.
    var target := GridSpace.to_grid(hit.position + hit.normal * 0.05)
    target = _snap_origin_for(current_def, target, current_rot)  # center footprint on cursor
    var check := brick_system.can_place(current_def, target, current_rot)
    ghost.visible = true
    ghost.position = GridSpace.to_world(target)
    ghost.set_valid(check.ok, check.get("reason", ""))            # icon + outline, not color-only
    _pending = {pos = target, ok = check.ok}
```

Feel details that matter: nudge by `hit.normal` so clicking a brick's top targets the layer above it; center the footprint under the cursor (`_snap_origin_for` subtracts half the rotated extents) so big plates don't hang off to one side; commit on *release* if you support drag-paint.

## 6. Rotation input

```gdscript
func _unhandled_input(event: InputEvent) -> void:
    if event.is_action_pressed("build_rotate"):        # R / RB
        current_rot = (current_rot + 1) % 4
        ghost.set_yaw(current_rot)                      # rotates mesh 90° * rot
    elif event.is_action_pressed("build_layer_up"):     # raise target plate layer
        layer_offset += 1
    elif event.is_action_pressed("build_layer_down"):
        layer_offset = maxi(layer_offset - 1, 0)
```

Ghost mesh yaw: `ghost.rotation.y = current_rot * PI / 2.0` — but the *logic* always uses the integer `rot` with `GridSpace.rotated_footprint`. Never derive grid state from node transforms.

## 7. Chunked MultiMesh renderer

```gdscript
# chunk_renderer.gd — subscribes to BrickSystem signals.
class_name ChunkRenderer
extends Node3D

var _dirty: Dictionary = {}        # Vector2i -> true
var _chunk_mms: Dictionary = {}    # Vector2i -> {Mesh: MultiMeshInstance3D}

func _ready() -> void:
    brick_system.piece_placed.connect(func(_i, _d, pos, _r, _c): _mark(pos))
    brick_system.piece_removed.connect(func(_i): pass) # removal callers also _mark(pos)

func _mark(pos: Vector3i) -> void:
    _dirty[GridSpace.chunk_key(pos)] = true

func _process(_dt: float) -> void:
    for key in _dirty.keys():
        _rebake_chunk(key)
    _dirty.clear()

func _rebake_chunk(key: Vector2i) -> void:
    var by_mesh: Dictionary = {}   # Mesh -> Array[{xform, color}]
    for id in brick_system.pieces:
        var p: Dictionary = brick_system.pieces[id]
        if GridSpace.chunk_key(p.pos) != key:
            continue               # for big builds keep a per-chunk index instead
        var t := Transform3D(Basis(Vector3.UP, p.rot * PI / 2.0), GridSpace.to_world(p.pos))
        by_mesh.get_or_add(p.def.mesh, []).append({xform = t, color = palette[p.color]})
    var mms: Dictionary = _chunk_mms.get_or_add(key, {})
    for mesh in by_mesh:
        var mmi: MultiMeshInstance3D = mms.get(mesh)
        if mmi == null:
            mmi = MultiMeshInstance3D.new()
            mmi.multimesh = MultiMesh.new()
            mmi.multimesh.transform_format = MultiMesh.TRANSFORM_3D
            mmi.multimesh.use_colors = true
            mmi.multimesh.mesh = mesh
            add_child(mmi)
            mms[mesh] = mmi
        var list: Array = by_mesh[mesh]
        mmi.multimesh.instance_count = list.size()
        for i in list.size():
            mmi.multimesh.set_instance_transform(i, list[i].xform)
            mmi.multimesh.set_instance_color(i, list[i].color)
```

Requirements for per-instance color: the piece material must read `INSTANCE_CUSTOM`/instance color — with `StandardMaterial3D` set `vertex_color_use_as_albedo = true` (instance color feeds `COLOR`). Keep ONE shared material across all pieces so chunks batch. Maintain a per-chunk piece index (`Dictionary chunk -> Array[id]`) once builds exceed a few thousand pieces so rebake doesn't scan the world.

## 8. Chunk colliders

```gdscript
# One StaticBody3D per chunk; one BoxShape3D per piece (box approximation).
func _rebake_chunk_collision(key: Vector2i) -> void:
    var body: StaticBody3D = _bodies.get_or_add(key, _make_body(key))
    for owner_id in body.get_shape_owners():
        body.shape_owner_clear_shapes(owner_id)
    for id in _chunk_index[key]:
        var p: Dictionary = brick_system.pieces[id]
        var cells := brick_system.world_cells(p.def, p.pos, p.rot)
        var aabb := _cells_aabb(cells)                     # min/max in world space
        var shape := BoxShape3D.new()
        shape.size = aabb.size
        var owner_id := body.create_shape_owner(body)
        body.shape_owner_add_shape(owner_id, shape)
        body.shape_owner_set_transform(owner_id,
            Transform3D(Basis(), aabb.get_center()))
```

Debounce: collision rebake can lag rendering by a frame or two without anyone noticing — batch it on a timer, not per placement.

## 9. Command-pattern undo (with inventory symmetry)

```gdscript
class_name BuildOp
extends RefCounted
func apply(sys: BrickSystem, inv: Inventory) -> void: pass
func revert(sys: BrickSystem, inv: Inventory) -> void: pass

class PlaceOp extends BuildOp:
    var def: PieceDef; var pos: Vector3i; var rot: int; var color: int
    var placed_id := -1
    func apply(sys, inv):
        inv.take_piece(def)
        placed_id = sys.place(def, pos, rot, color)
    func revert(sys, inv):
        sys.remove(placed_id)
        inv.give_piece(def)

class CompositeOp extends BuildOp:
    var ops: Array[BuildOp] = []
    func apply(sys, inv):
        for op in ops: op.apply(sys, inv)
    func revert(sys, inv):
        for i in range(ops.size() - 1, -1, -1): ops[i].revert(sys, inv)

# undo_stack.gd
var _undo: Array[BuildOp] = []
var _redo: Array[BuildOp] = []

func do_op(op: BuildOp) -> void:
    op.apply(brick_system, inventory)
    _undo.append(op)
    _redo.clear()

func undo() -> void:
    if _undo.is_empty(): return
    var op: BuildOp = _undo.pop_back()
    op.revert(brick_system, inventory)
    _redo.append(op)
```

Drag-paint and multi-select emit ONE `CompositeOp`. `RemoveOp` mirrors `PlaceOp` (stores def/pos/rot/color at capture time so revert can re-place). This op layer is also your network message format and your replay format — do not add a second mutation path.

## 10. Break-apart debris pool

```gdscript
# debris_pool.gd — pre-warmed RigidBody3D pool for detached fragments.
const POOL_SIZE := 64
var _free: Array[RigidBody3D] = []

func _ready() -> void:
    for i in POOL_SIZE:
        var b := RigidBody3D.new()
        b.freeze = true
        var mi := MeshInstance3D.new(); b.add_child(mi)
        var cs := CollisionShape3D.new(); cs.shape = BoxShape3D.new(); b.add_child(cs)
        add_child(b)
        _free.append(b)
    brick_system.island_detached.connect(_on_detached)

func _on_detached(ids: Array[int]) -> void:
    # Cluster whole fragment into ONE body (merge AABBs; small clusters keep detail).
    if _free.is_empty():
        _convert_to_pickups(ids)          # cap exceeded: skip physics, pay out studs
        return
    var b: RigidBody3D = _free.pop_back()
    _fit_body_to_cluster(b, ids)          # sets mesh(es), box size, mass, position
    for id in ids:
        brick_system.remove_silent(id)    # no re-flood cascade from inside a cascade
    b.freeze = false
    b.apply_impulse(Vector3(randf_range(-1, 1), 2.5, randf_range(-1, 1)))
    get_tree().create_timer(3.0).timeout.connect(func(): _retire(b, ids))

func _retire(b: RigidBody3D, ids: Array[int]) -> void:
    b.freeze = true
    b.position = Vector3(0, -100, 0)
    _free.append(b)
    _spawn_stud_pickups(b.position, ids)  # pooled Area3D coins with magnet-to-player
```

Hard rules: pool exhaustion degrades gracefully (straight to pickups, never allocate); `remove_silent` bypasses detachment checks while a cascade is already being processed; stud pickups use their own pool with an `Area3D` + magnet lerp toward the player.

## 11. Orbit camera for build mode

```gdscript
# orbit_camera.gd
extends Node3D  # pivot; Camera3D child at (0, 0, distance)

@export var distance := 18.0
var _yaw := 0.0
var _pitch := -0.6

func _unhandled_input(e: InputEvent) -> void:
    if e is InputEventMouseMotion and Input.is_action_pressed("cam_orbit"):
        _yaw -= e.relative.x * 0.008
        _pitch = clampf(_pitch - e.relative.y * 0.008, -1.35, -0.1)
    elif e.is_action_pressed("cam_zoom_in"):
        distance = maxf(distance * 0.9, 4.0)
    elif e.is_action_pressed("cam_zoom_out"):
        distance = minf(distance * 1.1, 80.0)

func _process(dt: float) -> void:
    rotation = Vector3(_pitch, _yaw, 0)
    $Camera3D.position = Vector3(0, 0, distance)
    # Focus follows the cursor's grid target (smoothed), so building tall stays comfortable.
    position = position.lerp(focus_target, 1.0 - exp(-8.0 * dt))
```

Clamp pitch away from the poles; pan the pivot with middle-drag mapped onto the camera's XZ basis; in play mode hand control to [game-player-controller](../game-player-controller/SKILL.md) and keep this rig for build mode only.

## 12. Blueprint save/load

```gdscript
func save_blueprint(path: String) -> void:
    var pieces_out: Array = []
    for id in brick_system.pieces:
        var p: Dictionary = brick_system.pieces[id]
        pieces_out.append({ "def": String(p.def.id),
            "pos": [p.pos.x, p.pos.y, p.pos.z], "rot": p.rot, "color": p.color })
    pieces_out.sort_custom(_canonical_order)             # brick-data-model.md §7
    var doc := { "format": "brickgame.blueprint", "version": 2,
        "meta": { "created_utc": Time.get_datetime_string_from_system(true),
                  "piece_count": pieces_out.size() },
        "palette": palette_hex, "pieces": pieces_out }
    var tmp := path + ".tmp"
    var f := FileAccess.open(tmp, FileAccess.WRITE)
    f.store_string(JSON.stringify(doc))
    f.close()
    DirAccess.rename_absolute(tmp, path)                 # atomic-ish: temp then rename

func load_blueprint(path: String) -> bool:
    var f := FileAccess.open(path, FileAccess.READ)
    if f == null: return false
    var doc = JSON.parse_string(f.get_as_text())
    if doc == null or doc.get("format") != "brickgame.blueprint": return false
    doc = migrate_blueprint(doc)                         # reference.md §3.4
    brick_system.clear()
    for pc in doc.pieces:
        var def: PieceDef = catalog.by_id(pc.def)
        if def == null: push_warning("unknown piece %s" % pc.def); continue
        brick_system.place(def, Vector3i(pc.pos[0], pc.pos[1], pc.pos[2]), pc.rot, pc.color)
    return true
```

Loading via `place()` recomputes the connection graph for free and validates every piece — a corrupted blueprint degrades to warnings, not a crash. For versioned world saves and migration tables, compose with the `godot-save-load-system` skill.

## 13. Input map (suggested actions)

| Action | Kbd/Mouse | Gamepad |
|---|---|---|
| `build_place` | LMB | A / Cross |
| `build_remove` | RMB | B / Circle |
| `build_rotate` | R | RB |
| `build_layer_up/down` | Wheel (+Shift) | D-pad U/D |
| `build_paint` | P then LMB | X / Square |
| `build_eyedrop` | Alt+LMB | LB hold |
| `cam_orbit` | MMB drag | R-stick |
| `undo` / `redo` | Ctrl+Z / Ctrl+Y | View+A / View+B |

Register through the Input Map (compose with `game-input-handling` for rebinding), never hardcoded keycodes.

## 14. Performance checklist (Godot-specific)

- [ ] One shared `StandardMaterial3D` (`vertex_color_use_as_albedo = true`); colors via instance color only
- [ ] `MultiMesh.instance_count` set once per rebake; no per-frame instance writes
- [ ] Per-chunk piece index maintained incrementally (no world scans in `_rebake_chunk`)
- [ ] Collision rebake debounced on a 0.1–0.2 s timer
- [ ] Debris/pickup/VFX pools pre-warmed in `_ready`; zero `new()` during play
- [ ] Profile with the built-in profiler at 10k/50k pieces before adding LOD complexity
