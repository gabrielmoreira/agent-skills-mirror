---
name: threejs-game-development
version: 1.0.1
description: >-
  Owns the Three.js r160+ layer of a browser 3D game: scene graph, glTF with
  DRACO/KTX2, animation, Rapier or cannon-es, EffectComposer, dispose, and Vite.
  Use when starting or fixing a vanilla Three.js/WebGL web game (r3f only if
  asked). Not for the HTML5 game shell (browser-game-architecture), cross-engine
  FPS diagnosis (webgl-performance-tuning), Godot/Unity, or 2D Canvas/Pixi.
risk: safe
source: opus
date_added: 2026-07-15
---

# threejs-game-development

Own the Three.js-specific layer of a browser 3D game: renderer and scene-graph setup, the game loop, the glTF asset pipeline, input, physics integration, animation, postprocessing, memory discipline, and the Vite toolchain that ships it. Engine-agnostic design theory and the surrounding web-app shell belong to sibling skills — this skill makes the *Three.js* part correct, fast, and leak-free.

## When to Use

- Starting a new browser 3D game with vanilla Three.js (Vite + TypeScript scaffold)
- Structuring the game loop: fixed-timestep simulation, render interpolation, pause/timescale, tab-away safety
- Loading and managing assets: glTF + DRACO / KTX2 / Meshopt, preload manifests, caching, cloning skinned meshes
- Choosing and wiring collision/physics: none vs raycast-only vs three-mesh-bvh vs Rapier vs cannon-es
- Character movement, camera follow, animation crossfades, raycast picking
- Touch controls and mobile-safe render settings for WebGL games
- Postprocessing chains (EffectComposer) that survive resize and DPR changes
- Fixing leaks, hitches, GC churn, or WebGL context loss; dispose semantics
- Production builds with Vite: decoder files, base paths, code splitting, compression
- Adding a light WebXR mode to an existing Three.js game

**Trigger keywords:** three.js, threejs, webgl game, web game 3d, gltf, EffectComposer, Rapier three, Vite three, setAnimationLoop, InstancedMesh, BatchedMesh, WebGPURenderer, r3f, react-three-fiber.

### Do not use

- **Offline / film rendering** (Blender Cycles, path tracers) — out of scope entirely
- **React apps**: only reach for `@react-three/fiber` if the user explicitly asks for React — see "React (r3f) policy" below. Default is vanilla Three.js
- **2D-only games** — Canvas2D/Pixi territory; Three.js is overkill
- **Godot / Unity / native engines** — use the `godot-*` and engine-specific skills
- **Pure shader authoring / VFX deep-dives** — `game-technical-art-vfx`
- **Generic web-app concerns** (routing, auth, backend) — not a game skill problem

### Bundled references — load on demand

Do not paste these wholesale into context. Load the specific file when the task demands it:

| File | Load when… |
|---|---|
| `reference.md` | You need API details: renderer options, color management, cameras, lights/shadows, materials, geometry, instancing, textures, loaders, animation system, raycasting, postprocessing, audio, timing, dispose semantics, artifacts/gotchas, debugging toolkit |
| `architecture.md` | You are structuring the codebase: Game class, fixed-timestep loop, state machine, entities/systems, event bus, input action mapping, physics sync, asset manager, level lifecycle, pooling, TypeScript patterns |
| `recipes.md` | You need copy-paste code: Vite+TS scaffold, renderer + resize, loop class, loader stack, Rapier character controller, touch joystick, gamepad, bloom composer, pooling, deep-dispose, debug rig, production build |
| `examples.md` | You need a worked end-to-end reference: complete minimal game, animated glTF character with state machine, Rapier physics playground, mobile endless-runner skeleton |

### Routing to sibling skills

| Need | Skill |
|---|---|
| Overall web-game shell: menus, saves, meta-loop, session flow | `browser-game-architecture` |
| Lighting theory, PBR channel rules, post look-dev, quality tiers | `game-3d-rendering` |
| DCC export, glTF authoring, texture budgets, import hygiene | `game-assets-pipeline` |
| Camera *feel*: follow rigs, shake, framing (engine-agnostic) | `game-camera-system` |
| Input abstraction patterns (engine-agnostic) | `game-input-handling` |
| Profiling methodology and tooling discipline | `game-performance-profiling` |
| Shipping: perf audit, compatibility, release checklist | `web-game-release-review` |

This skill owns the Three.js *implementation* of those concerns; siblings own the engine-agnostic theory.

## Prerequisites

