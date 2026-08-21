# Three.js Game Development — Examples

*Four worked, runnable builds demonstrating the skill's patterns end-to-end. Loaded on demand from SKILL.md.*

All examples target Three.js r160+ (~r165) in a Vite `vanilla-ts` project: `import * as THREE from 'three'`, addons from `'three/addons/...'`, sRGB output (the default), ACESFilmic tone mapping, and `renderer.setAnimationLoop`. Every example uses a fixed-timestep accumulator with a clamped frame delta, a DPR clamp, and scratch temps in hot loops.

## Example A: "Orb Collector" — complete minimal game in one file

**What it demonstrates**

- The entire skeleton of a playable game in one file: loop, input, movement, camera, pickups, HUD, win/lose, restart.
- Fixed-timestep accumulator with `MAX_FRAME` clamp; cosmetic animation on frame time.
- Kinematic movement without a physics library (manual velocity + ground clamp).
- Smooth third-person follow camera via `THREE.MathUtils.damp`.
- Object pooling (orbs recycled, never created/destroyed at runtime); shared geometry/material.
- Reset discipline: retry restores initial state without reloading; DOM HUD updated only on change; HMR-safe dispose.

**Setup**

```bash
npm create vite@latest orb-collector -- --template vanilla-ts
cd orb-collector && npm i three && npm i -D @types/three
```

Replace `index.html` and `src/main.ts` with the files below; delete the template's `style.css` and `counter.ts`.

```html
<!-- index.html -->
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Orb Collector</title>
  <style>
    html, body { margin: 0; height: 100%; overflow: hidden; background: #000; }
    canvas { display: block; }
    #hud { position: fixed; top: 12px; left: 12px; color: #fff; font: 700 20px system-ui; }
    #gameover { position: fixed; inset: 0; display: none; flex-direction: column; align-items: center;
                justify-content: center; gap: 16px; background: rgba(0,0,0,.65); color: #fff; font: 700 28px system-ui; }
    #gameover.visible { display: flex; }
    #retry { font: 600 18px system-ui; padding: 10px 28px; cursor: pointer; }
  </style>
</head>
<body>
  <canvas id="game"></canvas>
  <div id="hud">Score: 0 | 60s</div>
  <div id="gameover"><span id="final"></span><button id="retry">Play again</button></div>
  <script type="module" src="/src/main.ts"></script>
</body>
</html>
```

