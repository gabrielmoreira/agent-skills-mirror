# Three.js Game Development — Architecture

*How to organize a Three.js game codebase: loop, entities, physics sync, assets, and lifecycle. Loaded on demand from SKILL.md.*

## Scope & composition boundary

This file covers **Three.js-specific game architecture**: the render/update loop, entity organization, physics synchronization, asset and level lifecycle, and the code structure that holds a running game together inside the canvas.

Everything *around* the canvas — routing, DOM menu screens, meta-progression UI, save-slot management, analytics, service workers — belongs to the **browser-game-architecture** skill. The handoff line is explicit: **browser-game-architecture owns the app shell that creates a `<canvas>` and calls `new Game(canvas).start()`; this file owns everything from that call inward.** The Game exposes a small surface (start, dispose, event bus, state machine) that the shell consumes; the shell never reaches into scenes, entities, or the renderer.

Related siblings: camera feel and tuning theory → **game-camera-system**; engine-agnostic input theory → **game-input-handling**; deep FSM/HSM theory → **game-state-machine**; measuring what is slow → **game-performance-profiling**. Within this package: API facts live in reference.md, copy-paste setups in recipes.md, assembled games in examples.md.

## Folder layout

Concrete tree for a Vite + TypeScript Three.js game:

```
public/
  draco/              # DRACO decoder wasm/js — must be static, not bundled
  basis/              # KTX2/Basis transcoder files — same rule
  models/             # .glb files fetched at runtime
  audio/              # .ogg/.mp3 fetched at runtime
src/
  core/
    Game.ts           # composition root — wires everything (section 3)
    Loop.ts           # fixed-timestep loop driver (section 4)
    Time.ts           # game-time/wall-time model (section 5)
    Events.ts         # typed EventBus (section 8)
    Input.ts          # device listeners → action snapshot (section 9)
  systems/            # PhysicsSystem, CameraSystem, AudioSystem, AnimationSystem
  entities/           # Entity base + concrete entities (Player, Enemy, Pickup)
  levels/             # Level implementations + Level interface
  assets/
    manifest.ts       # typed asset manifest (keys → urls)
    AssetManager.ts   # preload/get/release/refcount (section 11)
  ui/                 # DOM HUD overlay — reads events, writes DOM (section 15)
  config/             # tuning constants, quality tiers, collision groups
  main.ts             # entry: creates canvas host, new Game(...), start()
```

Rules: decoder/transcoder binaries stay in `public/` so loaders can fetch them by URL (Vite will not bundle wasm side-files correctly from `src/`). Gameplay code in `systems/`, `entities/`, `levels/` must not import from `ui/` — it emits events; UI subscribes. `config/` is plain data so designers (or you, later) tune without touching logic.

## Composition root: the Game class

One class owns construction and teardown. Dependencies are created here and **passed down explicitly** (constructor injection). No module-level singletons: singletons make teardown impossible (a disposed renderer lingering in a module closure), break unit tests (state leaks between tests), and hide the dependency graph. With injection, `game.dispose()` provably releases everything, and a headless test can construct a `World` with a stub physics system.

```ts
import * as THREE from 'three';
import { Loop } from './Loop';
import { GameTime } from './Time';
import { EventBus, type GameEvents } from './Events';
import { InputSystem } from './Input';
import { AssetManager } from '../assets/AssetManager';
import { PhysicsSystem } from '../systems/PhysicsSystem';
import { GameStateMachine } from './StateMachine';
import { World } from '../entities/World';

export class Game {
  readonly renderer: THREE.WebGLRenderer;
  readonly scene = new THREE.Scene();
  readonly camera: THREE.PerspectiveCamera;
  readonly events = new EventBus<GameEvents>();
  readonly time = new GameTime();
  readonly loop: Loop;
  readonly input: InputSystem;
  readonly assets: AssetManager;
  readonly physics: PhysicsSystem;
  readonly world: World;
  readonly fsm: GameStateMachine;

  constructor(private readonly canvas: HTMLCanvasElement) {
    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    // r152+ defaults: outputColorSpace = SRGBColorSpace; leave them alone.
    this.camera = new THREE.PerspectiveCamera(60, 1, 0.1, 500);

    this.loop = new Loop(this.renderer);
    this.input = new InputSystem(canvas);
    this.assets = new AssetManager();
    this.physics = new PhysicsSystem(this.events);
    this.world = new World();
    this.fsm = new GameStateMachine(this);

    // Fixed-rate simulation order matters: input snapshot → physics → gameplay.
    this.loop.onUpdate((dt) => {
      this.input.snapshot();
      this.fsm.update(dt);          // states decide what actually runs
    });
    // Per-frame presentation: interpolate visuals, then draw.
    this.loop.onRender((dt, alpha) => {
      this.physics.syncVisuals(alpha);
      this.renderer.render(this.scene, this.camera);
    });
  }

  async start(): Promise<void> {
    await this.physics.init();      // RAPIER.init() — wasm load
    this.input.attach();
    this.fsm.transition('boot');
    this.loop.start();
  }

  dispose(): void {
    this.loop.stop();
    this.input.detach();
    this.world.clear();
    this.physics.dispose();
    this.assets.disposeAll();
    this.renderer.dispose();
  }
}
```