- Node.js 18+ and npm
- A modern browser with WebGL 2 support (Chrome/Edge/Firefox/Safari)
- Three.js r160 or newer installed (`npm i three`)
- TypeScript types (`npm i -D @types/three`)
- Vite as the dev server / bundler (`npm create vite@latest`)
- **Windows host is primary.** Use PowerShell for all CLI commands. Path separators in examples use `/` for cross-tool compatibility, but Windows backslash `\` is equally valid in PowerShell.

## Version contract (r160+, assume ~r165)

Write and expect modern API. When copying code from old tutorials, rewrite these red flags on sight:

| Legacy (pre-r152/r155) | Modern (r160+) |
|---|---|
| `import X from 'three/examples/jsm/...'` | `import X from 'three/addons/...'` |
| `renderer.outputEncoding = THREE.sRGBEncoding` | `renderer.outputColorSpace = THREE.SRGBColorSpace` (already the default) |
| `texture.encoding = THREE.sRGBEncoding` | `texture.colorSpace = THREE.SRGBColorSpace` |
| `renderer.physicallyCorrectLights = true` | Default behavior; `useLegacyLights` is removed (r165) |
| `renderer.gammaOutput / gammaFactor` | Gone — color management handles it |
| `THREE.Geometry` | `THREE.BufferGeometry` only |
| GammaCorrectionShader at end of composer | `OutputPass` (r154+) |

Other r160+ facts to rely on:

- Color/albedo/emissive textures need `texture.colorSpace = THREE.SRGBColorSpace`; normal/roughness/metalness/AO/data textures stay linear (`NoColorSpace`). `GLTFLoader` sets this correctly for you.
- `BatchedMesh` (r159+) batches *different* geometries sharing one material into one draw call; `InstancedMesh` repeats *one* geometry.
- `renderer.setAnimationLoop(fn)` is the canonical loop driver (required for WebXR; equivalent to rAF otherwise).
- `WebGPURenderer` + TSL node materials exist and are maturing; target `WebGLRenderer` for shipping games, note WebGPU as forward-looking only.

## Procedure

### 1. Scaffold the project

```powershell
npm create vite@latest my-game -- --template vanilla-ts
cd my-game
npm i three
npm i -D @types/three
npm i @dimforge/rapier3d-compat   # only if physics chosen (see table below)
```

For the full scaffold (index.html, CSS, vite.config, entry, resize handling) load `recipes.md`.

### 2. Configure renderer defaults

```ts
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)); // ALWAYS clamp DPR
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
```

### 3. Build the game loop (fixed-timestep)

Canonical pattern — fixed-timestep simulation with clamped frame delta and render-side interpolation:

```ts
const FIXED_DT = 1 / 60;
const MAX_FRAME = 0.25;            // tab-away / breakpoint guard
let accumulator = 0;
let last = performance.now();

