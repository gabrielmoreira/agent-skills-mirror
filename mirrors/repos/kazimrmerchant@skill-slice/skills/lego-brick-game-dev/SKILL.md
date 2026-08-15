---
name: lego-brick-game-dev
version: 1.0.1
description: "Assembles Godot 4 stud-and-plate construction: anisotropic grid math, occupancy plus connector validation, union-find islands, MultiMesh dirty chunks, and kinematic assembly versus pooled debris. Use for brick-building sandboxes, snap-to-grid toys, or brick-built characters. Do not use for voxel terrain without connectors, ungridded physics toys, or branded LEGO/minifigure IP."
risk: safe
source: opus-skills-library
date_added: 2026-07-15
---

# LEGO-Style / Brick-by-Brick Game Development

Build games that feel like construction toys: modular pieces, satisfying snaps,
readable builds, and worlds you can take apart. This file is the playbook; deep
dives live in sibling files (see **Package map** at the bottom for when to load
each).

## When to Use

Use when designing or implementing any game where the core verb is *assembling
modular pieces on a grid*: brick-building sandboxes, construction-toy games,
snap-to-grid base builders, brick-built characters/levels,
destruction-into-parts economies, or a "LEGO-like" concept prototype. Also use
when retrofitting an existing game with a modular build mode.

**Trigger keywords:** brick building game, construction toy, modular assembly,
snap-to-grid building, studs-and-plates, brick destruction, LEGO-like
prototype, piece catalog, brick connectivity, build mode.

### Do not use for

- **Voxel terrain deformation** (Minecraft-style cubes with no connectivity
  semantics) — bricks are *pieces with connectors*, not cells with materials.
  Reuse the grid math here, but the connectivity model is the differentiator.
- **Free-form physics sandboxes with no grid** — different fantasy; only borrow
  the break-apart pooling recipes.
- **Generic loop/pacing/balancing design** → use
  [gameplay-and-design](../gameplay-and-design/SKILL.md).
- **Character movement/camera outside build mode** → use
  [game-player-controller](../game-player-controller/SKILL.md).
- **Asset import/export pipelines** → use
  [game-assets-pipeline](../game-assets-pipeline/SKILL.md).

## IP Safety Ground Rules (Non-Negotiable)

Teach and ship **original brick-toy** design. Functional mechanisms (studs,
modular interlock, grid pitch) are implementable ideas, but:

1. **Never ship LEGO trademarks**: the word LEGO, logos, "minifigure", official
   set/theme names.
2. **No trademarked minifig face** (the classic smiley) and no logo embossing
   on studs. Design original character proportions and faces.
3. **Use neutral vocabulary** in code, UI, and store copy: brick, stud, plate,
   tile, slope, clip, hinge, pin, modular kit, brick-built, fig.
4. **Original color names** ("Signal Red", not official palette names) and
   **original piece IDs** (`brick_2x4`, not official element numbers).
5. A publisher/licensor contract overrides this section — otherwise assume
   unlicensed.

## Fantasy Pillars

Every design/taste decision must cite one of these. If a feature serves none,
cut it.

1. **Modular joy** — the snap is the atom of fun. Placement must feel *certain*:
   audible click, visual seat, instant validity feedback. If snapping feels
   mushy or ambiguous, nothing downstream saves the game.
2. **Readable pieces** — a player identifies any piece's footprint and function
   from silhouette at gameplay camera distance. Bevels, studs, and palette
   exist to serve readability.
3. **Constructive agency** — builds *matter*: they persist, they can be played
   with/on, they can be broken back into parts. Building that is purely
   decorative with no re-entry into the loop is a diorama, not a game (a valid
   concept — but choose it deliberately).

## Prerequisites

- **Engine**: Godot 4.x (Forward+ renderer). Recipes target GDScript 4.x.
- **Companion skills**: Load [gameplay-and-design](../gameplay-and-design/SKILL.md)
  for loop nesting and economy balancing; [game-player-controller](../game-player-controller/SKILL.md)
  for play-mode controllers; [game-assets-pipeline](../game-assets-pipeline/SKILL.md)
  for piece mesh authoring.
