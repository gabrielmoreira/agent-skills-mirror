# Examples — Three Concept-Game Vertical Slices

Three fully scoped slices that exercise different parts of the brick stack. Each is buildable by a solo dev; each proves (or kills) a distinct hypothesis. Pick ONE — do not blend them for a first prototype. All names/themes are original and IP-safe.

---

## Slice A: "Brickfall Bastion" — build-defense

**Pitch:** Waves of tumble-bots march on your gate. Between waves, spend harvested studs to build walls, towers, and traps brick-by-brick. Everything you build can be chipped apart — theirs and yours.

**Hypothesis proven:** the *build ↔ destroy economy* is fun under pressure. This slice stresses: destruction cascades, stud pickups, rebuild speed, and stability tier 1.

**Pillars served:** constructive agency (builds are your defense), modular joy (fast confident placement under a timer).

### Piece subset (keep it this small)

`brick_1x2`, `brick_2x4`, `brick_2x8`, `plate_2x4`, `tile_2x2` (walkway tops), `slope_45_2x1` (deflectors), `window_1x2x2` (arrow slits). Seven pieces. No joints, no figs.

### Scope box

| In | Out |
|---|---|
| One lane, one gate, 5 waves | Pathfinding around player walls (enemies attack what blocks them) |
| Enemy = capsule that melees bricks (edge HP) | Enemy variety, ranged, flying |
| Stud economy: harvest drops, build costs | Meta progression, unlocks |
| Stability tier 1 (cantilever cap) | Tier 2 torque, physics collapse |
| Build phase timer 60 s | Simultaneous build-during-combat |

### Loop

`wave ends → studs magnet in → 60 s build phase (repair + extend) → wave hits → bricks chip into debris/studs → repeat`. Difficulty = wave DPS vs. your architecture quality.

### Milestones

| # | Deliverable | Gate |
|---|---|---|
| A0 | Lane graybox + place/remove + stud counter | Build a wall in < 30 s using drag-paint |
| A1 | Enemy that damages edges; debris → pickups | Watching a wall crumble reads clearly at gameplay camera |
| A2 | Wave loop + build timer + costs | A tester survives wave 3 by *rebuilding smarter*, not just bigger |
| A3 | Feel pass: chip VFX, click, wave stingers | Testers describe destruction as "satisfying" unprompted |
| A4 | 5-wave slice + win/lose + retry | 3 of 5 new players finish; median session ≥ 12 min |

**Kill criterion:** if A2 testers just build one thick cube every time (no architectural decisions), the defense fantasy is dead — either add enemy siege variety (out of scope) or kill the slice.

**Telemetry:** studs earned/spent per wave, pieces placed per build phase, % of placements that are repairs vs. new structure.

---

## Slice B: "Studbound Speedway" — build-a-kart physics playground

**Pitch:** Assemble a kart from a small kit — chassis plates, wheels, pins, seat, deflectors — then drive it down a hazard gauntlet. Parts shear off on impact. Limp to the finish or pit-rebuild with whatever you salvaged.

**Hypothesis proven:** *jointed sub-assemblies + functional building* are fun: does building something that WORKS (rolls, steers, survives) beat building something that merely looks right?

**Pillars served:** constructive agency (your engineering determines the run), readable pieces (function must be legible: wheels roll, slopes deflect).

### Piece subset

`plate_2x8` (chassis), `plate_2x4`, `brick_1x2`, `slope_45_2x1` (ram/aero), `beam_1x4_holes`, `pin`, `wheel_small` + `axle_2`, `fig_torso`+`fig_head` (driver, socket-mounted). Nine defs. Exactly one joint type (pin/axle revolute).

### Scope box

| In | Out |
|---|---|
| One kart = one rigid body + 4 wheel joints | Suspension, motors, gearing |
| Shear rule: impact impulse > edge strength × k → piece detaches | Full stress sim (tier 2) |
| One 90-second gauntlet track, 3 hazards | Track editor, opponents |
| Pit zone: 30 s rebuild from salvage | Economy, shops |
| Kart save/load as blueprint `group` | Livery/decals |

### Loop

`build kart on a 6×10 pad → roll out → hazards shear pieces → pit or push on → finish line scores (time × surviving pieces)`. The score formula forces the build-tough vs. build-light tradeoff.

### Milestones