renderer.setAnimationLoop(() => {
  const now = performance.now();
  const frame = Math.min((now - last) / 1000, MAX_FRAME);
  last = now;
  accumulator += frame;

  input.poll();                    // one snapshot per frame
  while (accumulator >= FIXED_DT) {
    simulate(FIXED_DT);            // gameplay + physics.step(FIXED_DT)
    accumulator -= FIXED_DT;
  }
  const alpha = accumulator / FIXED_DT;
  syncVisuals(alpha);              // interpolate body → mesh transforms
  updatePresentation(frame);       // mixers, camera damp, particles, HUD
  renderer.render(scene, camera);  // or composer.render()
});
```

**Loop rules:**
- Never step physics with a variable dt.
- Clamp the frame delta or a background tab will explode the simulation on return.
- Call `clock.getDelta()` at most once per frame (better: own the timing as above).
- Pause = stop accumulating, keep rendering.

Full loop class with timescale and `visibilitychange` handling → load `recipes.md`. Where the loop lives in the codebase → load `architecture.md`.

### 4. Set up the asset pipeline (glTF-first)

- **One format: `.glb`** (binary glTF). It carries meshes, PBR materials, skins, morphs, and animations. FBX/OBJ only as intermediate DCC formats — convert before shipping. Authoring rules → `game-assets-pipeline`.
- **Compression:** Draco (smallest geometry, one-time decode cost) or Meshopt (near-Draco size, much faster decode, also compresses animation) — prefer Meshopt via `gltf-transform optimize`. Textures: KTX2/Basis (stays compressed on GPU — the only fix for texture *memory*, not just download size).
- **Decoders:** `DRACOLoader` and `KTX2Loader` need their decoder/transcoder folders copied into `public/` (from `node_modules/three/examples/jsm/libs/`). `MeshoptDecoder` is a pure JS/WASM module import. Wiring recipe → `recipes.md`.
- **Preload via a typed manifest** before gameplay; show progress from `LoadingManager`. Loading mid-gameplay causes hitches (decode + GPU upload). Warm shaders with `renderer.compileAsync(scene, camera)` after load.
- **Never `.clone()` a skinned mesh** — use `SkeletonUtils.clone()` (`three/addons/utils/SkeletonUtils.js`).
- Cache by URL; share geometries/materials across instances; refcount before disposing shared assets (see Memory rules below).

### 5. Choose and wire collision / physics

| Situation | Choice |
|---|---|
| Puzzle/menu-driven, no dynamics | **No physics.** Transforms + `MathUtils` + distance checks |
| Character vs static level, picking, hitscan | **three-mesh-bvh** — BVH-accelerated raycast/shapecast against level geometry; write your own kinematics |
| Rigid-body dynamics, stacks, joints, robust character controller | **Rapier** (`@dimforge/rapier3d-compat`) — fast WASM, ships a `KinematicCharacterController` (slopes, steps, snap-to-ground). Default for real physics |
| Tiny bundle, simple dynamics, WASM disallowed | **cannon-es** — pure JS, easy API, slower, weaker trimesh support |
| Legacy ammo.js codebase | Maintain only; don't start new projects on it |

**Integration rules:**
- The physics world steps **inside the fixed update** with `FIXED_DT`.
- Copy body transforms to meshes after stepping (physics owns dynamic transforms — never write mesh positions back except for kinematic bodies).
- Build colliders from simplified shapes (capsule/box/hull), not render meshes.
- Never scale a mesh to "resize" its collider.

Sync architecture → load `architecture.md`. Full Rapier setup + character controller → load `recipes.md`.

### 6. Wire input

- Use **Pointer Events** (`pointerdown/move/up` + `setPointerCapture`) — one code path for mouse, touch, and pen. Never mix in `mousedown`/`touchstart` handlers alongside.
- Abstract device → **action map** (`moveX/moveY/jump/fire`), then gameplay reads a per-frame snapshot. Enables rebinding, gamepad, touch, and replays without touching game code. Pattern → load `architecture.md`.
- Gamepad API is poll-based: read `navigator.getGamepads()` once per frame inside `input.poll()`; apply a dead zone (~0.15).
- Keyboard: track `event.code` (layout-independent) in a `Set`; ignore repeats; clear the set on `blur`.
- Pointer lock (`canvas.requestPointerLock()`) for FPS-style mouselook; must be called from a user gesture; listen for `pointerlockchange` to pause on Esc.

### 7. Mobile pass

- `touch-action: none` on the canvas CSS or the browser will scroll/zoom instead of sending you pointermoves.
- Clamp DPR to 1.5–2; expose a render-scale setting (`renderer.setPixelRatio` is your cheapest quality knob).
- Virtual joystick = two pointer regions (left stick, right look) tracked by pointerId — hand-rolled recipe in `recipes.md`; multi-touch means you must track pointers by id, never "the" pointer.
- Budgets drop hard: ≤100–150 draw calls, ≤300k triangles, one shadow-casting light or baked/blob shadows, skip postprocessing on low-end.
- Handle `visibilitychange` (pause + mute), `orientationchange`/resize, and WebGL `webglcontextlost`/`restored` (prevent default, rebuild).
- Audio and fullscreen require a user gesture: unlock `AudioContext` on first tap.
- Test with real CPU throttling (DevTools 6×) — desktop GPUs hide sins.

### 8. Postprocessing (EffectComposer)

- Use `EffectComposer` with `OutputPass` (r154+) as the final pass — do not use `GammaCorrectionShader`.
- Ensure the composer survives resize: call `composer.setSize(w, h)` and `composer.setPixelRatio(dpr)` alongside the renderer resize.
- On mobile/low-end, skip postprocessing entirely or reduce to a single pass.

Bloom composer recipe → load `recipes.md`.

### 9. Memory & dispose discipline

Removing an object from the scene frees **nothing** on the GPU. The rules:

1. GPU resources live in `BufferGeometry`, `Material`, `Texture`, `WebGLRenderTarget`, and skeleton bone textures. Each needs `.dispose()` explicitly.
2. Disposing a material does **not** dispose its textures — walk the material's texture slots.
3. Shared assets: refcount. Disposing a geometry/material still used elsewhere causes silent re-upload or broken rendering.
4. Level teardown checklist: stop the loop's spawners → remove event listeners → free physics bodies → traverse and deep-dispose the level subtree → clear pools → verify. Deep-dispose utility → load `recipes.md`.
5. Verify with `renderer.info.memory` (geometries/textures counts) — it must return to baseline after a load→unload cycle. If it climbs, you leak.
6. Full app teardown (SPA route change): also `renderer.dispose()`, `renderer.forceContextLoss()`, drop the canvas.

Per-frame allocations are the other memory sin: no `new Vector3()` / `.clone()` in the loop — hoist scratch temps to module scope and `.copy()` into them.

### 10. Production build with Vite

- Ensure decoder files (DRACO, KTX2) are in `public/` and referenced by absolute path.
- Set `base` in `vite.config.ts` if the game is served from a subpath.
- Use code splitting for large assets or optional modes (e.g., WebXR).
- Enable compression plugins (`vite-plugin-compression` for gzip/brotli).
- Run `npm run build` and verify the output serves correctly from the target path.

Full production build config → load `recipes.md`.

### 11. WebXR (light mode, if requested)

- `renderer.xr.enabled = true`, add `VRButton`/`XRButton` from `three/addons/webxr/`.
- Drive everything through `renderer.setAnimationLoop` (rAF does not fire in XR sessions).
- Per-eye rendering roughly doubles GPU cost: drop postprocessing first, keep DPR at 1, use `renderer.xr.setFramebufferScaleFactor` to trade sharpness for frame rate.
- Controllers via `renderer.xr.getController(i)` with `select` events.
- Treat XR as a bonus mode, not the primary target, unless the user says otherwise.

## Mental model: anatomy of a frame

```
poll input (snapshot devices once)
  → fixed-step simulation ×N   (gameplay logic, physics.step(FIXED_DT))
  → sync visuals               (copy/interpolate body transforms → meshes)
  → variable-rate update       (AnimationMixer, camera damping, particles, UI)
  → render                     (renderer or EffectComposer)