- **Reference files** (load as needed — see Package map at bottom):
  - `reference.md` — connectivity/stability algorithms, blueprint
    serialization, save formats, multiplayer notes, accessibility.
  - `brick-data-model.md` — piece taxonomy data, connector types, JSON schemas,
    coordinate conventions.
  - `godot-recipes.md` — Godot 4 node architecture, grid/snap GDScript,
    MultiMesh chunks, pooling, camera, undo.
  - `examples.md` — three scoped concept-game vertical slices with milestones
    and kill criteria.

## Procedure

### 1. Define the Grid & Coordinate System

The grid is anisotropic: horizontal unit = 1 stud pitch (cell); vertical unit =
1 plate height = 0.4 cell. A standard brick = 3 plates tall (1.2 cells).

1. Store all positions as `Vector3i` in (stud, plate, stud) space.
2. Convert to world coordinates via constants **only** at render/physics time.
   Centralize conversion in one constants module — never scatter magic numbers.
3. Quantize rotation: yaw ∈ {0°, 90°, 180°, 270°} for grid pieces. Continuous
   DOF (hinges, turntables, pins) creates a *jointed sub-assembly* that leaves
   the grid and becomes its own frame — treat it as a mounted child build, not
   a grid resident.

> **Load `reference.md`** for full connectivity/stability algorithms and
> coordinate conventions. **Load `brick-data-model.md`** for JSON schemas and
> connector type definitions.

### 2. Implement Occupancy + Connector Checks

Pieces occupy voxels **AND** expose connectors. Both checks must pass to place.

1. **Occupancy check**: does the piece's voxel footprint fit at the target
   position without overlapping existing pieces?
2. **Connector check**: does at least one valid connector pair exist between the
   new piece and an existing piece (or ground)?
3. Reject placement if either check fails. Report the reason diegetically
   ("no support", "overlaps") — never rely on color alone (accessibility).

### 3. Build the Connection Graph

The connection graph is the source of truth for structure.

1. Nodes = placed pieces; edges = realized connections.
2. Compute assembly islands via union-find.
3. On removal, trigger a **local re-flood** to detect splits.
4. Grounded islands are stable; airborne islands fall (or float — decide once,
   early, per game).
5. **Never serialize derived data** (connection edges, islands) in blueprints
   — recompute on load; serializing invites corruption drift.

### 4. Curate the Piece Catalog

Curate ruthlessly. A 25-piece catalog with clean roles beats 400 pieces of
noise. Canonical starter set:

| Family | Members | Role |
|---|---|---|
| Bricks | 1x1, 1x2, 1x4, 2x2, 2x4, 2x8 | Mass, walls, the workhorses |
| Plates | 1x1 … 4x8 (⅓ brick height) | Floors, offsets, fine vertical control |
| Tiles | 1x1, 1x2, 2x2 (plate height, no top studs) | Smooth capping, roads, "finished" surfaces |
| Slopes | 45° 2x1, 33° 3x1, inverted | Roofs, ramps, softened silhouettes |
| Round | 1x1 round brick/plate, dome | Pillars, organic accents |
| Brackets | 1x2–1x2 90° stud redirect | Sideways building |
| Clips & bars | 1x1 clip, 1x4 bar | Rotating mounts, held items |
| Hinges | 1x2 hinge base + top | Doors, ramps, limited-DOF joints |
| Pins & beams | pin, 1x4/1x6 pin-hole beam | Technic-like rotation axes, wheels (abstract, original geometry) |
| Specials | arch, window frame, door frame, turntable, wheel+axle | Set dressing with honest footprints |
| Fig parts | head, torso, legs, hair/hat, held-item socket | Generic brick-built characters (original faces only) |

Rules: every piece has an exact voxel footprint (no "roughly 1x2"); decorative
pieces still occupy honestly; introduce piece *families* gradually via
progression.

> **Load `brick-data-model.md`** for full piece data, connector types, and JSON
> schemas.

### 5. Implement the Core Loop

```
browse catalog → select piece → ghost preview (snap + validity)
   → place/snap (click!) → validate connection → decorate (paint/tiles)
   → stress-test / play with the build → disassemble or destroy → studs/parts
   → back to catalog (richer inventory)
```

