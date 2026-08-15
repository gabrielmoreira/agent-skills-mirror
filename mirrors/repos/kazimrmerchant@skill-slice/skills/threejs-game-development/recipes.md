# Three.js Game Development — Recipes

*Copy-paste, adapt names. Targets Three.js r160+ with Vite + TypeScript; later recipes reuse `renderer`/`scene`/`camera`/`loop`/`assets` from recipes 2–5. Loaded on demand from SKILL.md.*

## 1. Project scaffold (Vite + TS)
When: starting any new Three.js game project.

```bash
npm create vite@latest my-game -- --template vanilla-ts
cd my-game
npm i three @dimforge/rapier3d-compat
npm i -D @types/three vite-plugin-glsl   # vite-plugin-glsl is OPTIONAL — only for .glsl imports
# Copy decoders into public/ so they ship with the build (PowerShell: use Copy-Item -Recurse):
mkdir -p public/draco public/basis
cp -r node_modules/three/examples/jsm/libs/draco/gltf/. public/draco/
cp -r node_modules/three/examples/jsm/libs/basis/. public/basis/
```

`index.html`:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />
  <title>my-game</title>
</head>
<body>
  <canvas id="game"></canvas>
  <div id="hud"></div>
  <script type="module" src="/src/main.ts"></script>
