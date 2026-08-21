# Reference — Brick Game Systems Deep Dive

Algorithms and formats behind `SKILL.md`. Data shapes: `brick-data-model.md`. Godot code: `godot-recipes.md`.

## 1. Connectivity algorithms

### 1.1 Candidate connection detection (on placement)

For a piece being placed at `pos` with rotation `rot`:

1. Rotate its `socket_cells`; for each world socket cell `c`, look up `occupancy[c + (0,-1,0)]`. If a piece is there AND exposes a stud at that cell → candidate rigid edge.
2. Rotate its `stud_cells`; for each world stud cell `c`, look up `occupancy[c + (0,+1,0)]`. If a piece there exposes a socket at that cell → candidate rigid edge.
3. Side connectors (clip/bar, pin/hole, hinge): match on (adjacent cell, opposing `dir`, compatible type). These produce *joint* candidates, not rigid edges — accepting one converts the placement into a sub-assembly mount (see §1.4).
4. Deduplicate by neighbor id; edge strength = number of mated stud pairs (or the connector's strength).

Cost: O(footprint size) hash lookups. This is the hot path — keep it allocation-free.

### 1.2 Islands via union-find

Maintain a disjoint-set over piece ids with path compression + union by size. On placement: `union(new, neighbor)` per edge. Ground contact is modeled as union with a sentinel `GROUND = 0` node for any piece with a `y == 0` footprint cell.

- `is_grounded(id)` = `find(id) == find(GROUND)` — O(α) per query.
- Union-find handles *merges* incrementally but not *splits*; removals need §1.3.

### 1.3 Removal and re-islanding (bounded flood)

Removing a piece can split its island. Full-graph recompute is O(V+E) — fine at 1k pieces, painful at 50k. Do a bounded multi-source BFS instead:

```
on remove(piece P):
  N = neighbors(P); delete P and its edges
  unvisited = set(N)
  while unvisited:
    seed = pop(unvisited)
    frontier = [seed]; component = {seed}; grounded = false
    while frontier:
      cur = frontier.pop()
      if cur touches ground or is GROUND-united shortcut: grounded = true  # can early-exit
      for nb in adjacency[cur]:
        if nb not in component:
          component.add(nb); frontier.push(nb)
          unvisited.discard(nb)
    if not grounded: emit island_detached(component)
  rebuild union-find lazily (or rebuild only the affected components)
```

Optimizations that matter in practice:

- **Early exit** a BFS the moment it touches ground — most removals never detach anything, so typical cost is a few dozen hops.
- **Skip the BFS entirely** if the removed piece had ≤ 1 edge (a leaf can't split anything).
- After a detach event, the union-find is stale for the affected ids only; rebuild those components lazily on next query, or just re-run unions over the surviving component's edges.
- Batch removals (explosions) into one pass: delete all pieces first, then flood once from the union of their neighbors.

### 1.4 Jointed sub-assemblies

A revolute connector (bar/clip, pin, hinge, turntable) does NOT join grids. Instead:

- The child side becomes a `group` (see blueprint schema) with its own local grid and its own connection graph.
- The mount stores: parent piece id, child group id, joint type, axis, limits, current pose.
- Placement *within* a group uses the same occupancy/connection code, in group-local space.
- Nesting is allowed (hinged door on a rotating turret) but cap depth at 3–4; beyond that you are building a ragdoll, not a toy.
- Physics: a group maps to one `RigidBody3D` (or an `AnimatableBody3D` if pose is player-driven) jointed to the parent body. Bricks inside stay logical.

## 2. Stability and support checks

Pick the cheapest tier your fantasy needs. Ship tier 1 for most concept games; tier 2 makes stress challenges possible; tier 3 is for collapse spectacle only.

| Tier | Rule | Cost | Fantasy |
|---|---|---|---|
| 0 | Grounded-island check only (§1.2) | ~free | Floating islands fall as a unit |
| 1 | Support depth: BFS distance from ground ≤ per-edge cantilever cap | O(island) on change, amortized | Long unsupported arms sag/refuse |
| 2 | Load/torque heuristic per edge | O(island) with caching | Bridges have real limits; stress challenges |
| 3 | Physics handoff for verdicts | expensive, momentary | Collapse set-pieces |

### 2.1 Tier 1 — support depth

`support_depth(piece)` = min hops to any grounded piece, weighted: a hop across an edge of strength `s` costs `ceil(4 / s)` (4-stud connections are strong; 1-stud connections are weak). Refuse placement (or mark "strained" with a visual wobble) when depth exceeds `MAX_DEPTH` (tune ≈ 12). Recompute lazily per island, only when that island mutates; cache per piece.

### 2.2 Tier 2 — load and torque heuristic

For each edge E in a grounded island (approximate, good enough to *feel* right):

1. Compute the mass hanging "beyond" E: run a BFS from the far side of E with E removed; sum piece masses → `load(E)` and its center of mass `com(E)`.
2. Lever arm `L` = horizontal distance from `com(E)` to E's connection cell.
3. Stress = `load(E) * max(L, 0.5) / strength(E)`.
4. If stress > `YIELD`, mark E overstressed: creak audio + wobble shader at 80%, break (detach the far side via §1.3) at 100%.

Cache per-edge results; invalidate only the ancestor path when a subtree changes. Evaluate at ≤ 10 Hz on a background thread (or time-sliced) — stability does not need frame-rate fidelity.

### 2.3 Tier 3 — physics verdicts

When a stress event fires (wrecking ball, explosion): convert the affected island to clustered rigidbodies (recipes §10), let the engine resolve for 2–5 s, then bake survivors back to grid (round transforms to nearest cell/rot; discard pieces that moved > 1 cell from any valid snap — they become debris/pickups). One-way per event; never run continuous physics on the whole build.

## 3. Blueprint serialization

### 3.1 Format decisions

- **JSON for interchange** (schema in `brick-data-model.md` §7): debuggable, diffable, versionable. Gzip it for storage/network (`.bgz`) — brick data compresses 10–20× because it is repetitive.
- **Determinism is a feature**: canonical sort + palette indirection + sequential re-id on export ⇒ identical builds produce identical bytes ⇒ checksums detect corruption, diffs power blueprint-challenge grading, and dedupe works in user-generated-content libraries.
- **Never serialize derived data** (edges, islands, stress caches, chunk indices). Recompute on load through the normal `place()` path so loading also validates.

### 3.2 Compaction for large builds

- Palette indirection (color index, not RGBA per piece).
- Def-table indirection: `"defs": ["brick_2x4", ...]`, pieces reference by index.
- Row RLE: runs of identical `(def, rot, color)` pieces along +x compress to `{"run": n}` — walls and floors collapse dramatically.
- Quantize nothing else; positions are already ints.

### 3.3 Integrity

- `meta.checksum` = sha256 over the canonical pieces array (post-sort, pre-compression).
- On load: verify format tag → version gate → checksum (warn, don't hard-fail) → per-piece validation via `can_place` (unknown defs warn and skip; overlaps indicate corruption — abort and offer the backup).

### 3.4 Versioning and migration

Keep a linear migration chain; each step is a pure JSON→JSON function:

| From → To | Migration |
|---|---|
| v1 → v2 | Wrap loose color hex strings into the palette table; add `groups: []` |
| v2 → v3 (future) | e.g. add `decals`; default `[]` |

Run migrations in order until `version == CURRENT`. Test with a frozen corpus of old-version fixture files in CI — a blueprint that loaded yesterday must load forever.

## 4. Save formats (world vs blueprint vs profile)

| File | Contents | Cadence |
|---|---|---|
| Blueprint (`.bgz`) | One build, shareable, no player data | On explicit save/export |
| World save | Terrain/props state + embedded blueprints + placed-piece live ids | Autosave 60–120 s + on quit + before destructive events |
| Profile | Inventory, studs, unlocks, settings | On change, debounced |

Rules (compose with the `godot-save-load-system` skill for the full architecture):

- **Atomic writes always**: write `file.tmp`, flush/close, rename over the target. Keep 2–3 rotating backups (`save.1`, `save.2`); on corruption, fall back silently and tell the player once.
- **Autosave during build mode must not hitch**: serialize from a snapshot (duplicate the pieces dict — it's plain data) on a thread; never mid-cascade (destruction events defer autosave).
- Undo history is session-only; never persisted.
- Cloud-save conflicts (Steam Cloud etc.): pick newest by *play time*, not wall clock, and keep the loser as a recovery slot. Never silently merge.

## 5. Multiplayer notes (light — design before netcode)

Co-building is the natural multiplayer mode and it maps cleanly onto the op layer:

- **Server-authoritative op log.** The only network mutations are the command ops (`PlaceOp`, `RemoveOp`, `PaintOp`, composites). Server validates with the same `can_place` and broadcasts accepted ops with a sequence number. Clients apply in order.
- **Prediction**: the local client applies its op optimistically (ghost → placed) and rolls back if the server rejects (rare: conflicts on the same cells). Because ops carry full revert info, rollback = `revert()`.
- **Conflict policy**: first accepted op wins the cells; the loser's client shows the invalid thunk. Optionally soft-lock a small region (chunk or selection box) per active builder to make conflicts near-impossible in co-op.
- **Late join** = latest world snapshot (a blueprint) + op tail since that snapshot. Snapshot every N ops.
- **Determinism dividend**: because the entire sim is integer grid state + ordered ops, replays and spectating are the same machinery as late join.
- **Anti-grief** (public sessions): per-player undo, region permissions, and rate-limit ops per second server-side.

Defer anything beyond this (physics sync for debris is cosmetic — let each client simulate its own debris locally from the same detach event).

## 6. Accessibility

### 6.1 Color vision

- Base palette on colorblind-safe anchors — the Okabe–Ito set is a solid starting point: `#E69F00` orange, `#56B4E9` sky, `#009E73` green, `#F0E442` yellow, `#0072B2` blue, `#D55E00` vermillion, `#CC79A7` purple, plus black/white/grays. Expand by value (light/dark variants) rather than by adjacent hues.
- **Secondary coding**: color is never the only channel. Swatches get names (tooltip + selected-color readout); optional "pattern studs" mode embosses a subtle glyph per color family on stud tops for sorting tasks; challenge targets reference colors by name AND swatch.
- Ghost validity: valid = seated + link icon; invalid = offset + ⊘ icon + reason text. Test the whole build UI in deuteranopia/protanopia/tritanopia simulation before calling M3 (feel pass) done.

### 6.2 Motor and input

- Full rebinding (compose with `game-input-handling`); no chord-only critical actions.
- Hold-to-repeat placement with adjustable rate; toggle alternatives for every hold (orbit, drag-paint).
- Cursor snap assist: enlarge the effective pick target to the nearest valid cell within a radius (huge for gamepad building).
- No time pressure in build modes by default; timed challenges are opt-in variants.

### 6.3 Vision and comfort

- UI/text scale slider; high-contrast outline mode for the ghost and selection.
- Camera: adjustable orbit sensitivity, invert axes, reduced-motion option that dampens focus lerp.
- Photosensitivity: destruction VFX and stud sparkles must respect a flash-reduction setting (no full-screen flashes > 3 Hz, ever).

### 6.4 Cognitive

- Blueprint challenges show one layer at a time with a "pieces remaining" tray — never a wall of instructions.
- Free build has zero fail states; stress warnings are visual/audio cues, not punishments.
- Every icon action has a text label option.

## 7. Verification recipes

- **Connectivity fuzz**: script 10k random place/remove ops; assert occupancy↔pieces invariants and union-find == flood-fill island counts after every 100 ops.
- **Round-trip test**: random build → save → load → save; byte-compare the two files (canonicalization catches drift).
- **Detach oracle**: hand-author 10 fixture builds with known cut points; assert exact detached sets.
- **Perf gate**: scripted 50k-piece build; assert placement p95 < 2 ms and steady-state 60 fps before shipping new renderer work.
- **Migration corpus**: one fixture blueprint per historical version loads clean in CI.