```ts
// src/main.ts
import * as THREE from 'three';

// ------------------------------------------------------------------ renderer / scene
const canvas = document.querySelector<HTMLCanvasElement>('#game')!;
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)); // DPR clamp
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.toneMapping = THREE.ACESFilmicToneMapping; // sRGB output is already the default
renderer.shadowMap.enabled = true;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0b1026);
scene.fog = new THREE.Fog(0x0b1026, 25, 70);
const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 200);
camera.position.set(0, 6, 9);

scene.add(new THREE.HemisphereLight(0x99aaff, 0x223322, 0.7));
const sun = new THREE.DirectionalLight(0xffffff, 2.2);
sun.position.set(10, 16, 8);
sun.castShadow = true;
sun.shadow.camera.left = sun.shadow.camera.bottom = -30;
sun.shadow.camera.right = sun.shadow.camera.top = 30;
scene.add(sun);

const ground = new THREE.Mesh(new THREE.PlaneGeometry(120, 120),
  new THREE.MeshStandardMaterial({ color: 0x2d4f33, roughness: 1 }));
ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true; scene.add(ground);

const player = new THREE.Mesh(new THREE.CapsuleGeometry(0.4, 0.8, 4, 12),
  new THREE.MeshStandardMaterial({ color: 0x4ecdc4, roughness: 0.4 }));
player.castShadow = true; scene.add(player);

// ------------------------------------------------------------------ input
const keys = new Set<string>(); // poll by physical key code, layout-independent
window.addEventListener('keydown', (e) => keys.add(e.code));
window.addEventListener('keyup', (e) => keys.delete(e.code));

// ------------------------------------------------------------------ orb pool (shared geo/mat)
const ARENA = 28, ORB_COUNT = 12;
const orbGeometry = new THREE.SphereGeometry(0.35, 16, 12);
const orbMaterial = new THREE.MeshStandardMaterial({ color: 0xffc94d, emissive: 0xff9500, emissiveIntensity: 1.8 });
interface Orb { mesh: THREE.Mesh; phase: number }
const orbs: Orb[] = [];
for (let i = 0; i < ORB_COUNT; i++) {
  const mesh = new THREE.Mesh(orbGeometry, orbMaterial);
  scene.add(mesh);
  orbs.push({ mesh, phase: Math.random() * Math.PI * 2 });
}
function respawnOrb(orb: Orb): void {
  orb.mesh.position.set((Math.random() * 2 - 1) * ARENA, 0.6, (Math.random() * 2 - 1) * ARENA);
}

// ------------------------------------------------------------------ state / HUD
const state = { score: 0, timeLeft: 60, playing: true };
const velocity = new THREE.Vector3();
const hud = document.querySelector<HTMLDivElement>('#hud')!;
const overlay = document.querySelector<HTMLDivElement>('#gameover')!;
const finalText = document.querySelector<HTMLSpanElement>('#final')!;
let hudScore = -1, hudTime = -1;
function refreshHud(): void { // touch the DOM only when a displayed value changes
  const t = Math.max(0, Math.ceil(state.timeLeft));
  if (state.score === hudScore && t === hudTime) return;
  hudScore = state.score; hudTime = t;
  hud.textContent = `Score: ${hudScore} | ${hudTime}s`;
}
function resetGame(): void { // reset discipline: restore initial state, never reload
  state.score = 0; state.timeLeft = 60; state.playing = true;
  velocity.set(0, 0, 0); player.position.set(0, 0.8, 0);
  orbs.forEach(respawnOrb);
  overlay.classList.remove('visible');
  refreshHud();
}
document.querySelector('#retry')!.addEventListener('click', resetGame);
function endGame(): void {
  state.playing = false;
  finalText.textContent = `Time! Final score: ${state.score}`;
  overlay.classList.add('visible');
}

// ------------------------------------------------------------------ simulation (fixed step)
const SPEED = 9, PICKUP_SQ = 1.25 * 1.25;
const inputDir = new THREE.Vector3(), camTarget = new THREE.Vector3(); // scratch temps: no allocation in loop
function fixedUpdate(dt: number): void {
  if (!state.playing) return;
  state.timeLeft -= dt;
  if (state.timeLeft <= 0) { endGame(); return; }
  inputDir.set(Number(keys.has('KeyD')) - Number(keys.has('KeyA')), 0,
    Number(keys.has('KeyS')) - Number(keys.has('KeyW')));
  if (inputDir.lengthSq() > 0) inputDir.normalize();
  velocity.x = THREE.MathUtils.damp(velocity.x, inputDir.x * SPEED, 10, dt);
  velocity.z = THREE.MathUtils.damp(velocity.z, inputDir.z * SPEED, 10, dt);
  player.position.addScaledVector(velocity, dt);
  player.position.x = THREE.MathUtils.clamp(player.position.x, -ARENA, ARENA);
  player.position.z = THREE.MathUtils.clamp(player.position.z, -ARENA, ARENA);
  player.position.y = 0.8; // manual ground clamp — no physics engine needed here
  for (const orb of orbs) {
    if (orb.mesh.position.distanceToSquared(player.position) < PICKUP_SQ) {
      state.score += 1;
      respawnOrb(orb); // pool: recycle in place, never dispose/recreate
    }
  }
}

// ------------------------------------------------------------------ presentation (frame time)
function present(frameDt: number, elapsed: number): void {
  camTarget.set(player.position.x, player.position.y + 5, player.position.z + 8);
  camera.position.x = THREE.MathUtils.damp(camera.position.x, camTarget.x, 3.5, frameDt);
  camera.position.y = THREE.MathUtils.damp(camera.position.y, camTarget.y, 3.5, frameDt);
  camera.position.z = THREE.MathUtils.damp(camera.position.z, camTarget.z, 3.5, frameDt);
  camera.lookAt(player.position.x, 1, player.position.z);
  for (const orb of orbs) { // cosmetic bob/spin runs on frame time, not fixed time
    orb.mesh.position.y = 0.6 + Math.sin(elapsed * 2.5 + orb.phase) * 0.18;
    orb.mesh.rotation.y = elapsed + orb.phase;
  }
  refreshHud();
}

// ------------------------------------------------------------------ loop
const FIXED_DT = 1 / 60, MAX_FRAME = 0.25; // clamp tab-switch/GC hitches: no spiral of death
let last = performance.now() / 1000, accumulator = 0;
renderer.setAnimationLoop(() => {
  const now = performance.now() / 1000;
  const frameDt = Math.min(now - last, MAX_FRAME);
  last = now; accumulator += frameDt;
  while (accumulator >= FIXED_DT) { fixedUpdate(FIXED_DT); accumulator -= FIXED_DT; }
  present(frameDt, now);
  renderer.render(scene, camera);
});
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
if (import.meta.hot) { // dispose on Vite HMR so dev reloads don't leak GPU memory
  import.meta.hot.dispose(() => {
    renderer.setAnimationLoop(null);
    orbGeometry.dispose(); orbMaterial.dispose(); renderer.dispose();
  });
}
resetGame();
```

**Why it's built this way**

- The fixed-timestep accumulator with `MAX_FRAME` clamp (architecture.md: "the game loop") keeps gameplay identical at 30/60/144 Hz; camera easing and orb bobbing live in the presentation phase on frame time (architecture.md: "simulation/presentation split").
- Orbs never leave the scene graph — collection teleports them (recipes.md: "object pooling"); with shared geometry/material, runtime allocation and dispose churn are both zero, so the only dispose site is teardown.
- `MathUtils.damp` for velocity and camera is framerate-independent smoothing (recipes.md: "damp, don't lerp by constant") — a raw `lerp(a, b, 0.1)` per frame feels different at every refresh rate.
- Score/time render through a DOM overlay behind a dirty check (recipes.md: "HUD via DOM, update on change") — cheaper and crisper than in-canvas text.
- `resetGame()` is the single authority for initial state, called at boot and on retry (architecture.md: "reset discipline") — restart bugs come from state that only page-load ever initialized.

**Extension ideas**

- Add a dash on Shift with a cooldown bar (second DOM element, dirty-flag updated).
- Give orbs point tiers by color, one shared material per tier.
- Persist a best score in `localStorage` and show it on the game-over overlay.

## Example B: Animated glTF character with a crossfade state machine

> **Asset assumption** — expects `public/models/character.glb`: a skinned character whose animation clips are named exactly `Idle`, `Run`, and `Jump`. Any Mixamo-style humanoid rig works — bake idle/run/jump onto one skeleton, rename the clips, export as `.glb`. Producing and optimizing that file is the job of the **game-assets-pipeline** skill; route export questions there. Copy the Draco decoder into `public/draco/` (see Setup) even for uncompressed models — the wired loader stack then handles compressed ones for free.

