# Brick Data Model

Piece types, connectivity graph, and JSON schemas for brick-by-brick games. This is the authoritative vocabulary — code, save files, and tools all derive from these definitions. IP note: all IDs, names, and dimensions here are original/functional; never import official element numbers or color names.

## 1. Units and coordinate conventions

| Concept | Definition |
|---|---|
| **Cell** | 1 stud pitch. The horizontal atom. World size = `CELL` (recommend `1.0` world units at prototype scale; retune later via one constant). |
| **Plate height** | Vertical atom = `0.4 × CELL`. |
| **Brick height** | 3 plates = `1.2 × CELL`. |
| **Grid position** | `[x, y, z]` integers: `x`, `z` in studs; `y` in plates. Y-up. |
| **World conversion** | `world = (x * CELL, y * CELL * 0.4, z * CELL)` — done in exactly one place in code. |
| **Piece origin** | The min-corner voxel of the piece's *rotated* footprint sits at the piece's grid position. |
| **Rotation** | `rot ∈ {0,1,2,3}` = counter-clockwise 90° steps about +Y. Rotate each footprint offset by `(x,z) → (z, -x)` per step, then renormalize offsets so the min corner is `(0,0,0)`. |
| **Naming** | `WxD` = studs along local X × studs along local Z at `rot = 0` (e.g. `brick_2x4`: W=2, D=4). |