Design rules:

1. **Catalog browse must be < 3 s to any core piece.** Hotbar the 8–12
   workhorse pieces; search/categories for the rest.
2. **Ghost preview is always-on** while a piece is selected. It shows position,
   rotation, AND validity before commit. Never let a click surprise the player.
3. **Validation is diegetic**: valid = seated ghost + highlight of the studs
   that will connect; invalid = offset ghost + icon + reason ("no support",
   "overlaps"). Never rely on color alone.
4. **Decoration is a separate cheap pass** (paint tool, tile capping) so
   players rough-in shape first, beautify second.
5. **Close the loop with re-entry**: destruction/disassembly returns resources
   (studs, parts) that feed the next build. This converts "undo" from admin
   into economy.

### 6. Implement Build Modes (in priority order)

Ship in priority order — each is a multiplier on the previous:

1. **Free place** — grid-snapped single placement with ghost. The MVP.
2. **Drag-paint** — hold-and-drag places a row/column of the selected piece.
3. **Multi-select** — box-select placed pieces; move/delete/recolor as a unit
   (one composite undo op).
4. **Copy/stamp patterns** — selection → sub-blueprint clipboard → stamp
   repeatedly (with rotation).
5. **Mirror mode** — live mirroring across a user-set plane.
6. **Section planes** — clip rendering above a chosen plate layer to edit
   interiors.

Every mode routes through the same `PlaceOp`/`RemoveOp` command layer — undo,
networking, and replays all depend on this single choke point.

> **Load `godot-recipes.md` §9** for the command layer implementation.

### 7. Implement Physics (Two Regimes)

Never blur these two regimes:

- **Assembly regime (default)**: placed pieces are static/kinematic. Collision
  = merged static shapes per chunk. Zero per-brick physics cost. Stability is
  *simulated logically* (support/torque heuristics), not by the physics engine.
- **Break-apart regime (moments)**: on damage/collapse, the affected island (or
  fragment) converts to pooled `RigidBody3D` debris — one body per *fragment
  cluster*, not per brick, unless the cluster is small (≤ ~8 bricks). Debris
  lives 2–5 s, then despawns into stud pickups.
- **The transition is one-way per event**: assembly → debris → pickups. Never
  let debris re-snap mid-flight; re-attachment happens through the build loop.
- **Jointed sub-assemblies** (vehicles, hinged doors): the island becomes one
  `RigidBody3D` with baked compound collision; internal bricks stay logical.
  Joints (pins/hinges) map to physics joints between sub-assembly bodies only.

**Budget**: worst case ≤ 64 active rigid bodies on screen. Enforce with
cluster merging and pool caps, not hope.

> **Load `reference.md`** for full stability/support algorithms.

### 8. Implement Build UX

- **Rotation**: a single key/button steps yaw 90°; show a rotation gizmo
  (arrow arc) on the ghost. Gamepad: shoulder buttons. Never require dragging a
  3D gizmo handle for yaw.
- **Vertical control**: scroll/shoulder shifts the target plate layer; default
  targets the top of the stack under the cursor (raycast top face → next free
  plate).
- **Color picker**: curated palette grid (12–24 swatches), each with a name
  tooltip; eyedropper samples a placed brick; paint tool repaints without
  re-placing.
- **Undo stack**: command pattern, unlimited depth in-session; groups
  drag-paint and multi-ops into single entries; **restores inventory** on undo
  of a place and restores placement on undo of a delete. Redo is mandatory.
- **Camera**: orbit around a focus point that follows the build's bounds (or
  the cursor target), scroll zoom, plate-height panning; clamp pitch; optional
  first-person walk mode for playtesting builds.
- **Feedback**: snap click (pitch varied ±10% to avoid ear fatigue), stud
  sparkle on connect, soft error thunk + reason on invalid. The click IS
  game-feel budget line-item #1.

> **Load `godot-recipes.md` §12** for camera implementation.

### 9. Optimize Performance

Numbers assume Godot 4.x Forward+.

1. **Never one Node per brick.** Placed bricks are data (grid entries + graph
   nodes) rendered via MultiMesh.