**What it demonstrates**

- A loader stack: `GLTFLoader` + `DRACOLoader` pointed at a locally hosted decoder, disposed after loading.
- An `AnimationController`: actions map, crossfade transitions, one-shot `Jump` returning to locomotion via the mixer's `finished` event.
- Facing the movement direction with damped quaternion slerp; movement speed driving the Idle/Run threshold.
- `SkeletonUtils.clone` spawning 3 NPCs with independent mixers, wandering on timers (plain `.clone()` breaks skinned meshes).
- Mixers advanced in the presentation phase; `castShadow` enabled by traversal.

**Setup**

```bash
npm create vite@latest character-demo -- --template vanilla-ts
cd character-demo && npm i three && npm i -D @types/three
cp -r node_modules/three/examples/jsm/libs/draco/ public/draco/
# place character.glb at public/models/character.glb
```

Vite's dev server and default build target both support the top-level `await` used below.

```ts
// src/main.ts
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import * as SkeletonUtils from 'three/addons/utils/SkeletonUtils.js';

// ------------------------------------------------------------------ renderer / scene
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)); // DPR clamp
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.shadowMap.enabled = true;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x202533);
scene.fog = new THREE.Fog(0x202533, 20, 60);
const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(0, 4, 8); camera.lookAt(0, 1, 0);
scene.add(new THREE.HemisphereLight(0xbcd4ff, 0x3a3325, 0.8));
const sun = new THREE.DirectionalLight(0xffffff, 2);
sun.position.set(6, 12, 4); sun.castShadow = true; scene.add(sun);
const ground = new THREE.Mesh(new THREE.CircleGeometry(30, 48),
  new THREE.MeshStandardMaterial({ color: 0x39424e, roughness: 1 }));
ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true; scene.add(ground);

const keys = new Set<string>();
window.addEventListener('keydown', (e) => keys.add(e.code));
window.addEventListener('keyup', (e) => keys.delete(e.code));

// ------------------------------------------------------------------ crossfade state machine
class AnimationController {
  readonly mixer: THREE.AnimationMixer;
  private actions = new Map<string, THREE.AnimationAction>();
  private current: THREE.AnimationAction | null = null;
  private locomotion = 'Idle';
  private oneShotActive = false;

  constructor(root: THREE.Object3D, clips: THREE.AnimationClip[]) {
    this.mixer = new THREE.AnimationMixer(root);
    for (const clip of clips) this.actions.set(clip.name, this.mixer.clipAction(clip));
    this.mixer.addEventListener('finished', () => { // only LoopOnce actions fire this
      this.oneShotActive = false;
      this.crossfadeTo(this.locomotion, 0.2);
    });
  }

  /** Desired looping state (Idle/Run); deferred while a one-shot plays. */
  setLocomotion(name: string, fade = 0.25): void {
    this.locomotion = name;
    if (!this.oneShotActive) this.crossfadeTo(name, fade);
  }

  /** Play Jump (etc.) once, then fall back to the current locomotion. */
  playOneShot(name: string, fade = 0.1): void {
    const action = this.actions.get(name);
    if (!action || this.oneShotActive) return;
    action.setLoop(THREE.LoopOnce, 1);
    action.clampWhenFinished = true; // hold last frame during the fade back
    this.oneShotActive = true;
    this.crossfadeTo(name, fade);
  }

  private crossfadeTo(name: string, fade: number): void {
    const next = this.actions.get(name);
    if (!next || next === this.current) return;
    next.reset().fadeIn(fade).play();
    this.current?.fadeOut(fade);
    this.current = next;
  }

  update(dt: number): void { this.mixer.update(dt); }
}

// ------------------------------------------------------------------ loading + NPC clones
const draco = new DRACOLoader();
draco.setDecoderPath('/draco/');
const loader = new GLTFLoader();
loader.setDRACOLoader(draco);
const gltf = await loader.loadAsync('/models/character.glb');
draco.dispose(); // all loads done — free the decoder workers
gltf.scene.traverse((o) => { if ((o as THREE.Mesh).isMesh) o.castShadow = true; });
scene.add(gltf.scene);
const playerRoot = gltf.scene;
const playerAnim = new AnimationController(playerRoot, gltf.animations);
playerAnim.setLocomotion('Idle');

interface Npc { root: THREE.Object3D; anim: AnimationController; heading: number; nextDecision: number; moving: boolean }
const npcs: Npc[] = [];
for (let i = 0; i < 3; i++) {
  const root = SkeletonUtils.clone(playerRoot); // rebinds skeletons — plain .clone() breaks skinning
  root.position.set(Math.cos(i * 2.1) * 5, 0, Math.sin(i * 2.1) * 5);
  root.traverse((o) => { if ((o as THREE.Mesh).isMesh) o.castShadow = true; });
  scene.add(root);
  const anim = new AnimationController(root, gltf.animations); // independent mixer per clone
  anim.setLocomotion('Idle');
  npcs.push({ root, anim, heading: Math.random() * Math.PI * 2, nextDecision: 1 + i, moving: false });
}

window.addEventListener('keydown', (e) => { // edge event: fires once per press
  if (e.code === 'Space' && !e.repeat) playerAnim.playOneShot('Jump');
});

// ------------------------------------------------------------------ simulation
const UP = new THREE.Vector3(0, 1, 0);
const inputDir = new THREE.Vector3(), targetQuat = new THREE.Quaternion(); // scratch temps
const PLAYER_SPEED = 4, NPC_SPEED = 1.6;
let elapsed = 0;

function fixedUpdate(dt: number): void {
  elapsed += dt;
  inputDir.set(Number(keys.has('KeyD')) - Number(keys.has('KeyA')), 0,
    Number(keys.has('KeyS')) - Number(keys.has('KeyW')));
  const moving = inputDir.lengthSq() > 0;
  if (moving) {
    inputDir.normalize();
    targetQuat.setFromAxisAngle(UP, Math.atan2(inputDir.x, inputDir.z));
    playerRoot.quaternion.slerp(targetQuat, 1 - Math.exp(-12 * dt)); // damped slerp toward heading
    playerRoot.position.addScaledVector(inputDir, PLAYER_SPEED * dt);
    playerRoot.position.clampLength(0, 13); // stay on the platter
  }
  playerAnim.setLocomotion(moving ? 'Run' : 'Idle'); // speed threshold drives the state

  for (const npc of npcs) { // wander on timers
    if (elapsed >= npc.nextDecision) {
      npc.moving = Math.random() < 0.7;
      npc.heading = Math.random() * Math.PI * 2;
      npc.nextDecision = elapsed + 1.5 + Math.random() * 2.5;
      npc.anim.setLocomotion(npc.moving ? 'Run' : 'Idle');
    }
    if (!npc.moving) continue;
    if (npc.root.position.lengthSq() > 144) { // steer back toward center
      npc.heading = Math.atan2(-npc.root.position.x, -npc.root.position.z);
    }
    targetQuat.setFromAxisAngle(UP, npc.heading);
    npc.root.quaternion.slerp(targetQuat, 1 - Math.exp(-8 * dt));
    npc.root.position.x += Math.sin(npc.heading) * NPC_SPEED * dt;
    npc.root.position.z += Math.cos(npc.heading) * NPC_SPEED * dt;
  }
}

// ------------------------------------------------------------------ loop
const FIXED_DT = 1 / 60, MAX_FRAME = 0.25;
let last = performance.now() / 1000, accumulator = 0;
renderer.setAnimationLoop(() => {
  const now = performance.now() / 1000;
  const frameDt = Math.min(now - last, MAX_FRAME);
  last = now; accumulator += frameDt;
  while (accumulator >= FIXED_DT) { fixedUpdate(FIXED_DT); accumulator -= FIXED_DT; }
  playerAnim.update(frameDt); // mixers advance on frame time: presentation phase
  for (const npc of npcs) npc.anim.update(frameDt);
  renderer.render(scene, camera);
});
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
```