Why anisotropic integers: float positions drift and break equality checks; the 0.4 vertical ratio is what makes plates/offset building (and the whole system's expressive depth) possible.

## 2. Connector types

Connectors are typed, oriented attachment points in piece-local grid space.

| Type | Dir | Mates with | Joint | Default strength |
|---|---|---|---|---|
| `stud` | `+y` | `socket` | rigid | 1 per stud |
| `socket` | `-y` | `stud` | rigid | — (receptor) |
| `bar` | axis (`+x`/`+z`) | `clip` | revolute (about bar axis) | 1 |
| `clip` | side | `bar` | revolute | 1 |
| `pin` | axis | `pin_hole` | revolute (free spin) | 2 |
| `pin_hole` | axis | `pin` | revolute | — (receptor) |
| `hinge_m` | side | `hinge_f` | revolute, limited (−45°..+180° typ.) | 2 |
| `hinge_f` | side | `hinge_m` | revolute, limited | — (receptor) |
| `axle_socket` | `-y`/side | `axle` | rigid or revolute (wheels) | 2 |

Rules:

- **Rigid mates** (`stud`↔`socket`) keep both pieces in the same grid frame and add an edge to the connection graph.
- **Jointed mates** (revolute) split the assembly into two frames: the child side becomes a *sub-assembly* with its own local grid, mounted at the joint. Grid math never spans a joint.
- Connector `strength` feeds the stability heuristics (`reference.md` §2) and connection HP for destruction.
- Tiles have `socket`s but no `stud`s — that asymmetry is what makes them "finishing" pieces.

## 3. Piece taxonomy (starter catalog data)

Footprints listed as `W×D×H` (H in plates). `studs`/`sockets` default to "one per top/bottom footprint cell" unless noted.

| id | Family | W×D×H | Connector exceptions | Notes |
|---|---|---|---|---|
| `brick_1x1` | brick | 1×1×3 | — | |
| `brick_1x2` | brick | 1×2×3 | — | |
| `brick_1x4` | brick | 1×4×3 | — | |
| `brick_2x2` | brick | 2×2×3 | — | |
| `brick_2x4` | brick | 2×4×3 | — | The workhorse |
| `brick_2x8` | brick | 2×8×3 | — | |
| `plate_1x1` … `plate_4x8` | plate | W×D×1 | — | |
| `tile_1x1`, `tile_1x2`, `tile_2x2` | tile | W×D×1 | **no studs** | Smooth top |
| `slope_45_2x1` | slope | 1×2×3 | studs on back cell only | Front face slanted |
| `slope_33_3x1` | slope | 1×3×3 | studs on back cell only | |
| `slope_inv_45_2x1` | slope | 1×2×3 | sockets on front cell only | Overhang underside |
| `round_1x1` | round | 1×1×3 | — | Cylindrical mesh, square footprint |
| `dome_1x1` | round | 1×1×2 | no studs | Cap piece |
| `bracket_1x2_1x2` | bracket | 1×2×2 + side wing | 2 side-facing `stud (+x)` | Enables sideways building |
| `clip_1x1` | clip | 1×1×1 | 1 `clip` side | |
| `bar_1x4` | bar | 1×4×1 | `bar` along top | |
| `hinge_base_1x2` | hinge | 1×2×1 | 1 `hinge_f` side | |
| `hinge_top_1x2` | hinge | 1×2×1 | 1 `hinge_m` side | |
| `pin` | pin | (connector-only) | `pin` both ends | No footprint of its own |
| `beam_1x4_holes` | beam | 1×4×3 | 3 `pin_hole` through X | |
| `turntable_2x2` | special | 2×2×2 | top half revolute about +Y | Splits frames |
| `wheel_small` + `axle_2` | special | — | `axle`/`axle_socket` | Vehicle basics |
| `arch_1x4` | special | 1×4×3 | sockets at end cells only | Middle cells occupy but don't accept studs from below |
| `window_1x2x2` | special | 1×2×6 | — | Frame + transparent inset |
| `door_1x2x3` | special | 1×2×9 | hinge built-in | |
| `fig_legs`, `fig_torso`, `fig_head`, `fig_hair` | fig | see §8 | stacked via `stud`/`socket` | Original proportions |

Curation rule: introduce one *family* at a time in progression; each family must add a new building capability (mass → offsets → finishing → angles → sideways → motion).

## 4. PieceDefinition schema

```json
{
  "$id": "brickgame.piece_def.v1",
  "type": "object",
  "required": ["id", "family", "footprint", "connectors", "mesh", "mass"],
  "properties": {
    "id":        { "type": "string", "pattern": "^[a-z0-9_]+$" },
    "family":    { "enum": ["brick","plate","tile","slope","round","bracket",
                            "clip","bar","hinge","pin","beam","special","fig"] },
    "footprint": {
      "description": "Occupied voxels in piece-local (stud,plate,stud) space, min corner (0,0,0).",
      "type": "array", "items": { "type": "array", "items": {"type":"integer"}, "minItems": 3, "maxItems": 3 }
    },
    "connectors": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["type", "cell", "dir"],
        "properties": {
          "type":     { "enum": ["stud","socket","bar","clip","pin","pin_hole",
                                 "hinge_m","hinge_f","axle","axle_socket"] },
          "cell":     { "type": "array", "items": {"type":"integer"}, "minItems": 3, "maxItems": 3 },
          "dir":      { "enum": ["+y","-y","+x","-x","+z","-z"] },
          "strength": { "type": "integer", "default": 1 },
          "joint":    { "enum": ["rigid","revolute","revolute_limited"], "default": "rigid" },
          "limits_deg": { "type": "array", "items": {"type":"number"}, "minItems": 2, "maxItems": 2 }
        }
      }
    },
    "mesh":      { "type": "string", "description": "res:// path or asset key" },
    "collision": { "type": "string", "enum": ["box_auto","mesh","compound"], "default": "box_auto" },
    "mass":      { "type": "number", "description": "kg-ish; 2x4 brick ≈ 1.0 baseline" },
    "paintable": { "type": "boolean", "default": true },
    "cost_studs": { "type": "integer", "default": 1 },
    "tags":      { "type": "array", "items": {"type": "string"} }
  }
}
```

Example — `brick_1x2` (footprint cells span 3 plates of height):

```json
{
  "id": "brick_1x2", "family": "brick", "mass": 0.25, "cost_studs": 2,
  "footprint": [[0,0,0],[0,1,0],[0,2,0],[0,0,1],[0,1,1],[0,2,1]],
  "connectors": [
    { "type": "stud",   "cell": [0,2,0], "dir": "+y" },
    { "type": "stud",   "cell": [0,2,1], "dir": "+y" },
    { "type": "socket", "cell": [0,0,0], "dir": "-y" },
    { "type": "socket", "cell": [0,0,1], "dir": "-y" }
  ],
  "mesh": "res://assets/pieces/brick_1x2.glb"
}
```

Convention: a `stud` at cell `c` mates with a `socket` at cell `c + (0,1,0)` in world grid space (the socket cell sits directly above the stud's cell top). Keep this the *only* mating rule for rigid connections — one rule, zero special cases.

## 5. PlacedPiece schema (world/blueprint resident)

```json
{
  "$id": "brickgame.placed_piece.v1",
  "type": "object",
  "required": ["id", "def", "pos", "rot", "color"],
  "properties": {
    "id":    { "type": "integer", "description": "Unique within the build; monotonically assigned; never reused within a session." },
    "def":   { "type": "string",  "description": "PieceDefinition id" },
    "pos":   { "type": "array", "items": {"type":"integer"}, "minItems": 3, "maxItems": 3 },
    "rot":   { "type": "integer", "minimum": 0, "maximum": 3 },
    "color": { "type": "integer", "description": "Index into the blueprint/world palette" },
    "group": { "type": "integer", "description": "Optional sub-assembly id (jointed frames)", "default": 0 }
  }
}
```

## 6. Connection edge (derived — never serialized)

```json
{
  "$id": "brickgame.connection.v1",
  "type": "object",
  "properties": {
    "a": { "type": "integer" }, "b": { "type": "integer" },
    "type": { "enum": ["stud","bar_clip","pin","hinge","axle"] },
    "strength": { "type": "integer", "description": "Sum of mated connector strengths (e.g. 4 studs = 4)" },
    "hp": { "type": "number", "description": "Runtime damage pool = strength * HP_PER_STRENGTH" }
  }
}
```

Invariants:

- Edges are recomputed from placed pieces on load (`reference.md` §3). A blueprint that serializes edges is malformed.
- Multiple mated studs between the same two pieces = ONE edge with summed strength (keeps the graph small and union-find fast).
- `a < b` normalized ordering for dedupe.

## 7. Blueprint schema (v2, versioned)

```json
{
  "$id": "brickgame.blueprint.v2",
  "type": "object",
  "required": ["format", "version", "meta", "palette", "pieces"],
  "properties": {
    "format":  { "const": "brickgame.blueprint" },
    "version": { "type": "integer" },
    "meta": {
      "type": "object",
      "properties": {
        "name":        { "type": "string" },
        "author":      { "type": "string" },
        "created_utc": { "type": "string", "format": "date-time" },
        "app_version": { "type": "string" },
        "piece_count": { "type": "integer" },
        "bounds":      { "type": "array", "description": "[min[3], max[3]] in grid units" },
        "checksum":    { "type": "string", "description": "sha256 of canonical pieces array" }
      }
    },
    "palette": {
      "type": "array",
      "items": { "type": "object", "properties": {
        "rgba": { "type": "string", "pattern": "^#[0-9A-Fa-f]{6,8}$" },
        "name": { "type": "string" } } }
    },
    "pieces": { "type": "array", "items": { "$ref": "brickgame.placed_piece.v1" } },
    "groups": {
      "type": "array",
      "description": "Jointed sub-assemblies: mount piece, joint type, current pose.",
      "items": { "type": "object", "properties": {
        "id": { "type": "integer" },
        "parent_group": { "type": "integer" },
        "joint": { "enum": ["revolute","revolute_limited","fixed"] },
        "mount_piece": { "type": "integer" },
        "pose_deg": { "type": "number" } } }
    }
  }
}
```

Canonicalization (required for stable checksums, diffs, and multiplayer):

1. Sort `pieces` by `(pos.y, pos.z, pos.x, def, rot, color)`.
2. Renumber `id` sequentially after sorting when *exporting* a blueprint (world saves keep live ids).
3. Palette entries sorted by first use.

Serialization, compression, and migration tables: `reference.md` §3.

## 8. Fig (character) data

Generic brick-built character — original proportions, no trademarked face designs.

```json
{
  "fig": {
    "slots": ["legs", "torso", "head", "headgear", "held_l", "held_r", "back"],
    "stack_rule": "legs.stud -> torso.socket -> torso.stud -> head.socket -> head.stud -> headgear.socket",
    "held_rule":  "hand exposes 1 'clip'; held items expose 'bar'",
    "footprint":  "legs occupy 1x2 base; whole fig ≈ 1x2x12 plates",
    "face":       { "type": "decal_id", "note": "Original faces only. Ship a face editor rather than premade iconic faces." }
  }
}
```

Fig parts are ordinary pieces (family `fig`) with standard connectors — the character system falls out of the data model for free: figs can be posed via clip joints, mounted on builds via their leg sockets, and customized via the palette.

## 9. Inventory and economy data

```json
{
  "inventory": {
    "studs": 1240,
    "pieces": { "brick_2x4": 96, "plate_2x4": 40, "tile_2x2": 12 },
    "unlocked_families": ["brick", "plate", "tile"],
    "unlocked_colors": [0, 1, 2, 5, 8]
  },
  "drop_table_note": "destroyed piece → floor(cost_studs * 0.75) studs; disassembled (undo/removed) piece → returns the piece itself"
}
```

The 0.75 destruction haircut vs. full-value disassembly is the lever that makes careful disassembly and careless smashing *feel* different — tune it, don't delete it.

## 10. Godot mapping notes

| Schema | Godot type |
|---|---|
| PieceDefinition | `Resource` (`class_name PieceDef`) exported as `.tres`, one per piece; catalog = `Array[PieceDef]` |
| PlacedPiece | plain `Dictionary` or lightweight `RefCounted` — NOT a Node |
| Occupancy | `Dictionary` keyed by `Vector3i` → piece id |
| Connection graph | adjacency `Dictionary` int → `Array[int]` + edge dict keyed by `Vector2i(a,b)` |
| Blueprint | `JSON.stringify` / `JSON.parse_string` with the v2 schema |

Full implementations: `godot-recipes.md`.

## 11. Validation invariants (assert in debug builds)

- Every occupied voxel maps to exactly one piece id; every piece's voxels all map back to it.
- Every rigid edge's mated connector pair satisfies the §4 mating rule.
- Union-find island count == flood-fill island count (cross-check in tests).
- Blueprint round-trip: `load(save(world)) == world` piece-for-piece after canonicalization.
- No piece id reuse within a session (undo/redo must preserve identity).
