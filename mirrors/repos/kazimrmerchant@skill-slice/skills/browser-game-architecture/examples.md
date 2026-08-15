# browser-game-architecture — worked examples

Complete, runnable code. §1 is a full game in one file demonstrating the whole spine; §2–§8 are standalone drop-in modules. Every pattern here is explained in `reference.md` / `loop-and-state.md` — section pointers inline.

---

## 1. Complete minimal game (single HTML file)

A finished micro-game ("Dodger") exercising the entire architecture: fixed-timestep loop with render interpolation, scene stack (title / game / translucent pause / game over), action-safe input (keyboard + pointer, edge handling correct under fixed timestep), Web Audio unlock + synth SFX (zero assets), versioned localStorage save with flush-on-hide, DPR-aware letterbox scaling, lifecycle pause, crash overlay. Serve or open directly — no build step.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover, user-scalable=no">
<title>Dodger — browser-game-architecture demo</title>
<style>
  html, body { margin:0; height:100%; overflow:hidden; background:#000; overscroll-behavior:none; }
  #wrap { display:grid; place-items:center; height:100dvh; }
  canvas { touch-action:none; -webkit-tap-highlight-color:transparent;
           user-select:none; -webkit-user-select:none; }
</style>
</head>
<body>
<div id="wrap"><canvas id="game"></canvas></div>
<script>
'use strict';
const W = 960, H = 540;                    // logical resolution (reference.md §6.1)
const STEP = 1/60, MAX_DT = 0.25, MAX_STEPS = 5;

// ---------- crash overlay (reference.md §9) ----------
function crash(msg) {
  const d = document.createElement('div');
  d.style.cssText = 'position:fixed;inset:0;background:#200;color:#fcc;' +
    'font:14px/1.5 monospace;padding:24px;z-index:9;white-space:pre-wrap;';
  d.textContent = 'The game crashed.\n\n' + msg + '\n\nReload to try again.';
  document.body.appendChild(d);
}
addEventListener('error', e => crash(e.message + '\n' + e.filename + ':' + e.lineno));
addEventListener('unhandledrejection', e => crash(String(e.reason)));

// ---------- display: DPR-aware letterbox (reference.md §6.3) ----------
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d', { alpha: false });
function resize() {
  const dpr = Math.min(devicePixelRatio || 1, 2);
  const s = Math.min(innerWidth / W, innerHeight / H);
  const cssW = Math.floor(W * s), cssH = Math.floor(H * s);
  canvas.style.width = cssW + 'px'; canvas.style.height = cssH + 'px';
  canvas.width = Math.round(cssW * dpr); canvas.height = Math.round(cssH * dpr);
  ctx.setTransform(canvas.width / W, 0, 0, canvas.height / H, 0, 0);
}
addEventListener('resize', resize); resize();

// ---------- audio: unlock + synth (reference.md §3) ----------
const audio = {
  ctx: null, master: null, unlocked: false, enabled: true,
  init() {
    if (this.ctx) return;
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return;
    this.ctx = new AC();
    this.master = this.ctx.createGain();
    this.master.gain.value = 0.5;
    this.master.connect(this.ctx.destination);
  },
  unlock() {                                   // call from any user-gesture handler; idempotent
    this.init();
    if (!this.ctx || this.unlocked) return;
    this.ctx.resume().then(() => { this.unlocked = this.ctx.state === 'running'; });
    const b = this.ctx.createBuffer(1, 1, 22050);          // iOS belt-and-braces
    const s = this.ctx.createBufferSource();
    s.buffer = b; s.connect(this.master); s.start(0);
  },
  beep(freq = 440, dur = 0.08, type = 'square', vol = 0.2) {
    if (!this.ctx || !this.unlocked || !this.enabled) return;
    const t = this.ctx.currentTime;
    const o = this.ctx.createOscillator(), g = this.ctx.createGain();
    o.type = type; o.frequency.value = freq;
    g.gain.setValueAtTime(vol, t);
    g.gain.exponentialRampToValueAtTime(0.001, t + dur);
    o.connect(g); g.connect(this.master);
    o.start(t); o.stop(t + dur + 0.02);
  },
  suspend() { this.ctx?.suspend(); },
  resume() { if (this.unlocked) this.ctx?.resume(); },
};

// ---------- save: versioned + guarded (reference.md §5) ----------
const save = {
  KEY: 'dodger.save', V: 1, ok: true,
  data: { v: 1, best: 0 },
  load() {
    try {
      const parsed = JSON.parse(localStorage.getItem(this.KEY) ?? 'null');
      if (parsed && typeof parsed.best === 'number')       // validate; garbage → defaults
        this.data = { v: this.V, best: parsed.best };
    } catch { this.ok = false; }                           // private mode etc. → in-memory only
  },
  flush() {
    try { localStorage.setItem(this.KEY, JSON.stringify(this.data)); }
    catch { this.ok = false; }
  },
};
save.load();

// ---------- input: edges correct under fixed timestep (reference.md §2, loop-and-state.md §2.4) ----------
const input = {
  down: new Set(), pending: new Set(), pressed: new Set(),
  pointer: { x: W / 2, y: H / 2, held: false },
  isDown(c) { return this.down.has(c); },
  justPressed(c) { return this.pressed.has(c); },
  beginStep() {                                            // called at each SIM step, not per rAF frame
    this.pressed.clear();
    for (const c of this.pending) this.pressed.add(c);
    this.pending.clear();
  },
};
const GAME_KEYS = new Set(['ArrowLeft','ArrowRight','KeyA','KeyD','Space','Escape','Enter']);
addEventListener('keydown', e => {
  if (e.repeat) return;
  if (GAME_KEYS.has(e.code)) e.preventDefault();           // stop Space/arrows scrolling
  input.down.add(e.code); input.pending.add(e.code);
  audio.unlock();
});
addEventListener('keyup', e => input.down.delete(e.code));
addEventListener('blur', () => input.down.clear());        // no stuck keys after alt-tab
function toGame(e) {                                       // CSS px → logical units
  const r = canvas.getBoundingClientRect();
  return { x: (e.clientX - r.left) / r.width * W, y: (e.clientY - r.top) / r.height * H };
}
canvas.addEventListener('pointerdown', e => {
  canvas.setPointerCapture(e.pointerId);
  Object.assign(input.pointer, toGame(e), { held: true });
  input.pending.add('PointerDown');
  audio.unlock();
});
canvas.addEventListener('pointermove', e => { if (input.pointer.held) Object.assign(input.pointer, toGame(e)); });
canvas.addEventListener('pointerup', () => { input.pointer.held = false; });
canvas.addEventListener('pointercancel', () => { input.pointer.held = false; });

// ---------- scene stack (loop-and-state.md §5) ----------
const scenes = {
  stack: [], ops: [],                                      // ops: deferred mutations
  push(s, p)     { this.ops.push(() => { this.top()?.pause?.(); this.stack.push(s); s.enter?.(p); }); },
  pop(result)    { this.ops.push(() => { this.stack.pop()?.exit?.(); this.top()?.resume?.(result); }); },
  switchTo(s, p) { this.ops.push(() => { while (this.stack.length) this.stack.pop().exit?.(); this.stack.push(s); s.enter?.(p); }); },
  top() { return this.stack[this.stack.length - 1]; },
  applyOps() { for (const op of this.ops) op(); this.ops.length = 0; },
  update(dt) { this.top()?.update?.(dt); this.applyOps(); },
  render(ctx, alpha) {                                     // render from deepest opaque scene upward
    let i = this.stack.length - 1;
    while (i > 0 && this.stack[i].opaque === false) i--;
    for (; i < this.stack.length; i++) this.stack[i].render?.(ctx, alpha);
  },
};

// ---------- scenes ----------
const title = {
  update() {
    if (input.justPressed('Space') || input.justPressed('Enter') || input.justPressed('PointerDown')) {
      audio.beep(660, 0.1, 'triangle');                    // audible = unlock worked
      scenes.switchTo(game);
    }
  },
  render(ctx) {
    ctx.fillStyle = '#101018'; ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = '#e8e6df'; ctx.textAlign = 'center';
    ctx.font = 'bold 64px system-ui, sans-serif';
    ctx.fillText('DODGER', W / 2, 220);
    ctx.font = '24px system-ui, sans-serif';
    ctx.fillText('click / tap / space to start', W / 2, 300);   // the click IS the audio unlock
    ctx.fillText('best: ' + save.data.best, W / 2, 350);
  },
};

const game = {
  enter() {                                                // switchTo reuses this object → reset here
    this.player = { x: W / 2, px: W / 2, y: H - 60, w: 40, h: 40, speed: 420 };
    this.obstacles = [];                                   // pool these in a real game (§5)
    this.spawnT = 0; this.score = 0; this.time = 0;
  },
  update(dt) {
    if (input.justPressed('Escape')) { scenes.push(pause); return; }
    this.time += dt;
    const spawnEvery = Math.max(0.35, 0.9 - this.time * 0.01);

    const p = this.player;
    p.px = p.x;                                            // snapshot for render interpolation
    let dir = (input.isDown('ArrowRight') || input.isDown('KeyD') ? 1 : 0)
            - (input.isDown('ArrowLeft')  || input.isDown('KeyA') ? 1 : 0);
    if (input.pointer.held && Math.abs(input.pointer.x - p.x) > 4)
      dir = Math.sign(input.pointer.x - p.x);
    p.x = Math.max(p.w / 2, Math.min(W - p.w / 2, p.x + dir * p.speed * dt));

    this.spawnT += dt;
    if (this.spawnT >= spawnEvery) {
      this.spawnT -= spawnEvery;
      const size = 24 + Math.random() * 36;
      this.obstacles.push({ x: size / 2 + Math.random() * (W - size), y: -size, py: -size,
                            size, vy: 180 + this.time * 6, dead: false });
    }
    for (const o of this.obstacles) {
      o.py = o.y; o.y += o.vy * dt;
      if (o.y - o.size / 2 > H) { o.dead = true; this.score++; audio.beep(880, 0.05, 'sine', 0.08); }
      if (Math.abs(o.x - p.x) < (o.size + p.w) / 2 &&      // AABB overlap = death
          Math.abs(o.y - p.y) < (o.size + p.h) / 2) {
        audio.beep(120, 0.3, 'sawtooth', 0.25);
        save.data.best = Math.max(save.data.best, this.score);
        save.flush();                                      // immediate write on checkpoint
        scenes.switchTo(gameover, { score: this.score });
        return;
      }
    }
    this.obstacles = this.obstacles.filter(o => !o.dead);  // deferred-death sweep (loop-and-state.md §7)
  },
  render(ctx, alpha) {
    ctx.fillStyle = '#101018'; ctx.fillRect(0, 0, W, H);
    const p = this.player;
    const px = p.px + (p.x - p.px) * alpha;                // render interpolation (loop-and-state.md §2.2)
    ctx.fillStyle = '#7ec8a9';
    ctx.fillRect(px - p.w / 2, p.y - p.h / 2, p.w, p.h);
    ctx.fillStyle = '#d87060';
    for (const o of this.obstacles) {
      const oy = o.py + (o.y - o.py) * alpha;
      ctx.fillRect(o.x - o.size / 2, oy - o.size / 2, o.size, o.size);
    }
    ctx.fillStyle = '#e8e6df'; ctx.textAlign = 'left';
    ctx.font = '22px system-ui, sans-serif';
    ctx.fillText('score ' + this.score + '   best ' + save.data.best, 16, 32);
  },
};

const pause = {
  opaque: false,                                           // frozen gameplay renders underneath
  update() {
    if (input.justPressed('Escape') || input.justPressed('Space') || input.justPressed('PointerDown'))
      scenes.pop();
  },
  render(ctx) {
    ctx.fillStyle = 'rgba(0,0,0,0.55)'; ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = '#e8e6df'; ctx.textAlign = 'center';
    ctx.font = 'bold 44px system-ui, sans-serif';
    ctx.fillText('PAUSED', W / 2, H / 2 - 10);
    ctx.font = '22px system-ui, sans-serif';
    ctx.fillText('esc / tap to resume', W / 2, H / 2 + 34);
  },
};

const gameover = {
  enter(p) { this.score = p.score; this.t = 0; },
  update(dt) {
    this.t += dt;                                          // input grace so a death-tap doesn't instant-restart
    if (this.t > 0.5 && (input.justPressed('Space') || input.justPressed('Enter') || input.justPressed('PointerDown')))
      scenes.switchTo(game);
  },
  render(ctx) {
    ctx.fillStyle = '#181014'; ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = '#e8e6df'; ctx.textAlign = 'center';
    ctx.font = 'bold 52px system-ui, sans-serif';
    ctx.fillText('GAME OVER', W / 2, 230);
    ctx.font = '26px system-ui, sans-serif';
    ctx.fillText('score ' + this.score + '   best ' + save.data.best, W / 2, 290);
    if (this.t > 0.5) ctx.fillText('tap / space to retry', W / 2, 340);
  },
};

// ---------- loop: fixed timestep + interpolation (loop-and-state.md §2.2) ----------
let last, acc = 0;
function frame(now) {
  requestAnimationFrame(frame);
  const dt = Math.min((now - (last ?? now)) / 1000, MAX_DT);   // clamp: tab-return, breakpoints
  last = now;
  acc += dt;
  let steps = 0;
  while (acc >= STEP && steps < MAX_STEPS) {
    input.beginStep();                                     // edges consumed by SIM steps
    scenes.update(STEP);
    acc -= STEP; steps++;
  }
  if (steps === MAX_STEPS) acc = 0;                        // spiral-of-death guard
  scenes.render(ctx, acc / STEP);
}

// ---------- lifecycle (reference.md §7) ----------
addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'hidden') {
    if (scenes.top() === game) { scenes.push(pause); scenes.applyOps(); }
    audio.suspend();                                       // Web Audio keeps playing in hidden tabs otherwise
    save.flush();                                          // the reliable last-chance save hook
    last = undefined;                                      // + dt clamp = no time explosion on return
  } else {
    audio.resume();
  }
});
addEventListener('pagehide', () => save.flush());