2. **MultiMesh batching**: one `MultiMeshInstance3D` per (chunk, mesh) with
   per-instance color; re-bake only dirty chunks (16×16 studs, full height) on
   place/remove — never the whole build.
3. **Piece pooling**: pre-warm pools for ghosts, debris rigidbodies, stud
   pickups, snap VFX. Zero allocations during steady-state building.
4. **LOD for large builds**: near = instanced true geometry (studs modeled);
   mid = stud-less shells with normal-mapped studs; far = merged chunk mesh or
   imposter. Switch per chunk by distance.
5. **Collision**: merged static shapes per chunk; box-approximate per piece;
   refresh on the same dirty-chunk cadence.

**Targets**: 60 fps at 50k placed pieces; single placement < 2 ms (validation +
amortized chunk rebake); island re-check after removal < 1 ms typical via
local flood.

> **Load `godot-recipes.md`** for full node architecture, MultiMesh chunk
> GDScript, and pooling code.

### 10. Apply Art Direction

- **Material**: uniform slightly-glossy plastic (roughness ≈ 0.25–0.4); ONE
  material with per-instance color — this is both the look and the batching
  strategy.
- **Bevel everything**: ~0.02-cell edge bevels on every piece; bevels catch
  light and keep edges readable at distance. Bake into the mesh; don't rely on
  shader tricks at LOD0.
- **AO seats the pieces**: SSAO plus subtle baked contact-darkening at stud
  lines makes builds read as *connected*, not intersecting.
- **Palette constraints**: 12–24 curated colors in consistent saturation/value
  bands; grays + 2 accent hues for structural sets, brights for creative sets.
  Verify all pairs under colorblind simulation.
- **Scale cues**: depth-of-field / tilt-shift in photo mode, oversized world
  props (pencil, mug) sell the miniature fantasy without any licensed reference.
- **Faces & figs**: original proportions, printed-style flat facial features,
  no trademarked smiley. Give figs a silhouette differentiator (head shape,
  torso taper) so they're *yours*.

> **Load `reference.md` §6** for accessibility/colorblind verification details.

### 11. Prototype Milestones (Graybox → Vertical Slice)

Gate each milestone with a predicate; don't advance on vibes.

| # | Milestone | Gate predicate |
|---|---|---|
| 0 | Grid + ghost + place/remove one brick type | Place/remove 500 bricks, zero mis-snaps, undo works |
| 1 | Catalog (8 pieces) + rotation + color | Build a recognizable house in < 5 min, first try |
| 2 | Connectivity graph + support rule | Removing a load-bearing brick visibly drops the roof |
| 3 | Feel pass: click, sparkle, camera polish | 3 testers each build ≥ 10 min unprompted |
| 4 | Destruction → studs → spend loop | Testers voluntarily smash-and-rebuild; economy readouts sane |
| 5 | Vertical slice: one challenge mode + free build + save/load | New player completes a challenge unaided; blueprint round-trips |

**Kill criterion (pre-committed)**: if milestone 3 fails twice after feel
iteration, the core snap isn't fun — stop and re-examine piece scale/camera/
click before building more systems.

> **Load `examples.md`** for three full scoped concept-game vertical slices
> with milestones and kill criteria.

### 12. Design Progression for Concept Games

Sequence for a concept prototype:

1. **Free build** — sandbox with the starter catalog. Baseline test: is placing
   bricks fun for 10 minutes with zero goals? If not, fix feel before adding
   modes.
2. **Blueprint challenges** — rebuild a target following step-by-step
   instructions (auto-generated from a blueprint's layer order). Teaches
   catalog + camera; success = exact match diff.
3. **Constrained challenges** — "bridge this gap with ≤ 40 pieces / plates
   only". Creativity under constraint; validate functionally (walk a fig
   across), not by shape-matching.
4. **Functional/stress challenges** — leverage the stability sim: hold X
   weight, survive the wrecking ball. Your connectivity model becomes
   *content* here.
5. **Destruction economy** — smash brick-built world objects → studs → spend
   on catalog/palette unlocks. Unlock cadence: one new piece *family* (not one
   piece) per milestone, so each unlock changes what's buildable.

**Meta rule**: challenges must never punish creative solutions that meet the
functional predicate. Grade the outcome, not the method.

