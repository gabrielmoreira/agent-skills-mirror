# browser-game-architecture — subsystem reference

Deep reference for every subsystem of a browser game shell. Companion files: `loop-and-state.md` (loop, scenes, entities), `build-and-deploy.md` (tooling, shipping), `examples.md` (complete code).

---

## 1. Rendering backends

### 1.1 Choosing

| | Canvas 2D | WebGL (Three.js / Pixi) | DOM/CSS |
|---|---|---|---|
| Sweet spot | 2D arcade/action/puzzle, ≤ a few hundred draw calls | 3D; 2D with thousands of sprites, shaders, lighting | Board/card/word/menu games; UI-heavy |
| Text | Manual (`fillText`, no wrapping) | Hard (SDF/bitmap fonts or DOM overlay) | Free, accessible, selectable |
| Perf ceiling | CPU-bound rasterizer; fine to ~1–2k simple draws/frame | GPU; effectively unlimited for 2D | Layout engine; fine if only `transform`/`opacity` animate |
| Effort | Lowest | Highest | Low, until you fight layout |
| Accessibility | None built in (canvas is a bitmap) | None built in | Native (focus, screen readers) |

Hybrid (Canvas/WebGL playfield + DOM overlay for HUD/menus/dialogs) is the recommended default for anything with real UI. Position the overlay with absolute positioning over the canvas, `pointer-events: none` on the container and `pointer-events: auto` on interactive children so gameplay input passes through.

### 1.2 Canvas 2D setup

```js
const canvas = document.querySelector('#game');
const ctx = canvas.getContext('2d', { alpha: false }); // opaque = faster compositing
```

- `{ alpha: false }` when the canvas has no transparent background — lets the compositor skip blending with the page.
- `ctx.imageSmoothingEnabled = false` for pixel art (set it after every canvas resize — resizing resets context state).
- Sizing/DPR: §6. **Setting `canvas.width` clears the canvas and resets all context state** (transforms, smoothing, fillStyle) — re-apply after resize.
- Layering: multiple stacked canvases (static background / gameplay / FX) let you redraw only layers that change. Worth it only when a full-scene redraw measurably exceeds budget; start with one canvas.
- Static backgrounds: pre-render once into an offscreen canvas (`document.createElement('canvas')` or `new OffscreenCanvas(w,h)`), then blit with one `drawImage` per frame.
- Sprite atlases: pack sprites into one image, draw with the 9-arg `drawImage(img, sx, sy, sw, sh, dx, dy, dw, dh)`. One decoded image beats 50 small ones for cache and load behavior.
- Text: `fillText` is surprisingly expensive; cache rendered text to offscreen canvases if drawn every frame. Wait for `document.fonts.ready` (or `document.fonts.load('16px GameFont')`) before first canvas text render or you'll rasterize fallback-font text.
- Avoid per-frame `ctx.save()/restore()` chains deeper than needed and avoid `getImageData` in hot paths (GPU→CPU sync stall). For per-pixel work, do it once into an offscreen buffer.

### 1.3 WebGL / Three.js

Setup, materials, loaders, dispose, postprocessing: **defer to `threejs-game-development`** — do not duplicate here. What this skill owns even in a WebGL game:

- The loop, scenes, input, audio, save, scaling shell around the renderer (renderer's render call is invoked from *this* skill's loop, in the render phase, with interpolation alpha).
- **Context loss**: mandatory in production.

```js
canvas.addEventListener('webglcontextlost', (e) => {
  e.preventDefault();          // signals "I will restore" — without this, restore never fires
  loop.stop(); audio.duck();
});
canvas.addEventListener('webglcontextrestored', () => {
  recreateGPUResources();      // textures/buffers/programs are gone; re-upload all
  loop.start();
});
```

- Cap `renderer.setPixelRatio(Math.min(devicePixelRatio, 2))` — DPR 3 phones will melt at native res.

