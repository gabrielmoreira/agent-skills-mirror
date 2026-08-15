---
name: browser-game-architecture
version: 1.0.1
description: >-
  Owns the HTML5/itch.io game shell: fixed-timestep loop, scene stack, input,
  audio unlock, asset preload, versioned saves, letterbox scaling, and Vite/PWA
  build. Use when starting or restructuring a Canvas, WebGL, or DOM-hybrid web
  game. Not for Three.js renderer APIs (threejs-game-development), Godot/Unity,
  or generic SPA dashboards.
risk: safe
source: opus
date_added: 2026-07-15
---

# browser-game-architecture

Own the *whole-game shell* of a browser game, independent of rendering technology: the loop that drives it, the scenes that structure it, the input/audio/asset/save subsystems that every game needs, the scaling layer that makes it fit any screen, and the build that ships it to itch.io or the open web. Rendering-tech specifics (Three.js APIs, shader work) belong to sibling skills — this skill makes the *architecture around the renderer* correct, portable, and shippable.

The browser is a hostile game platform in specific, predictable ways: audio is locked until a user gesture, background tabs freeze `requestAnimationFrame`, mobile Safari fights you over scrolling and zoom, storage can be denied or wiped, and every player has a different screen. This skill exists because the same ten failures ship in almost every first browser game. Follow it and none of them will be yours.

## When to Use

- Starting any new browser game — before the first line of gameplay code, decide backend, loop, and module layout here
- Structuring a game loop: fixed-timestep simulation, render interpolation, pause, timescale, tab-away safety
- Scene/screen flow: boot → preload → title → gameplay → pause → game over, as a scene stack
- Input: unified keyboard/pointer/touch/gamepad behind an action-mapping layer
- Audio: Web Audio unlock pattern, music/SFX buses, mobile quirks
- Asset loading: preload manifests, progress bars, decode without jank, per-scene lazy loading
- Saving: localStorage vs IndexedDB choice, versioned save schemas, migrations, flush-on-hide
- Responsive scaling: logical resolution, letterboxing, devicePixelRatio, safe areas, orientation
- Making a game installable/offline with a PWA service worker (optional layer)
- Performance triage: GC pressure, per-frame allocation, draw-call and decode jank
- Shipping: Vite config, single-file builds, itch.io zip requirements, GitHub Pages/Netlify, cache busting

**Do not use for:**
- **Three.js API specifics** (materials, glTF, postprocessing, dispose) — use `threejs-game-development`
- **Native/engine games** (Godot, Unity, UE5) — use the `godot-*` and engine skills
- **Game design theory** (mechanics, economy, difficulty curves) — use `gameplay-and-design`
- **Deep engine-agnostic subsystem theory** — `game-input-handling`, `game-audio-system`, `game-state-machine`, `game-camera-system` own the concepts; this skill owns their *browser-specific implementation and integration*
- **Generic web apps** (SPAs, dashboards, sites) — use `frontend-ui-implementation`

## Prerequisites

### Bundled references — load on demand, do not paste wholesale into context

Load each reference file only when the task touches its domain:

- **`reference.md`** — Load when implementing any subsystem: rendering backend selection and setup (Canvas 2D, WebGL/Three.js, DOM hybrid), input (keyboard/pointer/touch/gamepad + action mapping), audio (unlock, buses, formats), asset loading, persistence (localStorage/IndexedDB, schema versioning, flush hooks), responsive scaling and DPR, page lifecycle, PWA, error resilience
- **`loop-and-state.md`** — Load when building or debugging the game loop or scene/state architecture: rAF timing, fixed timestep with accumulator and interpolation, spiral-of-death guards, clocks (pause/timescale/unscaled), background-tab behavior, scene stacks, entity architecture (OOP vs composition vs ECS), event bus, game-clock timers/tweens, determinism and seeded RNG, update ordering
- **`build-and-deploy.md`** — Load when scaffolding, building, or shipping: toolchain (zero-build vs Vite), project scaffold, asset pipeline at build time, single-file builds, deploy targets (itch.io in detail, GitHub Pages, Netlify/Cloudflare), service workers in production, performance budgets and profiling, release checklist, versioning/cache-busting
- **`examples.md`** — Load when you need copy-pasteable code: a full minimal single-file game (loop + scenes + input + audio + save + letterbox scaling), plus standalone drop-in modules: AssetLoader, AudioManager, SaveManager, letterbox canvas helper, object pool, service worker, itch.io-ready Vite config

### Sibling skill routing

| Need | Skill |
|---|---|
| Three.js renderer, glTF pipeline, physics, WebGL specifics | `threejs-game-development` |
| Input abstraction *theory* (buffering, coyote time, rebinding UX) | `game-input-handling` |
| Audio design theory (mixing, adaptive music, synthesis depth) | `game-audio-system` |
| FSM/HSM theory for entities and AI | `game-state-machine` |
| Profiling methodology and tooling discipline | `game-performance-profiling` |
| Pre-release audit: perf, compatibility, polish checklist | `web-game-release-review` |
| Automated browser QA (load page, console errors, screenshots) | `chrome-browser-automation` |
| Mechanics, progression, difficulty, meta-loop design | `gameplay-and-design` |

