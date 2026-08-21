---
name: webgl-performance-tuning
description: Profiles and tunes runtime FPS of canvas WebGL/WebGPU games via draw-call batching, instancing, KTX2, object pools, GC pauses, and engine knobs for Three.js, Phaser, PixiJS, Babylon.js, and Godot 4 Web. Use when FPS drops, jank, leaks, or context-lost appear. Not for native Unity/Unreal/Godot desktop builds, Core Web Vitals on document pages, or k6 API load tests.
version: 1.0.1
---

# WebGL Performance Tuning

> **Prime directive:** A frame is a budget, not a goal. At 60 Hz you have **16.67 ms**; at 120 Hz you have **8.33 ms**. Every millisecond is spent or wasted. Profile first, optimize the proven bottleneck, then re-profile. Never optimize on a hunch — the GPU and the JS heap lie to intuition constantly.

---

## When to Use

Activate this skill when the task involves the **runtime performance of a browser-based, canvas-rendered game or interactive 3D/2D scene**.

**USE when the user is:**
- Diagnosing low or unstable FPS in an HTML5/WebGL/WebGPU game (stutter, jank, dropped frames, "it runs at 60 on desktop but 20 on mobile").
- Reducing **draw calls** / batching geometry / building **texture atlases** or sprite sheets.
- Cutting **VRAM / heap memory** footprint, fixing **memory leaks** (growing heap, climbing GPU memory).
- Eliminating **garbage-collection (GC) pauses** — periodic hitches every few seconds.
- Configuring **texture compression** (KTX2, Basis Universal, ASTC, BC7/S3TC, ETC2) or mipmap strategy.
- Profiling or tuning **Three.js**, **Phaser** (3/4), **PixiJS**, **Babylon.js**, or **Godot 4 Web exports**.
- Migrating a renderer from **WebGL2 → WebGPU** or adding a WebGPU path with a WebGL2 fallback.
- Optimizing **shaders** (fill rate, overdraw, precision, branching) or adding **dynamic resolution** scaling.
- Fixing **`webglcontextlost`**, frame-clock drift on background tabs, or `MAX_TEXTURE_SIZE` failures.

**DO NOT use when the task is:**
- A **native desktop/console/mobile** build (Unity native, Unreal, native Godot/SDL/Vulkan) — different toolchain, different profilers.
- A **standard web page** with no `<canvas>`/WebGL/WebGPU rendering — that's general web perf (Core Web Vitals, bundle size, layout); route to a web-perf workflow instead.
- **Backend / game-server** optimization (netcode, tick rate, DB, matchmaking) — that's server engineering.
- Pure **art/asset authoring** with no runtime perf question (use an art-pipeline workflow).
- **Gameplay/design** balance, networking lag-compensation logic, or audio DSP.

**Trigger keywords:** `webgl`, `webgpu`, `fps drop`, `jank`, `stutter`, `frame budget`, `draw calls`, `batching`, `instancing`, `InstancedMesh`, `BatchedMesh`, `texture atlas`, `spritesheet`, `KTX2`, `basis universal`, `ASTC`, `mipmap`, `object pool`, `GC pause`, `garbage collection`, `memory leak`, `dispose`, `context lost`, `MAX_TEXTURE_SIZE`, `overdraw`, `fill rate`, `dynamic resolution`, `three.js stats`, `renderer.info`, `actualFps`, `godot monitor`, `Spector.js`, `tab suspend`, `requestAnimationFrame throttle`.

---

## Prerequisites

- A browser-based game or interactive scene using `<canvas>` with WebGL, WebGL2, or WebGPU.
- Local dev server capable of serving assets with correct CORS headers (e.g., `Access-Control-Allow-Origin`).
- **Windows host (PowerShell)** is the primary development environment. Adjust path separators for macOS/Linux where relevant.
- Chrome or Edge with DevTools + (optionally) the **Spector.js** browser extension installed.
- For KTX2 generation: `toktx` (KTX-Software) or `basisu` CLI installed and on `PATH`.
- For Godot 4 Web exports: Godot 4.x editor with Web export templates installed.

---

## 2026 Core Principles

State of the art as of 2026. The browser graphics stack has bifurcated; design for it.

### 1. WebGPU is primary, WebGL2 is the fallback

WebGL2 remains the compatibility floor, but WebGPU is the modern default. **Architect for a renderer abstraction**, not a hard WebGL2 dependency:

- WebGPU gives you **compute shaders** (GPU particle sim, culling, skinning), **explicit pipeline state objects** (no hidden state-change cost), **bind groups** (batched uniform/texture binding), and **`render bundles`** (pre-recorded command sequences — huge for draw-call-bound scenes).
- Three.js exposes this via `WebGPURenderer` + **TSL (Three Shading Language)**, which compiles one node graph to **both** WGSL and GLSL — write once, run on either backend.
- **Feature-detect and fall back gracefully**: `if (navigator.gpu && await navigator.gpu.requestAdapter())` → WebGPU, else WebGL2, else a "your browser is unsupported" path. Never assume.
- WebGL2 remains the **compatibility floor** (older Safari, locked-down enterprise, some Android WebViews). Godot 4 Web's "Compatibility" renderer is WebGL2; its WebGPU/Forward+ web path is still maturing in 2026, so test the actual export.

### 2. Draw calls are the #1 CPU-side cost — batch relentlessly

Each draw call is a CPU→GPU command with driver overhead. **Hundreds of draw calls per frame will starve the main thread before the GPU breaks a sweat.**

- **Instanced drawing** (`drawElementsInstanced` / WebGPU instance count): one call renders N copies that differ only by per-instance data (matrix, color, UV offset). This is the single highest-leverage technique for repeated geometry (trees, bullets, tiles, crowd).
- **Multi-draw / BatchedMesh** (`WEBGL_multi_draw` extension; native in WebGPU): one call renders many *different* geometries sharing a material + texture atlas. Three.js `BatchedMesh` wraps this.
- **Static batching**: merge non-moving meshes that share a material into one buffer at load time.
- **Atlas to kill state changes**: every texture bind and shader swap is a pipeline flush. Pack textures into atlases / array textures so a batch shares one bound texture.

### 3. Compressed textures (KTX2 / Basis) — not PNG/JPEG at runtime

PNG/JPEG must be **decoded to raw RGBA on the GPU** (a 2048² texture = 16 MB uncompressed VRAM regardless of file size). GPU-compressed formats stay compressed *in VRAM* and sample faster.

- **KTX2** is the container; **Basis Universal** is the codec. It **transcodes** at load to the device's native format: **ASTC** (modern mobile/Apple), **BC7/BC3 (S3TC/DXT)** (desktop), **ETC2** (older Android), with **UASTC** (high quality, larger) or **ETC1S** (small, good enough for UI/albedo) source modes.
- VRAM win: a BC7/ASTC 2048² is ~4 MB vs 16 MB raw — **4× less VRAM and bandwidth.**
- Always ship **mipmapped** KTX2 for anything sampled at varying distance. Mipmaps fix shimmer *and* save bandwidth (the GPU reads smaller levels for distant pixels). The exception: never-scaled fullscreen UI sprites — mips there are wasted memory.

### 4. Shader cost is fill-rate × complexity — measure overdraw

A cheap shader run on every pixel ten times over (overdraw) is more expensive than a complex shader run once. Sort transparent geometry, cut overdraw, prefer **`mediump`** precision on mobile fragment shaders where banding is invisible, avoid **`discard`** (it disables early-Z), and avoid divergent dynamic branching in fragment shaders.

### 5. GC suppression: steady-state allocation must approach zero

JS is garbage-collected; every per-frame allocation feeds a future stop-the-world pause that you'll see as a periodic hitch. **In the hot path (per-frame update + render), execute zero `new`, zero array/object literals, zero closures.** Pre-allocate pools, reuse vectors/matrices, write into typed-array buffers. Wasm engines (Godot, Unity Web) move the heap into linear memory — but you still pay for the JS↔Wasm boundary and any JS glue allocating per call.

### 6. The frame clock is hostile in background tabs

`requestAnimationFrame` is **paused** when the tab is hidden; `setTimeout`/`setInterval` are **throttled to ≥1 s** (and to ≥1/min after long backgrounding). A naive `delta = now - last` produces a **multi-second delta** on tab refocus, which teleports physics through walls and detonates animations. **Always clamp delta** and pause logic on `visibilitychange`.

---

## Procedure

Follow in order. Do **not** skip Step 1 — optimizing before profiling is how you spend a day speeding up code that was never the bottleneck.

### Step 1 — Profile and Benchmark (establish ground truth)

Identify whether you are **CPU-bound** (main thread / JS) or **GPU-bound** (fill rate / draw calls), and *where*. Symptoms:

- **CPU-bound:** the Performance flame chart shows long JS/scripting bars per frame; GPU is idle waiting. Cutting resolution does **not** help.
- **GPU-bound:** lowering canvas resolution or simplifying shaders restores FPS; the main thread has idle gaps.
- **GC-bound:** FPS is fine *except* for a rhythmic hitch every few seconds; the Memory timeline shows a sawtooth heap.