**Why it's built this way**

- `AnimationController` is the crossfade state machine from recipes.md ("animation crossfade state machine"): one owner of `current`, all transitions through `crossfadeTo`, one-shots resolved by the mixer's `finished` event instead of hand-rolled timers.
- Locomotion state is derived from movement each tick (`moving ? 'Run' : 'Idle'`), never set from input handlers — the recipes.md "state follows simulation" rule that prevents animation/movement drift.
- NPCs use `SkeletonUtils.clone` (recipes.md: "cloning skinned meshes") because skinned meshes share bone references that `Object3D.clone()` corrupts; each clone's own mixer keeps animations out of phase.
- Mixer updates take the raw frame delta in the presentation phase — animation is cosmetic and should match the display, while movement stays deterministic in `fixedUpdate` (architecture.md: "simulation/presentation split").
- The Draco decoder is hosted from `public/draco/` and disposed after loading — the recipes.md "loader stack" pattern avoids CDN coupling and frees the decoder workers.

**Extension ideas**

- Add a `Walk` clip and blend Idle/Walk/Run by continuous speed with `setEffectiveWeight`.
- Give the jump real vertical motion (kinematic arc in `fixedUpdate`) synced to the clip length.
- Route NPC wandering through a tiny utility-AI scorer (wander / follow / flee).

## Example C: Rapier physics playground

**What it demonstrates**

- `@dimforge/rapier3d-compat` init and a `World` stepped inside the fixed-timestep accumulator.
- 125 dynamic boxes rendered as one `InstancedMesh`, synced from body poses via `setMatrixAt`.
- Click-to-shoot: camera raycast for aim, pooled projectile bodies re-fired with `setLinvel`.
- Contact-force events filtered by magnitude for impact feedback (sound stub).
- Rapier debug-render lines toggled with `P`, with grow-only `BufferAttribute` reuse.
- Honest render interpolation: projectiles lerp prev/curr poses by the accumulator alpha; the box stack is synced raw (stated simplification).

**Setup**

```bash
npm create vite@latest rapier-playground -- --template vanilla-ts
cd rapier-playground && npm i three @dimforge/rapier3d-compat && npm i -D @types/three
```

The `-compat` build inlines the WASM, so no bundler config is needed. Replace `src/main.ts`; reuse Example A's `index.html` shell without the HUD elements.