The Game class **wires**; it does not contain gameplay. If `Game.ts` grows `takeDamage()` methods, you have a God object (see anti-patterns).

## The loop, properly housed

Simulation runs at a **fixed timestep** (deterministic, stable physics); rendering runs at display rate and interpolates. Driver is `renderer.setAnimationLoop`, not raw `requestAnimationFrame`: it is required for WebXR sessions, and it keeps one consistent scheduling path whether or not XR is active.

**Spiral of death:** if a frame takes longer than the work its accumulated fixed steps generate, the accumulator grows every frame and the game locks up doing catch-up steps forever. The `MAX_FRAME` clamp caps how much real time one frame may inject into the accumulator — after a long stall (tab switch, GC pause) the game *slows down* briefly instead of freezing.

```ts
import * as THREE from 'three';

export const FIXED_DT = 1 / 60;
const MAX_FRAME = 0.25; // seconds of real time; caps catch-up work

type UpdateFn = (fixedDt: number) => void;
type RenderFn = (frameDt: number, alpha: number) => void;

export class Loop {
  timescale = 1;
  private accumulator = 0;
  private last = 0;
  private paused = false;
  private readonly updates = new Set<UpdateFn>();
  private readonly renders = new Set<RenderFn>();
  private readonly onVisibility = (): void => {
    if (document.hidden) this.pause();
    else this.resume();
  };

  constructor(private readonly renderer: THREE.WebGLRenderer) {}

  onUpdate(fn: UpdateFn): () => void { this.updates.add(fn); return () => this.updates.delete(fn); }
  onRender(fn: RenderFn): () => void { this.renders.add(fn); return () => this.renders.delete(fn); }

  start(): void {
    this.last = performance.now();
    document.addEventListener('visibilitychange', this.onVisibility);
    this.renderer.setAnimationLoop(this.tick);
  }

  stop(): void {
    this.renderer.setAnimationLoop(null);
    document.removeEventListener('visibilitychange', this.onVisibility);
  }

  pause(): void { this.paused = true; }
  resume(): void { this.paused = false; this.last = performance.now(); this.accumulator = 0; }

  private tick = (now: number): void => {
    const rawDt = Math.min((now - this.last) / 1000, MAX_FRAME);
    this.last = now;
    if (this.paused) {
      // Presentation still renders (menus over frozen world), simulation halts.
      for (const r of this.renders) r(0, 1);
      return;
    }
    const dt = rawDt * this.timescale;
    this.accumulator += dt;
    while (this.accumulator >= FIXED_DT) {
      for (const u of this.updates) u(FIXED_DT);
      this.accumulator -= FIXED_DT;
    }
    const alpha = this.accumulator / FIXED_DT; // 0..1 blend between prev/curr sim state
    for (const r of this.renders) r(dt, alpha);
  };
}
```

Update subscribers receive `FIXED_DT` and may run 0..N times per frame. Render subscribers receive frame delta and `alpha` and run exactly once. Never mix the two: stepping physics in a render subscriber ties simulation to refresh rate (144 Hz monitors double your game speed).

## Time model

Keep two clocks. **Wall time** (`performance.now()`) drives the loop and UI animations. **Game time** is accumulated fixed steps scaled by `timescale` — it stops when paused and stretches in slow-mo.

```ts
export class GameTime {
  /** Seconds of simulated time. Only advanced by fixed updates. */
  elapsed = 0;
  advance(fixedDt: number): void { this.elapsed += fixedDt; }
}
```

Rules:

- Cooldowns, buff durations, spawn timers compare against `time.elapsed`, **never** `Date.now()` or `performance.now()`. Otherwise pausing the game lets cooldowns expire and slow-mo breaks ability timing.
- `loop.timescale = 0.2` gives slow motion for free: physics and gameplay slow together because both consume scaled dt through the accumulator.
- Pausing stops simulation (no fixed updates) but presentation may continue: the pause menu animates via wall time, the frozen world still renders each frame (see the `paused` branch in Loop).
- UI tween libraries and DOM animations use wall time; anything affecting game outcome uses game time.

## Game state machine

The Game owns one top-level FSM: `Boot → Menu → Loading → Play ⇄ Pause → GameOver`. States gate what runs: `Play.update` steps the world and physics; `Pause.update` does nothing; `Loading` drives the asset progress bar. States also gate input by choosing which action context is active.

```ts
export interface State {
  readonly name: string;
  enter(): void;
  exit(): void;
  update(fixedDt: number): void;
}

export class GameStateMachine {
  private current: State | null = null;
  private readonly states = new Map<string, State>();

  constructor(private readonly game: import('./Game').Game) {}

  register(state: State): void { this.states.set(state.name, state); }

  transition(name: string): void {
    const next = this.states.get(name);
    if (!next) throw new Error(`Unknown state: ${name}`);
    this.current?.exit();
    this.current = next;
    next.enter();
    this.game.events.emit('state:changed', { name });
  }

  update(fixedDt: number): void { this.current?.update(fixedDt); }
}
```

