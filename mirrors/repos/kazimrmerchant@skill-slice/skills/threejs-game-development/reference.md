# Three.js Game Development — Reference

*Deep API encyclopedia for shipping games on Three.js r160+ (WebGLRenderer, Vite + TypeScript). Loaded on demand from SKILL.md.*

## Renderer & context

| Option | Default | Tradeoff |
|---|---|---|
| `antialias` | `false` | MSAA on the default framebuffer. Near-free on desktop, measurable on mobile GPUs at high DPR. Ignored once you render through an EffectComposer (see Postprocessing). |
| `alpha` | `false` | Transparent canvas compositing with the page. Costs blending with the DOM every frame; keep `false` for games and clear to a color instead. |
| `stencil` | `true` (r163+: `false`) | Only needed for stencil-based effects (portals, masks). Disable if unused to save memory. |
| `powerPreference` | `'default'` | `'high-performance'` requests the discrete GPU on dual-GPU laptops. Set it for games. |
| `preserveDrawingBuffer` | `false` | Keeps the backbuffer readable for screenshots, but disables swap optimizations. Leave `false`; take screenshots by re-rendering then calling `toDataURL` in the same task. |
| `logarithmicDepthBuffer` | `false` | Massively reduces z-fighting for huge depth ranges, but breaks early-Z, costs fragment work, and conflicts with some depth-reading effects (soft particles, SSAO). Prefer tight near/far first. |

DPR clamping: rendering at `devicePixelRatio` 3 costs 9x the fragments of DPR 1. Clamp to 2 (or 1.5 on weak mobile GPUs) — visually near-identical, dramatically cheaper. See game-performance-profiling for measuring fill-rate limits.

```ts
import * as THREE from 'three';

const canvas = document.querySelector<HTMLCanvasElement>('#game')!;
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.toneMapping = THREE.ACESFilmicToneMapping;

window.addEventListener('resize', () => {
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
});

// Context loss happens on real devices (GPU resets, backgrounded tabs on mobile). Handle it.
canvas.addEventListener('webglcontextlost', (e) => {
  e.preventDefault();                 // signal that we will restore
  renderer.setAnimationLoop(null);    // stop the loop; GPU resources are gone
});
canvas.addEventListener('webglcontextrestored', () => {
  renderer.setAnimationLoop(gameLoop); // Three re-uploads geometries/textures lazily; expect a hitch as programs recompile
});
declare function gameLoop(time: number): void;
```

## Color management & tone mapping

Since r152 the pipeline is: **all lighting math in linear-sRGB working space → tone map → encode to sRGB on output**. `renderer.outputColorSpace = THREE.SRGBColorSpace` is the default; do not change it. `THREE.ColorManagement.enabled = true` is also default — `new THREE.Color('#ff8800')` is converted from sRGB to linear for you.

Texture colorSpace rules — the single most common source of "washed out / too dark" bugs:

| Map slot | colorSpace |
|---|---|
| `map` (albedo), `emissiveMap`, `sheenColorMap`, `specularColorMap` | `THREE.SRGBColorSpace` |
| `normalMap`, `roughnessMap`, `metalnessMap`, `aoMap`, `bumpMap`, `displacementMap`, `alphaMap` | `THREE.NoColorSpace` (linear — the default, leave alone) |
| Environment maps (HDR/EXR) | loaded linear by RGBELoader/EXRLoader — leave alone |

```ts
const albedo = await new THREE.TextureLoader().loadAsync('/tex/crate_albedo.jpg');
albedo.colorSpace = THREE.SRGBColorSpace; // required for hand-loaded color textures
```

Tone mapping (`renderer.toneMapping`, tuned with `renderer.toneMappingExposure`, default 1.0):

- `LinearToneMapping` — clips highlights hard; only for deliberately flat looks.
- `ReinhardToneMapping` — soft, desaturates highlights; dated look.
- `ACESFilmicToneMapping` — filmic contrast and highlight rolloff; the safe game default.
- `AgXToneMapping` (r160+) — best hue preservation under strong light; slightly lower contrast than ACES.
- `NeutralToneMapping` (r162+) — Khronos PBR Neutral; matches e-commerce/DCC reference renders, minimal color shift.

Common mistake: **double-correcting glTF textures.** GLTFLoader already assigns correct colorSpace per map slot per the glTF spec. Never loop over a loaded model's textures setting `SRGBColorSpace` — you will corrupt normal/roughness data. Only hand-loaded textures need manual assignment. Deeper lighting/material theory: see the game-3d-rendering skill.

## Scene graph & transforms

Every `Object3D` has local TRS (`position`, `quaternion`/`rotation`, `scale`) composed into `matrix`, and a `matrixWorld` = parent's `matrixWorld * matrix`. `matrixWorld` is refreshed by `renderer.render()` each frame via `scene.updateMatrixWorld()` — so mid-frame reads *after* you moved something are stale until you force an update:

```ts
object.updateWorldMatrix(true, false); // update ancestors + self, skip children — cheapest correct option
// or scene.updateMatrixWorld() to update everything (expensive; avoid per-query)
```