```ts
// src/main.ts
import * as THREE from 'three';
import RAPIER from '@dimforge/rapier3d-compat';

await RAPIER.init(); // WASM load — must finish before creating any world/body

// ------------------------------------------------------------------ renderer / scene
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)); // DPR clamp
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.shadowMap.enabled = true;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x11151c);
const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 200);
camera.position.set(12, 9, 16); camera.lookAt(0, 2, 0);
scene.add(new THREE.HemisphereLight(0xaabbff, 0x332211, 0.6));
const sun = new THREE.DirectionalLight(0xffffff, 2);
sun.position.set(10, 20, 6); sun.castShadow = true;
sun.shadow.camera.left = sun.shadow.camera.bottom = -25;
sun.shadow.camera.right = sun.shadow.camera.top = 25;
scene.add(sun);
const groundMesh = new THREE.Mesh(new THREE.BoxGeometry(40, 1, 40),
  new THREE.MeshStandardMaterial({ color: 0x3d4653, roughness: 1 }));
groundMesh.position.y = -0.5; groundMesh.receiveShadow = true; scene.add(groundMesh);

// ------------------------------------------------------------------ physics world
const FIXED_DT = 1 / 60;
const world = new RAPIER.World({ x: 0, y: -9.81, z: 0 });
world.timestep = FIXED_DT; // Rapier's step must equal the accumulator step
const eventQueue = new RAPIER.EventQueue(true);

world.createCollider(RAPIER.ColliderDesc.cuboid(20, 0.5, 20).setTranslation(0, -0.5, 0)); // static ground
for (const [x, z] of [[20.5, 0], [-20.5, 0], [0, 20.5], [0, -20.5]] as const) { // invisible walls
  world.createCollider(RAPIER.ColliderDesc.cuboid(x !== 0 ? 0.5 : 20, 4, z !== 0 ? 0.5 : 20).setTranslation(x, 4, z));
}

// ------------------------------------------------------------------ 5x5x5 stack: one InstancedMesh, 125 bodies
const N = 5, BOX = 0.9, COUNT = N * N * N;
const boxes = new THREE.InstancedMesh(new THREE.BoxGeometry(BOX, BOX, BOX),
  new THREE.MeshStandardMaterial({ color: 0xd98f4e, roughness: 0.7 }), COUNT);
boxes.castShadow = boxes.receiveShadow = true;
boxes.instanceMatrix.setUsage(THREE.DynamicDrawUsage); // rewritten every frame
scene.add(boxes);
const boxBodies: RAPIER.RigidBody[] = [];
for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) for (let z = 0; z < N; z++) {
  const body = world.createRigidBody(RAPIER.RigidBodyDesc.dynamic()
    .setTranslation((x - 2) * (BOX + 0.02), BOX / 2 + y * (BOX + 0.02), (z - 2) * (BOX + 0.02)));
  world.createCollider(RAPIER.ColliderDesc.cuboid(BOX / 2, BOX / 2, BOX / 2), body);
  boxBodies.push(body);
}

// ------------------------------------------------------------------ pooled projectiles (interpolated)
const SHOT_COUNT = 20, SHOT_SPEED = 28;
const shotGeometry = new THREE.SphereGeometry(0.35, 16, 12); // shared geo/mat across the pool
const shotMaterial = new THREE.MeshStandardMaterial({ color: 0x66ddff, emissive: 0x2288cc, emissiveIntensity: 1.2 });
interface Shot { mesh: THREE.Mesh; body: RAPIER.RigidBody; prev: THREE.Vector3; curr: THREE.Vector3 }
const shots: Shot[] = [];
for (let i = 0; i < SHOT_COUNT; i++) {
  const mesh = new THREE.Mesh(shotGeometry, shotMaterial);
  mesh.castShadow = true; mesh.visible = false; scene.add(mesh);
  const body = world.createRigidBody(RAPIER.RigidBodyDesc.dynamic().setTranslation(0, -50 - i * 2, 0));
  body.sleep(); // parked far below the arena until fired
  const collider = world.createCollider(RAPIER.ColliderDesc.ball(0.35).setDensity(4).setRestitution(0.4), body);
  collider.setActiveEvents(RAPIER.ActiveEvents.CONTACT_FORCE_EVENTS); // opt in to impact events
  shots.push({ mesh, body, prev: new THREE.Vector3(), curr: new THREE.Vector3() });
}
let nextShot = 0;

const raycaster = new THREE.Raycaster(), ndc = new THREE.Vector2(), spawnPos = new THREE.Vector3();
window.addEventListener('pointerdown', (e) => {
  ndc.set((e.clientX / window.innerWidth) * 2 - 1, -(e.clientY / window.innerHeight) * 2 + 1);
  raycaster.setFromCamera(ndc, camera); // aim ray from camera through the cursor
  const dir = raycaster.ray.direction;
  spawnPos.copy(raycaster.ray.origin).addScaledVector(dir, 1.2);
  const shot = shots[nextShot]; nextShot = (nextShot + 1) % SHOT_COUNT; // round-robin pool
  shot.body.setTranslation({ x: spawnPos.x, y: spawnPos.y, z: spawnPos.z }, true);
  shot.body.setLinvel({ x: dir.x * SHOT_SPEED, y: dir.y * SHOT_SPEED, z: dir.z * SHOT_SPEED }, true);
  shot.body.setAngvel({ x: 0, y: 0, z: 0 }, true);
  shot.prev.copy(spawnPos); shot.curr.copy(spawnPos); shot.mesh.visible = true;
});

const IMPACT_THRESHOLD = 800;
function onStrongImpact(force: number): void {
  // Sound stub: swap for a pooled WebAudio buffer source in a real game.
  console.log(`%cCLUNK  force=${force.toFixed(0)}`, 'color:#f80;font-weight:bold');
}

// ------------------------------------------------------------------ debug render toggle ('P')
let debugEnabled = false;
const debugLines = new THREE.LineSegments(new THREE.BufferGeometry(),
  new THREE.LineBasicMaterial({ vertexColors: true }));
debugLines.frustumCulled = false; debugLines.visible = false; scene.add(debugLines);
window.addEventListener('keydown', (e) => {
  if (e.code === 'KeyP') { debugEnabled = !debugEnabled; debugLines.visible = debugEnabled; }
});
function updateDebugLines(): void {
  const { vertices, colors } = world.debugRender(); // Rapier allocates these — debug-only cost
  const geo = debugLines.geometry;
  let pos = geo.getAttribute('position') as THREE.BufferAttribute | undefined;
  if (!pos || (pos.array as Float32Array).length < vertices.length) { // grow-only buffer reuse
    geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(vertices.length), 3));
    geo.setAttribute('color', new THREE.BufferAttribute(new Float32Array(colors.length), 4));
    pos = geo.getAttribute('position') as THREE.BufferAttribute;
  }
  const col = geo.getAttribute('color') as THREE.BufferAttribute;
  (pos.array as Float32Array).set(vertices); (col.array as Float32Array).set(colors);
  pos.needsUpdate = true; col.needsUpdate = true;
  geo.setDrawRange(0, vertices.length / 3);
}

// ------------------------------------------------------------------ sync + loop
const tmpMat = new THREE.Matrix4(), tmpPos = new THREE.Vector3();
const tmpQuat = new THREE.Quaternion(), unitScale = new THREE.Vector3(1, 1, 1); // scratch temps
function syncBoxes(): void {
  for (let i = 0; i < COUNT; i++) {
    const t = boxBodies[i].translation(), r = boxBodies[i].rotation();
    tmpMat.compose(tmpPos.set(t.x, t.y, t.z), tmpQuat.set(r.x, r.y, r.z, r.w), unitScale);
    boxes.setMatrixAt(i, tmpMat);
  }
  boxes.instanceMatrix.needsUpdate = true;
}
function fixedStep(): void {
  for (const s of shots) s.prev.copy(s.curr); // snapshot poses before stepping
  world.step(eventQueue);
  for (const s of shots) { const t = s.body.translation(); s.curr.set(t.x, t.y, t.z); }
  eventQueue.drainContactForceEvents((event) => { // impulse-magnitude filter
    const force = event.maxForceMagnitude();
    if (force > IMPACT_THRESHOLD) onStrongImpact(force);
  });
}

const MAX_FRAME = 0.25;
let last = performance.now() / 1000, accumulator = 0;
renderer.setAnimationLoop(() => {
  const now = performance.now() / 1000;
  const frameDt = Math.min(now - last, MAX_FRAME);
  last = now; accumulator += frameDt;
  while (accumulator >= FIXED_DT) { fixedStep(); accumulator -= FIXED_DT; }
  const alpha = accumulator / FIXED_DT;
  // Interpolation choice, stated honestly: fast player-visible projectiles lerp between the
  // last two physics poses so they never stutter; the box stack settles within seconds and
  // moves slowly, so it is synced at the raw fixed-step pose. Spheres are rotation-symmetric,
  // so skipping their rotation sync is also free.
  for (const s of shots) if (s.mesh.visible) s.mesh.position.lerpVectors(s.prev, s.curr, alpha);
  syncBoxes();
  if (debugEnabled) updateDebugLines();
  renderer.render(scene, camera);
});
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
```