A `PlayState.update` calls `game.physics.step(dt)` then `game.world.update(dt)`; entering `PauseState` emits an event the DOM menu listens to. Deeper theory — hierarchical states, transition guards, per-entity FSMs for AI — lives in the **game-state-machine** skill; keep this top-level one flat and boring.

## Entities & systems

The pragmatic default is **composition, not ECS**: an Entity holds an `Object3D` plus optional typed components (physics body handle, health, AI brain), and systems iterate the entity list. Add/remove is **deferred to end of frame** so systems never mutate the list they are iterating.

```ts
import * as THREE from 'three';
import type RAPIER from '@dimforge/rapier3d-compat';

export class Entity {
  readonly object3D = new THREE.Object3D();
  body?: RAPIER.RigidBody;
  health?: { hp: number; max: number };
  alive = true;
  update(_fixedDt: number): void {} // override in subclasses
  onDespawn(): void {}              // free body, return to pool, etc.
}

export interface System {
  update(fixedDt: number, entities: readonly Entity[]): void;
}

export class World {
  private readonly entities: Entity[] = [];
  private readonly pendingAdd: Entity[] = [];
  private readonly pendingRemove = new Set<Entity>();
  readonly systems: System[] = [];

  add(e: Entity): void { this.pendingAdd.push(e); }
  remove(e: Entity): void { e.alive = false; this.pendingRemove.add(e); }

  update(fixedDt: number): void {
    for (const e of this.entities) if (e.alive) e.update(fixedDt);
    for (const s of this.systems) s.update(fixedDt, this.entities);
    this.flush();
  }

  private flush(): void {
    if (this.pendingAdd.length > 0) {
      this.entities.push(...this.pendingAdd);
      this.pendingAdd.length = 0;
    }
    if (this.pendingRemove.size > 0) {
      for (const e of this.pendingRemove) {
        const i = this.entities.indexOf(e);
        if (i !== -1) this.entities.splice(i, 1);
        e.onDespawn();
      }
      this.pendingRemove.clear();
    }
  }

  clear(): void {
    for (const e of this.entities) e.onDespawn();
    this.entities.length = 0;
    this.pendingAdd.length = 0;
    this.pendingRemove.clear();
  }
}
```

**When to graduate to a real ECS** (miniplex for ergonomics, bitecs for raw throughput): when you have hundreds-plus of *homogeneous* entities (bullets, boids, voxel critters) where data-oriented iteration over packed component arrays pays off, or when component combinations explode past what optional fields express cleanly. The tradeoff: ECS buys cache-friendly iteration and query composability at the cost of indirection everywhere, harder debugging (state scattered across stores), and a learning tax on every contributor. For a typical scene with tens of heterogeneous actors, the class above wins. Do not implement your own ECS.

## Events

A small typed bus decouples gameplay from UI and audio. Rule: **gameplay emits, UI/audio subscribe.** Gameplay never imports from `ui/`.

```ts
export interface GameEvents {
  'state:changed': { name: string };
  'player:damaged': { hp: number; max: number };
  'enemy:killed': { points: number };
  'level:progress': { loaded: number; total: number };
  'physics:collision': { a: Entity; b: Entity; started: boolean };
}

export class EventBus<E extends Record<string, unknown>> {
  private readonly handlers = new Map<keyof E, Set<(p: never) => void>>();

  on<K extends keyof E>(key: K, fn: (payload: E[K]) => void): () => void {
    let set = this.handlers.get(key);
    if (!set) { set = new Set(); this.handlers.set(key, set); }
    set.add(fn as (p: never) => void);
    return () => set.delete(fn as (p: never) => void);
  }

  emit<K extends keyof E>(key: K, payload: E[K]): void {
    const set = this.handlers.get(key);
    if (set) for (const fn of set) (fn as (p: E[K]) => void)(payload);
  }

  clear(): void { this.handlers.clear(); }
}
```

Two discipline rules. First, handlers must never mutate entity lists mid-iteration — a `enemy:killed` handler that spawns loot calls `world.add()`, which defers, which is exactly why deferral exists; if a handler must remove entities, it goes through `world.remove()` (also deferred). Second, avoid event soup: within one system, direct method calls are clearer than events. Events are for crossing module boundaries (gameplay → UI/audio/analytics), not for a system talking to itself.

## Input architecture

Three layers, strictly ordered:

1. **Device listeners** — keyboard tracked in a `Set<string>` keyed by `event.code` (layout-independent), pointers in a `Map<number, PointerState>` keyed by `pointerId`, gamepads polled each frame via `navigator.getGamepads()`.
2. **Action map** — a rebindable table from `Action` to physical bindings. Gameplay never sees `'KeyW'`.
3. **Per-frame ActionState snapshot** — an immutable frame of "what is the player asking for," taken once per render frame and consumed by however many fixed updates run.

The snapshot is mandatory because fixed updates run **0..N times per frame**. If simulation reads live device state, a `justPressed` computed from raw events can be consumed by step 1 and invisible to step 2 — or seen twice across frames with zero steps. Freeze once; every step this frame sees the same truth.