### 1.4 DOM/CSS games

- Animate **only `transform` and `opacity`** (compositor-only; no layout/paint). Never animate `top/left/width/margin`.
- Batch reads before writes each frame; interleaved `offsetWidth` reads and style writes force synchronous layout ("layout thrashing").
- `will-change: transform` on the handful of elements that animate constantly — not on everything (each promoted layer costs memory).
- Use CSS transitions/animations for fire-and-forget effects; drive continuous motion from the rAF loop by writing `style.transform`.
- Disable text selection and callouts on game elements: `user-select: none; -webkit-user-select: none; -webkit-touch-callout: none;`.
- You keep free accessibility — preserve it: real `<button>`s, focus outlines on keyboard focus (`:focus-visible`), `aria-live="polite"` for score changes.

---

## 2. Input

Architecture: **device listeners write into a state object; gameplay reads named actions**. Gameplay code never touches `KeyboardEvent`. This gives rebinding, multi-device support, and replay/testing hooks for free. (Theory depth: `game-input-handling`.)

### 2.1 Keyboard

```js
const down = new Set(), pressed = new Set(); // pressed = this-frame edges
addEventListener('keydown', (e) => {
  if (e.repeat) return;                              // ignore OS auto-repeat
  if (GAME_KEYS.has(e.code)) e.preventDefault();     // stop Space/arrows scrolling the page
  if (!down.has(e.code)) pressed.add(e.code);
  down.add(e.code);
});
addEventListener('keyup', (e) => down.delete(e.code));
addEventListener('blur', () => down.clear());        // alt-tab with a key held = stuck key without this
// input.update() at the END of each simulation tick: pressed.clear()
```