// ---------- boot ----------
scenes.push(title); scenes.applyOps();
requestAnimationFrame(frame);
</script>
</body>
</html>
```

---

## 2. AssetLoader (manifest + progress + retry + fonts) — `reference.md` §4

```js
export class AssetLoader {
  images = new Map(); audio = new Map(); json = new Map();
  constructor(audioCtx) { this.ctx = audioCtx; }            // AudioContext for decodeAudioData

  /** manifest: { images:{name:url}, audio:{name:url}, json:{name:url}, fonts:{name:[family,url]} } */
  async loadAll(manifest, onProgress = () => {}) {
    const jobs = [];
    for (const [n, url] of Object.entries(manifest.images ?? {})) jobs.push({ store: this.images, n, fn: () => this.#image(url) });
    for (const [n, url] of Object.entries(manifest.audio  ?? {})) jobs.push({ store: this.audio,  n, fn: () => this.#audio(url) });
    for (const [n, url] of Object.entries(manifest.json   ?? {})) jobs.push({ store: this.json,   n, fn: () => this.#json(url) });
    for (const [n, [family, url]] of Object.entries(manifest.fonts ?? {})) jobs.push({ store: null, n, fn: () => this.#font(family, url) });
    let done = 0;
    await Promise.all(jobs.map(async (j) => {
      const value = await this.#retry(j.fn, j.n);
      j.store?.set(j.n, value);
      onProgress(++done, jobs.length);                      // progress by items — fine for games
    }));
  }

  async #retry(fn, name, tries = 2) {                       // retry once, then fail loudly with the asset name
    for (let i = 0; ; i++) {
      try { return await fn(); }
      catch (err) { if (i >= tries - 1) throw new Error(`Failed to load "${name}": ${err?.message ?? err}`); }
    }
  }
  async #fetch(url) {
    const r = await fetch(url);
    if (!r.ok) throw new Error(`HTTP ${r.status} ${url}`);
    return r;
  }
  async #image(url) {                                       // createImageBitmap = off-main-thread decode
    const blob = await (await this.#fetch(url)).blob();
    if ('createImageBitmap' in window) return createImageBitmap(blob);
    return new Promise((res, rej) => {                      // fallback path
      const img = new Image();
      img.onload = () => { URL.revokeObjectURL(img.src); res(img); };
      img.onerror = rej;
      img.src = URL.createObjectURL(blob);
    });
  }
  async #audio(url) {
    const ab = await (await this.#fetch(url)).arrayBuffer();
    return this.ctx.decodeAudioData(ab);
  }
  async #json(url) { return (await this.#fetch(url)).json(); }
  async #font(family, url) {                                // block preload on fonts or canvas text renders fallback
    const face = new FontFace(family, `url(${url})`);
    document.fonts.add(await face.load());
  }
}

// Preload scene usage:
//   await assets.loadAll(MANIFEST, (d, t) => { progress = d / t; });  // render() draws the bar
//   scenes.switchTo(titleScene);
// Catch the rejection and show a real error screen — never a stuck bar (reference.md §4.5).
```

---

## 3. AudioManager (buses, SFX variance, music crossfade) — `reference.md` §3

```js
export class AudioManager {
  constructor() {
    const AC = window.AudioContext || window.webkitAudioContext;
    this.ctx = new AC();                                    // ONE context for the whole game
    this.master   = this.#gain(this.ctx.destination, 1);
    this.musicBus = this.#gain(this.master, 0.8);
    this.sfxBus   = this.#gain(this.master, 1);
    this.buffers = new Map();
    this.currentMusic = null;
    this.unlocked = false;
    const unlock = () => this.unlock();
    addEventListener('pointerdown', unlock);
    addEventListener('keydown', unlock);
    addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden') this.ctx.suspend();
      else if (this.unlocked) this.ctx.resume();
    });
  }
  #gain(dest, v) { const g = this.ctx.createGain(); g.gain.value = v; g.connect(dest); return g; }

  unlock() {
    if (this.unlocked) return;
    this.ctx.resume().then(() => { this.unlocked = this.ctx.state === 'running'; });
    const s = this.ctx.createBufferSource();                // iOS silent-buffer kick
    s.buffer = this.ctx.createBuffer(1, 1, 22050);
    s.connect(this.master); s.start(0);
  }

  add(name, audioBuffer) { this.buffers.set(name, audioBuffer); }  // from AssetLoader.audio

  play(name, { vol = 1, rate = 1, vary = 0.06 } = {}) {
    const buf = this.buffers.get(name);
    if (!buf || !this.unlocked) return;
    const src = this.ctx.createBufferSource();
    src.buffer = buf;
    src.playbackRate.value = rate * (1 - vary / 2 + Math.random() * vary); // defeats machine-gun repetition
    const g = this.#gain(this.sfxBus, vol);
    src.connect(g);
    src.start();
    return src;                                             // caller may .stop() early
  }

  playMusic(name, { fade = 1, loop = true } = {}) {
    if (this.currentMusic?.name === name) return;
    const t = this.ctx.currentTime;
    if (this.currentMusic) {                                // crossfade out the old track
      const old = this.currentMusic;
      old.gain.gain.setTargetAtTime(0, t, fade / 3);
      old.src.stop(t + fade);
    }
    const src = this.ctx.createBufferSource();
    src.buffer = this.buffers.get(name);
    src.loop = loop;                                        // decoded-buffer looping is gapless
    const gain = this.#gain(this.musicBus, 0);
    src.connect(gain);
    gain.gain.setTargetAtTime(1, t, fade / 3);              // ramps, never abrupt .value (clicks)
    src.start(t);
    this.currentMusic = { src, gain, name };
  }

  setVolume(bus /* 'master'|'musicBus'|'sfxBus' */, v) {
    this[bus].gain.setTargetAtTime(v, this.ctx.currentTime, 0.03);
  }
}
```

---

## 4. SaveManager (versioned, migrated, debounced, flushed) + IndexedDB helper — `reference.md` §5

```js
export class SaveManager {
  /** migrations: { 1: saveV1 => saveV2, 2: saveV2 => saveV3, ... } */
  constructor({ key, version, defaults, migrations = {}, debounceMs = 2000 }) {
    this.key = key; this.version = version; this.migrations = migrations;
    this.debounceMs = debounceMs; this.timer = null; this.persistent = true;
    this.data = structuredClone(defaults);
    this.#load(defaults);
    addEventListener('visibilitychange', () => {            // the reliable flush hooks
      if (document.visibilityState === 'hidden') this.flush();
    });
    addEventListener('pagehide', () => this.flush());
  }

  #load(defaults) {
    let raw = null;
    try { raw = localStorage.getItem(this.key); }
    catch { this.persistent = false; return; }               // private mode → in-memory session
    if (!raw) return;
    try {
      let save = JSON.parse(raw);
      if (typeof save !== 'object' || save === null) throw 0;
      let v = save.v ?? 1;
      while (v < this.version) {                             // walk the migration chain
        const step = this.migrations[v];
        if (!step) throw new Error(`no migration from v${v}`);
        save = step(save); v++; save.v = v;
      }
      this.data = { ...structuredClone(defaults), ...save, v: this.version }; // defaults fill new fields
    } catch { /* corrupt → keep defaults; optionally stash raw for support */ }
  }

  markDirty() {                                              // call after mutating .data
    clearTimeout(this.timer);
    this.timer = setTimeout(() => this.flush(), this.debounceMs);
  }
  flush() {
    clearTimeout(this.timer); this.timer = null;
    if (!this.persistent) return;
    try { localStorage.setItem(this.key, JSON.stringify({ ...this.data, v: this.version })); }
    catch { this.persistent = false; }                       // quota/denied → degrade silently once
  }

  export() { return btoa(unescape(encodeURIComponent(JSON.stringify(this.data)))); }
  import(str) {
    this.data = JSON.parse(decodeURIComponent(escape(atob(str))));
    this.flush();
  }
}

// Usage:
//   const save = new SaveManager({
//     key: 'mygame.save', version: 2,
//     defaults: { v: 2, best: 0, settings: { volume: 1 } },
//     migrations: { 1: s => ({ ...s, settings: { volume: s.volume ?? 1 } }) },
//   });
//   save.data.best = 42; save.markDirty();                  // autosaves ≤2s later; flushes on hide
```

Minimal promisified IndexedDB key-value store (only when data outgrows localStorage — `reference.md` §5.1):

```js
export function idbStore(dbName = 'game', storeName = 'kv') {
  const open = new Promise((res, rej) => {
    const req = indexedDB.open(dbName, 1);
    req.onupgradeneeded = () => req.result.createObjectStore(storeName);
    req.onsuccess = () => res(req.result);
    req.onerror = () => rej(req.error);
  });
  const tx = async (mode, fn) => {
    const db = await open;
    return new Promise((res, rej) => {
      const t = db.transaction(storeName, mode);
      const r = fn(t.objectStore(storeName));
      t.oncomplete = () => res(r.result);
      t.onerror = () => rej(t.error);
    });
  };
  return {
    get: (k) => tx('readonly',  s => s.get(k)),              // structured clone: objects/blobs/typed arrays OK
    set: (k, v) => tx('readwrite', s => s.put(v, k)),
    del: (k) => tx('readwrite', s => s.delete(k)),
  };
}
```

---

## 5. Object pool + pooled particles — `build-and-deploy.md` §8.1

```js
export class Pool {
  constructor(factory, reset, initial = 32) {
    this.factory = factory; this.reset = reset; this.free = [];
    for (let i = 0; i < initial; i++) this.free.push(factory());
  }
  get(...args) {
    const o = this.free.pop() ?? this.factory();             // grows on demand; prewarm sizes worst case
    this.reset(o, ...args);
    return o;
  }
  release(o) { this.free.push(o); }
}

// Pooled particle burst — zero allocation after warm-up:
const particles = [];
const particlePool = new Pool(
  () => ({ x: 0, y: 0, vx: 0, vy: 0, life: 0 }),
  (p, x, y) => {
    p.x = x; p.y = y;
    const a = Math.random() * Math.PI * 2, s = 60 + Math.random() * 120;
    p.vx = Math.cos(a) * s; p.vy = Math.sin(a) * s; p.life = 0.5;
  },
);
export function burst(x, y, n = 20) { for (let i = 0; i < n; i++) particles.push(particlePool.get(x, y)); }
export function updateParticles(dt) {
  for (let i = particles.length - 1; i >= 0; i--) {          // backward + swap-remove: O(1), no filter() alloc
    const p = particles[i];
    p.life -= dt;
    if (p.life <= 0) {
      particlePool.release(p);
      particles[i] = particles[particles.length - 1];
      particles.pop();
      continue;
    }
    p.x += p.vx * dt; p.y += p.vy * dt; p.vy += 300 * dt;
  }
}
export function renderParticles(ctx) {
  ctx.fillStyle = '#ffd27a';
  for (let i = 0; i < particles.length; i++) {
    const p = particles[i];
    ctx.globalAlpha = Math.max(p.life / 0.5, 0);
    ctx.fillRect(p.x - 2, p.y - 2, 4, 4);
  }
  ctx.globalAlpha = 1;
}
```

---

## 6. Service worker + registration with update prompt — `reference.md` §8.2

```js
// sw.js — at build output root (scope = its directory). NOT for itch.io (build-and-deploy.md §7).
const VERSION = 'v1.4.0';                                    // stamp from APP_VERSION at build time
const CACHE = `mygame-${VERSION}`;
const PRECACHE = ['./', './index.html' /* + generated asset list */];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(PRECACHE)));
});
self.addEventListener('activate', (e) => {                   // delete every older versioned cache
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});
self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);
  if (e.request.mode === 'navigate') {                       // shell: network-first, cache fallback
    e.respondWith(
      fetch(e.request).then(r => {
        const copy = r.clone();
        caches.open(CACHE).then(c => c.put('./index.html', copy));
        return r;
      }).catch(() => caches.match('./index.html'))
    );
    return;
  }
  e.respondWith(                                             // assets: cache-first
    caches.match(e.request).then(hit => hit ?? fetch(e.request).then(r => {
      if (r.ok && url.origin === location.origin) {
        const copy = r.clone();
        caches.open(CACHE).then(c => c.put(e.request, copy));
      }
      return r;
    }))
  );
});
self.addEventListener('message', (e) => { if (e.data === 'skip-waiting') self.skipWaiting(); });
```

```js
// main.js — register in production only; update = explicit user action, never mid-session swap
if (import.meta.env.PROD && 'serviceWorker' in navigator) {
  navigator.serviceWorker.register('./sw.js').then((reg) => {
    reg.addEventListener('updatefound', () => {
      const w = reg.installing;
      w.addEventListener('statechange', () => {
        if (w.state === 'installed' && navigator.serviceWorker.controller)
          showUpdateToast('Update available', () => w.postMessage('skip-waiting'));
      });
    });
  });
  navigator.serviceWorker.addEventListener('controllerchange', () => location.reload());
}
```

---

## 7. Ship config: Vite + scripts + GitHub Pages CI — `build-and-deploy.md` §2, §5–6

```js
// vite.config.js
import { defineConfig } from 'vite';
import pkg from './package.json';                            // vite config supports JSON imports

