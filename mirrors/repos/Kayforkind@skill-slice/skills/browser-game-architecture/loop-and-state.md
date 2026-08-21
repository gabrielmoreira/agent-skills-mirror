# browser-game-architecture — game loop & state

The loop is the heart; scenes and state are the skeleton around it. This file covers timing, the loop patterns and their failure modes, clocks, scene stacks, entity architecture, events, timers/tweens, and determinism. FSM theory depth: `game-state-machine`.

---

## 1. Timing fundamentals

- `requestAnimationFrame(cb)` schedules `cb(timestamp)` before the next repaint, synced to the display (60Hz, 120Hz, 144Hz — **you do not control the rate**). The `timestamp` is a `DOMHighResTimeStamp` on the same clock as `performance.now()` — use it; don't call `performance.now()` again inside the callback.
- Each callback runs once; re-register every frame. Register **at the top** of the frame function so a thrown error doesn't silently kill the loop (pair with the crash overlay, `reference.md` §9).
- Never drive simulation with `setInterval`/`setTimeout` — unsynced to rendering, heavily throttled in background tabs, drift-prone. Timers are for non-frame logic only.
- Delta time (`dt`) = time since last frame. Frame-rate-independent movement means `pos += vel * dt` — anything else plays differently on a 144Hz monitor than a 60Hz one.
- **`dt` lies to you** in specific cases you must handle: first frame (no previous timestamp), returning from a background tab (dt = minutes), debugger breakpoints, system sleep. Hence the clamp — see §2.3.

## 2. Loop patterns

### 2.1 Variable timestep (use only for pure presentation)

```js
let last;
function frame(now) {
  requestAnimationFrame(frame);
  const dt = Math.min((now - (last ?? now)) / 1000, 0.25);
  last = now;
  update(dt);   // everything scales by dt
  render();
}
requestAnimationFrame(frame);
```

Simple, and adequate for games with no physics, no tunneling risk, and no feel-critical tuning (visual novels, card games, idle UIs). Its flaws: physics explodes under large/irregular dt (integration error scales with dt; fast objects tunnel through thin colliders), and gameplay tuned at 60fps *feels different* at 144fps. Any game where those matter gets:

### 2.2 Fixed timestep + accumulator + render interpolation (the default)

Simulation advances in fixed quanta; rendering runs at display rate and interpolates between the last two simulation states. ("Fix Your Timestep", Gaffer on Games — this is the canonical browser form.)

```js
const STEP = 1 / 60;        // simulation Hz — decoupled from display Hz
const MAX_DT = 0.25;        // clamp: tab-away, breakpoints
const MAX_STEPS = 5;        // spiral-of-death guard

let last, acc = 0;
function frame(now) {
  requestAnimationFrame(frame);
  let dt = (now - (last ?? now)) / 1000;
  last = now;
  acc += Math.min(dt, MAX_DT);

  let steps = 0;
  while (acc >= STEP && steps < MAX_STEPS) {
    previousState = snapshot(currentState); // only what render interpolates: transforms
    simulate(STEP);                         // ALWAYS the same dt — determinism lives here
    acc -= STEP; steps++;
  }
  if (steps === MAX_STEPS) acc = 0;         // overloaded: drop backlog, game slows rather than freezes

  render(acc / STEP);                       // alpha ∈ [0,1): how far into the *next* step we are
}
requestAnimationFrame(frame);
```

Render interpolation: `x = prev.x + (curr.x - prev.x) * alpha`. Without it, a 60Hz sim on a 144Hz display visibly stutters (frames repeat sim states unevenly). Snapshot only render-relevant state (positions/rotations), not the whole world. Acceptable simplification for jams: skip interpolation and render `currentState` — fine at sim Hz == common display Hz, revisit if players report stutter.

Choosing STEP: 60Hz default. 30Hz sim + interpolation is a legitimate mobile CPU saving for slow-paced games. 120Hz only for feel-critical action where you've measured headroom.

### 2.3 The two guards, and why both

- **dt clamp (`MAX_DT`)**: caps how much real time one frame may inject. Without it, returning from a 10-minute background tab enqueues 36,000 steps.
- **Step cap (`MAX_STEPS`)**: caps work per frame. If the machine can't simulate real-time (sim step costs > STEP of wall time), the accumulator grows each frame and update time grows unboundedly — the *spiral of death*. Cap it and drop the remainder: the game runs slower than real-time but stays interactive. If the cap trips regularly on target hardware, the sim is over budget — optimize or lower sim Hz; don't raise the cap.

### 2.4 Input edges under fixed timestep

`justPressed` edge sets must be cleared **after simulation steps consume them**, not per rAF frame. A frame can run 0 simulation steps (high-Hz display, accumulator not full); clearing edges in that frame drops the player's input. Correct pattern: input listeners write into a pending set; each `simulate()` reads it; clear only after at least one step ran (or hand the set to the loop and clear inside the while-loop after the first step).

## 3. Clock architecture