- `parent.add(child)` — child keeps its **local** transform (it visually jumps if parent isn't at origin).
- `parent.attach(child)` — child keeps its **world** transform (local is recomputed). Use for pickups, re-parenting held items, vehicle mounting.
- Static objects: set `obj.matrixAutoUpdate = false`, position them, then call `obj.updateMatrix()` **once**. Skips per-frame matrix composition for thousands of props.
- `layers`: bitmask on both objects and cameras/raycasters. `obj.layers.set(1)` + `camera.layers.enable(1)` renders it; a minimap camera with only layer 2 enabled skips everything else. Layer test uses the object's own layers, not inherited from parents.
- `Group` is a transform-only node — use it as a pivot or to move squads/level chunks together.
- `traverse()` visits every descendant with a closure call each — never traverse the scene per frame. Cache flat arrays of things you update (see architecture.md for entity registries).

World-space reads must use scratch objects — never allocate in the loop:

```ts
const _worldPos = new THREE.Vector3();
const _worldQuat = new THREE.Quaternion();
turret.getWorldPosition(_worldPos);
turret.getWorldQuaternion(_worldQuat);
```

## Cameras

`new THREE.PerspectiveCamera(fov, aspect, near, far)` — `fov` is **vertical** degrees. Horizontal FOV follows from aspect: `hFov = 2 * atan(tan(vFov/2) * aspect)`. Games typically use vFov 50–75; higher on ultrawide is automatic via aspect.

```ts
const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 300);

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix(); // forgetting this = stretched image after resize
});
```

Near/far and depth precision: depth buffer precision is hyperbolic — almost all of it lives near the near plane. **Raising `near` helps far more than lowering `far`.** `near: 0.001` is the classic z-fighting self-inflicted wound; use 0.1+ and keep far/near ratio under ~10,000 (see Common artifacts).

`OrthographicCamera(left, right, top, bottom, near, far)` for HUD and minimaps — define it in stable units (e.g. `-aspect..aspect` horizontal, `-1..1` vertical) and update on resize.

Multi-camera per frame (world + HUD overlay):

```ts
renderer.autoClear = false;
function render(): void {
  renderer.clear();
  renderer.render(scene, camera);      // world
  renderer.clearDepth();               // HUD always draws on top
  renderer.render(hudScene, hudCamera);
}
declare const scene: THREE.Scene, hudScene: THREE.Scene, hudCamera: THREE.OrthographicCamera;
```

## Lights & shadows

| Light | Relative cost | Notes |
|---|---|---|
| `AmbientLight` | free | Flat fill; no direction, no shadows. |
| `HemisphereLight` | ~free | Sky/ground gradient fill — better cheap ambient than AmbientLight. |
| `DirectionalLight` | low | Sun. One shadow-casting directional is the standard game budget. |
| `PointLight` | medium | Shadows need 6 cubemap faces — very expensive; avoid point shadows. |
| `SpotLight` | medium | Cheapest *shadowed* local light (single frustum). |
| `RectAreaLight` | high | No shadows; requires `RectAreaLightUniformsLib.init()` from addons. |
| `LightProbe` | ~free at runtime | Baked SH ambient; pairs with envMaps. |

Physical lighting is the only mode in r165 (`useLegacyLights` removed). Intensity units: Point/Spot in candela (or set `.power` in lumens), Directional in lux, RectArea in nits. A sunny-day directional is ~3–5 with ACES exposure ~1, not 1.0 — tune light intensity and `toneMappingExposure` together. Theory: game-3d-rendering skill.

Shadow map types (`renderer.shadowMap.type`): `BasicShadowMap` (hard, aliased, cheapest), `PCFShadowMap` (default), `PCFSoftShadowMap` (softer penumbra, the usual pick), `VSMShadowMap` (blurrable, all casters must also receive; leaks light between close surfaces). Enable with `renderer.shadowMap.enabled = true`.

The default directional shadow camera is tiny. Tune the frustum tightly around the play area — tighter frustum = more texels per meter = sharper shadows for free:

```ts
const sun = new THREE.DirectionalLight(0xffffff, 4);
sun.position.set(40, 60, 25);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);       // cost is memory + caster re-render; 1024 on mobile
const sc = sun.shadow.camera;             // an OrthographicCamera
sc.left = -30; sc.right = 30; sc.top = 30; sc.bottom = -30;
sc.near = 1; sc.far = 150;
sc.updateProjectionMatrix();
sun.shadow.bias = -0.0002;                // fights acne (surface self-shadowing stripes)
sun.shadow.normalBias = 0.02;             // fights acne on slopes without peter-panning
scene.add(sun, sun.target);               // target must be in the scene to move it
// Large worlds: snap sun.position/sun.target to follow the player each frame.
```

`bias` pushes the depth comparison (too much = shadows detach from objects, "peter-panning"); `normalBias` inflates the caster along normals (more robust, slight shadow shrink). Start with `normalBias`, add small negative `bias` only if needed. For big outdoor ranges use the CSM addon (`three/addons/csm/CSM.js`) — cascaded splits keep near shadows sharp. On mobile, prefer one baked lightmap + cheap "blob" shadows (a `PlaneGeometry` with a radial-gradient alpha texture under each character) over realtime shadow maps.

## Materials

| Material | Cost tier | Use case |
|---|---|---|
| `MeshBasicMaterial` | 1 (unlit) | UI in world, emissive fakes, lightmap-only surfaces. |
| `MeshLambertMaterial` | 2 | Diffuse-only; cheap mobile fallback. |
| `MeshPhongMaterial` | 2 | Cheap specular highlight; stylized/mobile. |
| `MeshStandardMaterial` | 3 | Metal/rough PBR. The default for glTF and for games. |
| `MeshPhysicalMaterial` | 4 | Adds clearcoat, transmission, sheen, iridescence. Hero assets only — transmission triggers an extra scene render. |
| `MeshToonMaterial` | 2 | Ramp-shaded cel look (`gradientMap`). |
| `MeshMatcapMaterial` | 1 | Lighting baked into a capture texture; great look/perf on mobile. |
| `MeshDepthMaterial` / `MeshNormalMaterial` | 1 | Debug and effect passes. |
| `ShaderMaterial` / `RawShaderMaterial` | varies | Custom GLSL — route to game-technical-art-vfx. |

`MeshStandardMaterial` channels:

- `map` — sRGB albedo. `color` multiplies it.
- `normalMap` + `normalScale` (Vector2; set negative Y for DirectX-baked normals from some DCC exports — see game-assets-pipeline).
- `roughnessMap` (green channel) / `metalnessMap` (blue channel) — deliberately share one texture (glTF's metallicRoughness packing). Scalar `roughness`/`metalness` multiply the maps.
- `aoMap` + `aoMapIntensity` — samples the UV set given by `aoMap.channel` (1 = geometry attribute `uv1`; GLTFLoader wires this automatically).
- `emissive` (color) × `emissiveMap` × `emissiveIntensity` — push intensity > 1 to feed bloom thresholds.
- `envMap` / `envMapIntensity` — per-material IBL override; usually set `scene.environment` once instead (PMREM-processed HDR), then tune `envMapIntensity` per material.

Transparency deep-dive:

- `transparent: true` — alpha blending. Object is moved to the sorted transparent pass (back-to-front by depth). Sorting is per-object, not per-triangle: intersecting or concave transparents will pop (see Common artifacts).
- `alphaTest: 0.5` — cutout (foliage, fences, hair cards). Stays in the **opaque** pass: depth-writes correctly, no sorting problems, hard edges. Prefer this over blending whenever the art allows.
- `alphaHash: true` (r154+) — stochastic transparency: order-independent, depth-writes, but noisy unless combined with TAA or high DPR.
- `depthWrite: false` on large blended surfaces (smoke, ghosts, glass) stops them from occluding transparents behind them; combine with explicit `renderOrder` for stable layering.
- `side: THREE.DoubleSide` doubles rasterized fragments and disables backface culling — use only where the camera genuinely sees both sides.
- "Objects invisible through my glass/water": the glass depth-writes and/or sorts in front of other transparents. Fix: `depthWrite: false` on the glass, then order explicitly — `water.renderOrder = 1; glass.renderOrder = 2;`.

`material.onBeforeCompile = (shader) => { /* patch shader.vertexShader / fragmentShader, add uniforms */ }` injects custom GLSL into built-in materials while keeping lights/shadows/fog — the right tool for wind sway or dissolve on StandardMaterial. Full shader workflows: game-technical-art-vfx skill.

## Geometry & BufferGeometry

A `BufferGeometry` is named `BufferAttribute`s plus an optional `index`:

- `position` — vec3 per vertex (required).
- `normal` — vec3, needed by all lit materials (`computeVertexNormals()` if missing).
- `uv` — vec2; `uv1` — second set for `aoMap`/`lightMap`.
- `index` — reuses vertices across triangles; keep it (memory + vertex-cache wins).

Interleaved attributes (`InterleavedBuffer`) improve cache locality; loaders produce them sometimes — treat as read-only unless you know the layout.

Static batching — merge many static meshes **sharing one material** into one draw call:

```ts
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

const parts: THREE.BufferGeometry[] = [];
for (const mesh of staticRocks) {
  mesh.updateWorldMatrix(true, false);
  const g = mesh.geometry.clone();
  g.applyMatrix4(mesh.matrixWorld);   // bake world transform in first — mandatory
  parts.push(g);
}
const merged = mergeGeometries(parts, false);
scene.add(new THREE.Mesh(merged, rockMaterial));
declare const staticRocks: THREE.Mesh[], rockMaterial: THREE.Material, scene: THREE.Scene;
```

Requirements: identical attribute sets on every input, one material, geometry becomes immovable per-object afterwards. For movable copies, use instancing instead.

`geometry.setDrawRange(start, count)` renders a subrange without reallocating — the standard trick for dynamic trail/particle buffers.

Bounding volumes: `boundingBox`/`boundingSphere` are computed lazily and **never auto-recomputed**. After mutating positions, call `computeBoundingSphere()` (frustum culling) and `computeBoundingBox()` (raycast broad-phase). Skinned/morphed meshes are culled by their bind-pose sphere — animated limbs leaving that sphere cause visible popping; fix by inflating `boundingSphere.radius` or `mesh.frustumCulled = false`.

## Instancing

`InstancedMesh` — one geometry, one material, N transforms, one draw call:

```ts
const dummy = new THREE.Object3D(); // scratch transform composer
const trees = new THREE.InstancedMesh(treeGeo, treeMat, 5000);
trees.instanceMatrix.setUsage(THREE.DynamicDrawUsage); // only if updated per frame

for (let i = 0; i < trees.count; i++) {
  dummy.position.set(Math.random() * 400 - 200, 0, Math.random() * 400 - 200);
  dummy.rotation.y = Math.random() * Math.PI * 2;
  dummy.scale.setScalar(0.8 + Math.random() * 0.4);
  dummy.updateMatrix();
  trees.setMatrixAt(i, dummy.matrix);
  trees.setColorAt(i, new THREE.Color().setHSL(0.3, 0.5, 0.4 + Math.random() * 0.2));
}
trees.instanceMatrix.needsUpdate = true;
if (trees.instanceColor) trees.instanceColor.needsUpdate = true;
trees.computeBoundingSphere(); // accounts for instance matrices — do this or culling clips instances
scene.add(trees);
declare const treeGeo: THREE.BufferGeometry, treeMat: THREE.Material, scene: THREE.Scene;
```

- Cheap "removal": swap the last live instance's matrix into slot `i`, then `trees.count--`. `count` can go back up to the constructor capacity later.
- Frustum culling is all-or-nothing (one bounding sphere for every instance). For world-spanning instancers, either keep `computeBoundingSphere()` accurate or set `frustumCulled = false` and chunk the world into several InstancedMeshes.
- Raycasting works: `intersectObject(trees)` hits carry `hit.instanceId`; read the transform back with `trees.getMatrixAt(hit.instanceId, m)`.

`BatchedMesh` (r159+) — **varied geometries**, one material, one draw call, with **per-instance frustum culling and visibility** (InstancedMesh has neither):

```ts
const batch = new THREE.BatchedMesh(256, 200_000, 600_000, sharedMat); // maxInstances, maxVerts, maxIndices
const rockId = batch.addGeometry(rockGeo);
const stumpId = batch.addGeometry(stumpGeo);
const a = batch.addInstance(rockId);
const b = batch.addInstance(stumpId);
batch.setMatrixAt(a, matrixA);
batch.setMatrixAt(b, matrixB);
batch.setVisibleAt(b, false);          // per-instance hide — no buffer shuffling needed
batch.perObjectFrustumCulled = true;   // culls instance-by-instance on CPU
scene.add(batch);
declare const rockGeo: THREE.BufferGeometry, stumpGeo: THREE.BufferGeometry, sharedMat: THREE.Material;
declare const matrixA: THREE.Matrix4, matrixB: THREE.Matrix4;
```

Rule of thumb: same mesh repeated → InstancedMesh; a kit of different static props sharing a texture atlas → BatchedMesh.

## Textures

- Filtering: `magFilter` (`LinearFilter` default; `NearestFilter` for pixel art) and `minFilter` (`LinearMipmapLinearFilter` default = trilinear). Disabling mipmaps (`generateMipmaps = false`) causes shimmering at distance — only do it for render targets and UI.
- Anisotropy fixes blurry ground planes at grazing angles: `tex.anisotropy = renderer.capabilities.getMaxAnisotropy();` (cheap on modern GPUs; clamp to 4–8 on mobile).
- Wrap: `wrapS`/`wrapT` = `ClampToEdgeWrapping` (default), `RepeatWrapping` (+ `tex.repeat.set(4, 4)`), `MirroredRepeatWrapping`.
- Power-of-two still matters: mipmaps and compressed formats want POT (KTX2/Basis requires multiple-of-4; POT is safest). WebGL2 tolerates NPOT but resize-on-upload and mip issues follow you.
- `flipY`: `TextureLoader` defaults `flipY = true`; **glTF textures use `flipY = false`** — the loader handles the UV convention. If you swap a texture onto a glTF material manually, set `flipY = false` or it renders upside-down.
- Compressed GPU textures (KTX2/Basis → transcoded to ASTC/ETC2/BC7 per device): PNG/JPG decompress to raw RGBA **in VRAM** — a 2048² PNG costs ~22 MB with mips regardless of file size. KTX2 stays compressed on-GPU: ~4–6x less VRAM, faster uploads, faster sampling. Non-negotiable for mobile. Authoring: game-assets-pipeline.
- `DataTexture` for procedural/lookup data: `new THREE.DataTexture(float32Array, w, h, THREE.RGBAFormat, THREE.FloatType)`, set `needsUpdate = true` after writes.
- `WebGLRenderTarget(w, h, { samples, type, depthBuffer })` — render-to-texture for minimaps, mirrors, post buffers. Its `.texture` plugs into materials; it needs its own `dispose()`.
- `texture.dispose()` frees the GPU copy only; the image/buffer stays in JS memory and the texture re-uploads if used again (`needsUpdate` fires implicitly).

## Loaders & asset pipeline

Full production wiring — Draco (mesh compression), KTX2 (texture compression), Meshopt (quantization). Decoder folders go in `public/` (copy from `node_modules/three/examples/jsm/libs/`):

```ts
import { GLTFLoader, type GLTF } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { KTX2Loader } from 'three/addons/loaders/KTX2Loader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';

const manager = new THREE.LoadingManager();
manager.onProgress = (url, loaded, total) => updateLoadingBar(loaded / total);
manager.onError = (url) => console.error(`Failed to load: ${url}`);

const draco = new DRACOLoader(manager).setDecoderPath('/draco/');
const ktx2 = new KTX2Loader(manager).setTranscoderPath('/basis/').detectSupport(renderer);
const gltfLoader = new GLTFLoader(manager)
  .setDRACOLoader(draco)
  .setKTX2Loader(ktx2)
  .setMeshoptDecoder(MeshoptDecoder);

const [level, hero] = await Promise.all([
  gltfLoader.loadAsync('/models/level01.glb'),
  gltfLoader.loadAsync('/models/hero.glb'),
]);
declare function updateLoadingBar(fraction: number): void;
declare const renderer: THREE.WebGLRenderer;
```

Anatomy of the result: `gltf.scene` is an `Object3D` hierarchy (meshes, bones, empties); `gltf.animations` is `AnimationClip[]` **not attached to anything** — you wire them to a mixer yourself (next section). Shadows are off by default:

```ts
level.scene.traverse((o) => {
  if ((o as THREE.Mesh).isMesh) { o.castShadow = true; o.receiveShadow = true; }
});
```

Spawning multiple characters: `gltf.scene.clone()` **breaks skinning** — cloned SkinnedMeshes still reference the original skeleton's bones. Use `SkeletonUtils.clone`:

```ts
import * as SkeletonUtils from 'three/addons/utils/SkeletonUtils.js';
const enemy = SkeletonUtils.clone(hero.scene);
```

Caching: keep one `Map<string, Promise<GLTF>>` keyed by URL so concurrent requests share one fetch; clone from the cached scene for spawns. Authoring/export (Blender settings, atlasing, LODs) lives in game-assets-pipeline, but the essential optimization one-liners are:

```
npx @gltf-transform/cli optimize input.glb output.glb --compress draco --texture-compress ktx2
npx @gltf-transform/cli meshopt input.glb output.glb        # meshopt alternative to draco
```

## Animation system

One `AnimationMixer` per skinned root; clips become stateful `AnimationAction`s:

```ts
const mixer = new THREE.AnimationMixer(hero.scene);
const actions = new Map(hero.animations.map((clip) => [clip.name, mixer.clipAction(clip)]));

const idle = actions.get('Idle')!;
const run = actions.get('Run')!;
const attack = actions.get('Attack')!;
idle.play();

function playRun(): void {
  run.reset();                       // clear time/weights from previous plays — forgetting this is the #1 bug
  idle.crossFadeTo(run.play(), 0.25, true); // warp=true time-scales both clips to sync stride during the fade
}

attack.setLoop(THREE.LoopOnce, 1);
attack.clampWhenFinished = true;     // hold the last pose instead of snapping to bind pose
mixer.addEventListener('finished', (e) => {
  if (e.action === attack) playRun();
});

run.timeScale = 1.4;                 // speed up without re-exporting
```

- Call `mixer.update(delta)` exactly once per frame, in the presentation/render update (not the fixed tick — see architecture.md).
- Loop modes: `LoopRepeat` (default), `LoopOnce`, `LoopPingPong`.
- Additive layers (aim offsets, breathing): `THREE.AnimationUtils.makeClipAdditive(clip)` then play at partial `weight` on top of the base locomotion action.
- Multiple clones: each `SkeletonUtils.clone` gets its **own mixer** (they share clip data, so memory is fine). Distant crowds: update mixers at reduced rates (every 2nd–4th frame) as an LOD.
- Root motion caveat: clips exported with hip translation move the mesh away from its physics body. Either bake movement out in the DCC (in-place clips, controller drives position — recommended) or sample the root bone's delta each frame, apply it to the controller, and zero the track.

## Raycasting & picking

```ts
const raycaster = new THREE.Raycaster();
const pointerNdc = new THREE.Vector2();

window.addEventListener('pointerdown', (e) => {
  pointerNdc.x = (e.clientX / window.innerWidth) * 2 - 1;   // NDC: [-1, 1]
  pointerNdc.y = -(e.clientY / window.innerHeight) * 2 + 1; // Y is flipped vs screen coords
  raycaster.setFromCamera(pointerNdc, camera);
  const hits = raycaster.intersectObjects(pickables, false); // curated list, recursive=false
  if (hits.length > 0) onPick(hits[0].object, hits[0].point);
});
declare const camera: THREE.PerspectiveCamera, pickables: THREE.Object3D[];
declare function onPick(obj: THREE.Object3D, point: THREE.Vector3): void;
```

- `raycaster.near`/`raycaster.far` bound the ray — set `far` to interaction range to skip distant geometry.
- `raycaster.layers` filters cheaply; put interactables on their own layer.
- `intersectObjects(list, recursive)` — recursion visits every descendant; keep a flat `pickables` array instead of casting against `scene.children` recursively.
- SkinnedMesh raycasts are expensive (per-vertex skinning on CPU). Raycast against invisible proxy capsules/boxes parented to characters instead.

For triangle-dense static meshes (level geometry, terrain), `three-mesh-bvh` turns O(n) triangle tests into O(log n):

```ts
import { computeBoundsTree, disposeBoundsTree, acceleratedRaycast } from 'three-mesh-bvh';

THREE.BufferGeometry.prototype.computeBoundsTree = computeBoundsTree;
THREE.BufferGeometry.prototype.disposeBoundsTree = disposeBoundsTree;
THREE.Mesh.prototype.raycast = acceleratedRaycast;

levelMesh.geometry.computeBoundsTree();  // one-time build cost
raycaster.firstHitOnly = true;           // early-out: huge win for ground checks / bullets
declare const levelMesh: THREE.Mesh;
```

Its `shapecast()` also powers sphere/capsule-vs-mesh queries — the basis of kinematic character controllers against level meshes (full recipe in recipes.md; Rapier via `@dimforge/rapier3d-compat` for dynamic physics). For hundreds of picks per frame (RTS selection), GPU picking — render IDs to a 1px render target — beats CPU rays; see recipes.md.

## Postprocessing

```ts
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

const msaaTarget = new THREE.WebGLRenderTarget(innerWidth, innerHeight, {
  samples: 4,                        // WebGL2 MSAA inside the composer
  type: THREE.HalfFloatType,         // HDR headroom so bloom thresholds work
});
const composer = new EffectComposer(renderer, msaaTarget);
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(innerWidth, innerHeight), 0.5, 0.4, 1.0);
composer.addPass(bloom);
composer.addPass(new OutputPass());  // ALWAYS the final pass (r154+)

window.addEventListener('resize', () => {
  composer.setSize(innerWidth, innerHeight);
  composer.setPixelRatio(Math.min(devicePixelRatio, 2));
});
// per frame: composer.render(); — instead of renderer.render()
declare const renderer: THREE.WebGLRenderer, scene: THREE.Scene, camera: THREE.Camera;
```

`OutputPass` interaction: intermediate passes run in **linear HalfFloat** buffers; tone mapping and sRGB encoding happen only in `OutputPass`, which reads `renderer.toneMapping` at render time. So **keep** `renderer.toneMapping = ACESFilmicToneMapping` set — do not clear it, and never add the legacy GammaCorrectionShader (double-encode). Without `OutputPass` the frame reaches screen linear and dark.

- Constructor `antialias: true` does nothing through a composer (you render into targets, not the backbuffer). Use the `samples` target above, or an `SMAAPass`/FXAA pass (blurrier, cheaper), or TAA (`TAARenderPass`, ghosting risk).
- Bloom workflow: keep threshold ~1.0 so only HDR emitters (emissiveIntensity > 1, bright lights) bloom — a low threshold blooms the whole frame into fog. Bloom is multiple downsampled blur passes: budget it.
- The pmndrs `postprocessing` npm package merges compatible effects into single fullscreen passes — measurably faster than stock addons when stacking 3+ effects; consider it before hand-optimizing.
- Mobile: every pass re-touches every pixel. Fill-rate-bound devices often gain 30–50% by skipping post entirely — make the whole chain toggleable (see web-game-release-review for shipping quality tiers).

## Audio

```ts
const listener = new THREE.AudioListener();
camera.add(listener);                          // ears follow the camera

const music = new THREE.Audio(listener);       // non-spatial: music, UI
const engine = new THREE.PositionalAudio(listener); // 3D: attach to an Object3D
carMesh.add(engine);
engine.setRefDistance(4);                      // full volume within 4m
engine.setDistanceModel('inverse');            // 'linear' | 'inverse' (default) | 'exponential'

const audioLoader = new THREE.AudioLoader();
audioLoader.load('/audio/engine.ogg', (buffer) => {
  engine.setBuffer(buffer);
  engine.setLoop(true);
});

// Autoplay policy: the AudioContext starts suspended until a user gesture.
window.addEventListener('pointerdown', () => {
  if (listener.context.state === 'suspended') void listener.context.resume();
  if (!music.isPlaying && music.buffer) music.play();
}, { once: true });
declare const camera: THREE.Camera, carMesh: THREE.Object3D;
```

Short SFX pooling: `Audio.play()` on an already-playing source restarts it, cutting off the previous shot. Keep a small ring of `Audio` objects sharing one decoded `AudioBuffer` and round-robin them for rapid-fire sounds.

## Timing

- `renderer.setAnimationLoop(loop)` over raw `requestAnimationFrame` — it handles XR and cleans up on context loss.
- `THREE.Clock.getDelta()` returns time since the *last* `getDelta()` call — call it at **exactly one site** per frame and pass `delta` down; two call sites silently halve everyone's delta.
- Clamp delta: after a tab-switch, rAF pauses and the first frame back reports a multi-second delta, teleporting physics. `const delta = Math.min(clock.getDelta(), 0.1);`
- Background tabs: rAF/`setAnimationLoop` stop entirely (and `setInterval` throttles to ≥1s). Pause gameplay on `document.visibilitychange` rather than trusting timers.
- Variable-rate rendering + fixed-timestep simulation (accumulator loop, interpolation) is the correct game structure — full pattern and code in architecture.md.

## Memory & disposal semantics

Three.js does not garbage-collect GPU resources. `dispose()` or leak:

| Class | `dispose()` frees | Common leak |
|---|---|---|
| `BufferGeometry` | VBOs/IBOs | Per-frame geometry rebuilds without disposing the old one |
| `Material` | Compiled program refs, uniforms | Assuming it disposes its textures — **it does not** |
| `Texture` | GPU texture object | Textures on disposed materials linger forever |
| `WebGLRenderTarget` | FBO + its internal texture(s) | Recreating targets on resize without disposing the old |
| `Skeleton` (`boneTexture`) | Bone data texture | Despawned enemies keeping skeleton textures |
| `renderer` | All + internal state | SPA route change leaving the old canvas/context alive |

**Removing an object from the scene frees nothing.** Deep-dispose on despawn:

```ts
function deepDispose(root: THREE.Object3D): void {
  root.traverse((obj) => {
    const mesh = obj as THREE.Mesh;
    if (mesh.geometry) mesh.geometry.dispose();
    const mats = Array.isArray(mesh.material) ? mesh.material : mesh.material ? [mesh.material] : [];
    for (const m of mats) {
      for (const value of Object.values(m)) {
        if ((value as THREE.Texture)?.isTexture) (value as THREE.Texture).dispose();
      }
      m.dispose();
    }
  });
  root.removeFromParent();
}
```

Shared assets make blind deep-dispose dangerous: disposing the material of one despawned enemy kills every clone using it. Refcount per asset key (increment on spawn, decrement on despawn, dispose at zero) — or simpler: never dispose shared library assets during play, only on level teardown.

Monitoring — watch these climb to catch leaks early:

```ts
setInterval(() => {
  const { memory, render, programs } = renderer.info;
  console.log(`geometries=${memory.geometries} textures=${memory.textures} ` +
              `drawCalls=${render.calls} tris=${render.triangles} programs=${programs?.length ?? 0}`);
}, 2000);
```

Full teardown (SPA unmount): stop the loop, deep-dispose the scene, `composer?.dispose()`, `renderer.dispose()`, then `renderer.forceContextLoss()` to release the context immediately instead of waiting for GC.

Classic leak patterns: window/DOM event listeners capturing the scene in closures (remove on teardown, or use `AbortController`), `setInterval` closures holding despawned entities, `AnimationMixer`s of removed characters still in your update list (call `mixer.stopAllAction()` and drop the ref; `mixer.uncacheRoot(root)` for full cleanup), and EffectComposer render targets duplicated across resize handlers.

## Math & smoothing utilities

`lerp(a, b, 0.1)` per frame is framerate-dependent — at 144 Hz it converges 2.4x faster than at 60 Hz. `MathUtils.damp` is the exponential-decay, framerate-independent version; `lambda` ≈ convergence speed (higher = snappier, ~1–20 useful range):

```ts
camera.position.x = THREE.MathUtils.damp(camera.position.x, target.x, 5, delta);
// Rotation: slerp toward a target quaternion with a damp-derived, frame-independent t
const t = 1 - Math.exp(-8 * delta);
mesh.quaternion.slerp(targetQuat, t);
declare const camera: THREE.Camera, mesh: THREE.Object3D, target: THREE.Vector3, targetQuat: THREE.Quaternion, delta: number;
```

- Scratch-object discipline: module-level `const _v1 = new THREE.Vector3()` reused in hot paths. `new Vector3()` per frame per entity = GC hitches. Never store a scratch object's value — `copy()` it out.
- `lookAt` pitfalls: it uses `object.up` (default +Y) — looking straight up/down degenerates (roll flips). For turrets/heads, build the quaternion explicitly or constrain pitch before calling.
- `MathUtils.clamp(x, min, max)` and `MathUtils.smoothstep(x, min, max)` cover most easing needs without a tween lib.
- `Math.random()` is not seedable. For deterministic procgen/replays, a tiny seeded PRNG:

```ts
function mulberry32(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
```

## Common artifacts & gotchas

- **Z-fighting**: shimmering coplanar surfaces. Fixes in order: raise `camera.near`; separate the geometry (offset decals a few mm); `polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1` on the decal material; `logarithmicDepthBuffer` as last resort (costs and caveats in Renderer section).
- **Shadow acne vs peter-panning**:

| Symptom | Cause | Fix |
|---|---|---|
| Stripes/moire on lit surfaces | Self-shadowing (bias too small) | Increase `shadow.normalBias` (0.01–0.05), then small negative `shadow.bias` |
| Shadows detached from feet | Bias too large | Reduce `bias` magnitude, prefer `normalBias`, tighten shadow camera frustum |

- **Transparent sort popping**: per-object depth sorting flips order as the camera moves. Fixes: split large transparents into chunks, set explicit `renderOrder`, `depthWrite: false`, or convert to `alphaTest`/`alphaHash`.
- **Fog and custom materials**: built-ins fog automatically (works with instancing too). `ShaderMaterial` needs `fog: true` **plus** the fog uniform/chunk includes in your GLSL, or fogged and unfogged objects visibly mismatch at distance.
- **NaN poisoning**: one NaN in a position attribute or object transform makes `computeBoundingSphere` produce NaN radius → the mesh (or its whole subtree) vanishes, and raycasts silently miss. Symptoms: object disappears permanently after a physics explosion or divide-by-zero. Hunt: `console.assert(!Number.isNaN(body.position.x))` at the physics→visual sync point; check `geometry.boundingSphere.radius` for NaN.
- **Skinned mesh popping out of view**: bind-pose bounding sphere doesn't cover animation extremes. Inflate `mesh.geometry.boundingSphere.radius` after load or set `frustumCulled = false` on characters.
- **Morph targets + instancing**: `InstancedMesh` morph support is recent and partial; skinning on `InstancedMesh`/`BatchedMesh` is not supported in core. Crowds of animated characters need per-clone SkinnedMeshes (with mixer-rate LOD) or a custom bone-texture/VAT approach — see game-technical-art-vfx.
- **Mobile `mediump` artifacts**: banding, jittering vertices far from origin, broken highlights. Keep world coordinates small (recenter/floating origin for big worlds) and test on real Android hardware, not desktop emulation.
- **iOS Safari memory**: hard per-tab GPU+JS memory caps — exceeding them kills the tab with no error. KTX2 textures and 1024²-max shadow maps are effectively mandatory; see web-game-release-review.
- **Context limits**: ~16 textures per shader, capped uniform vectors (limits bones per SkinnedMesh — Three falls back to bone textures), capped vertex attributes. Query `renderer.capabilities` before designing über-materials.

## Debugging toolkit

- `renderer.info` — `render.calls` (draw calls: the headline number; sub-100s desktop, ~50 mobile), `render.triangles`, `memory.geometries`/`memory.textures` (leak detectors), `programs` (shader variant count — a growing list means material permutation churn). Resets each frame unless `renderer.info.autoReset = false`.
- FPS/frametime: `Stats` from `three/addons/libs/stats.module.js`, or the `stats-gl` npm package for GPU timing (measures actual GPU cost, not just JS). Deeper profiling methodology: game-performance-profiling.
- Quick tuning rig:

```ts
import GUI from 'lil-gui';
const gui = new GUI();
gui.add(sun, 'intensity', 0, 10);
gui.add(renderer, 'toneMappingExposure', 0, 3);
gui.add(bloom, 'strength', 0, 2);
declare const sun: THREE.DirectionalLight, renderer: THREE.WebGLRenderer;
declare const bloom: { strength: number };
```

- Spector.js (browser extension): capture one frame → inspect every draw call, its shaders, uniforms, and render targets in order. The tool for "why is this drawn twice" and "what pass is eating my frame".
- three-devtools browser extension: live scene-graph inspection of a running page.
- Helpers: `AxesHelper` (orientation), `GridHelper` (ground reference), `Box3Helper` (bounds), `new THREE.CameraHelper(sun.shadow.camera)` — **the** tool for shadow frustum tuning, `SkeletonHelper` (bone debugging), `DirectionalLightHelper`/`SpotLightHelper`.
- `scene.overrideMaterial = new THREE.MeshNormalMaterial()` (or a wireframe `MeshBasicMaterial`) renders everything with one material — isolates whether a bug is material-side or geometry-side, and approximates vertex-bound cost with zero shading.
- Draw-call hot list: temporarily patch `Object3D.prototype.onAfterRender` to push `{ name, triangles }` per drawn object into an array, then `console.table` it sorted — instantly names your most expensive meshes.

## WebGPU / TSL forward note

Three ships a `WebGPURenderer` with TSL (Three Shading Language) — a node-based shader system that compiles to both WGSL and GLSL. It promises compute shaders, lower CPU overhead, and portable materials. It is not the shipping target yet: browser coverage is incomplete (notably older Safari/Android), and the API surface is still moving release-to-release. Ship on `WebGLRenderer`; keep custom shader work isolated behind `onBeforeCompile`/small ShaderMaterials so a future migration to node materials touches few files. Re-evaluate once your target audience's WebGPU support crosses your browser-support bar (see web-game-release-review).

Concrete copy-paste setups live in recipes.md; structural decisions in architecture.md; full worked games in examples.md.