**Why it's built this way**

- `world.timestep` equals the accumulator's `FIXED_DT` and `world.step` runs only inside the `while` drain — the architecture.md "physics owns the fixed step" rule; stepping with a variable delta makes stacks explode nondeterministically.
- One `InstancedMesh` for 125 boxes is one draw call regardless of pile chaos (recipes.md: "InstancedMesh body sync"); bodies are the source of truth, synced one way into pure-presentation matrices.
- Projectiles come from a round-robin pool of parked, sleeping bodies (recipes.md: "object pooling") — creating/removing Rapier bodies at fire rate would thrash the broadphase and the GC.
- Contact-force events with a magnitude threshold (recipes.md: "collision events via EventQueue") react only to meaningful hits, not micro-contacts while the stack settles.
- The prev/curr + alpha lerp is render interpolation from architecture.md ("fixed steps, smooth rendering"), applied only where players can perceive stutter — the documented simplification.

**Extension ideas**

- Add a `RAPIER.KinematicCharacterController` walking through the rubble.
- Color instances by speed with `setColorAt` + `instanceColor.needsUpdate` for a heatmap.
- Replace the console stub with pooled WebAudio buffers, pitch-randomized by impact force.

## Example D: Mobile endless-runner skeleton

**What it demonstrates**

- Three-lane auto-runner where the world moves toward a stationary player — coordinates stay near the origin, avoiding float32 precision jitter on long runs.
- Swipe input via pointer events (pointerdown/pointerup deltaX threshold) plus A/D keys; `touch-action: none`.
- Lane changes eased with `MathUtils.damp`; obstacle pool with a time-based difficulty ramp.
- AABB-ish distance collision, game-over overlay, reset without reload.
- Mobile preset chosen once at boot from a coarse-pointer media query: DPR cap 1.5, no shadows, cheaper material.
- `visibilitychange` pause and a HUD distance counter updated only on integer change.

**Setup**

```bash
npm create vite@latest lane-runner -- --template vanilla-ts
cd lane-runner && npm i three && npm i -D @types/three
```