**Tooling:**

| Tool | When to use | What it tells you |
|---|---|---|
| **Chrome DevTools → Performance** | Record 5–10 s of gameplay. Read per-frame budget, widest bars, "GPU" track, "Frames" track for dropped frames. | CPU vs GPU bound; scripting cost per frame. |
| **Chrome DevTools → Memory** | Heap snapshot + allocation timeline. | Leaks, per-frame allocations, sawtooth GC pattern. |
| **Spector.js** (extension or embedded) | Capture a single frame's complete WebGL/WebGPU command stream — every draw call, state change, bound texture, shader. | "Why do I have 800 draw calls." Definitive draw-call inspector. |
| **Three.js `renderer.info`** | Live `calls`, `triangles`, `points`, `geometries`, `textures`. Pair with `stats.js` for FPS/ms/MB overlay. | Draw-call count, VRAM object counts. |
| **Phaser `game.loop.actualFps`** | Debug draw-call/texture counters. | Real FPS vs target; batcher state. |
| **Godot 4 Web Monitors** (Debugger panel) | `Object/Objects`, `Raster/Total Objects In Frame`, `Raster/Draw Calls In Frame`, `Memory/Video Mem`, `Memory/Static`. | Engine-level draw calls, object counts, video memory. |

**Drop-in profiling HUD (engine-agnostic, GC-free):**

```ts
/** Zero-allocation frame profiler. Sample once per frame; reads are O(1). */
export class FrameProfiler {
  private readonly frameMs: Float32Array;   // ring buffer of frame durations
  private readonly scratch: Float32Array;   // reused for percentile sort
  private idx = 0;
  private filled = false;
  private last = performance.now();

  // Long-task / GC-hitch detector
  private hitchThresholdMs: number;
  public hitches = 0;

  constructor(samples = 120, hitchThresholdMs = 33) {
    this.frameMs = new Float32Array(samples);
    this.scratch = new Float32Array(samples);
    this.hitchThresholdMs = hitchThresholdMs; // ~2 missed frames at 60Hz
  }

  /** Call exactly once at the top of every frame. */
  tick(now: number): void {
    const dt = now - this.last;
    this.last = now;
    this.frameMs[this.idx] = dt;
    this.idx = (this.idx + 1) % this.frameMs.length;
    if (this.idx === 0) this.filled = true;
    if (dt > this.hitchThresholdMs) this.hitches++;
  }

  private count(): number {
    return this.filled ? this.frameMs.length : this.idx;
  }

  avgMs(): number {
    const n = this.count();
    if (n === 0) return 0;
    let sum = 0;
    for (let i = 0; i < n; i++) sum += this.frameMs[i];
    return sum / n;
  }

  fps(): number {
    const a = this.avgMs();
    return a > 0 ? 1000 / a : 0;
  }

  /** 95th-percentile frame time — the metric users actually feel. GC-free. */
  p95Ms(): number {
    const n = this.count();
    if (n === 0) return 0;
    for (let i = 0; i < n; i++) this.scratch[i] = this.frameMs[i];
    // Insertion sort over the live window (n is small, e.g. 120; allocation-free).
    for (let i = 1; i < n; i++) {
      const v = this.scratch[i];
      let j = i - 1;
      while (j >= 0 && this.scratch[j] > v) { this.scratch[j + 1] = this.scratch[j]; j--; }
      this.scratch[j + 1] = v;
    }
    return this.scratch[Math.min(n - 1, Math.floor(n * 0.95))];
  }
}

// Usage:
const profiler = new FrameProfiler();
function loop(now: number) {
  profiler.tick(now);
  // ... update + render ...
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);
// Inspect from console: profiler.fps(), profiler.p95Ms(), profiler.hitches
```

**Read draw calls every frame in Three.js:**

```ts
import * as THREE from 'three';

const renderer = new THREE.WebGLRenderer(); // or WebGPURenderer
function reportGpu() {
  const i = renderer.info;
  console.log(
    `draws=${i.render.calls}  tris=${i.render.triangles}  ` +
    `geos=${i.memory.geometries}  texs=${i.memory.textures}`
  );
}
// renderer.info.autoReset === true resets render.* each frame automatically.
// memory.* are persistent counts — watch them climb to spot leaks.
```

### Step 2 — Reduce Draw Calls (batch, instance, atlas)

**Order of leverage for draw calls:**
1. **Atlas everything** that shares a material →
2. **Instance repeated geometry** →
3. **BatchedMesh/multi-draw** varied geometry →
4. **Merge truly static geometry**.