```ts
export const Actions = ['moveX', 'moveY', 'jump', 'fire', 'pause'] as const;
export type Action = (typeof Actions)[number];

export interface ActionState {
  readonly axes: Readonly<Record<'moveX' | 'moveY', number>>;
  readonly held: ReadonlySet<Action>;
  readonly justPressed: ReadonlySet<Action>;
}

export class InputSystem {
  private readonly keys = new Set<string>();
  private prevHeld = new Set<Action>();
  private current: ActionState = { axes: { moveX: 0, moveY: 0 }, held: new Set(), justPressed: new Set() };
  private bindings: Record<Action, string[]> = {
    moveX: ['KeyA', 'KeyD'], moveY: ['KeyW', 'KeyS'],
    jump: ['Space'], fire: ['Mouse0'], pause: ['Escape'],
  };
  private readonly onKeyDown = (e: KeyboardEvent): void => { this.keys.add(e.code); };
  private readonly onKeyUp = (e: KeyboardEvent): void => { this.keys.delete(e.code); };
  private readonly onPointerDown = (e: PointerEvent): void => { this.keys.add(`Mouse${e.button}`); };
  private readonly onPointerUp = (e: PointerEvent): void => { this.keys.delete(`Mouse${e.button}`); };

  constructor(private readonly canvas: HTMLCanvasElement) {}

  attach(): void {
    window.addEventListener('keydown', this.onKeyDown);
    window.addEventListener('keyup', this.onKeyUp);
    this.canvas.addEventListener('pointerdown', this.onPointerDown);
    window.addEventListener('pointerup', this.onPointerUp);
  }

  detach(): void {
    window.removeEventListener('keydown', this.onKeyDown);
    window.removeEventListener('keyup', this.onKeyUp);
    this.canvas.removeEventListener('pointerdown', this.onPointerDown);
    window.removeEventListener('pointerup', this.onPointerUp);
  }

  rebind(action: Action, codes: string[]): void { this.bindings[action] = codes; }

  /** Called once per frame, before any fixed updates consume state. */
  snapshot(): void {
    const held = new Set<Action>();
    for (const action of Actions) {
      if (this.bindings[action].some((c) => this.keys.has(c))) held.add(action);
    }
    const justPressed = new Set<Action>([...held].filter((a) => !this.prevHeld.has(a)));
    const axis = (neg: string, pos: string): number =>
      (this.keys.has(pos) ? 1 : 0) - (this.keys.has(neg) ? 1 : 0);
    this.current = {
      axes: { moveX: axis('KeyA', 'KeyD'), moveY: axis('KeyS', 'KeyW') },
      held, justPressed,
    };
    this.prevHeld = held;
  }

  get state(): ActionState { return this.current; }
}
```

Gamepad axes merge into the same snapshot at poll time; touch joystick/button overlays are a recipe (see recipes.md). Buffered inputs, dead zones, and chorded bindings theory lives in the **game-input-handling** skill.

## Physics integration

Ownership rule, applied per body type:

- **Dynamic bodies own their transforms.** After the physics step, copy body position/rotation *to* the mesh. Never write a dynamic body's transform from gameplay except via teleport APIs.
- **Kinematic bodies are driven by gameplay.** Write `setNextKinematicTranslation` *before* the step from controller logic.
- **Render interpolation:** store previous and current transform per body each step; in `syncVisuals(alpha)` lerp position and slerp rotation. Without this, 60 Hz physics on a 144 Hz display visibly stutters.