```html
<!-- index.html -->
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <title>Lane Runner</title>
  <style>
    html, body { margin: 0; height: 100%; overflow: hidden; background: #000; }
    canvas { display: block; touch-action: none; } /* browser must not steal swipes */
    #hud { position: fixed; top: max(12px, env(safe-area-inset-top)); left: 12px;
           color: #fff; font: 700 22px system-ui; }
    #gameover { position: fixed; inset: 0; display: none; flex-direction: column; align-items: center;
                justify-content: center; gap: 16px; background: rgba(0,0,0,.65); color: #fff; font: 700 26px system-ui; }
    #gameover.visible { display: flex; }
    #retry { font: 600 18px system-ui; padding: 12px 32px; cursor: pointer; }
  </style>
</head>
<body>
  <div id="hud">0 m</div>
  <div id="gameover"><span id="final"></span><button id="retry">Run again</button></div>
  <script type="module" src="/src/main.ts"></script>
</body>
</html>
```

```ts
// src/main.ts
import * as THREE from 'three';

// ------------------------------------------------------------------ mobile preset (chosen once at boot)
const isCoarse = window.matchMedia('(pointer: coarse)').matches;
const preset = { maxDpr: isCoarse ? 1.5 : 2, shadows: !isCoarse };
const matFor = (color: number): THREE.Material => isCoarse
  ? new THREE.MeshLambertMaterial({ color })                   // cheap per-vertex lighting
  : new THREE.MeshStandardMaterial({ color, roughness: 0.8 }); // PBR on desktop

const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, preset.maxDpr)); // DPR clamp per tier
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.shadowMap.enabled = preset.shadows;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x1a1030);
scene.fog = new THREE.Fog(0x1a1030, 30, 90);
const camera = new THREE.PerspectiveCamera(65, window.innerWidth / window.innerHeight, 0.1, 150);
camera.position.set(0, 5, 8); camera.lookAt(0, 1, -10);
scene.add(new THREE.HemisphereLight(0x7788ff, 0x221133, 1.2));
const sun = new THREE.DirectionalLight(0xffffff, 1.6);
sun.position.set(4, 10, 4); sun.castShadow = preset.shadows; scene.add(sun);

// The PLAYER stays at z=0 forever and the WORLD flows toward +z. On an "infinite" run,
// moving the player forward pushes coordinates past float32 precision (visible jitter
// beyond ~10k units); moving the world keeps everything near the origin.
const LANES = [-2.2, 0, 2.2];
const ground = new THREE.Mesh(new THREE.PlaneGeometry(12, 160), matFor(0x2b2140));
ground.rotation.x = -Math.PI / 2; ground.position.z = -60;
ground.receiveShadow = preset.shadows; scene.add(ground);

const stripeGeometry = new THREE.PlaneGeometry(0.25, 3); // scrolling stripes sell the speed
const stripeMaterial = new THREE.MeshBasicMaterial({ color: 0x6650a8 });
const stripes: THREE.Mesh[] = [];
for (let i = 0; i < 24; i++) {
  const s = new THREE.Mesh(stripeGeometry, stripeMaterial);
  s.rotation.x = -Math.PI / 2;
  s.position.set(i % 2 === 0 ? -1.1 : 1.1, 0.01, -(i >> 1) * 10);
  stripes.push(s); scene.add(s);
}

const player = new THREE.Mesh(new THREE.BoxGeometry(0.9, 1.4, 0.9), matFor(0x4ecdc4));
player.position.set(0, 0.7, 0); player.castShadow = preset.shadows; scene.add(player);

// ------------------------------------------------------------------ obstacle pool
const OBSTACLE_COUNT = 10, SPAWN_Z = -80, KILL_Z = 6;
interface Obstacle { mesh: THREE.Mesh; active: boolean }
const obstacleGeometry = new THREE.BoxGeometry(1.6, 1.6, 1.6); // shared geo/mat
const obstacleMaterial = matFor(0xe84855);
const obstacles: Obstacle[] = [];
for (let i = 0; i < OBSTACLE_COUNT; i++) {
  const mesh = new THREE.Mesh(obstacleGeometry, obstacleMaterial);
  mesh.visible = false; mesh.castShadow = preset.shadows; scene.add(mesh);
  obstacles.push({ mesh, active: false });
}
function spawnObstacle(): void {
  const slot = obstacles.find((o) => !o.active);
  if (!slot) return; // pool exhausted this instant — skip, never allocate
  slot.active = true; slot.mesh.visible = true;
  slot.mesh.position.set(LANES[Math.floor(Math.random() * 3)], 0.8, SPAWN_Z);
}

// ------------------------------------------------------------------ input: swipe + keys
let lane = 1, downX = 0, downId = -1;
const SWIPE_PX = 40;
window.addEventListener('pointerdown', (e) => { downX = e.clientX; downId = e.pointerId; });
window.addEventListener('pointerup', (e) => {
  if (e.pointerId !== downId) return;
  const dx = e.clientX - downX; // release vs press: one lane step per swipe gesture
  if (Math.abs(dx) >= SWIPE_PX) lane = THREE.MathUtils.clamp(lane + Math.sign(dx), 0, 2);
});
window.addEventListener('keydown', (e) => {
  if (e.code === 'KeyA') lane = Math.max(0, lane - 1);
  if (e.code === 'KeyD') lane = Math.min(2, lane + 1);
});

// ------------------------------------------------------------------ state / HUD
const state = { running: true, elapsed: 0, distance: 0, spawnTimer: 0.5 };
const hud = document.querySelector<HTMLDivElement>('#hud')!;
const overlay = document.querySelector<HTMLDivElement>('#gameover')!;
const finalText = document.querySelector<HTMLSpanElement>('#final')!;
let hudDistance = -1;
function refreshHud(): void { // DOM write only when the integer meter count changes
  const d = Math.floor(state.distance);
  if (d !== hudDistance) { hudDistance = d; hud.textContent = `${d} m`; }
}
function resetGame(): void { // reset discipline: full state restore, no reload
  state.running = true; state.elapsed = 0; state.distance = 0; state.spawnTimer = 0.5;
  lane = 1; player.position.x = 0; player.rotation.z = 0;
  for (const o of obstacles) { o.active = false; o.mesh.visible = false; }
  overlay.classList.remove('visible');
  refreshHud();
}
document.querySelector('#retry')!.addEventListener('click', resetGame);
function gameOver(): void {
  state.running = false;
  finalText.textContent = `Wipeout at ${Math.floor(state.distance)} m`;
  overlay.classList.add('visible');
}

// ------------------------------------------------------------------ simulation
const BASE_SPEED = 10, RAMP = 0.25, MAX_SPEED = 26;
function fixedUpdate(dt: number): void {
  if (!state.running) return;
  state.elapsed += dt;
  const speed = Math.min(BASE_SPEED + state.elapsed * RAMP, MAX_SPEED); // difficulty ramp
  state.distance += speed * dt;
  state.spawnTimer -= dt;
  if (state.spawnTimer <= 0) {
    spawnObstacle();
    state.spawnTimer = Math.max(0.45, 1.4 - state.elapsed * 0.02); // spawn faster over time
  }
  for (const o of obstacles) {
    if (!o.active) continue;
    o.mesh.position.z += speed * dt; // the world moves; the player never does
    if (o.mesh.position.z > KILL_Z) { o.active = false; o.mesh.visible = false; continue; }
    // AABB-ish check: overlapping in z and near enough in x. Uses the eased player x, so a
    // half-finished lane change can still clip a corner — intentional fairness.
    if (Math.abs(o.mesh.position.z - player.position.z) < 1.2 &&
        Math.abs(o.mesh.position.x - player.position.x) < 1.1) { gameOver(); return; }
  }
  for (const s of stripes) { // wrap stripes for a continuous speed cue
    s.position.z += speed * dt;
    if (s.position.z > 5) s.position.z -= 120;
  }
}

// ------------------------------------------------------------------ loop
const FIXED_DT = 1 / 60, MAX_FRAME = 0.25;
let last = performance.now() / 1000, accumulator = 0, paused = false;
renderer.setAnimationLoop(() => {
  if (paused) return;
  const now = performance.now() / 1000;
  const frameDt = Math.min(now - last, MAX_FRAME);
  last = now; accumulator += frameDt;
  while (accumulator >= FIXED_DT) { fixedUpdate(FIXED_DT); accumulator -= FIXED_DT; }
  // eased lane change + lean are cosmetic: presentation phase, frame dt
  player.position.x = THREE.MathUtils.damp(player.position.x, LANES[lane], 10, frameDt);
  player.rotation.z = THREE.MathUtils.damp(player.rotation.z, (LANES[lane] - player.position.x) * -0.15, 8, frameDt);
  refreshHud();
  renderer.render(scene, camera);
});
document.addEventListener('visibilitychange', () => { // pause in background
  paused = document.hidden;
  if (!paused) last = performance.now() / 1000; // no giant post-resume delta
});
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
resetGame();
```