Frustum-cull *before* you draw — the cheapest draw call is the one you skip.

**Instanced meshes in Three.js** — render thousands of objects in **one** draw call:

```ts
import * as THREE from 'three';

const COUNT = 10_000;
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshStandardMaterial();

// One InstancedMesh = one draw call for all COUNT instances.
const mesh = new THREE.InstancedMesh(geometry, material, COUNT);
mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage); // hint: matrices change often
scene.add(mesh);

// Reusable scratch objects — allocated ONCE, never inside the loop.
const _m = new THREE.Matrix4();
const _pos = new THREE.Vector3();
const _axis = new THREE.Vector3();
const _quat = new THREE.Quaternion();
const _scale = new THREE.Vector3(1, 1, 1);
const _color = new THREE.Color();

// Initialize per-instance transform + color.
for (let i = 0; i < COUNT; i++) {
  _pos.set(
    (Math.random() - 0.5) * 200,
    (Math.random() - 0.5) * 200,
    (Math.random() - 0.5) * 200,
  );
  _axis.copy(_pos).normalize();
  _quat.setFromAxisAngle(_axis, Math.random() * Math.PI);
  _m.compose(_pos, _quat, _scale);
  mesh.setMatrixAt(i, _m);
  _color.setHSL(i / COUNT, 0.7, 0.5);
  mesh.setColorAt(i, _color);
}
mesh.instanceMatrix.needsUpdate = true;
if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;

// Per-frame update of a single instance — GC-free (reuses scratch objects):
function moveInstance(i: number, x: number, y: number, z: number): void {
  _pos.set(x, y, z);
  _m.compose(_pos, _quat, _scale);
  mesh.setMatrixAt(i, _m);
  mesh.instanceMatrix.needsUpdate = true; // set once after a batch of writes
}
```

**BatchedMesh** — many *different* geometries, one draw call (Three.js, uses multi-draw):

```ts
import * as THREE from 'three';

// Budget the buffers up front: max instances, max vertices, max indices.
const MAX_INSTANCES = 256;
const MAX_VERTS = 50_000;
const MAX_INDICES = 100_000;

const batched = new THREE.BatchedMesh(MAX_INSTANCES, MAX_VERTS, MAX_INDICES, material);
const boxId = batched.addGeometry(new THREE.BoxGeometry(1, 1, 1));
const sphereId = batched.addGeometry(new THREE.SphereGeometry(0.6, 16, 12));

const boxInst = batched.addInstance(boxId);
const sphereInst = batched.addInstance(sphereId);

const _tmp = new THREE.Matrix4();
batched.setMatrixAt(boxInst, _tmp.makeTranslation(-2, 0, 0));
batched.setMatrixAt(sphereInst, _tmp.makeTranslation(2, 0, 0));
batched.perObjectFrustumCulled = true; // per-instance culling, still one draw
scene.add(batched);
```

**Raw WebGL2 instancing** (when not using an engine):

```ts
function setupInstancing(gl: WebGL2RenderingContext, program: WebGLProgram): number {
  const INSTANCES = 5000;

  // Per-instance offset buffer (vec3 per instance).
  const offsets = new Float32Array(INSTANCES * 3);
  for (let i = 0; i < INSTANCES; i++) {
    offsets[i * 3 + 0] = (Math.random() - 0.5) * 100;
    offsets[i * 3 + 1] = (Math.random() - 0.5) * 100;
    offsets[i * 3 + 2] = (Math.random() - 0.5) * 100;
  }

  const offsetBuf = gl.createBuffer()!;
  gl.bindBuffer(gl.ARRAY_BUFFER, offsetBuf);
  gl.bufferData(gl.ARRAY_BUFFER, offsets, gl.STATIC_DRAW);

  const loc = gl.getAttribLocation(program, 'aOffset');
  gl.enableVertexAttribArray(loc);
  gl.vertexAttribPointer(loc, 3, gl.FLOAT, false, 0, 0);
  gl.vertexAttribDivisor(loc, 1); // advance once PER INSTANCE, not per vertex

  // Draw: vertexCount per instance, INSTANCES copies, ONE call.
  // gl.drawElementsInstanced(gl.TRIANGLES, indexCount, gl.UNSIGNED_SHORT, 0, INSTANCES);
  return INSTANCES;
}
```

**Phaser** — pooled sprites + a single texture atlas keep the batcher hot:

```ts
// Load ONE atlas (TexturePacker / free-tex-packer JSON-hash format).
// All frames sharing this atlas batch into one draw call automatically.
this.load.atlas('game', 'assets/game.png', 'assets/game.json');

// Pool projectiles instead of create/destroy (see Step 4 for the pool pattern).
const bullets = this.add.group({
  defaultKey: 'game',
  defaultFrame: 'bullet',
  maxSize: 200,
  classType: Phaser.GameObjects.Image,
});
function fire(x: number, y: number) {
  const b = bullets.get(x, y) as Phaser.GameObjects.Image | null;
  if (!b) return;            // pool exhausted — drop, never allocate
  b.setActive(true).setVisible(true);
}
```

### Step 3 — Optimize Texture & Asset Memory

**KTX2 / Basis Universal in Three.js** (transcodes to the device's native compressed format):

```ts
import * as THREE from 'three';
import { KTX2Loader } from 'three/examples/jsm/loaders/KTX2Loader.js';

const ktx2 = new KTX2Loader()
  .setTranscoderPath('https://unpkg.com/three/examples/jsm/libs/basis/')
  .detectSupport(renderer); // picks ASTC / BC7 / ETC2 based on GPU capability

ktx2.load('assets/albedo.ktx2', (texture) => {
  texture.colorSpace = THREE.SRGBColorSpace; // albedo/UI = sRGB; data maps = NoColorSpace
  texture.anisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy());
  material.map = texture;
  material.needsUpdate = true;
});
```

Generate KTX2 offline with `toktx` (KTX-Software) or `basisu`:

```bash
# UASTC = high quality (normals, detailed albedo); larger.
toktx --t2 --encode uastc --uastc_quality 2 --genmipmap albedo.ktx2 albedo.png

# ETC1S = small, great for UI / low-detail albedo; supercompressed with Zstd.
toktx --t2 --encode etc1s --clevel 4 --qlevel 200 --genmipmap --zcmp 19 ui.ktx2 ui.png
```

**Texture sizing rules:**

- **Power-of-two** dimensions for anything mipmapped or tiled/`REPEAT`. WebGL2 *allows* NPOT with mips, but POT keeps compression and mip generation clean. Cap at the platform's `MAX_TEXTURE_SIZE` (query it — many mobile GPUs are 4096, some 8192; do not blindly ship 8192²).
- **Mipmaps on** for 3D/world textures (fixes shimmer, saves bandwidth). **Mipmaps off** for pixel-exact UI/HUD sprites never sampled minified (`generateMipmaps = false`, `minFilter = LinearFilter`) — saves 33% VRAM.
- **Right-size to screen footprint.** A prop that's never more than 200 px on screen does not need a 2048² texture. Downscale source assets to their real on-screen budget.

```ts
// Query the hard texture-size ceiling before allocating.
const maxTex = renderer.capabilities.maxTextureSize; // Three.js
// Raw: const maxTex = gl.getParameter(gl.MAX_TEXTURE_SIZE);
if (desiredSize > maxTex) {
  console.warn(`Texture ${desiredSize} exceeds GPU max ${maxTex}; clamping.`);
}

// UI texture: disable mips to save VRAM.
const uiTex = new THREE.Texture(image);
uiTex.generateMipmaps = false;
uiTex.minFilter = THREE.LinearFilter;
uiTex.magFilter = THREE.LinearFilter;
uiTex.needsUpdate = true;
```

### Step 4 — Eliminate Garbage-Collection Spikes

**The rule:** in `update()` and `render()`, allocate nothing. Pre-allocate everything; reuse it.

**Generic, type-safe object pool (zero steady-state allocation):**

```ts
/** Fixed-capacity object pool. acquire()/release() never allocate after warm-up. */
export class ObjectPool<T> {
  private readonly free: T[] = [];
  private readonly factory: () => T;
  private readonly reset: (obj: T) => void;
  private liveCount = 0;
  private readonly max: number;

  constructor(factory: () => T, reset: (obj: T) => void, prewarm: number, max = prewarm) {
    this.factory = factory;
    this.reset = reset;
    this.max = max;
    for (let i = 0; i < prewarm; i++) this.free.push(factory()); // allocate up front
  }

  acquire(): T | null {
    let obj = this.free.pop();
    if (!obj) {
      if (this.liveCount >= this.max) return null; // hard cap — never grow in hot path
      obj = this.factory();                         // cold-path growth only
    }
    this.liveCount++;
    return obj;
  }

  release(obj: T): void {
    this.reset(obj);
    this.free.push(obj);
    this.liveCount--;
  }

  get inUse(): number { return this.liveCount; }
  get available(): number { return this.free.length; }
}

// --- Example: a particle pool ---
interface Particle { x: number; y: number; vx: number; vy: number; life: number; }

const particles = new ObjectPool<Particle>(
  () => ({ x: 0, y: 0, vx: 0, vy: 0, life: 0 }),
  (p) => { p.x = 0; p.y = 0; p.vx = 0; p.vy = 0; p.life = 0; },
  500,  // prewarm
  1000, // hard cap
);

// Hot path — no `new`, no allocation:
function spawnParticle(x: number, y: number) {
  const p = particles.acquire();
  if (!p) return; // pool exhausted — drop gracefully
  p.x = x; p.y = y; p.vx = 1; p.vy = -1; p.life = 1.0;
}

function killParticle(p: Particle) {
  particles.release(p); // return to pool, never GC
}
```

**Clamp delta time and handle background-tab suspension:**

```ts
let lastTime = performance.now();
const MAX_DELTA_MS = 100; // never integrate more than 100ms in one step

function loop(now: number) {
  let dt = now - lastTime;
  lastTime = now;

  // Clamp: prevents physics teleport after tab refocus.
  if (dt > MAX_DELTA_MS) dt = MAX_DELTA_MS;

  // ... update(dt) + render() ...
  requestAnimationFrame(loop);
}

// Reset clock on visibility return to avoid a spike.
document.addEventListener('visibilitychange', () => {
  if (!document.hidden) {
    lastTime = performance.now(); // discard the gap
  }
});
```

**Reusable math scratch objects (Three.js) — never allocate in the loop:**

```ts
// Declare ONCE at module scope.
const _v3 = new THREE.Vector3();
const _m4 = new THREE.Matrix4();
const _q = new THREE.Quaternion();

// Reuse in every frame — no `new`, no `{}`.
function updateTransform(obj: THREE.Object3D, x: number, y: number, z: number) {
  _v3.set(x, y, z);
  obj.position.copy(_v3);
  // ... reuse _m4, _q as needed ...
}
```

### Step 5 — Dynamic Resolution Scaling

Scale the canvas render resolution to maintain frame budget on variable hardware:

```ts
// Render at a fraction of the CSS pixel size, then upscale via CSS.
// Target: keep p95 frame time under budget.
const profiler = new FrameProfiler();

function adjustResolution(canvas: HTMLCanvasElement, targetMs: number) {
  const p95 = profiler.p95Ms();
  const cssW = canvas.clientWidth;
  const cssH = canvas.clientHeight;
  let scale = parseFloat(canvas.dataset.renderScale || '1.0');

  if (p95 > targetMs * 1.1 && scale > 0.5) {
    scale -= 0.05; // under budget → shrink
  } else if (p95 < targetMs * 0.8 && scale < 1.0) {
    scale += 0.05; // over budget → grow
  }

  canvas.dataset.renderScale = scale.toFixed(2);
  canvas.width = Math.round(cssW * scale);
  canvas.height = Math.round(cssH * scale);
  // renderer.setSize(canvas.width, canvas.height, false); // Three.js
}
```

### Step 6 — Explicit GPU Resource Disposal

Geometries, materials, textures, render targets, and FBOs are **not** GC'd; they hold GPU handles. Explicitly dispose on unload/scene-change.

```ts
import * as THREE from 'three';

function disposeMaterial(material: THREE.Material): void {
  const m = material as unknown as Record<string, unknown>;
  for (const key of Object.keys(m)) {
    const value = m[key];
    if (value && (value as THREE.Texture).isTexture) {
      (value as THREE.Texture).dispose(); // dispose every map: map, normalMap, etc.
    }
  }
  material.dispose();
}

function disposeObject(obj: THREE.Object3D): void {
  obj.traverse((child) => {
    const mesh = child as THREE.Mesh;
    if (mesh.geometry) mesh.geometry.dispose();
    const mat = mesh.material;
    if (Array.isArray(mat)) mat.forEach(disposeMaterial);
    else if (mat) disposeMaterial(mat);
  });
}

// On scene unload:
function teardown(scene: THREE.Scene, renderer: THREE.WebGLRenderer): void {
  disposeObject(scene);
  renderer.renderLists.dispose();
  // renderTargets: rt.dispose(); controls/loaders: cancel pending loads.
}
```

### Step 7 — WebGL Context-Loss Recovery

```ts
const canvas = renderer.domElement;
let running = true;

canvas.addEventListener('webglcontextlost', (e) => {
  e.preventDefault();   // MANDATORY: without this the context will not be restorable
  running = false;
  console.warn('WebGL context lost — pausing render loop.');
}, false);

canvas.addEventListener('webglcontextrestored', () => {
  console.warn('WebGL context restored — recreating GPU resources.');
  // All buffers/textures/programs are gone. Re-upload geometry, reload textures,
  // recompile shaders, then resume. (Three.js re-uploads lazily on next render;
  // raw WebGL apps must explicitly rebuild every GPU object here.)
  rebuildGpuResources();
  running = true;
  requestAnimationFrame(loop);
}, false);

function loop(now: number) {
  if (!running) return;
  // ... update + render ...
  requestAnimationFrame(loop);
}
function rebuildGpuResources() { /* re-create VBOs, textures, FBOs, programs */ }
```

### Step 8 — WebGPU Feature Detection and Fallback

```ts
async function initRenderer(canvas: HTMLCanvasElement) {
  // Try WebGPU first.
  if (navigator.gpu) {
    try {
      const adapter = await navigator.gpu.requestAdapter();
      if (adapter) {
        const device = await adapter.requestDevice();
        // Initialize WebGPU renderer path.
        return { type: 'webgpu' as const, device };
      }
    } catch (e) {
      console.warn('WebGPU init failed, falling back to WebGL2:', e);
    }
  }

  // Fall back to WebGL2.
  const gl = canvas.getContext('webgl2');
  if (gl) {
    return { type: 'webgl2' as const, gl };
  }

  // Unsupported.
  throw new Error('No WebGPU or WebGL2 support in this browser.');
}
```

---

## Pitfalls

| Symptom | Likely cause | Resolution |
|---|---|---|
| `WebGL context lost` / black canvas mid-session | GPU reset, driver TDR, OOM, too many live contexts, or background-tab GPU reclaim | Listen for `webglcontextlost`, **`preventDefault()`**, stop the loop, then re-create all GPU resources on `webglcontextrestored`. See Step 7 code. |
| Heap or `renderer.info.memory.textures/geometries` climbs forever | Missing `dispose()` — geometries, materials, textures, render targets, and FBOs are **not** GC'd; they hold GPU handles | Explicitly dispose on unload/scene-change. See Step 6 disposal code. |
| Rhythmic hitch every few seconds, otherwise smooth | GC stop-the-world from per-frame allocations | Apply Step 4: pool objects, reuse math scratch, ban hot-loop allocators. Confirm with a Memory allocation-timeline recording. |
| Physics teleports / animations jump after switching tabs back | Multi-second `delta` because rAF paused while hidden | Clamp `frameDt` (Step 4) **and** reset `lastTime` on `visibilitychange`. Never integrate an unclamped delta. |
| Timers (`setTimeout`/`setInterval`) drift or fire late in background | Browser throttles background timers to ≥1 s (≥1 min after long backgrounding) | Drive all game timing from `requestAnimationFrame` + the accumulator, not wall-clock timers. Treat the tab as paused when hidden. |
| Texture upload silently fails / appears black on some devices | Exceeds `MAX_TEXTURE_SIZE` (often 4096 on mobile), or NPOT + mips + `REPEAT` on a strict path | Query `gl.MAX_TEXTURE_SIZE` and clamp; use POT for mipmapped/repeating textures; provide a downscaled variant for low-cap GPUs. |
| Banding in gradients/skies; shimmering surfaces | `mediump` where `highp` is needed; or missing mipmaps causing aliasing | Promote that specific computation/varying to `highp`; enable mipmaps + anisotropy for minified world textures. |
| Asset load fails with a CORS error; texture is black/tainted canvas | Cross-origin image without CORS headers; `gl.readPixels`/`toDataURL` taints the canvas | Set `image.crossOrigin = 'anonymous'` (Three.js: `loader.setCrossOrigin('anonymous')`) **and** serve assets with `Access-Control-Allow-Origin`. Same-origin or a proxy if the host won't send headers. |
| WebGPU init throws or returns null adapter | No WebGPU support, software adapter, or disabled by policy | Always `await navigator.gpu?.requestAdapter()`, null-check, and fall back to WebGL2. Never assume `navigator.gpu` exists. |
| Mobile FPS fine but device overheats / throttles after minutes | Sustained GPU load → thermal throttling drops the clock | Add dynamic resolution (Step 5), cap DPR, cap target FPS to 30 on low-end, reduce post-processing. Thermal limits are real budget. |
| Godot Web export: huge `.wasm`, slow first load, low FPS | Forward+ renderer chosen for web, uncompressed textures, no threads | Use the **Compatibility (WebGL2)** renderer for web, enable **VRAM-compressed** texture import, enable threads (COOP/COEP headers) where hosting allows, and shrink the export. |

**Hard rules — never violate:**

1. **Never optimize before profiling.** The GPU and JS heap lie to intuition. Record, find the widest bar, fix that.
2. **Never allocate in the hot path.** Zero `new`, zero object literals, zero closures in `update()`/`render()`. Pool everything.
3. **Never ship uncompressed textures to production.** PNG/JPEG decode to raw RGBA in VRAM. Use KTX2/Basis.
4. **Never integrate an unclamped delta.** Background tabs produce multi-second deltas. Clamp to `MAX_DELTA_MS` and reset on `visibilitychange`.
5. **Never skip `dispose()`.** GPU resources are not GC'd. Every geometry, material, texture, and render target must be explicitly disposed on teardown.
6. **Never assume `navigator.gpu` exists.** Feature-detect WebGPU, fall back to WebGL2, and test both paths.
7. **Never assume `MAX_TEXTURE_SIZE`.** Query it per device and clamp. Many mobile GPUs cap at 4096.
8. **Never ignore `webglcontextlost`.** Without `preventDefault()` the context is not restorable. Handle it, stop the loop, rebuild on restore.

---

## Verification

Do not report the task complete until **every** box is checked against a **real recording on a representative low/mid device** (not just a desktop dev machine). "Looks smooth on my M-series laptop" is not verification.

**Frame timing**
- [ ] **p95 frame time ≤ target budget** (≤16.67 ms for 60 Hz; ≤8.33 ms for 120 Hz) over a 30 s gameplay capture — not just average FPS.
- [ ] **Zero hitches > 2× budget** during steady-state play (`FrameProfiler.hitches === 0` over 30 s after warm-up).
- [ ] FPS holds within ±5% of target during the heaviest scene (peak entity count, peak particles, full post-processing).

**Draw calls & GPU**
- [ ] Draw calls within target for the platform: typically **< 150** for mobile-targeted 2D/light-3D, **< 500** for desktop-targeted scenes (verify the actual number via `renderer.info.render.calls` / Spector.js / Godot Monitor — these are starting targets; set the real cap from the device profile).
- [ ] Repeated geometry is **instanced or batched** (confirmed in a Spector.js capture: no N near-identical draw calls).
- [ ] Texture binds per frame minimized via atlases/array textures (Spector.js shows few `bindTexture` state changes).

**Memory**
- [ ] **VRAM under cap**: `renderer.info.memory.textures` and `.geometries` are **stable** (not climbing) across 5 minutes of play and repeated scene loads/unloads. Target VRAM ceiling met for the device tier (e.g. ≤256 MB textures on mid mobile).
- [ ] All world/3D textures are **KTX2/Basis-compressed** with mipmaps; UI textures are right-sized with mips disabled where appropriate.
- [ ] A heap snapshot before vs. after a scene load → unload → reload cycle shows **no net retained growth** (no detached geometries/textures/listeners).

**Garbage collection**
- [ ] The Memory allocation timeline over 30 s of steady-state play shows a **flat heap** (no sawtooth) — hot path allocates effectively nothing.
- [ ] All per-frame entities (bullets, particles, enemies, tweens) are **pooled**, not `new`-ed/destroyed per spawn.

**Robustness**
- [ ] `webglcontextlost` is handled with `preventDefault()` and a working `webglcontextrestored` rebuild (test by toggling the GPU / using `WEBGL_lose_context`).
- [ ] Tab switch (hide ≥10 s, then refocus) does **not** cause a physics jump, animation blowup, or NaN — delta is clamped and the clock resets.
- [ ] On a device with `MAX_TEXTURE_SIZE === 4096`, no texture exceeds the cap; assets degrade gracefully.
- [ ] Cross-origin assets load without CORS/taint errors; `crossOrigin` is set and headers verified.
- [ ] **WebGPU path tested AND WebGL2 fallback tested** — both render correctly; the fallback triggers cleanly when `navigator.gpu` is absent.

**Sign-off**
- [ ] Numbers captured **before and after** are recorded (draw calls, p95 ms, VRAM, hitch count) proving the optimization moved the proven bottleneck — not a guessed one.

---

## Related Skills

- **`web-perf-optimization`** — Core Web Vitals, bundle size, layout thrashing for non-canvas web pages.
- **`game-asset-pipeline`** — Art/asset authoring, texture packing, mesh decimation workflows.
- **`godot-web-export`** — Godot 4 Web export configuration, COOP/COEP headers, thread enablement.