export default defineConfig({
  base: './',                                                // itch.io + Pages subpaths both need relative
  define: { APP_VERSION: JSON.stringify(pkg.version) },      // one constant: title screen, save, SW, ?v=
  build: { target: 'es2020', assetsInlineLimit: 4096 },
  server: { host: true },                                    // test on a real phone over LAN during dev
});
```

```jsonc
// package.json (scripts)
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "smoke": "node smoke.mjs",
    // butler: itch.io CLI. $npm_package_version is POSIX-shell syntax — on Windows run via Git Bash/WSL
    "deploy:itch": "npm run build && butler push dist USER/GAME:html5 --userversion $npm_package_version"
  }
}
```

```yaml
# .github/workflows/pages.yml — deploy dist/ to GitHub Pages on push to main
name: deploy
on: { push: { branches: [main] } }
permissions: { contents: read, pages: write, id-token: write }
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci && npm run build
      - uses: actions/upload-pages-artifact@v3
        with: { path: dist }
  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment: { name: github-pages }
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

---

## 8. Automated smoke test (Puppeteer) — `build-and-deploy.md` §9

Catches path 404s, boot crashes, and blank canvas on every deploy. Run `npm run preview` (serves `dist/` at `:4173`), then `node smoke.mjs`. Requires `npm i -D puppeteer`.