This skill owns the *integration*: how these subsystems compose into one game that boots, runs, pauses, saves, and ships.

## Procedure

### Step 1 — Decide the rendering backend

Decide this first; it constrains everything downstream. Full trade-off detail in `reference.md` §1.

```
Is the game 3D, or does it need thousands of sprites / shaders / lighting?
├─ YES → WebGL. Use Three.js (compose with threejs-game-development)
│         or Pixi.js for 2D-at-scale. Plan for context loss handling.
└─ NO → Is it primarily a board / card / word / menu-driven game where
        the "board" is a layout, not a simulation?
        ├─ YES → DOM/CSS hybrid. Native text, accessibility, CSS animation
        │         (transform/opacity only). Canvas only for particles/FX.
        └─ NO → Canvas 2D. The default for arcade/action/puzzle 2D games.
                One canvas, logical resolution, DPR-aware backing store.
```

Hybrid is normal and good: Canvas playfield + DOM overlay for HUD/menus is the highest-leverage split — you get canvas performance where it matters and free text layout, focus handling, and CSS where it doesn't. Rule: **one owner per pixel region** — never composite DOM elements *under* a transparent canvas that repaints every frame.

### Step 2 — Scaffold the architecture spine

Canonical module layout (names matter less than the dependency direction — subsystems never import scenes; scenes import subsystems):

```
src/
  main.js          // boot: create systems, register scenes, start loop
  core/
    loop.js        // fixed-timestep driver (loop-and-state.md §2)
    scenes.js      // scene stack manager (loop-and-state.md §5)
    events.js      // tiny pub/sub bus
    clock.js       // game time, timescale, pause; unscaled UI time
  systems/
    input.js       // device listeners → action map (reference.md §2)
    audio.js       // AudioContext, unlock, buses (reference.md §3)
    assets.js      // manifest loader with progress (reference.md §4)
    save.js        // versioned persistence (reference.md §5)
    display.js     // canvas, resize, DPR, letterbox (reference.md §6)
  scenes/
    boot.js        // sync init, then push preload
    preload.js     // load manifest, draw progress, then push title
    title.js
    game.js
    pause.js       // pushed OVER game; game renders beneath, frozen
    gameover.js
  game/            // actual gameplay: entities, levels, rules
```

Boot order is fixed: **display → input → audio(construct only) → save(read) → scene stack → loop start**. Audio *unlock* happens later, on first user gesture — never at boot.

### Step 3 — Implement the game loop

Load `loop-and-state.md` §2 for full implementation details. Core requirements:

1. Use `requestAnimationFrame` as the driver.
2. **Clamp delta time**: `dt = min(dt, 250ms)` before the accumulator, always. First frame after tab-return can be 30+ seconds.
3. **Fixed timestep for simulation** if gameplay involves physics, collision, or anything tunable by feel. Render interpolates. Variable timestep is acceptable only for pure-presentation games.
4. Guard against spiral-of-death (accumulator cap).
5. Pause the clock on `visibilitychange → hidden`.

### Step 4 — Implement subsystems

Load `reference.md` for the relevant sections as you implement each subsystem:

1. **Display** (§6): DPR-aware canvas with a logical resolution. Backing store = CSS size × min(devicePixelRatio, 2); draw in logical units via one `setTransform`. Never draw in CSS pixels on a 1× backing store — it's blurry everywhere that matters.
2. **Input** (§2): Unified keyboard/pointer/touch/gamepad behind an action-mapping layer. Use `e.code` for movement keys (positional — WASD works on AZERTY), `e.key` for typed text. Set `touch-action: none` on the game surface plus `preventDefault` discipline.
3. **Audio** (§3): Create the `AudioContext` up front (it starts `suspended`), call `resume()` inside the first `pointerdown`/`keydown`. Design the title screen to require a click ("Click to start") so unlock is guaranteed. Music/SFX buses, mobile quirks.
4. **Assets** (§4): Preload manifests with progress bars. Never start the loop against half-loaded assets; never render canvas text before `document.fonts.ready`. Decode without jank; per-scene lazy loading.
5. **Save** (§5): localStorage vs IndexedDB choice. Version the save schema from day one: `{ v: 1, ... }` plus a migration table. Wrap all storage access in try/catch — private mode and quota denials are real. Save on `visibilitychange → hidden`, not `beforeunload` (which never fires on mobile process-kill). Debounce autosaves; flush on hide.

### Step 5 — Wire page lifecycle

1. On `visibilitychange → hidden`: pause the clock, suspend/duck audio, flush save.
2. On `visibilitychange → visible`: resume clock, resume audio.
3. rAF stops in background tabs but Web Audio keeps playing — silent-tab music is a top player complaint. Always suspend audio on hide.

### Step 6 — Build and deploy

Load `build-and-deploy.md` for full details. Key decisions:

1. **Toolchain**: zero-build single file for jams/prototypes; Vite for anything with more than ~3 files or any dependency.
2. **Relative asset paths** (`./` base) so the same build works on itch.io's CDN subdirectory, GitHub Pages subpaths, and local file testing.
3. **Single-file builds** for itch.io when needed.
4. **itch.io**: zip requirements, CDN subdirectory path issues — ship a build in week one to find these early.
5. **GitHub Pages / Netlify / Cloudflare**: standard static hosting with cache-busting.

### Step 7 — Quick-start checklist (for a new game, in order)

1. Pick backend via the decision tree in Step 1; pick logical resolution (960×540 and 1280×720 are safe 16:9 defaults; design portrait-first ~720×1280 if mobile-primary).
2. Scaffold: zero-build single file for jams/prototypes, Vite for anything with more than ~3 files or any dependency.
3. Drop in the spine: loop, scene stack, display/resize, input, from `examples.md`.
4. Add the preload scene with a manifest before adding the third asset, not after the thirtieth.
5. Wire audio unlock into the title screen's "click to start".
6. Add SaveManager with `v: 1` the moment anything is worth persisting.
7. Wire `visibilitychange` → pause + save flush.
8. Ship a build to the target platform in week one — itch.io path/zip issues are cheaper to find early.
9. Before release: run `web-game-release-review`; smoke-test with `chrome-browser-automation`.

## Pitfalls

These are the defects that ship in almost every first browser game. Each is cheap now and expensive later.

1. **Unclamped delta time.** First frame after tab-return can be 30+ seconds, blowing through the accumulator and freezing the game. Always `dt = min(dt, 250ms)` before the accumulator. (loop-and-state.md §2)
2. **Variable timestep for physics/collision.** Makes gameplay feel different at different frame rates and breaks replay/determinism. Use fixed timestep with render interpolation. (loop-and-state.md §2)
3. **Audio not unlocked.** `AudioContext` created at boot stays `suspended` without a user gesture. Create up front, call `resume()` inside first `pointerdown`/`keydown`, and require a click on the title screen. (reference.md §3)
4. **Mobile scroll/zoom hijacks input.** Missing `touch-action: none` on the game surface or missing `preventDefault` on touch events. Mobile Safari will fight the player. (reference.md §2)
5. **Wrong key property.** Using `e.key` for movement (breaks on AZERTY — WASD becomes ZQSD). Use `e.code` for movement keys (positional), `e.key` for typed text. (reference.md §2)
6. **Blurry canvas on high-DPR screens.** Drawing in CSS pixels on a 1× backing store. Backing store must be CSS size × min(devicePixelRatio, 2), with one `setTransform` to draw in logical units. (reference.md §6)
7. **Save lost on mobile process-kill.** `beforeunload` never fires on mobile. Save on `visibilitychange → hidden` instead. Debounce autosaves; flush on hide. (reference.md §5)
8. **Unversioned save schema.** No migration path when the schema changes. Version from day one: `{ v: 1, ... }` plus a migration table. Wrap all storage access in try/catch — private mode and quota denials are real. (reference.md §5)
9. **Silent-tab music.** rAF stops in background tabs but Web Audio keeps playing. Players return to a tab with music blaring. Always suspend/duck audio on `visibilitychange → hidden`. (reference.md §7)
10. **Per-frame allocation causing GC hitches.** Closures, array literals, or object creation inside update/render. Pool particles/projectiles; reuse vectors. GC hitches are the #1 cause of periodic stutter in JS games. (build-and-deploy.md §8)
11. **Half-loaded assets at loop start.** Starting the loop before assets finish loading causes missing sprites, jank, and decode stalls. Load behind a real progress screen. Never render canvas text before `document.fonts.ready`. (reference.md §4)
12. **Absolute asset paths.** Breaks on itch.io's CDN subdirectory, GitHub Pages subpaths, and local file testing. Always use relative paths (`./` base). (build-and-deploy.md §6)
13. **DOM under transparent canvas.** Compositing DOM elements under a canvas that repaints every frame causes rendering conflicts and perf loss. One owner per pixel region. (reference.md §1)

## Verification

### Automated smoke test (via `chrome-browser-automation`)

Minimum automated smoke test:

1. Load the built game over HTTP (not `file://`).
2. Assert zero console errors.
3. Assert the canvas is non-blank after boot.
4. Dispatch a `pointerdown` (unlock + start).
5. Step 2 seconds.
6. Assert still no console errors.
7. Screenshot for the record.

### Manual test matrix before shipping

- **Desktop**: Chrome, Firefox, Safari
- **Mobile**: one Android Chrome device, one iOS Safari device
- **Both orientations** on each mobile device
- Full release checklist in `build-and-deploy.md` §9

### Pre-release audit

Before release, run `web-game-release-review` for a full perf, compatibility, and polish checklist. Compose with `chrome-browser-automation` for automated browser QA (load → no console errors → screenshot → input event → screenshot diff).