```ts
import RAPIER from '@dimforge/rapier3d-compat';
import * as THREE from 'three';
import { FIXED_DT } from '../core/Loop';
import type { EventBus, GameEvents } from '../core/Events';
import type { Entity } from '../entities/World';

// Collision groups as typed constants: high 16 bits = membership, low 16 = filter.
export const Groups = {
  STATIC: 0x0001, PLAYER: 0x0002, ENEMY: 0x0004, PICKUP: 0x0008,
} as const;
export const interactionGroups = (member: number, filter: number): number =>
  (member << 16) | filter;

interface Tracked { entity: Entity; prevPos: THREE.Vector3; prevRot: THREE.Quaternion; }

export class PhysicsSystem {
  world!: RAPIER.World;
  private eventQueue!: RAPIER.EventQueue;
  private readonly tracked = new Map<number, Tracked>(); // body handle → entity link

  constructor(private readonly events: EventBus<GameEvents>) {}

  async init(): Promise<void> {
    await RAPIER.init();
    this.world = new RAPIER.World({ x: 0, y: -9.81, z: 0 });
    this.world.timestep = FIXED_DT;
    this.eventQueue = new RAPIER.EventQueue(true);
  }

  register(entity: Entity, body: RAPIER.RigidBody): void {
    entity.body = body;
    body.userData = entity; // body↔entity link for collision dispatch
    const t = body.translation(); const r = body.rotation();
    this.tracked.set(body.handle, {
      entity,
      prevPos: new THREE.Vector3(t.x, t.y, t.z),
      prevRot: new THREE.Quaternion(r.x, r.y, r.z, r.w),
    });
  }

  unregister(entity: Entity): void {
    if (!entity.body) return;
    this.tracked.delete(entity.body.handle);
    this.world.removeRigidBody(entity.body); // also frees attached colliders
    entity.body = undefined;
  }

  step(): void {
    // Snapshot prev transforms before stepping (for interpolation).
    for (const { entity, prevPos, prevRot } of this.tracked.values()) {
      const t = entity.body!.translation(); const r = entity.body!.rotation();
      prevPos.set(t.x, t.y, t.z); prevRot.set(r.x, r.y, r.z, r.w);
    }
    this.world.step(this.eventQueue);
    this.eventQueue.drainCollisionEvents((h1, h2, started) => {
      const a = this.tracked.get(this.world.getCollider(h1).parent()?.handle ?? -1)?.entity;
      const b = this.tracked.get(this.world.getCollider(h2).parent()?.handle ?? -1)?.entity;
      if (a && b) this.events.emit('physics:collision', { a, b, started });
    });
  }

  syncVisuals(alpha: number): void {
    const pos = new THREE.Vector3(); const rot = new THREE.Quaternion();
    for (const { entity, prevPos, prevRot } of this.tracked.values()) {
      const t = entity.body!.translation(); const r = entity.body!.rotation();
      pos.set(t.x, t.y, t.z); rot.set(r.x, r.y, r.z, r.w);
      entity.object3D.position.lerpVectors(prevPos, pos, alpha);
      entity.object3D.quaternion.slerpQuaternions(prevRot, rot, alpha);
    }
  }

  dispose(): void { this.tracked.clear(); this.world?.free(); this.eventQueue?.free(); }
}
```

`step()` runs inside a fixed update (PlayState); `syncVisuals(alpha)` runs in the render subscriber. Colliders get `setActiveEvents(RAPIER.ActiveEvents.COLLISION_EVENTS)` and `setCollisionGroups(interactionGroups(...))` at creation (see recipes.md for body/collider construction).

**cannon-es differences:** cannon-es is pure JS (no wasm init await), uses `world.step(FIXED_DT)` or the built-in `fixedStep()` helper, links via `body.addEventListener('collide', ...)` per body instead of a drained queue, and its `userData` equivalent is just a property you attach. Same ownership and interpolation rules apply unchanged. For static level geometry against character capsules without a full physics engine, `three-mesh-bvh` raycast/shapecast collision is the lighter option.

## Asset manager

Manifest-driven: one typed manifest is the single source of truth for keys and URLs; `get` returns strong types; refcounting plus level-scoped groups make teardown mechanical.

```ts
import * as THREE from 'three';
import type { GLTF } from 'three/addons/loaders/GLTFLoader.js';
import * as SkeletonUtils from 'three/addons/utils/SkeletonUtils.js';

export const manifest = {
  models: { player: '/models/player.glb', crate: '/models/crate.glb' },
  textures: { ground: '/models/ground_diffuse.ktx2' },
  audio: { jump: '/audio/jump.ogg' },
} as const;
export type ModelKey = keyof typeof manifest.models;
export type TextureKey = keyof typeof manifest.textures;
export type AudioKey = keyof typeof manifest.audio;

interface Loaded { asset: GLTF | THREE.Texture | AudioBuffer; refs: number; }

export class AssetManager {
  private readonly cache = new Map<string, Loaded>();
  private readonly groups = new Map<string, string[]>();

  // Loader wiring (GLTFLoader + DRACO/KTX2 decoder paths) lives in recipes.md.
  constructor(
    private readonly loadModel: (url: string) => Promise<GLTF> = defaultModelLoader,
    private readonly loadTexture: (url: string) => Promise<THREE.Texture> = defaultTextureLoader,
    private readonly loadAudio: (url: string) => Promise<AudioBuffer> = defaultAudioLoader,
  ) {}

  async loadGroup(
    group: string,
    keys: { models?: ModelKey[]; textures?: TextureKey[]; audio?: AudioKey[] },
    onProgress?: (loaded: number, total: number) => void,
  ): Promise<void> {
    const jobs: Array<[string, Promise<Loaded['asset']>]> = [
      ...(keys.models ?? []).map((k): [string, Promise<GLTF>] =>
        [`model:${k}`, this.loadModel(manifest.models[k])]),
      ...(keys.textures ?? []).map((k): [string, Promise<THREE.Texture>] =>
        [`texture:${k}`, this.loadTexture(manifest.textures[k])]),
      ...(keys.audio ?? []).map((k): [string, Promise<AudioBuffer>] =>
        [`audio:${k}`, this.loadAudio(manifest.audio[k])]),
    ];
    let done = 0;
    const owned: string[] = [];
    await Promise.all(jobs.map(async ([key, promise]) => {
      const existing = this.cache.get(key);
      if (existing) { existing.refs++; }
      else { this.cache.set(key, { asset: await promise, refs: 1 }); }
      owned.push(key);
      onProgress?.(++done, jobs.length);
    }));
    this.groups.set(group, owned);
  }

  getModel(key: ModelKey): GLTF { return this.mustGet(`model:${key}`) as GLTF; }
  getTexture(key: TextureKey): THREE.Texture { return this.mustGet(`texture:${key}`) as THREE.Texture; }
  getAudio(key: AudioKey): AudioBuffer { return this.mustGet(`audio:${key}`) as AudioBuffer; }

  /** Clone for spawned characters — plain .clone() breaks skinned meshes. */
  spawnModel(key: ModelKey): THREE.Object3D { return SkeletonUtils.clone(this.getModel(key).scene); }

  disposeGroup(group: string): void {
    for (const key of this.groups.get(group) ?? []) this.release(key);
    this.groups.delete(group);
  }

  private release(key: string): void {
    const entry = this.cache.get(key);
    if (!entry || --entry.refs > 0) return;
    const a = entry.asset;
    if (a instanceof THREE.Texture) a.dispose();
    else if ('scene' in a) a.scene.traverse((o) => { if (o instanceof THREE.Mesh) {
      o.geometry.dispose();
      for (const m of Array.isArray(o.material) ? o.material : [o.material]) m.dispose();
    }});
    this.cache.delete(key);
  }

  disposeAll(): void { for (const g of [...this.groups.keys()]) this.disposeGroup(g); }
}

declare function defaultModelLoader(url: string): Promise<GLTF>;
declare function defaultTextureLoader(url: string): Promise<THREE.Texture>;
declare function defaultAudioLoader(url: string): Promise<AudioBuffer>;
```