- **`e.code` for positional bindings** (`'KeyW'`, `'Space'`, `'ArrowLeft'`) — WASD stays a left-hand cluster on AZERTY/Dvorak. **`e.key` for semantic/typed input** (name entry, "press M for map" where the letter matters).
- Also clear held state on `visibilitychange → hidden`.
- Don't `preventDefault()` everything — keep F5/F12/Cmd+R working; guard only the keys you use.
- Listeners on `window`, not the canvas (canvas isn't focusable by default; if you need scoped listening, add `tabindex="0"` and manage focus).

### 2.2 Pointer (mouse + touch + pen, unified)

Use **Pointer Events** — one code path for all devices; do not write separate mouse/touch handlers.

```css
#game { touch-action: none; } /* stop browser pan/zoom gestures on the game surface */
```

```js
canvas.addEventListener('pointerdown', (e) => {
  canvas.setPointerCapture(e.pointerId); // keep receiving moves after leaving the element
  addPointer(e);
});
canvas.addEventListener('pointermove', (e) => movePointer(e));
canvas.addEventListener('pointerup', (e) => removePointer(e));
canvas.addEventListener('pointercancel', (e) => removePointer(e)); // OS gesture stole it — treat as release, always handle
```

Coordinate conversion (CSS px → logical game units) — required whenever the canvas is CSS-scaled or letterboxed:

```js
function toGame(e) {
  const r = canvas.getBoundingClientRect();
  return {
    x: (e.clientX - r.left) / r.width  * LOGICAL_W,
    y: (e.clientY - r.top)  / r.height * LOGICAL_H,
  };
}
```

Multi-touch: key pointers by `e.pointerId` in a Map. A virtual joystick is: `pointerdown` in the left half anchors the stick at the touch point; `pointermove` gives a clamped offset vector; `pointerup/cancel` releases. Buttons live in the right half keyed by their own pointerIds.

Also on mobile: `-webkit-tap-highlight-color: transparent;` on the game surface; `contextmenu` → `preventDefault()` if long-press/right-click matters; iOS pinch: Safari may still fire `gesturestart` — `preventDefault()` it.

### 2.3 Gamepad

Event-driven for connection, **polled** for state (the Gamepad API has no button events):

```js
let padIndex = null;
addEventListener('gamepadconnected', (e) => { padIndex ??= e.gamepad.index; showToast('Gamepad connected'); });
addEventListener('gamepaddisconnected', (e) => { if (e.gamepad.index === padIndex) { padIndex = null; pauseGame(); } });

function pollPad() { // call once per simulation tick
  if (padIndex === null) return null;
  const gp = navigator.getGamepads()[padIndex];   // fresh snapshot every poll — objects are not live in all browsers
  if (!gp) return null;
  const dz = 0.15, ax = gp.axes[0], ay = gp.axes[1];
  const mag = Math.hypot(ax, ay);
  const move = mag < dz ? {x:0,y:0}
    : { x: ax/mag * (mag-dz)/(1-dz), y: ay/mag * (mag-dz)/(1-dz) }; // radial deadzone, rescaled
  return { move, jump: gp.buttons[0].pressed, dash: gp.buttons[1].pressed }; // standard mapping: 0=A/×, 1=B/○
}
```

- Radial deadzone (shown) beats per-axis deadzone (per-axis makes diagonals feel notched).
- Chrome requires a button press before gamepads appear — show "press any button" on the input settings screen.
- Pause the game on disconnect; it's a hardware event mid-play.

### 2.4 Action mapping layer

```js
const BINDINGS = {
  left:  ['KeyA', 'ArrowLeft'],
  right: ['KeyD', 'ArrowRight'],
  jump:  ['Space', 'KeyZ'],
  pause: ['Escape', 'KeyP'],
};
// input.isDown('jump'), input.justPressed('jump'), input.axis('left','right') → -1..1
```

Merge keyboard + gamepad + touch into these actions inside the input system. `justPressed` edges are consumed by the **simulation tick**, not the render frame — with a fixed-timestep loop, clear edge sets after simulation steps run, or a press landing on a 0-step frame gets lost (see `loop-and-state.md` §2.4). Jump buffering (accept a press up to ~100ms before landing) lives above this layer, in the controller.

---

## 3. Audio

(Theory depth: `game-audio-system`. This is the browser-specific shell.)

### 3.1 Autoplay policy and the unlock pattern

All browsers block audible playback until a user gesture. `new AudioContext()` before a gesture starts in state `'suspended'`. The pattern:

```js
class AudioSys {
  constructor() {
    this.ctx = new (window.AudioContext || window.webkitAudioContext)();
    this.master = this.ctx.createGain();
    this.music  = this.ctx.createGain();
    this.sfx    = this.ctx.createGain();
    this.music.connect(this.master); this.sfx.connect(this.master);
    this.master.connect(this.ctx.destination);
    this.unlocked = false;
  }
  unlock() { // call from the FIRST pointerdown/keydown; safe to call repeatedly
    if (this.unlocked) return;
    this.ctx.resume().then(() => { this.unlocked = this.ctx.state === 'running'; });
    // iOS belt-and-braces: play a silent buffer inside the gesture call stack
    const b = this.ctx.createBuffer(1, 1, 22050);
    const s = this.ctx.createBufferSource(); s.buffer = b; s.connect(this.master); s.start(0);
  }
}
addEventListener('pointerdown', () => audio.unlock(), { once: false });
addEventListener('keydown',     () => audio.unlock());
```

Design rule: **make the title screen require a click** ("Click / tap to start"). That single interaction unlocks audio deterministically; games that boot straight into gameplay end up with racy unlock bugs.

iOS extras: audio routes through the *ringer* switch for Web Audio in some iOS versions — if the phone is on silent, the game may be silent; nothing to fix, but don't chase it as a bug. After long backgrounding, `ctx.state` can be `'interrupted'`/`'suspended'` — re-`resume()` on `visibilitychange → visible`.

### 3.2 Web Audio vs `<audio>` elements

- **Web Audio (`AudioBufferSourceNode`)** for all SFX and for music you want gapless/looped: sample-accurate scheduling, overlapping instances, per-bus gain, effects. Buffer sources are one-shot — create a new source per play (cheap; the decoded buffer is shared).
- **`<audio>` element** (optionally piped through `createMediaElementSource`) only for long streamed music where you don't want the whole file decoded in memory. Looping `<audio>` has an audible gap in some browsers — for seamless loops, use a decoded buffer with `source.loop = true` and `loopStart/loopEnd`.

```js
play(name, { vol = 1, rate = 1 } = {}) {
  const src = this.ctx.createBufferSource();
  src.buffer = this.buffers.get(name);
  src.playbackRate.value = rate * (0.97 + Math.random() * 0.06); // ±3% pitch variance defeats machine-gun repetition
  const g = this.ctx.createGain(); g.gain.value = vol;
  src.connect(g); g.connect(this.sfx);
  src.start();
  return src;
}
```

- Volume changes: `gain.setTargetAtTime(v, ctx.currentTime, 0.03)` — never set `.value` abruptly on running audio (clicks). Music crossfade = two gains with opposing ramps.
- Persist volume settings via SaveManager; apply to bus gains at boot.
- **Never create more than one AudioContext.** Browsers cap concurrent contexts (~4–6); multiple contexts is the classic copy-paste bug when each module makes its own.

### 3.3 Formats and loading

- **MP3 or AAC (.m4a): universal**, use one of these as your only format. Dual-format (`.ogg` + `.m4a`) is legacy practice — only bother if you need Vorbis/Opus quality-per-byte and can ship fallbacks. Safari does not play Ogg containers.
- Load: `fetch(url).then(r => r.arrayBuffer()).then(ab => ctx.decodeAudioData(ab))`. Decoding is async but decoded PCM is big (~10MB/min stereo) — decode SFX and short loops eagerly, keep long music streamed or decode on scene entry.
- Procedural synth (oscillator + gain envelope) is a legitimate zero-asset alternative for jam games: sine/triangle osc → gain with exponential decay → bus. Keeps builds tiny.

### 3.4 Lifecycle integration

On `visibilitychange → hidden`: `ctx.suspend()` (rAF stops but Web Audio keeps playing — a hidden tab blasting music is a top player complaint). On visible: `resume()` only if the user had unlocked and audio was enabled.

---

## 4. Asset loading

### 4.1 Manifest + loader

Central manifest, typed by loader; a preload scene owns the load and draws progress. No gameplay module fetches its own assets ad hoc.

```js
const MANIFEST = {
  images: { player: './assets/player.png', tiles: './assets/tiles.png' },
  audio:  { jump: './assets/jump.m4a', music: './assets/theme.m4a' },
  json:   { level1: './assets/level1.json' },
  fonts:  { game: ['GameFont', './assets/gamefont.woff2'] },
};
```

Loader contract: `await assets.loadAll(MANIFEST, onProgress)` → resolves when everything is decoded and usable; `onProgress(done, total)` drives the bar. Count *completed items* (progress by items, not bytes, is fine for games). Full implementation: `examples.md` §2.

### 4.2 Images

- `createImageBitmap(blob)` decodes **off the main thread** — prefer it over `new Image()` for anything big; `img.decode()` is the fallback that at least avoids decode-on-first-draw jank.
- First-draw stutter: browsers may decode lazily; after load, draw each image once to a 1×1 offscreen canvas ("warm-up blit") during the load screen.
- Atlases over loose files (§1.2). Pixel-art: keep atlas ≤ 2048×2048 for old-mobile GPU safety when the atlas will become a WebGL texture.

### 4.3 Fonts

```js
const face = new FontFace('GameFont', 'url(./assets/gamefont.woff2)');
document.fonts.add(await face.load());
```

Canvas text rendered before the font is ready silently uses the fallback font and *stays wrong* in any cached text-canvas. Block the preload scene on font load. WOFF2 only (universal since 2016).

### 4.4 Audio and data

Audio per §3.3 (decode during preload; long music can lazy-load on scene entry). JSON via `fetch().then(r => r.json())`. Validate shape at load time — a level file failing at parse beats failing mid-gameplay.

### 4.5 Strategy

- **Small game (< ~10MB): load everything up front** behind one progress bar. Simplicity wins.
- Larger: split per-scene manifests; preload scene loads `core` (title + UI + player), gameplay scenes load their own chunk behind a mini-loader. Prefetch the *next* level during play (fire-and-forget `loadAll` without awaiting).
- Failures: retry once, then show a real error ("Failed to load — check connection, reload"), never a stuck bar. Loader wraps each fetch with retry + a name-tagged error.
- Cache-busting interplay with hashed filenames: `build-and-deploy.md` §10.

---

## 5. Persistence (save systems)

### 5.1 localStorage vs IndexedDB

| | localStorage | IndexedDB |
|---|---|---|
| API | Sync, strings only | Async, structured clone (objects, blobs, typed arrays) |
| Capacity | ~5MB/origin | Large (browser-managed quota, usually ≫ 50MB) |
| Use for | Settings, progress flags, high scores, small save slots — **the right choice for ~90% of games** | Level editors, replays, large blobs, downloaded asset caches |

localStorage's synchronous cost is irrelevant at game-save sizes (a few KB, written occasionally). Choose IndexedDB only when data is big or binary. If IndexedDB: use the tiny `idb` wrapper or a ~30-line promisified helper — raw IDB's event API is not worth hand-writing (helper in `examples.md` §4).

### 5.2 Non-negotiable rules (either backend)

1. **Wrap every access in try/catch.** Storage throws in some private modes, at quota, and under strict privacy settings. A game that crashes on save is worse than one that can't save — degrade to in-memory and tell the user once.
2. **Version the schema**: `{ v: 2, data: {...} }` with a migration table:

```js
const MIGRATIONS = {
  1: (s) => ({ ...s, settings: { volume: s.volume ?? 1 } }), // v1 → v2
};
function migrate(save) {
  let v = save.v ?? 1;
  while (v < CURRENT_V) { save = MIGRATIONS[v](save); v++; save.v = v; }
  return save;
}
```

3. **Validate on load**: `JSON.parse` in try/catch, check required fields, fall back to defaults on garbage. Corrupt saves happen (partial writes, users editing them).
4. **Namespace the key**: `'mygame.save.v-slot0'` — localStorage is per-origin, and itch.io-style hosting can put multiple games on one origin. (Note: itch.io serves uploads from per-game subdomains precisely to isolate storage, but never rely on hosting details.)
5. **Never store secrets or trust the data** — everything client-side is player-editable. Design so that cheating in a single-player save harms no one; server-authoritative anything is out of scope here.

### 5.3 When to write

- **Debounced autosave**: mark dirty on change, write at most every ~2s.
- **Flush on `visibilitychange → hidden`** — the *reliable* last-chance hook, including mobile task-switch/kill. Also flush on `pagehide`. **Do not rely on `beforeunload`** (doesn't fire on mobile process death) — use it only as an extra desktop flush.
- Immediate write on explicit checkpoints (level complete, purchase, settings change).

```js
addEventListener('visibilitychange', () => { if (document.visibilityState === 'hidden') save.flush(); });
addEventListener('pagehide', () => save.flush());
```

Full SaveManager (debounce + migrations + memory fallback): `examples.md` §4.

### 5.4 Durability honesty

Browser storage is **best-effort**: Safari deletes storage for sites unused ~7 days (as an installed PWA this doesn't apply); users clear site data. `navigator.storage.persist()` requests durability (often auto-granted for installed PWAs). For a free web game this is acceptable — but offer **export/import save** (serialize to a base64 string the player copies, or download/upload a `.json` file) if progress is many hours. Cloud saves need a backend — out of scope; note the itch.io caveat that different builds may not share storage, so don't promise persistence across game updates unless tested.

---

## 6. Responsive scaling & display

### 6.1 The three-resolution model

1. **Logical resolution** — fixed design-space units all gameplay/UI code uses (e.g. 960×540). Never changes at runtime.
2. **CSS size** — element size after fitting to the window.
3. **Backing store** — physical pixels: `cssSize × dpr`.

### 6.2 Scaling strategies

- **Letterbox (fit)** — `scale = min(winW/W, winH/H)`, center, bars on the short axis. Uniform scale, one aspect to design/test. **Default.**
- **Fill-and-extend** — fill the window; keep a guaranteed safe zone (e.g. 16:9 core) and let the world extend beyond it. Best-feeling on mobile; every UI anchor must be edge-relative, and beware fairness (wider view = more visibility).
- **Integer scale** — letterbox rounded down to whole multiples. Pixel art only.
- Avoid pure stretch (distorts) and pure native-resolution (every player sees different world amounts unless you design for it).

### 6.3 Crisp DPR-aware canvas (the canonical resize)

```js
function resize() {
  const dpr = Math.min(devicePixelRatio || 1, 2);      // cap: DPR 3+ costs pixels players can't see
  const scale = Math.min(innerWidth / W, innerHeight / H);
  const cssW = Math.floor(W * scale), cssH = Math.floor(H * scale);
  canvas.style.width = cssW + 'px'; canvas.style.height = cssH + 'px';
  canvas.width  = Math.round(cssW * dpr);              // resets ALL context state
  canvas.height = Math.round(cssH * dpr);
  ctx.setTransform(canvas.width / W, 0, 0, canvas.height / H, 0, 0); // draw in logical units
  ctx.imageSmoothingEnabled = SMOOTHING;               // re-apply after reset
}
addEventListener('resize', resize);
matchMedia(`(resolution: ${devicePixelRatio}dppx)`).addEventListener('change', resize, { once: true }); // DPR change (zoom / monitor move)
```

Center via CSS on the parent: `display:grid; place-items:center; height:100dvh; background:#000;` (use `dvh`, not `vh` — mobile URL-bar collapse makes `100vh` overflow). Handle `orientationchange` by just handling `resize`. Debounce is optional; the resize itself is cheap, but avoid re-allocating offscreen buffers on every intermediate event.

### 6.4 Mobile page shell

```html
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover, user-scalable=no">
```

```css
html, body { margin:0; height:100%; overflow:hidden; overscroll-behavior:none; background:#000; }
```

- `viewport-fit=cover` + `env(safe-area-inset-*)` padding keeps HUD out of notches/home-indicator zones (matters in fill mode and installed PWAs; letterbox bars usually absorb it).
- Orientation: you cannot force it on the mobile web (`screen.orientation.lock()` needs fullscreen and still fails on iOS Safari). Detect wrong orientation and show a "rotate device" overlay; pause while shown.
- Fullscreen: `canvas.requestFullscreen()` from a user gesture; iOS iPhone Safari doesn't support element fullscreen for canvas — PWA standalone mode (§8) is the iOS "fullscreen".

### 6.5 UI scaling

UI in logical units scales uniformly with everything else — usually right. Ensure touch targets ≥ ~44 CSS px *after* scaling on the smallest supported screen; if the game is dense, scale UI on its own layer (DOM overlay with its own `rem`-based sizing is easiest).

---

## 7. Page lifecycle

Events that matter, and the canonical handler set:

| Event | Fires when | Do |
|---|---|---|
| `visibilitychange → hidden` | Tab switch, minimize, mobile task-switch, screen lock | Pause clock, suspend audio, flush save. **The** reliable hook. |
| `visibilitychange → visible` | Return | Reset loop's `last` timestamp (or rely on dt clamp), resume audio if enabled, stay on pause menu (desktop) / auto-resume (ambient mobile games) |
| `pagehide` | Navigation away, bfcache entry | Flush save |
| `blur` / `focus` (window) | Focus loss even while visible | Clear held-input state; optional soft pause |
| `freeze` / `resume` (Page Lifecycle API, Chromium) | Background CPU freeze | Nothing extra if the hidden handler already saved |

Background-tab timing behavior (rAF frozen, timers throttled to ≥1s, Web Audio unthrottled) and the returning-tab dt spike: `loop-and-state.md` §4. Design decision to make explicitly: does *hidden* mean "paused" (action games — yes) or "keeps simulating" (idle games — compute offline progress from wall-clock delta on return instead of actually ticking).

---

## 8. PWA (optional layer)

Worth it when: players return repeatedly, offline play is plausible, or you want home-screen install. Skip for jam games. Two pieces:

### 8.1 Manifest

```json
{ "name": "My Game", "short_name": "MyGame", "start_url": "./", "scope": "./",
  "display": "fullscreen", "orientation": "landscape", "background_color": "#000000",
  "theme_color": "#000000",
  "icons": [ { "src": "./icons/icon-192.png", "sizes": "192x192", "type": "image/png" },
             { "src": "./icons/icon-512.png", "sizes": "512x512", "type": "image/png" },
             { "src": "./icons/maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" } ] }
```

`display: fullscreen` (falls back to `standalone`); `orientation` in the manifest *does* lock orientation for the installed app on Android — the only reliable orientation lock on the web. iOS ignores most of it but honors standalone + apple-touch-icon; add `<meta name="apple-mobile-web-app-capable" content="yes">` and a 180×180 `apple-touch-icon`.

### 8.2 Service worker

Strategy for games: **precache the app shell + assets, versioned cache name, cache-first for hashed assets, network-first for `index.html`.** The classic footgun is a SW serving a stale `index.html` that references deleted hashed bundles → white screen for returning players. Rules:

1. Cache name includes the build version; delete old caches in `activate`.
2. `index.html`: network-first with cache fallback (offline still works, updates arrive).
3. Hashed assets: cache-first (immutable by construction).
4. Update UX: on `updatefound`/waiting worker, show "Update available — restart", then `skipWaiting()` + reload. Never silently `skipWaiting()` mid-session — a live game losing its old assets mid-play is a crash.
5. **Test the update path before shipping the SW at all.** A broken SW is worse than none; you can't remotely purge users' caches except by shipping a new SW they can still fetch.

Minimal correct worker + registration: `examples.md` §6. Offline itch.io builds don't need this — itch's wrapper handles hosting; SWs are for your own domain / GitHub Pages / Netlify.

---

## 9. Error resilience

- Global handlers from day one — a blank black canvas is undebuggable from a player report:

```js
addEventListener('error', (e) => showCrashOverlay(e.message, e.filename, e.lineno));
addEventListener('unhandledrejection', (e) => showCrashOverlay(String(e.reason)));
```

`showCrashOverlay` = DOM overlay (not canvas — the renderer may be the thing that died): apologetic message, error text, "copy details" button, reload button. In dev builds, include the stack.
- Guard the loop: one thrown frame must not kill the rAF chain silently. Catch in the frame driver, stop the loop, show the overlay — a frozen-but-explained game beats a silent freeze. Do NOT swallow-and-continue every frame (log spam + corrupted state).
- Asset load failures: §4.5 (retry once, then explicit error screen).
- Save failures: §5.2 (in-memory fallback + one-time notice).
- WebGL context loss: §1.3.
- Feature detection at boot for anything below your baseline (e.g. `PointerEvent`, `AudioContext`): show "browser not supported" with specifics rather than dying mid-boot. Evergreen browsers make this rare; in-app webviews (Instagram/Facebook browsers) are the usual offenders and *do* reach real players.