Distinguish three times and pipe them explicitly — never read `performance.now()` from gameplay code:

- **Wall time**: rAF timestamps. Only the loop driver sees it.
- **Game time**: advances by `STEP * timescale` per simulation step; frozen while paused. Drives gameplay, cooldowns, animation, tweens.
- **Unscaled/UI time**: advances by real (clamped) dt even during pause/slow-mo. Drives menu animation, pause-screen effects.

```js
class Clock {
  t = 0; unscaled = 0; timescale = 1; paused = false;
  tick(dt)        { this.unscaled += dt; if (!this.paused) this.t += dt * this.timescale; }
  get dt()        { return this.paused ? 0 : STEP * this.timescale; }
}
```

Timescale gives slow-mo/fast-forward for free *if* nothing bypasses the clock. Two implementation choices for slow-mo with fixed timestep: scale the dt fed to the accumulator (fewer sim steps per real second — cheap, physics quality unchanged per step) — preferred; or scale within `simulate` (constant step count, scaled per-step dt — reintroduces variable-dt error). Pause = `clock.paused = true` plus the scene stack showing a pause scene (§5); don't stop the rAF loop itself — menus still animate and render.

## 4. Background-tab behavior

Facts to design around:

- **rAF stops entirely** in hidden tabs. Your game does not tick at all while hidden.
- `setTimeout`/`setInterval` throttle to ≥1s (Chromium "intensive throttling" can be worse). Don't move the loop to timers to "keep running" — it's fighting the platform.
- **Web Audio keeps playing** — suspend on hidden (`reference.md` §3.4).
- On return, the next rAF timestamp jumps by the whole hidden duration → the dt clamp absorbs it.

Policy per genre: action/puzzle → auto-pause on hidden, stay paused on return (desktop) or auto-resume (casual mobile); idle games → don't simulate while hidden, compute offline progress analytically from the wall-clock gap on return; anything with timers the player perceives as real-time (energy refill) → store absolute timestamps in the save, derive on load — never tick real-world timers with the game loop.

## 5. Scene management (scene stack)

A **stack**, not a single-current-scene switcher — because pause menus, dialogs, and inventory screens are scenes *over* gameplay, and a stack gives you that without flags.

Scene interface and manager contract:

```js
class Scene {
  enter(params) {}   // pushed / switched to
  exit() {}          // popped / replaced — release listeners, timers, scene-scoped assets
  pause() {}         // another scene pushed on top
  resume(result) {}  // top scene popped, this is top again; result = popped scene's return value
  update(dt) {}      // called only if this scene is top, OR below a scene marked updateBelow
  render(ctx, alpha) {} // called for every scene from the lowest visible one up (see below)
  opaque = true;     // false → scenes below still render (pause overlay over frozen gameplay)
  updateBelow = false; // true → the scene below keeps updating (non-modal HUD overlays)
}
```

Manager rules (full implementation: `examples.md` §1):

- `push(scene)` → `top.pause()`, `scene.enter()`. `pop(result)` → `top.exit()`, `newTop.resume(result)`. `replace(scene)` → exit all or just top per need (`switchTo` that clears the stack is the common variant for title→game).
- **Render pass**: find the deepest scene from the top that is `opaque`, render from it upward. Pause menu (`opaque = false`) over gameplay renders the frozen game underneath, then the overlay.
- **Update pass**: top scene always; walk down while scenes set `updateBelow`.
- Defer stack mutations requested mid-update to end-of-frame (queue them) — mutating the stack while iterating it is a classic corruption bug.
- Transitions (fade/slide) are themselves easiest as a pushed `TransitionScene` that renders the fade and pops itself, or as manager-level alpha handling. Keep gameplay ignorant of transitions.

Standard flow: `Boot → Preload → Title ⇄ Settings; Title → Game; Game + push(Pause); Game → replace(GameOver) → Title`.

## 6. State machines

Two distinct layers; don't conflate them:

- **App/flow state** = the scene stack (§5). "Am I on the title screen or paused" is not an enum in gameplay code — it's which scenes are stacked.
- **Entity state** (player: idle/run/jump/fall; enemy AI states): explicit FSM per entity. Minimal robust form:

```js
class FSM {
  constructor(owner, states, initial) { this.owner = owner; this.states = states; this.set(initial); }
  set(name, params) {
    this.states[this.name]?.exit?.(this.owner);
    this.name = name; this.t = 0;
    this.states[name].enter?.(this.owner, params);
  }
  update(dt) {
    this.t += dt;
    const next = this.states[this.name].update?.(this.owner, dt, this.t);
    if (next) this.set(next); // update returns a state name to transition
  }
}
```

Rules that keep FSMs sane: transitions happen in exactly one place (`set`); states own their enter/exit side effects (animation, sfx, hitboxes); `this.t` (time-in-state) is the most-used variable in game feel code — build it in. Hierarchical machines, transition tables, and AI depth: `game-state-machine`.

## 7. Entity architecture