(The three `declare function` lines stand in for the loader wiring implemented in recipes.md — inject real implementations at construction.) After a group loads, warm shaders before gameplay: `await renderer.compileAsync(scene, camera)` during the Loading state, so first sight of a material doesn't hitch.

## Level/scene lifecycle

Levels hot-swap; the renderer, camera, and Game live across them. A level owns a scene subtree, an asset group, physics bodies, and pools — and must fully release them.

```ts
export interface Level {
  readonly name: string;
  /** Fetch this level's asset group; report progress to the loading screen. */
  load(onProgress: (loaded: number, total: number) => void): Promise<void>;
  /** Build scene graph, spawn entities, create physics bodies. */
  build(): void;
  /** Enable input contexts, start music, begin simulation. */
  activate(): void;
  update(fixedDt: number): void;
  /**
   * Teardown checklist — every item, every time:
   * 1. Unsubscribe all EventBus/DOM listeners taken during build/activate.
   * 2. Kill tweens, intervals, and pending timeouts owned by the level.
   * 3. Unregister and free all physics bodies (PhysicsSystem.unregister).
   * 4. Deep-dispose the level subtree: traverse → geometry.dispose(),
   *    material(s).dispose(); remove root from scene.
   * 5. assets.disposeGroup(this.name) — refcounts release shared assets.
   * 6. Clear object pools (pools are per-level; drop them entirely).
   * 7. Verify: renderer.info.memory.geometries/textures returned to the
   *    pre-level baseline in dev builds — assert or warn on leaks.
   */
  teardown(): void;
}
```

The Loading state drives the sequence: `old.teardown()` → `next.load()` → `next.build()` → `next.activate()` → transition to Play. Because the renderer persists, compiled programs for shared materials survive the swap — one reason to never recreate the renderer between levels.

## Spawning & object pooling

Allocation during gameplay causes GC hitches. Pool anything spawned in bursts (bullets, particles, hit effects, enemies in waves).

```ts
export class Pool<T> {
  private readonly free: T[] = [];
  private readonly inUse = new Set<T>();

  constructor(
    private readonly factory: () => T,
    private readonly reset: (item: T) => void,
    prewarm = 0,
  ) {
    for (let i = 0; i < prewarm; i++) this.free.push(factory());
  }

  acquire(): T {
    const item = this.free.pop() ?? this.factory();
    this.reset(item);
    this.inUse.add(item);
    return item;
  }

  release(item: T): void {
    if (this.inUse.delete(item)) this.free.push(item);
  }

  releaseAll(): void { for (const item of this.inUse) this.free.push(item); this.inUse.clear(); }
  get active(): number { return this.inUse.size; }
}
```

The `reset` hook must restore **everything** a previous life may have touched: position/rotation/scale, `visible`, physics body velocity and translation (`setLinvel`, `setTranslation`, wake), `AnimationMixer.setTime(0)` and action states, material overrides (emissive flash from damage, opacity from fade-out), and any timers on the entity. A pool that skips one field produces the classic "bullet spawns already exploding" bug. Pools live per-level and are dropped in teardown — pooled objects hold level-scoped geometry and bodies, so a global pool would leak across levels.

## Camera architecture

The camera is its own entity/system, never a child of the player and never updated inside player code. Player logic decides where the player is; the camera system decides how to look at it — separating them lets you swap rigs (follow, orbit, cutscene) without touching gameplay.