```

Scene graph rules that prevent 80% of beginner bugs:

- An `Object3D`'s `position/quaternion/scale` are **local** to its parent. World transform lives in `matrixWorld`, updated during render (or via `updateWorldMatrix(true, false)` when you need it mid-frame).
- `parent.add(child)` re-parents and *changes world position* unless you use `parent.attach(child)` (keeps world transform).
- Nothing renders without: a camera in a sane position, a light (for lit materials), and geometry with a material. Debug "black screen" in that order.
- One renderer, one canvas, one loop. Multiple scenes/cameras are fine (HUD pass, minimap) — multiple renderers are not.

## Performance budgets & triage

| Symptom | First suspects |
|---|---|
| High CPU, low GPU | Draw calls (`renderer.info.render.calls`), per-frame allocation/GC, matrix updates on thousands of static objects (`matrixAutoUpdate = false`), unbatched raycasting |
| High GPU, frame drops at high DPR | Fill rate/overdraw (transparent layers, post passes), shadow map size, DPR unclamped |
| Hitches/stutters | Mid-gameplay loading, shader compilation (warm with `compileAsync`), GC pauses, texture decode/upload |
| Memory climbs per level | Missing dispose (rule 5 above) |

**Targets:** desktop web ≤ ~1000 draw calls / ≤ 2–3M tris; mobile web ≤ ~150 calls / ≤ 300k tris; 16.6ms frame with ≥ 4ms headroom.

**Weapons:** `InstancedMesh`/`BatchedMesh`, `BufferGeometryUtils.mergeGeometries` for static clumps, LOD, frustum-friendly scene structure, shared materials, KTX2 textures, render-scale slider. Methodology → `game-performance-profiling`; ship gate → `web-game-release-review`.

## React (r3f) policy

Default answer is **vanilla Three.js**. Only if the user explicitly wants React, switch to `@react-three/fiber` + `drei` and keep the paradigm pure — never drive a vanilla imperative scene from React state per frame, and never `setState` inside `useFrame`. Concept mapping when translating:

| Vanilla | r3f |
|---|---|
| `scene.add(mesh)` | JSX: `<mesh>` declares graph; unmount auto-disposes |
| `renderer.setAnimationLoop` | `useFrame((state, delta) => ...)` with `useRef` mutation |
| Manual loaders + cache | `useGLTF` / `useLoader` (suspense, cached) |
| Manual resize | `<Canvas>` handles it |
| This skill's loop/physics/memory rules | Still apply — fixed step via accumulator inside `useFrame`, `@react-three/rapier` for physics |

## Pitfalls

1. `new Vector3/Quaternion/Matrix4` (or `.clone()`) inside the loop — GC churn; hoist scratch objects.
2. Per-entity `new Material()`/`new Geometry()` for identical entities — share and instance.
3. Stepping physics with variable frame dt — non-deterministic, explodes on hitches.
4. Unclamped `setPixelRatio(devicePixelRatio)` — a DPR-3 phone renders 9× the pixels.
5. Removing meshes without disposing (leak), or disposing shared assets in use (breakage) — refcount.
6. Loading assets on demand mid-gameplay — preload via manifest; hitches are a design failure.
7. Raycasting the whole scene recursively every frame — target lists, `layers`, or three-mesh-bvh.
8. `clock.getDelta()` called from multiple places — each call resets it; own timing centrally.
9. No frame-delta clamp — returning from a background tab teleports/explodes everything.
10. `transparent: true` everywhere — overdraw + sort popping; use `alphaTest` for cutouts.
11. Shadow maps on every light / 4096 maps by default — one sun-shadow + cheats first.
12. Updating DOM HUD (`innerText`, styles) every frame unconditionally — write on change only.
13. Copy-pasting pre-r152 tutorial code without applying the Version-contract table above.
14. `scene.traverse()` per frame to find objects — cache references at spawn time.
15. `matrixAutoUpdate` left on for thousands of static objects.
16. Sequential `await load(); await load();` — `Promise.all` the manifest.
17. Mixing r3f and vanilla idioms in one codebase.
18. Using `.clone()` on a skinned mesh instead of `SkeletonUtils.clone()` — broken skinning.
19. Forgetting `texture.colorSpace = THREE.SRGBColorSpace` for color textures loaded outside `GLTFLoader`.
20. Not handling `webglcontextlost` — the game silently dies on context switch.

## Verification

Run through this checklist before calling a task done:

- [ ] `renderer.info.memory` returns to baseline after a level load→unload cycle
- [ ] `renderer.info.render.calls` within budget on the heaviest scene
- [ ] 60 fps with DevTools 6× CPU throttle (or explicit 30 fps mobile target held)
- [ ] No per-frame allocations in the hot path (DevTools allocation sampling while idling in-game)
- [ ] Touch: joystick + camera work simultaneously (multi-touch by pointerId), page doesn't scroll
- [ ] Tab-away 30s → return: no physics explosion, audio muted while hidden
- [ ] Context-lost handler present; resize/orientation handled; DPR clamped
- [ ] Production `vite build` served from a subpath works (decoder files, base path)
- [ ] Ship gate run via `web-game-release-review`

### Quick verification commands

```powershell
# Confirm Three.js version is r160+
npm ls three