Three tiers — pick by game size, and **start smaller than you think**:

1. **Plain objects + arrays** (jam / small game): `const bullets = []`, each `{x,y,vx,vy,dead}`; systems are plain functions `updateBullets(dt)`. Honest, fast, zero abstraction tax. Most single-mechanic games never need more.
2. **Entity base class + composition** (mid-size): `Entity` with `update/render/dead`; behaviors composed as owned components (`this.body = new Body()`, `this.fsm = new FSM(...)`) — composition over inheritance; inheritance trees (`Enemy extends Actor extends Sprite`) rot fast. A single `world` holding typed arrays of entities (`world.enemies`, `world.bullets`) beats one mega-array plus `instanceof` filtering — iteration and collision pairing become trivial.
3. **ECS** (large / perf-critical): entities are ids, components are data in flat arrays, systems iterate component sets. Wins when entity counts are high (thousands) and behaviors combinatorial. In JS its cache-locality benefits only fully materialize with typed-array storage — real engineering. **Do not cargo-cult ECS into a 20-entity puzzle game.**

Universal rules regardless of tier:

- **Deferred death**: mark `dead = true` during update; sweep once after the update pass (`arr = arr.filter(e => !e.dead)` or swap-remove). Splicing mid-iteration skips entities.
- **Deferred spawn**: push into a `pending` list, append after the pass — spawning mid-iteration mutates the array being walked.
- Pool high-churn entities (bullets, particles): `build-and-deploy.md` §8, pool code `examples.md` §5.
- Update order must be explicit and stable (§10).

## 8. Events (decoupling)

A tiny pub/sub bus decouples gameplay from presentation: gameplay emits facts (`bus.emit('enemy-died', e)`); audio/UI/particles subscribe. Gameplay never calls `audio.play` directly — that coupling is what makes systems untestable and un-reusable.

```js
class Bus {
  #m = new Map();
  on(t, fn) { (this.#m.get(t) ?? this.#m.set(t, new Set()).get(t)).add(fn); return () => this.#m.get(t)?.delete(fn); }
  emit(t, data) { this.#m.get(t)?.forEach(fn => fn(data)); }
}
```

Discipline: events are **past-tense facts**, not commands (`'coin-collected'`, not `'play-coin-sound'`); subscribers must not mutate gameplay state that the emitting system is mid-iterating (defer via queue if needed); scenes store the unsubscribe functions returned by `on` and call them in `exit()` — leaked subscriptions from dead scenes are the #1 bus bug (double sounds after every restart).

## 9. Timers & tweens on the game clock

Anything time-based in gameplay runs on **game time** (§3), never `setTimeout` (ignores pause, throttles in background, unsynced with sim):

```js
class Timers {
  list = [];
  after(delay, fn) { const t = { at: clock.t + delay, fn }; this.list.push(t); return t; }
  update() {
    for (const t of this.list) if (!t.done && clock.t >= t.at) { t.done = true; t.fn(); }
    this.list = this.list.filter(t => !t.done);
  }
}
```

Tweens likewise: advance `elapsed` by game dt, `p = clamp(elapsed/duration)`, apply `ease(p)`, done at p=1 (fire onComplete once). Easing set that covers 95% of game feel: `easeOutCubic` (UI in), `easeInCubic` (UI out), `easeOutBack` (pop/overshoot), `easeOutElastic` (juicy lands). Deeper tween patterns: `game-tween-animation`. UI-only animation may run on unscaled time so menus stay lively during pause — decide per tween via a flag, not a second tween system.

## 10. Determinism & seeded RNG

`Math.random()` is unseedable — replays, daily-challenge seeds, and reproducible bug reports all require your own PRNG:

```js
function mulberry32(seed) {           // tiny, fast, good-enough distribution for games
  let a = seed >>> 0;
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
```

- **Two streams minimum**: `rngSim(seed)` for gameplay (deterministic), `rngFx()` for cosmetics (particles, pitch variance). Cosmetic draws consuming the sim stream silently desyncs replays.
- Full determinism additionally requires: fixed timestep (§2.2 — non-negotiable), stable iteration order (arrays, not object-key order), no gameplay reads of wall time, and inputs recorded per *simulation step index* (that's the whole replay format: seed + per-step input list).
- Daily challenge seed: `hash(dateString)` → seed. Same puzzle for everyone, no server.

## 11. Update ordering

Within one simulation step, order is a design decision — make it explicit and constant, because "sometimes the bullet hits, sometimes not, same setup" bugs are almost always order-instability:

```
1. timers/tweens (game-clock)       4. physics integrate + collide
2. read input → intents             5. post-collision reactions (damage, pickups; via events/queues)
3. AI / controllers (set velocities) 6. deferred spawn/despawn sweep
                                     7. camera (after final positions)   [render interpolates later]
```

Camera strictly after movement, or the view lags a frame behind the player. Spawn/despawn strictly last (§7). If two systems mutating shared state have unclear precedence, route one through the event queue so it happens in a defined phase.