```js
// smoke.mjs
import puppeteer from 'puppeteer';

const URL = process.env.GAME_URL ?? 'http://localhost:4173';
const errors = [];

const browser = await puppeteer.launch();
const page = await browser.newPage();
page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
page.on('pageerror', e => errors.push(String(e)));
page.on('requestfailed', r => errors.push(`REQUEST FAILED ${r.url()}`));

await page.goto(URL, { waitUntil: 'networkidle0', timeout: 30000 });
await new Promise(r => setTimeout(r, 1000));                 // let boot/preload settle

// Blank check: canvas must not be one solid color. (2D canvas; for WebGL, screenshot-diff
// against a known-good image instead — the drawing buffer isn't readable by default.)
const blank = await page.evaluate(() => {
  const c = document.querySelector('canvas');
  if (!c) return 'no canvas found';
  const ctx = c.getContext('2d');
  if (!ctx) return false;                                    // non-2D context: skip pixel check
  const d = ctx.getImageData(0, 0, c.width, c.height).data;
  for (let i = 4; i < d.length; i += 4)
    if (d[i] !== d[0] || d[i + 1] !== d[1] || d[i + 2] !== d[2]) return false;
  return 'canvas is a solid color';
});

await page.mouse.click(400, 300);                            // gesture: audio unlock + start game
await new Promise(r => setTimeout(r, 2500));                 // run real gameplay frames
await page.screenshot({ path: 'smoke.png' });                // artifact for the record
await browser.close();

if (errors.length || blank) {
  console.error('SMOKE FAIL', { blank, errors });
  process.exit(1);
}
console.log('SMOKE PASS');
```