```ts
import * as THREE from 'three';

export class FollowCameraSystem {
  private readonly offset = new THREE.Vector3(0, 4, 8);
  private readonly lookTarget = new THREE.Vector3();
  private shakeOffset = new THREE.Vector3();
  private shakeAmp = 0;

  constructor(private readonly camera: THREE.PerspectiveCamera, private target: THREE.Object3D) {}

  shake(amplitude: number): void { this.shakeAmp = Math.max(this.shakeAmp, amplitude); }

  /** Runs in render phase with frame dt — camera smoothing is presentation. */
  update(frameDt: number): void {
    const desired = this.target.position.clone().add(this.offset);
    // Framerate-independent damping: lambda ~4 = snappy, ~1 = floaty.
    this.camera.position.x = THREE.MathUtils.damp(this.camera.position.x, desired.x, 4, frameDt);
    this.camera.position.y = THREE.MathUtils.damp(this.camera.position.y, desired.y, 4, frameDt);
    this.camera.position.z = THREE.MathUtils.damp(this.camera.position.z, desired.z, 4, frameDt);
    // Shake is an additive layer on top of the rig, decaying each frame.
    this.shakeAmp = THREE.MathUtils.damp(this.shakeAmp, 0, 8, frameDt);
    this.shakeOffset.set(
      (Math.random() - 0.5) * this.shakeAmp,
      (Math.random() - 0.5) * this.shakeAmp, 0,
    );
    this.camera.position.add(this.shakeOffset);
    this.lookTarget.lerp(this.target.position, 0.2);
    this.camera.lookAt(this.lookTarget);
  }
}
```

Because visuals are interpolated in `syncVisuals`, the camera follows the *interpolated* target and stays smooth. Deadzone framing, collision-aware booms, FOV kicks, and tuning philosophy live in the **game-camera-system** skill.

## UI/HUD layer

Default to a **DOM overlay**: a `position: absolute` container over the canvas with `pointer-events: none`, and `pointer-events: auto` only on interactive children. DOM gives you text layout, accessibility, and CSS animation for free.

Two rules:

- HUD updates **on change via events**, never per-frame. A health bar subscribes to `player:damaged` and writes `style.width` once; writing DOM every frame forces layout/paint work that competes with WebGL.
- The HUD reads game state only through the EventBus — never pokes entities, and gameplay never queries the DOM.

In-canvas UI (sprites, billboards, `troika-three-text` for crisp SDF text) is warranted only when UI must exist *in the 3D world* (nameplates over heads, damage numbers, diegetic screens) or inside WebXR where DOM is unavailable. Menus, settings screens, and anything outside active play belong to the app shell — see **browser-game-architecture**.

## Persistence

Thin, typed, versioned, defensive:

```ts
interface SaveDataV1 {
  version: 1;
  settings: { volume: number; quality: 'low' | 'medium' | 'high' };
  progress: { unlockedLevels: string[]; bestScores: Record<string, number> };
}
const DEFAULTS: SaveDataV1 = {
  version: 1,
  settings: { volume: 0.8, quality: 'medium' },
  progress: { unlockedLevels: ['level-1'], bestScores: {} },
};
const KEY = 'mygame:save';

export class SaveStore {
  load(): SaveDataV1 {
    try {
      const raw = localStorage.getItem(KEY);
      if (!raw) return structuredClone(DEFAULTS);
      const parsed: unknown = JSON.parse(raw);
      if (typeof parsed === 'object' && parsed !== null && (parsed as { version?: number }).version === 1) {
        return { ...structuredClone(DEFAULTS), ...(parsed as Partial<SaveDataV1>), version: 1 };
      }
      return structuredClone(DEFAULTS); // unknown version → migrate or reset
    } catch { return structuredClone(DEFAULTS); } // private mode / quota / corrupt JSON
  }

  save(data: SaveDataV1): void {
    try { localStorage.setItem(KEY, JSON.stringify(data)); } catch { /* private mode: ignore */ }
  }
}
```

Save settings and progress; never save transient state (entity positions, active timers, current HP mid-run) — resumable mid-level saves are a serialization project of their own, and the app-level save strategy (slots, cloud) is **browser-game-architecture** territory.

## Resize, DPR & quality scaling

Exactly one owner of resize — a `ResizeObserver` on the canvas host — updates renderer size, camera aspect, and composer/render-target sizes together. Scattered resize handlers drift out of sync.

Quality is **data**, applied by one function:

```ts
export interface QualitySettings {
  dpr: number; shadows: boolean; shadowMapSize: number; post: boolean; renderScale: number;
}
export const QualityTiers = {
  low:    { dpr: 1,   shadows: false, shadowMapSize: 512,  post: false, renderScale: 0.75 },
  medium: { dpr: 1.5, shadows: true,  shadowMapSize: 1024, post: true,  renderScale: 1 },
  high:   { dpr: 2,   shadows: true,  shadowMapSize: 2048, post: true,  renderScale: 1 },
} as const satisfies Record<string, QualitySettings>;

export function applyQuality(renderer: THREE.WebGLRenderer, q: QualitySettings): void {
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, q.dpr) * q.renderScale);
  renderer.shadowMap.enabled = q.shadows;
  // Shadow map size changes require light.shadow.map?.dispose() + needsUpdate;
  // composer pass toggles read q.post. Wire both where those objects live.
}
```