## Pitfalls

- **Unreadable micro-pieces** in the gameplay catalog (1x1 quarter-tiles,
  greebles). Detail pieces belong in a late-game "detailing" family, never in
  the hotbar.
- **Soft-body / per-brick physics spam** — simulating every brick as a
  rigidbody. Islands and clusters, always.
- **Free-float placement mixed into the grid fantasy** — if anything can go
  anywhere, the snap stops meaning something. Off-grid = jointed sub-assembly,
  explicitly.
- **One Node per brick** — dies around ~5k pieces.
- **Serializing derived data** (connection edges, islands) in blueprints —
  recompute on load; serializing invites corruption drift.
- **Undo that leaks resources** — undo of place must refund; undo of delete
  must re-spend.
- **Full-rebuild renderers** — re-baking all MultiMeshes on every placement.
- **Free 360° rotation on grid pieces** — quantize yaw or watch every
  connection edge case explode.
- **Trademark risk** — official names, logo-embossed studs, the classic smiley
  face, licensed theme trade dress. See IP ground rules above.
- **Catalog bloat before feel** — adding piece #50 before the snap of piece #1
  feels great.
- **Color-only validity feedback** — always include a text/icon reason for
  invalid placement (accessibility).

## Verification

Run through this checklist before shipping any milestone:

- [ ] Grid uses stud/plate anisotropic units; all positions `Vector3i`; world
      conversion centralized in one constants module
- [ ] Occupancy AND connector checks both gate placement
- [ ] Connection graph with union-find islands; removal re-floods locally
- [ ] Ghost preview shows position + rotation + validity + reason before commit
- [ ] All mutations flow through command ops (place/remove/paint/move); undo/
      redo with inventory symmetry
- [ ] Assembly is kinematic; break-apart uses pooled clustered rigidbodies with
      hard caps (≤ 64 active)
- [ ] MultiMesh chunked rendering with dirty-chunk rebake only; no per-brick
      Nodes
- [ ] Curated palette (12–24), colorblind-verified, named swatches
- [ ] Snap feedback: pitch-varied click + stud highlight + seated ghost
- [ ] Destruction returns studs/parts; the economy closes the loop
- [ ] Blueprint save/load round-trips byte-stable (derived data recomputed)
- [ ] Milestone gates 0–5 passed in order; feel gate (M3) before systems depth
- [ ] Zero trademarked names/logos/faces in assets, code identifiers, UI copy
- [ ] Fig characters use original proportions and face designs

**Performance verification commands (Godot 4.x):**

```
# In Godot debugger console or print():
# Verify placement latency
print("Place op ms: ", Time.get_ticks_usec() - start_us)
# Target: < 2000 (2 ms)

# Verify active rigidbody count
print("Active bodies: ", get_tree().get_nodes_in_group("debris").size())
# Target: ≤ 64

# Verify FPS at scale
print("FPS: ", Engine.get_frames_per_second())
# Target: ≥ 60 at 50k placed pieces
```

## Package Map

| File | Load when |
|---|---|
| `reference.md` | You need connectivity/stability algorithms, blueprint serialization, save formats, multiplayer notes, or accessibility/colorblind verification (§6) |
| `brick-data-model.md` | You need piece taxonomy data, connector types, JSON schemas, or coordinate conventions |
| `godot-recipes.md` | You need Godot 4 node architecture, grid/snap GDScript, MultiMesh chunks, pooling, camera (§12), or undo command layer (§9) |
| `examples.md` | You need scoped concept-game vertical slices with milestones and kill criteria |

## Related Skills

- [gameplay-and-design](../gameplay-and-design/SKILL.md) — loops, pacing, feel,
  balancing the stud economy (sinks/faucets)
- [game-player-controller](../game-player-controller/SKILL.md) — play-mode
  movement and cameras; the build-mode orbit camera stays in this skill
- [game-assets-pipeline](../game-assets-pipeline/SKILL.md) — piece mesh
  authoring, naming, import presets, collision meshes, LOD chain
- `godot-save-load-system` — save architecture beyond recipes here
- `godot-scene-organization` — scene layout beyond recipes here