| # | Deliverable | Gate |
|---|---|---|
| B0 | Pad + kart assembly → one RigidBody with wheel joints | Anything with 4 wheels drives; anything without doesn't |
| B1 | Shear-on-impact detach (recipes §10 pool) | Losing your front slope visibly changes the next collision |
| B2 | Gauntlet + timer + pit rebuild | Testers redesign between runs (observed, unprompted) |
| B3 | Feel: engine putter, shear *crack*, wobble on strain | Crash compilations are voluntarily replayed |
| B4 | Score screen + blueprint save of best kart | A saved kart reloads and drives identically |

**Kill criterion:** if B2 shows testers converging on one dominant kart shape within 3 runs, the design space is too flat — widen hazard variety once; if it persists, kill.

**Telemetry:** pieces at start vs. finish, pit usage rate, distinct kart topologies per player (hash the blueprint).

---

## Slice C: "Pocket Diorama" — cozy free-build with blueprint challenges

**Pitch:** A palm-sized floating island. Build tiny scenes — a cottage, a pier, a windmill — in pure zen, or follow layer-by-layer blueprint challenges to learn techniques. Finish with photo mode: tilt-shift, golden hour, done.

**Hypothesis proven:** the *snap itself* carries a game with zero pressure — pure modular joy + readable beauty. This is the feel-first slice: if this isn't pleasant, your foundation is wrong for ALL brick games.

**Pillars served:** modular joy (the whole game IS the snap), readable pieces (dioramas must read as scenes at photo distance).

### Piece subset

Full starter families: bricks, plates, tiles, slopes, round, `arch_1x4`, `window_1x2x2`, `door_1x2x3`, one fig. ~20 defs, 16-color palette (colorblind-verified, named swatches).

### Scope box

| In | Out |
|---|---|
| One 24×24 island, plate-layer terrain | Terrain editing, water sim |
| Free build + full undo + mirror mode | Multi-select/stamp (add post-slice) |
| 3 blueprint challenges (cottage/pier/windmill), layer-by-layer UI | Challenge editor |
| Photo mode: orbit, DOF/tilt-shift, time-of-day slider | Sharing/export beyond screenshots |
| Ambient audio + snap click suite | Music system |

### Loop

`pick blueprint or free build → place/paint/cap with tiles → step back (orbit) → photo → next idea`. Session shape is intentionally loop-light: the reward is the diorama itself plus a completion stamp per challenge.

### Milestones

| # | Deliverable | Gate |
|---|---|---|
| C0 | Island + 8 pieces + ghost/undo/palette | 10-minute unprompted build (the Kleenex test) — THE gate |
| C1 | Full catalog + mirror + tile capping | A tester's cottage is recognizable as a cottage in a blind screenshot test |
| C2 | Blueprint challenge UI (layer tray, match diff) | A new player finishes the cottage unaided in < 15 min |
| C3 | Photo mode + ambience | Testers screenshot without being asked |
| C4 | Save/load + 3 challenges + polish | Blueprint round-trip byte-stable; zero placement bugs in a 1-hour soak |

**Kill criterion:** C0 failing twice after feel iteration (click/camera/scale passes) kills not just the slice but the current foundation — fix the snap before attempting ANY brick game.

**Telemetry:** session length, pieces per session, undo rate (high undo + long sessions = engaged tinkering; high undo + short sessions = fighting the controls), photo-mode entries.

---

## Choosing between the slices

| You want to validate… | Build |
|---|---|
| Destruction economy, combat pressure | **A — Brickfall Bastion** |
| Functional/jointed building, physics spectacle | **B — Studbound Speedway** |
| Core feel, UX depth, art direction | **C — Pocket Diorama** |

If this is your first brick game: **build C first anyway** (even a 2-day cut of C0–C1). A and B both sit on top of the snap; C is the cheapest honest test of it. Then carry the validated foundation into A or B.

## Shared verification (all slices)

- [ ] Slice uses ≤ 10 piece defs (A/B) or ≤ 20 (C) — catalog restraint held
- [ ] All mutations went through the op layer; undo worked in every playtest
- [ ] Connectivity fuzz test (reference.md §7) green before each playtest build
- [ ] Milestone gates hit in order; no gate skipped on vibes
- [ ] Kill criteria were written down BEFORE the milestone, not after
- [ ] Zero trademarked names/faces/logos in any slice asset or UI string