Dynamic resolution: track a smoothed frame time; if it exceeds budget (16.6 ms) for ~30 consecutive frames, step `renderScale` down; only step back up after a longer stable window (hysteresis prevents oscillating between tiers every second). Measure first — see **game-performance-profiling**.

## TypeScript patterns

- **Strict mode always** (`"strict": true`, plus `noUncheckedIndexedAccess` — it catches `entities[i]` being possibly undefined).
- **Typed asset keys from the manifest**: `as const` on the manifest and `keyof typeof manifest.models` (section 11) makes `assets.getModel('playr')` a compile error. Brand further if keys travel far: `type ModelKey = keyof typeof manifest.models & { readonly __brand?: never }` is rarely needed; keyof usually suffices.
- **Narrowing Object3D**: use `instanceof THREE.Mesh` guards in traversals; for `userData`, define one interface and a guard rather than sprinkling casts:

```ts
interface GameUserData { entity?: Entity; interactable?: boolean; }
const dataOf = (o: THREE.Object3D): GameUserData => o.userData as GameUserData;
```

- **Readonly vectors in public APIs**: expose `readonly position: Readonly<THREE.Vector3>` (a type-level `Readonly` on getters) so callers can read `.x` but `.set()` is a compile error — mutation goes through methods you control.
- **Prefer const-object unions over enums**: `const Actions = [...] as const` and derived union types (section 9) erase cleanly, work with `keyof`, and avoid enum's runtime object and import quirks under `isolatedModules`.
- **No `any` from GLTF**: `GLTFLoader` results are loosely typed; wrap extraction once — `const mesh = gltf.scene.getObjectByName('Body'); if (!(mesh instanceof THREE.SkinnedMesh)) throw new Error('Body missing')` — and export typed handles, so `any` never leaks into gameplay.

## Determinism, debug & testing hooks

- **Seeded RNG, injected**: gameplay takes a `rand: () => number` dependency, never calls `Math.random()` directly. mulberry32 is four lines:

```ts
export function mulberry32(seed: number): () => number {
  return () => {
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
```

- **Headless-testable gameplay**: fixed timestep + seeded RNG + injected dependencies means `World`, entities, and systems run in Vitest with no renderer. Enforce it by folder boundary: nothing under `entities/` or gameplay `systems/` imports `three`'s renderer or anything from `ui/` — entities use `Object3D` (pure math, no GL) which works headless. Lint rule or code review; either way, the boundary is the test strategy.
- **Debug flags via URL**: `const debug = new URLSearchParams(location.search); if (debug.has('debug'))...` — `?debug=physics` toggles a Rapier debug-render pass (`world.debugRender()` returns vertex/color buffers to feed a `LineSegments`), `?debug=stats` mounts an FPS meter.
- **Dev-only global handle**: `if (import.meta.env.DEV) (window as { __game?: Game }).__game = game;` — console poking during development, stripped from production by Vite's define replacement.

## Architecture anti-patterns

1. **God Game class** — Game grows `damagePlayer()`, `spawnWave()`, inventory logic. Game wires; gameplay lives in entities/systems/states.
2. **Gameplay importing the renderer** — an enemy that calls `renderer.render` or reads canvas size couples simulation to presentation and kills headless tests. Gameplay touches `Object3D` math only.
3. **Physics stepped in render** — `world.step()` inside the render callback ties simulation rate to refresh rate. Physics steps only in fixed update.
4. **DOM as source of truth** — reading `input.value` or checking `classList` to decide gameplay. State lives in TS objects; DOM is a projection.
5. **Singletons everywhere** — module-level `export const game = new Game()` blocks teardown, leaks across hot reloads, and makes two-instance tests impossible. Constructor injection (section 3).
6. **Async level-load races** — player triggers level 2, then level 3 before 2 finishes; both loads complete and both `build()`. Guard with a generation counter:

```ts
private loadGen = 0;
async switchLevel(next: Level): Promise<void> {
  const gen = ++this.loadGen;
  await next.load(() => {});
  if (gen !== this.loadGen) return; // superseded — discard silently
  this.current?.teardown(); this.current = next; next.build(); next.activate();
}
```

7. **Event-bus-for-everything** — systems emitting events to themselves, three-hop event chains for what should be one method call. Events cross module boundaries; direct calls within a boundary.
8. **Premature ECS** — adopting bitecs for 12 entities adds indirection with zero payoff. Composition first; graduate on measured need (section 7).
9. **Per-frame HUD writes** — `hpLabel.textContent = ...` in the render loop forces continuous style/layout work. Update on change via events.
10. **Pools that never reset** — reused bullets keep old velocity, old emissive flash, old mixer time. The reset hook restores every mutated field (section 13).
11. **Listeners added in constructors, never removed** — every `addEventListener` needs a stored handler reference and a matching `remove` in `detach`/`teardown`; anonymous inline handlers are unremovable leaks.
12. **Recreating the renderer per level** — throws away compiled shaders and GPU uploads, causes context churn. One renderer for the app's lifetime; levels swap subtrees (section 12).

API details in reference.md; copy-paste setups in recipes.md; these patterns assembled into running games in examples.md.