</body>
</html>
```

`src/style.css` (the template's `main.ts` imports it):

```css
* { margin: 0; padding: 0; }
html, body { height: 100%; overflow: hidden; background: #000; }
/* display:block kills the baseline gap; dvh handles mobile toolbars; touch-action feeds recipe 10 */
#game { display: block; width: 100vw; height: 100dvh; touch-action: none; }
#hud { position: fixed; inset: 0; pointer-events: none; }
```

`vite.config.ts`:

```ts
import { defineConfig } from 'vite';
// import glsl from 'vite-plugin-glsl'; // optional — uncomment if you write .glsl files

export default defineConfig({
  base: './',             // relative URLs: the build works on itch.io and any subpath
  server: { host: true }, // expose on LAN for phone testing: http://<your-ip>:5173
  // plugins: [glsl()],
  // Keep assetsInlineLimit at its 4 KB default: the draco/basis decoders live in
  // public/, which Vite copies verbatim and never inlines — no override needed.
});
```

Notes/pitfalls:
- tsconfig: the vanilla-ts template default already has `"strict": true` — keep it.
- The `/draco/` and `/basis/` paths are referenced by recipe 5; a 404 there means you skipped the copy step. Why a DOM `#hud` overlay → architecture.md.

## 2. Renderer + resize + DPR clamp
When: every project — the one-time renderer setup.

```ts
import * as THREE from 'three';

export function createRenderer(canvas: HTMLCanvasElement): THREE.WebGLRenderer {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)); // DPR clamp: >2 burns fill rate invisibly
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.toneMapping = THREE.ACESFilmicToneMapping; // output is sRGB by default since r152
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  return renderer;
}

export function bindResize(renderer: THREE.WebGLRenderer, camera: THREE.PerspectiveCamera,
  composer?: { setSize(w: number, h: number): void; setPixelRatio(r: number): void }): ResizeObserver {
  const canvas = renderer.domElement;
  const observer = new ResizeObserver(() => {
    const w = canvas.clientWidth, h = canvas.clientHeight, dpr = Math.min(window.devicePixelRatio, 2);
    renderer.setPixelRatio(dpr);
    renderer.setSize(w, h, false); // false: CSS already sizes the element
    composer?.setPixelRatio(dpr);
    composer?.setSize(w, h);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  });
  observer.observe(canvas);
  return observer;
}

export function bindContextLoss(renderer: THREE.WebGLRenderer, onLost: () => void, onRestored: () => void): void {
  renderer.domElement.addEventListener('webglcontextlost', (e) => {
    e.preventDefault(); // REQUIRED — without it the context is never restored
    onLost();           // pause the loop, show an overlay
  });
  renderer.domElement.addEventListener('webglcontextrestored', onRestored); // three re-uploads GPU state
}
```

Notes/pitfalls:
- ResizeObserver beats the `resize` event: it fires for split view, rotation, devtools — any element size change.
- `texture.colorSpace = THREE.SRGBColorSpace` goes on COLOR maps only (recipe 5), never normal/roughness/AO. Renderer option depth → reference.md.

## 3. Fixed-timestep Loop class
When: every project — physics needs deterministic steps; rendering runs per frame.

```ts
import * as THREE from 'three';

export const FIXED_DT = 1 / 60;
const MAX_FRAME = 0.25; // clamp: no giant catch-up burst after a tab stall

export class Loop {
  timescale = 1; // 0.2 = slow-mo for free
  readonly onFixed: Array<(dt: number) => void> = [];
  readonly onFrame: Array<(dt: number, alpha: number) => void> = [];
  private accumulator = 0; private last = 0;
  private paused = false; private running = false;

  constructor(private renderer: THREE.WebGLRenderer) {
    document.addEventListener('visibilitychange', () => {
      this.paused = document.hidden;
      this.last = performance.now(); // avoid one huge dt on return
    });
  }

  start(): void {
    if (this.running) return;
    this.running = true;
    this.last = performance.now();
    this.renderer.setAnimationLoop((t) => this.tick(t)); // also drives WebXR (recipe 18)
  }

  stop(): void { this.running = false; this.renderer.setAnimationLoop(null); }
  pause(p = true): void { this.paused = p; if (!p) this.last = performance.now(); }

  private tick(time: number): void {
    if (this.paused) return;
    const frame = Math.min((time - this.last) / 1000, MAX_FRAME) * this.timescale;
    this.last = time;
    this.accumulator += frame;
    while (this.accumulator >= FIXED_DT) {
      for (const fn of this.onFixed) fn(FIXED_DT);
      this.accumulator -= FIXED_DT;
    }
    const alpha = this.accumulator / FIXED_DT; // 0..1 — interpolate visuals with this to kill stutter
    for (const fn of this.onFrame) fn(frame, alpha);
  }
}

// Usage:
const loop = new Loop(renderer);
loop.onFixed.push((dt) => world.step());                 // physics + gameplay
loop.onFrame.push((dt) => anim.update(dt));              // animation mixers
loop.onFrame.push(() => renderer.render(scene, camera)); // register render LAST
loop.start();
```

Notes/pitfalls:
- `pause()` for menus; `timescale` for slow-mo/hitstop.
- Why fixed-step gameplay + variable-step rendering → architecture.md.

## 4. Environment lighting quickstart
When: PBR materials look flat/black — you need image-based lighting before anything else.

```ts
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';

// A) Zero-asset neutral studio IBL — good prototype default. Run ONCE, not per frame.
export function applyRoomEnvironment(renderer: THREE.WebGLRenderer, scene: THREE.Scene): void {
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  pmrem.dispose();
}

// B) HDR equirect: real sky + matching reflections.
export async function applyHdrEnvironment(scene: THREE.Scene, url: string): Promise<void> {
  const hdr = await new RGBELoader().loadAsync(url); // e.g. '/hdri/sky_2k.hdr' in public/
  hdr.mapping = THREE.EquirectangularReflectionMapping;
  scene.environment = hdr;
  scene.background = hdr;
  scene.backgroundBlurriness = 0.1;
  scene.environmentIntensity = 1.0; // r163+ — global IBL dial
}

// IBL lights the scene but casts NO shadows — add one sun for grounding.
export function addSun(scene: THREE.Scene): THREE.DirectionalLight {
  const sun = new THREE.DirectionalLight(0xffffff, 3);
  sun.position.set(8, 12, 5);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, { left: -20, right: 20, top: 20, bottom: -20, far: 50 });
  sun.shadow.bias = -0.0005; // fights shadow acne
  scene.add(sun);
  return sun;
}
```

Notes/pitfalls:
- The shadow camera box must cover the play area: too big = blocky shadows, too small = clipped.
- Lighting model details → reference.md.

## 5. Asset loader stack + typed manifest
When: any project with GLB models, compressed textures, or audio — one preload, typed access everywhere.

```ts
import * as THREE from 'three';
import { GLTFLoader, type GLTF } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { KTX2Loader } from 'three/addons/loaders/KTX2Loader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import * as SkeletonUtils from 'three/addons/utils/SkeletonUtils.js';

export const MANIFEST = {
  models: { player: '/models/player.glb', level: '/models/level.glb' },
  textures: { crate: '/textures/crate.ktx2' },
  audio: { shoot: '/audio/shoot.ogg', music: '/audio/music.ogg' },
} as const;
export type ModelName = keyof typeof MANIFEST.models;
export type TextureName = keyof typeof MANIFEST.textures;
export type AudioName = keyof typeof MANIFEST.audio;

export class AssetManager {
  private manager = new THREE.LoadingManager();
  private gltfLoader: GLTFLoader;
  private ktx2: KTX2Loader;
  private audioLoader = new THREE.AudioLoader(this.manager);
  private models = new Map<ModelName, GLTF>();
  private textures = new Map<TextureName, THREE.Texture>();
  private audio = new Map<AudioName, AudioBuffer>();

  constructor(renderer: THREE.WebGLRenderer) {
    const draco = new DRACOLoader(this.manager).setDecoderPath('/draco/');
    this.ktx2 = new KTX2Loader(this.manager).setTranscoderPath('/basis/').detectSupport(renderer);
    this.gltfLoader = new GLTFLoader(this.manager)
      .setDRACOLoader(draco).setKTX2Loader(this.ktx2).setMeshoptDecoder(MeshoptDecoder);
  }

  async preloadAll(onProgress?: (ratio: number) => void): Promise<void> {
    this.manager.onProgress = (_url, loaded, total) => onProgress?.(loaded / total);
    await Promise.all([
      ...Object.entries(MANIFEST.models).map(async ([n, url]) =>
        this.models.set(n as ModelName, await this.gltfLoader.loadAsync(url))),
      ...Object.entries(MANIFEST.textures).map(async ([n, url]) => {
        const tex = await this.ktx2.loadAsync(url);
        tex.colorSpace = THREE.SRGBColorSpace; // COLOR maps only — normal/rough/AO stay linear
        this.textures.set(n as TextureName, tex);
      }),
      ...Object.entries(MANIFEST.audio).map(async ([n, url]) =>
        this.audio.set(n as AudioName, await this.audioLoader.loadAsync(url))),
    ]);
  }

  getModel(name: ModelName): GLTF { return this.models.get(name)!; }
  getTexture(name: TextureName): THREE.Texture { return this.textures.get(name)!; }
  getAudio(name: AudioName): AudioBuffer { return this.audio.get(name)!; }
  /** Independent copy — REQUIRED for SkinnedMesh; plain .clone() breaks bone bindings. */
  spawn(name: ModelName): THREE.Object3D { return SkeletonUtils.clone(this.models.get(name)!.scene); }
}

// Usage: progress bar + shader warmup.
const assets = new AssetManager(renderer);
const bar = document.querySelector<HTMLDivElement>('#progress')!;
await assets.preloadAll((r) => { bar.style.width = `${(r * 100).toFixed(0)}%`; });
scene.add(assets.spawn('player'));
await renderer.compileAsync(scene, camera); // compile shaders now, not on first visible frame
```

Notes/pitfalls:
- LoadingManager totals grow as nested resources (textures inside GLBs) are discovered — progress can jump backwards; clamp in the UI.
- Why one manifest instead of scattered `load()` calls → architecture.md.

## 6. Animation controller (crossfade state machine)
When: a character with idle/run/jump clips needs smooth transitions and one-shots that return to idle.

```ts
import * as THREE from 'three';

export class AnimationController {
  private mixer: THREE.AnimationMixer;
  private actions = new Map<string, THREE.AnimationAction>();
  private current: THREE.AnimationAction | null = null;

  constructor(root: THREE.Object3D, clips: THREE.AnimationClip[], private idleName = 'idle') {
    this.mixer = new THREE.AnimationMixer(root);
    for (const clip of clips) this.actions.set(clip.name, this.mixer.clipAction(clip));
    this.mixer.addEventListener('finished', (e) => {
      if (e.action === this.current) this.play(this.idleName, 0.2); // one-shots auto-return
    });
  }

  play(name: string, fadeSecs = 0.25): void {
    const next = this.actions.get(name);
    if (!next || next === this.current) return;
    next.enabled = true;
    next.reset().setEffectiveTimeScale(1).setEffectiveWeight(1).play();
    if (this.current) this.current.crossFadeTo(next, fadeSecs, false);
    this.current = next;
  }

  playOnce(name: string, fadeSecs = 0.1): void {
    const action = this.actions.get(name);
    if (!action) return;
    action.setLoop(THREE.LoopOnce, 1);
    action.clampWhenFinished = true; // hold the last frame instead of snapping to T-pose
    this.play(name, fadeSecs);
  }

  update(delta: number): void { this.mixer.update(delta); }
}

// Usage: clips come from the ORIGINAL gltf; the mixer targets the SkeletonUtils clone (recipe 5).
const gltf = assets.getModel('player');
const model = assets.spawn('player');
const anim = new AnimationController(model, gltf.animations);
anim.play('idle'); // per frame: anim.update(dt); on move: play('run'); on jump: playOnce('jump')
```

Notes/pitfalls:
- Clip names must match your DCC export — `console.log(gltf.animations.map(c => c.name))` first.
- Blend trees and locomotion layers → architecture.md.

## 7. Rapier physics world + third-person kinematic character controller
When: the flagship setup — a walkable character with gravity, jumping, steps and slopes, plus dynamic props.

```ts
import * as THREE from 'three';
import RAPIER from '@dimforge/rapier3d-compat';

export interface BodyMeshPair { body: RAPIER.RigidBody; mesh: THREE.Object3D; }

export async function createPhysics() {
  await RAPIER.init(); // loads the embedded WASM — call ONCE before any RAPIER usage
  const world = new RAPIER.World({ x: 0, y: -9.81, z: 0 });
  world.timestep = 1 / 60; // matches FIXED_DT from recipe 3 (also the default)
  return { world, eventQueue: new RAPIER.EventQueue(true), pairs: [] as BodyMeshPair[] };
}

export function createGround(world: RAPIER.World, scene: THREE.Scene): void {
  world.createCollider(RAPIER.ColliderDesc.cuboid(25, 0.5, 25).setTranslation(0, -0.5, 0));
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(50, 1, 50), new THREE.MeshStandardMaterial({ color: 0x777777 }));
  mesh.position.y = -0.5;
  mesh.receiveShadow = true;
  scene.add(mesh);
}

export function createDynamicBox(world: RAPIER.World, scene: THREE.Scene, pairs: BodyMeshPair[],
  pos: THREE.Vector3, size = 1): BodyMeshPair {
  const body = world.createRigidBody(RAPIER.RigidBodyDesc.dynamic().setTranslation(pos.x, pos.y, pos.z));
  world.createCollider(
    RAPIER.ColliderDesc.cuboid(size / 2, size / 2, size / 2)
      .setActiveEvents(RAPIER.ActiveEvents.COLLISION_EVENTS), // events are opt-in per collider
    body);
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(size, size, size), new THREE.MeshStandardMaterial({ color: 0xcc6633 }));
  mesh.castShadow = true;
  scene.add(mesh);
  const pair = { body, mesh };
  pairs.push(pair);
  return pair;
}

export class PlayerController {
  readonly body: RAPIER.RigidBody;
  grounded = false;
  readonly speed = 6;
  readonly jumpSpeed = 8;
  private collider: RAPIER.Collider;
  private controller: RAPIER.KinematicCharacterController;
  private velocityY = 0;

  constructor(world: RAPIER.World, spawn: THREE.Vector3, public mesh: THREE.Object3D) {
    this.body = world.createRigidBody(
      RAPIER.RigidBodyDesc.kinematicPositionBased().setTranslation(spawn.x, spawn.y, spawn.z));
    // capsule(halfHeight, radius): total height = 2 * (0.6 + 0.35) = 1.9 m
    this.collider = world.createCollider(RAPIER.ColliderDesc.capsule(0.6, 0.35), this.body);
    this.controller = world.createCharacterController(0.01); // "skin" offset — keep small
    this.controller.enableAutostep(0.4, 0.2, true);          // maxStepHeight, minWidth, includeDynamic
    this.controller.enableSnapToGround(0.4);                  // stick to ground going downhill
    this.controller.setSlopeClimbAngle((50 * Math.PI) / 180);
    this.controller.setApplyImpulsesToDynamicBodies(true);    // push boxes around
  }

  /** Call from the FIXED step. input.x/z is camera-relative with length <= 1. */
  fixedUpdate(dt: number, input: { x: number; z: number; jump: boolean }): void {
    if (this.grounded) this.velocityY = input.jump ? this.jumpSpeed : -0.5; // downward bias keeps snap working
    else this.velocityY -= 9.81 * dt;
    const desired = { x: input.x * this.speed * dt, y: this.velocityY * dt, z: input.z * this.speed * dt };
    this.controller.computeColliderMovement(this.collider, desired);
    this.grounded = this.controller.computedGrounded();       // jump reset comes from here
    const move = this.controller.computedMovement();          // collision-corrected translation
    const pos = this.body.translation();
    this.body.setNextKinematicTranslation({ x: pos.x + move.x, y: pos.y + move.y, z: pos.z + move.z });
    if (input.x !== 0 || input.z !== 0) this.mesh.rotation.y = Math.atan2(input.x, input.z); // face movement
  }

  /** Call from the FRAME step: capsule center -> model feet. */
  syncMesh(): void {
    const p = this.body.translation();
    this.mesh.position.set(p.x, p.y - 0.95, p.z);
  }
}
```

Wiring it together (keyboard input + the Loop from recipe 3):

```ts
const keys = new Set<string>();
window.addEventListener('keydown', (e) => keys.add(e.code));
window.addEventListener('keyup', (e) => keys.delete(e.code));

function readInput(camera: THREE.Camera): { x: number; z: number; jump: boolean } {
  const fwd = new THREE.Vector3();
  camera.getWorldDirection(fwd); fwd.y = 0; fwd.normalize();
  const right = new THREE.Vector3().crossVectors(fwd, camera.up).normalize();
  const v = new THREE.Vector3();
  if (keys.has('KeyW')) v.add(fwd);
  if (keys.has('KeyS')) v.sub(fwd);
  if (keys.has('KeyD')) v.add(right);
  if (keys.has('KeyA')) v.sub(right);
  if (v.lengthSq() > 1) v.normalize();
  return { x: v.x, z: v.z, jump: keys.has('Space') };
}

const { world, eventQueue, pairs } = await createPhysics();
createGround(world, scene);
createDynamicBox(world, scene, pairs, new THREE.Vector3(2, 3, 0));
const player = new PlayerController(world, new THREE.Vector3(0, 2, 0), assets.spawn('player'));
scene.add(player.mesh);

loop.onFixed.push((dt) => {
  player.fixedUpdate(dt, readInput(camera)); // merge touch (10) + gamepad (11) here too
  world.step(eventQueue);
  eventQueue.drainCollisionEvents((h1, h2, started) => {
    if (started) { /* map collider handles -> entities at creation time, react here */ }
  });
});
loop.onFrame.push(() => {
  player.syncMesh();
  for (const { body, mesh } of pairs) { // physics is the source of truth; meshes are visuals
    const p = body.translation(), q = body.rotation();
    mesh.position.set(p.x, p.y, p.z);
    mesh.quaternion.set(q.x, q.y, q.z, q.w);
  }
});
```

Notes/pitfalls:
- `await RAPIER.init()` must finish before ANY Rapier call — top-level await in the entry module is fine with Vite.
- Collision events need `ActiveEvents.COLLISION_EVENTS` set; keep a `Map<number, Entity>` keyed by `collider.handle`.
- Kinematic controllers ignore forces — moving platforms require you to add the platform delta to `desired` yourself. Body/mesh sync rationale → architecture.md; full Rapier API → reference.md.

## 8. cannon-es minimal alternative
When: you want a small pure-JS engine (no WASM) and only need spheres/boxes/planes.

```ts
import * as THREE from 'three';
import * as CANNON from 'cannon-es';
import { FIXED_DT } from './Loop'; // recipe 3

const world = new CANNON.World({ gravity: new CANNON.Vec3(0, -9.82, 0) });
const ground = new CANNON.Body({ type: CANNON.Body.STATIC, shape: new CANNON.Plane() });
ground.quaternion.setFromEuler(-Math.PI / 2, 0, 0); // planes face +z by default; rotate to face up
world.addBody(ground);

const ball = new CANNON.Body({ mass: 1, shape: new CANNON.Sphere(0.5), position: new CANNON.Vec3(0, 5, 0) });
world.addBody(ball);
const ballMesh = new THREE.Mesh(new THREE.SphereGeometry(0.5, 24, 16), new THREE.MeshStandardMaterial());
scene.add(ballMesh);

loop.onFixed.push(() => world.step(FIXED_DT));
loop.onFrame.push(() => {
  ballMesh.position.set(ball.position.x, ball.position.y, ball.position.z);
  ballMesh.quaternion.set(ball.quaternion.x, ball.quaternion.y, ball.quaternion.z, ball.quaternion.w);
});
```

Notes/pitfalls:
- Prefer cannon-es when bundle size and simplicity win; prefer Rapier for the character controller, trimesh colliders, joints at scale, and raw speed — and `rapier3d-compat` embeds its WASM, so Vite needs zero config either way.
- `CANNON.Vec3` and `THREE.Vector3` are different classes — copy components explicitly.

## 9. Raycast picking
When: clicking/tapping objects, hover highlights, hit-scan weapons.

```ts
import * as THREE from 'three';

const raycaster = new THREE.Raycaster();
const ndc = new THREE.Vector2();
const pickables: THREE.Object3D[] = []; // curate this — NEVER raycast scene.children recursively
let hovered: THREE.Object3D | null = null;
let downId: number | null = null;

canvas.addEventListener('pointermove', (e) => {
  ndc.set((e.clientX / innerWidth) * 2 - 1, -(e.clientY / innerHeight) * 2 + 1);
  raycaster.setFromCamera(ndc, camera);
  hovered = raycaster.intersectObjects(pickables, false)[0]?.object ?? null; // false: no recursion
  canvas.style.cursor = hovered ? 'pointer' : 'default';
});
canvas.addEventListener('pointerdown', (e) => { downId = e.pointerId; });
canvas.addEventListener('pointerup', (e) => {
  if (e.pointerId !== downId) return; // pointerId guard: ignore a second finger's release
  downId = null;
  if (hovered) console.log('clicked', hovered.name);
});

// Layers filtering instead of a pickables array:
raycaster.layers.set(2);
someMesh.layers.enable(2); // stays on layer 0 for rendering AND joins layer 2 for picking
```

For large static meshes (levels, terrain), add three-mesh-bvh (`npm i three-mesh-bvh`):

```ts
import { computeBoundsTree, disposeBoundsTree, acceleratedRaycast } from 'three-mesh-bvh';
THREE.BufferGeometry.prototype.computeBoundsTree = computeBoundsTree;
THREE.BufferGeometry.prototype.disposeBoundsTree = disposeBoundsTree;
THREE.Mesh.prototype.raycast = acceleratedRaycast;
levelMesh.geometry.computeBoundsTree(); // once, after load
raycaster.firstHitOnly = true;          // big win when you only need the nearest hit
```

Notes/pitfalls:
- Raycasting the whole scene recursively is the classic frame killer — curate `pickables` or use layers.
- Skinned meshes raycast against the bind pose; accept the approximation or use BVH refit.

## 10. Touch controls: virtual joystick + look region
When: shipping to phones — left half moves, right half looks, both simultaneously. No library.

```ts
export class TouchControls {
  moveX = 0; moveY = 0; // normalized stick (magnitude <= 1) — merge with WASD/gamepad action state
  private lookDX = 0; private lookDY = 0;
  private pointers = new Map<number, { side: 'move' | 'look'; ox: number; oy: number; lx: number; ly: number }>();
  private readonly radius = 60; // joystick throw in px

  constructor(private el: HTMLElement, private nub?: HTMLElement) {
    el.addEventListener('pointerdown', this.onDown);
    el.addEventListener('pointermove', this.onMove);
    el.addEventListener('pointerup', this.onEnd);
    el.addEventListener('pointercancel', this.onEnd);
  }

  /** Read-and-clear the accumulated look delta once per frame. */
  consumeLook(): { dx: number; dy: number } {
    const out = { dx: this.lookDX, dy: this.lookDY };
    this.lookDX = this.lookDY = 0;
    return out;
  }

  private onDown = (e: PointerEvent): void => {
    if (e.pointerType !== 'touch') return;
    this.el.setPointerCapture(e.pointerId); // keep events even if the finger leaves the element
    const side = e.clientX < innerWidth / 2 ? 'move' : 'look'; // floating stick: origin = touch point
    this.pointers.set(e.pointerId, { side, ox: e.clientX, oy: e.clientY, lx: e.clientX, ly: e.clientY });
    if (side === 'move' && this.nub) this.nub.style.opacity = '1';
  };

  private onMove = (e: PointerEvent): void => {
    const p = this.pointers.get(e.pointerId);
    if (!p) return;
    if (p.side === 'move') {
      let dx = e.clientX - p.ox, dy = e.clientY - p.oy;
      const len = Math.hypot(dx, dy);
      if (len > this.radius) { dx *= this.radius / len; dy *= this.radius / len; } // clamp to ring
      this.moveX = dx / this.radius; this.moveY = dy / this.radius;
      if (this.nub) this.nub.style.transform = `translate(${p.ox + dx}px, ${p.oy + dy}px)`;
    } else {
      this.lookDX += e.clientX - p.lx; this.lookDY += e.clientY - p.ly;
      p.lx = e.clientX; p.ly = e.clientY;
    }
  };

  private onEnd = (e: PointerEvent): void => {
    const p = this.pointers.get(e.pointerId);
    if (!p) return;
    this.pointers.delete(e.pointerId);
    if (p.side === 'move') { this.moveX = this.moveY = 0; if (this.nub) this.nub.style.opacity = '0'; }
  };
}
```

Optional visual nub — add `<div id="nub"></div>` inside `#hud`:

```css
#nub { position: fixed; left: -24px; top: -24px; width: 48px; height: 48px; border-radius: 50%;
       background: rgba(255, 255, 255, 0.25); pointer-events: none; opacity: 0; }
```

Notes/pitfalls:
- `touch-action: none` on the canvas (recipe 1) is mandatory, or the browser eats pointermove for scrolling.
- The `Map<pointerId, ...>` is what lets move + look work at once — never track "the" touch.

## 11. Gamepad polling
When: controller support — sticks have no events; poll every frame.

```ts
export class GamepadInput {
  moveX = 0; moveY = 0; lookX = 0; lookY = 0;
  jumpPressed = false; firePressed = false; // true ONLY on the frame the button goes down
  private last: boolean[] = [];

  /** Call once per frame, before reading values. */
  poll(): void {
    const pad = navigator.getGamepads()[0];
    if (!pad) { this.moveX = this.moveY = this.lookX = this.lookY = 0; return; }
    const radial = (x: number, y: number): [number, number] => {
      const len = Math.hypot(x, y);
      if (len < 0.15) return [0, 0];            // radial dead zone — per-axis makes diagonals notchy
      const s = (len - 0.15) / (1 - 0.15);      // rescale so movement starts at zero
      return [(x / len) * s, (y / len) * s];
    };
    [this.moveX, this.moveY] = radial(pad.axes[0], pad.axes[1]);
    [this.lookX, this.lookY] = radial(pad.axes[2], pad.axes[3]);
    const now = pad.buttons.map((b) => b.pressed);
    this.jumpPressed = now[0] === true && this.last[0] !== true; // A / Cross — edge detection
    this.firePressed = now[7] === true && this.last[7] !== true; // RT / R2
    this.last = now;
  }
}
```

Notes/pitfalls:
- Gamepads are invisible until a button is pressed (browser privacy) — show a "press any button" hint.
- Autofire/held behavior reads `now[7]` directly instead of the edge.

## 12. Postprocessing composer (bloom done right)
When: glow on emissive materials without washing out the whole frame.

```ts
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

export function createComposer(renderer: THREE.WebGLRenderer, scene: THREE.Scene, camera: THREE.Camera) {
  const size = renderer.getSize(new THREE.Vector2());
  const target = new THREE.WebGLRenderTarget(size.x, size.y, {
    type: THREE.HalfFloatType, // HDR buffer: bloom needs values > 1.0
    samples: 4,                // MSAA inside the composer (WebGL2)
  });
  const composer = new EffectComposer(renderer, target);
  composer.addPass(new RenderPass(scene, camera));
  const bloom = new UnrealBloomPass(size, 0.6, 0.4, 0.85); // strength, radius, threshold
  composer.addPass(bloom);
  composer.addPass(new OutputPass()); // tone mapping + sRGB — ALWAYS the last pass
  return { composer, bloom };
}

// Usage — branch at init; mobile skips the composer entirely (recipe 19):
const post = isMobile ? null : createComposer(renderer, scene, camera);
bindResize(renderer, camera, post?.composer); // recipe 2 calls setSize + setPixelRatio on resize
loop.onFrame.push(() => post ? post.composer.render() : renderer.render(scene, camera));
```

Notes/pitfalls:
- KEEP `renderer.toneMapping = ACESFilmicToneMapping` set — OutputPass reads the renderer's tone mapping and output color space.
- Threshold 0.85 blooms only bright/emissive pixels; lower strength before lowering threshold. Pass pipeline depth → reference.md.

## 13. Object pool
When: anything spawned in bursts — projectiles, particles, pickups. Mid-game allocation = GC hitches.

```ts
import * as THREE from 'three';

export class Pool<T> {
  private free: T[] = [];
  private active = new Set<T>();
  constructor(private factory: () => T, private resetFn: (item: T) => void) {}
  prewarm(count: number): void { for (let i = 0; i < count; i++) this.free.push(this.factory()); }
  acquire(): T { const item = this.free.pop() ?? this.factory(); this.active.add(item); return item; }
  release(item: T): void {
    if (!this.active.delete(item)) return; // double-release guard
    this.resetFn(item);
    this.free.push(item);
  }
  /** Snapshot copy — safe to release() while iterating. */
  activeItems(): T[] { return [...this.active]; }
}

// Pooled projectiles: ONE shared geometry + material; park with visible = false.
interface Projectile { mesh: THREE.Mesh; velocity: THREE.Vector3; life: number; }
const projGeo = new THREE.SphereGeometry(0.1, 8, 6);
const projMat = new THREE.MeshBasicMaterial({ color: 0xffe066 });
const projectiles = new Pool<Projectile>(
  () => {
    const mesh = new THREE.Mesh(projGeo, projMat);
    mesh.visible = false;
    scene.add(mesh); // add ONCE; toggle visibility instead of add/remove churn
    return { mesh, velocity: new THREE.Vector3(), life: 0 };
  },
  (p) => { p.mesh.visible = false; p.velocity.set(0, 0, 0); p.life = 0; });
projectiles.prewarm(64);

export function fire(origin: THREE.Vector3, dir: THREE.Vector3): void {
  const p = projectiles.acquire();
  p.mesh.position.copy(origin);
  p.mesh.visible = true;
  p.velocity.copy(dir).multiplyScalar(30);
  p.life = 3;
}

loop.onFixed.push((dt) => {
  for (const p of projectiles.activeItems()) {
    p.life -= dt;
    if (p.life <= 0) { projectiles.release(p); continue; }
    p.mesh.position.addScaledVector(p.velocity, dt);
  }
});
```

Notes/pitfalls:
- Never clone geometry/material per projectile — share them across the pool.
- Where pools sit in the entity lifecycle → architecture.md.

## 14. Deep dispose + level teardown
When: switching levels or despawning models — three.js never frees GPU memory for you.

```ts
import * as THREE from 'three';

const TEXTURE_SLOTS = ['map', 'normalMap', 'roughnessMap', 'metalnessMap', 'aoMap',
  'emissiveMap', 'envMap', 'alphaMap', 'lightMap'] as const;

export function disposeObject3D(root: THREE.Object3D): void {
  const seen = new Set<THREE.Texture>(); // avoid double-dispose of shared textures
  root.traverse((obj) => {
    const mesh = obj as THREE.Mesh;
    if (mesh.geometry) mesh.geometry.dispose();
    const mats = Array.isArray(mesh.material) ? mesh.material : mesh.material ? [mesh.material] : [];
    for (const mat of mats) {
      for (const slot of TEXTURE_SLOTS) {
        const tex = (mat as unknown as Record<string, THREE.Texture | undefined>)[slot];
        if (tex && !seen.has(tex)) { seen.add(tex); tex.dispose(); }
      }
      mat.dispose();
    }
    if ((obj as THREE.SkinnedMesh).isSkinnedMesh) {
      (obj as THREE.SkinnedMesh).skeleton.dispose(); // frees the GPU boneTexture
    }
  });
  root.removeFromParent();
}

// Level teardown with verification — both counts should drop:
console.log('before', { ...renderer.info.memory }); // { geometries, textures }
disposeObject3D(currentLevelRoot);
console.log('after', { ...renderer.info.memory });
```

Notes/pitfalls:
- If `textures` doesn't drop, something still holds one — usually `scene.environment` or a pooled material.
- Don't dispose textures owned by the AssetManager (recipe 5) if other levels reuse them.

## 15. HUD (DOM overlay)
When: score, health, menus — DOM beats in-scene text for crispness, layout, and accessibility.

```html
<div id="hud">
  <div id="score"></div>
  <div id="damage-flash"></div>
</div>
```

```css
#hud { position: fixed; inset: 0; pointer-events: none; font-family: system-ui, sans-serif; color: #fff; }
#hud button { pointer-events: auto; } /* interactive children opt back in */
#score { position: absolute; top: 12px; left: 12px; font-size: 24px; text-shadow: 0 1px 2px #000; }
#damage-flash { position: absolute; inset: 0; background: rgba(255, 0, 0, 0.35); opacity: 0; }
#damage-flash.active { animation: flash 0.3s ease-out; }
@keyframes flash { from { opacity: 1; } to { opacity: 0; } }
```

```ts
const scoreEl = document.querySelector<HTMLDivElement>('#score')!;
const flashEl = document.querySelector<HTMLDivElement>('#damage-flash')!;

let lastScore = -1;
export function setScore(score: number): void {
  if (score === lastScore) return; // NEVER touch the DOM per frame unless the value changed
  lastScore = score;
  scoreEl.textContent = `Score: ${score}`;
}

flashEl.addEventListener('animationend', () => flashEl.classList.remove('active'));
export function damageFlash(): void {
  flashEl.classList.remove('active');
  void flashEl.offsetWidth; // force reflow so re-adding the class restarts the animation
  flashEl.classList.add('active');
}
```

Notes/pitfalls:
- `pointer-events: none` on the container is what lets input reach the canvas underneath.
- Updating `textContent` with an identical value still triggers layout — hence the change guard.

## 16. Audio setup
When: any game with sound — autoplay unlock, overlapping SFX, and 3D positional audio.

```ts
import * as THREE from 'three';

export function createAudio(camera: THREE.Camera): THREE.AudioListener {
  const listener = new THREE.AudioListener();
  camera.add(listener);
  // Browsers create the AudioContext suspended until a user gesture — resume inside one (iOS:
  // the resume() call must happen synchronously in the handler, not behind an await).
  window.addEventListener('pointerdown', () => {
    if (listener.context.state === 'suspended') void listener.context.resume();
  }, { once: true });
  return listener;
}

// One THREE.Audio can't overlap itself — rotate through a pool of instances.
const sfxPool: THREE.Audio[] = [];
export function playSfx(listener: THREE.AudioListener, buffer: AudioBuffer, volume = 1): void {
  let audio = sfxPool.find((a) => !a.isPlaying);
  if (!audio) { audio = new THREE.Audio(listener); sfxPool.push(audio); }
  audio.setBuffer(buffer);
  audio.setVolume(volume);
  audio.play();
}

// Usage with the manifest (recipe 5) + a positional emitter:
const listener = createAudio(camera);
playSfx(listener, assets.getAudio('shoot'), 0.8);
const engine = new THREE.PositionalAudio(listener);
engine.setBuffer(assets.getAudio('music'));
engine.setRefDistance(4); // full volume within 4 units, falls off beyond
engine.setLoop(true);
carMesh.add(engine);      // the sound moves with the mesh
engine.play();
```

Notes/pitfalls:
- Keep music as plain `THREE.Audio` (non-positional); only diegetic sources need `PositionalAudio`.

## 17. Stats + lil-gui debug rig
When: tuning exposure/lights/fog and watching frame cost — dev builds only. `npm i -D lil-gui`.

```ts
import type * as THREE from 'three';
import type { Loop } from './Loop'; // recipe 3

export async function initDebug(opts: { renderer: THREE.WebGLRenderer; scene: THREE.Scene;
  sun: THREE.DirectionalLight; loop: Loop }): Promise<void> {
  const enabled = import.meta.env.DEV || new URLSearchParams(location.search).has('debug');
  if (!enabled) return;
  // Dynamic imports = the tree-shake story: this ships as a lazy chunk, downloaded only when debug is on.
  const [{ default: Stats }, { GUI }] = await Promise.all([
    import('three/addons/libs/stats.module.js'),
    import('lil-gui'),
  ]);

  const stats = new Stats();
  document.body.appendChild(stats.dom);
  opts.loop.onFrame.unshift(() => stats.begin()); // first subscriber
  opts.loop.onFrame.push(() => stats.end());      // last subscriber — wraps the whole frame

  const gui = new GUI();
  gui.add(opts.renderer, 'toneMappingExposure', 0, 3, 0.01).name('exposure');
  gui.add(opts.sun, 'intensity', 0, 10, 0.1).name('sun');
  const fog = opts.scene.fog as THREE.Fog | null;
  if (fog) { gui.add(fog, 'near', 0, 100); gui.add(fog, 'far', 0, 500); }
}
```

Notes/pitfalls:
- Call `initDebug` AFTER registering the render callback so `stats.end()` lands after it.
- Static imports of Stats/GUI would ship in every production bundle — keep them dynamic.

## 18. WebXR minimal
When: adding a VR mode to an existing game.

```ts
import { VRButton } from 'three/addons/webxr/VRButton.js';

renderer.xr.enabled = true;
renderer.xr.setFramebufferScaleFactor(1.0); // lower to ~0.8 on weak headsets; set BEFORE session start
document.body.appendChild(VRButton.createButton(renderer));

// The Loop (recipe 3) already uses renderer.setAnimationLoop, so XR just works:
// while presenting, the headset drives the loop at its native refresh rate.
loop.onFrame.push(() => {
  if (renderer.xr.isPresenting) renderer.render(scene, camera); // composers break in XR — render direct
  else composer.render();
});
```

Notes/pitfalls:
- `requestAnimationFrame` does NOT fire in XR sessions — `setAnimationLoop` is mandatory.
- The headset owns the camera transform: move a parent rig `Group` for locomotion, never the camera.
- WebXR needs HTTPS (localhost exempt) — use a dev cert or adb reverse for device testing.

## 19. Mobile performance preset
When: one build serving desktop and phones — detect capability and degrade gracefully.

```ts
import * as THREE from 'three';

// Capability detection, not UA sniffing: "primary input is imprecise" ~= phone/tablet.
export const isMobile = window.matchMedia('(pointer: coarse)').matches;

export interface QualityPreset {
  maxDpr: number; shadows: boolean; shadowMapSize: number; useComposer: boolean; anisotropy: number;
}
export const DESKTOP: QualityPreset = { maxDpr: 2, shadows: true, shadowMapSize: 2048, useComposer: true, anisotropy: 8 };
export const MOBILE: QualityPreset = { maxDpr: 1.5, shadows: true, shadowMapSize: 1024, useComposer: false, anisotropy: 4 };
// If a single 1024 cascade-less map still tanks the frame rate, set shadows: false and fake a blob shadow.

export function applyQuality(preset: QualityPreset, renderer: THREE.WebGLRenderer,
  sun: THREE.DirectionalLight, colorTextures: THREE.Texture[]): void {
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, preset.maxDpr));
  renderer.shadowMap.enabled = preset.shadows;
  sun.castShadow = preset.shadows;
  sun.shadow.mapSize.setScalar(preset.shadowMapSize);
  sun.shadow.map?.dispose(); // force re-allocation at the new size
  sun.shadow.map = null;
  for (const tex of colorTextures) { tex.anisotropy = preset.anisotropy; tex.needsUpdate = true; }
}

// Usage: const preset = isMobile ? MOBILE : DESKTOP; applyQuality(preset, renderer, sun, texList);
// Then branch composer creation on preset.useComposer (recipe 12).
```

Notes/pitfalls:
- One sun + one 1024 map, no composer, DPR 1.5 is the mobile sweet spot; CSM is a desktop luxury.
- The full quality-tier decision table → architecture.md.

## 20. Production build & deploy
When: shipping to itch.io, GitHub Pages, or any static host.

```bash
npm run build      # outputs dist/
npx vite preview   # sanity-check the production build locally before uploading
```

- `base: './'` (recipe 1) makes asset URLs relative — the build runs from any subpath (itch.io iframes, `user.github.io/repo/`).
- `public/` is copied verbatim into `dist/` — verify `dist/draco/` and `dist/basis/` exist, or GLB loading dies in production only.
- Precompression: skip compression plugins — let the host serve brotli/gzip (itch.io, Netlify, Cloudflare Pages all do).

Code-split the heavy stuff so the menu paints instantly:

```ts
// main.ts — three.js and the game only download when the player clicks Play.
document.querySelector('#play')!.addEventListener('click', async () => {
  const { Game } = await import('./core/Game'); // becomes its own chunk with three inside
  new Game(document.querySelector('#game') as HTMLCanvasElement).start();
});
```

Bundle analysis — `npm i -D rollup-plugin-visualizer`, then:

```ts
// vite.config.ts
import { defineConfig } from 'vite';
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig({
  base: './',
  server: { host: true },
  plugins: [visualizer({ open: true, gzipSize: true })], // writes stats.html after build
});
```

Notes/pitfalls:
- itch.io: zip the CONTENTS of `dist/` so `index.html` sits at the ZIP ROOT, upload, tick "This file will be played in the browser".
- If the visualizer shows three.js in the entry chunk despite the dynamic import, some menu code statically imports it — hunt that down.

Structural context for these recipes lives in architecture.md; API depth in reference.md; assembled games in examples.md.