**Why it's built this way**

- Moving the world instead of the player is the architecture.md "floating origin" pattern in its simplest form — an endless runner is exactly where forward drift eventually breaks float32 precision, and here avoiding it costs nothing.
- The mobile preset (recipes.md: "quality tiers / mobile preset") is decided once at boot from `(pointer: coarse)` — DPR 1.5, no shadows, Lambert materials — instead of adapting mid-game, which causes visible pops and shader recompiles.
- Swipes resolve on `pointerup` against a recorded `pointerdown` (recipes.md: "gesture input via pointer events"): one discrete lane step per gesture, immune to noisy `pointermove` streams; `touch-action: none` stops the browser hijacking the pan.
- Lane state is an integer in the simulation; the eased x-position is presentation-only `MathUtils.damp` (architecture.md: "simulation/presentation split") — gameplay never depends on an animation finishing.
- Obstacles come from a fixed pool sized for the worst-case spawn rate (recipes.md: "object pooling"); a skipped spawn on exhaustion is invisible, a GC pause on mobile is not. `visibilitychange` + `MAX_FRAME` make backgrounding doubly safe.

**Extension ideas**

- Add jump/slide on swipe up/down (track deltaY too) with obstacle types requiring each.
- Swap the player box for the Example B character and crossfade a `Slide` clip on gesture.
- Add coin rows between obstacles using an `InstancedMesh` pool and a magnet power-up.

## Which example to start from

| Your goal | Start from | Why |
| --- | --- | --- |
| Any first prototype / game jam seed | **A — Orb Collector** | Complete loop, input, camera, HUD, and reset in one file; delete the orbs and build on the skeleton. |
| Character or animation-driven games | **B — glTF crossfade** | Loader stack, crossfade state machine, and skinned-clone spawning are the hard 20% of every character game. |
| Physics-driven gameplay or destruction | **C — Rapier playground** | Fixed-step world, instanced body sync, pooled projectiles, and collision events transfer directly. |
| Mobile arcade / hyper-casual | **D — Endless runner** | Gesture input, mobile preset, world-moves-to-player, and lifecycle pausing are the mobile-specific essentials. |