# Run the dev server
npm run dev

# Production build
npm run build

# Preview the production build
npm run preview
```

**Expected `npm ls three` output:** `three@0.160.0` or higher.

**Expected `renderer.info.memory` check (in console during gameplay):**
```ts
console.log(renderer.info.memory);  // { geometries: N, textures: M }
```
After a full load→unload cycle, N and M must return to their pre-load baseline. If they climb, there is a leak.

## Progress checklist (working a task)

1. [ ] Scaffold or locate project; confirm three version ≥ r160 and Vite config (load `recipes.md`)
2. [ ] Renderer defaults + resize + DPR clamp in place
3. [ ] Fixed-timestep loop owns all timing; delta clamped
4. [ ] Physics choice made from the table and wired in the fixed step
5. [ ] Asset manifest preloads everything; decoders wired; skinned clones via SkeletonUtils
6. [ ] Input action map covers keyboard + pointer + touch (+ gamepad if asked)
7. [ ] Dispose path written *with* the spawn path, not after
8. [ ] Mobile pass: budgets, touch-action, visibilitychange, audio unlock
9. [ ] Run the Verification checklist above before calling it done

## Related skills

- `browser-game-architecture` — web-game shell, menus, saves, meta-loop
- `game-3d-rendering` — lighting theory, PBR, post look-dev, quality tiers
- `game-assets-pipeline` — DCC export, glTF authoring, texture budgets
- `game-camera-system` — camera feel: follow rigs, shake, framing
- `game-input-handling` — input abstraction patterns (engine-agnostic)
- `game-performance-profiling` — profiling methodology and tooling
- `web-game-release-review` — shipping: perf audit, compatibility, release checklist
