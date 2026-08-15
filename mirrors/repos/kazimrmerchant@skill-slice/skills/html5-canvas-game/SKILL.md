---
name: html5-canvas-game
description: "Builds no-engine browser games with Canvas2D (raw WebGL2 only when Canvas stalls), a fixed-timestep loop, sprites, AABB, scenes, and WebAudio unlock-on-gesture. Use when the user wants a lightweight HTML5 canvas game without Phaser or Three.js. Not for Phaser scenes/physics (phaser-game-development) or 3D scene graphs (three-js-web-game). Never move in pixels-per-frame or blit an Image before onload."
version: 1.0.1
---

## When to Use

Use this skill when building a browser game with hand-controlled rendering: 2D sprites, particles, custom shaders, or pixel-precise visuals from AI-art/SVG assets. This is the lightest web-delivery path (zero framework, zero build step). 

Prefer this over `three-js-web-game` when you don't need a 3D scene graph. Reach for **Canvas2D** first; drop to **raw WebGL** only when Canvas2D stalls (see Procedure Step 10).

> **Trauma-informed default:** every scene must be pausable and interruptible. Never lock the player in an unskippable sequence, never autoplay loud audio, and keep pacing under the player's control. Wire `Escape`/`P` → pause on day one, not later.

## Prerequisites

- **Host:** Windows (PowerShell primary)
- **Browser:** Google Chrome (for standard and headless verification)
- **Server:** Node.js (for `npx serve`) or Python (for `python -m http.server`)
- **Assets:** Rasterized images/SVGs from `game-art-pipeline`

## Procedure

### 1. Project shape

Create a static file structure. No build step. TypeScript is optional — if used, run `npx tsc --watch` in one terminal and serve the emitted JS.

```text
game/
  index.html      ← canvas + one <script type="module">
  main.js         ← loop, scenes
  engine.js       ← Assets, Input, Audio, math helpers (reusable)
  assets/
    hero.png      ← from game-art-pipeline (AI art / rasterized SVG)
    tiles.png
    hit.wav
```

`index.html`:
```html
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    html, body { margin: 0; height: 100%; background: #0b0e14; overflow: hidden; }
    #game { display: block; width: 100vw; height: 100vh; touch-action: none; }
  </style>
</head>
<body>
  <canvas id="game"></canvas>
  <script type="module" src="./main.js"></script>
</body>
</html>
```
`touch-action: none` stops the browser stealing pointer gestures for scroll/zoom.

### 2. The render loop — fixed update, dt-scaled

Never move things by "pixels per frame." Frame rate varies. Move by **pixels per second × dt**. Use a fixed-timestep accumulator so physics/collision are deterministic, and interpolate the draw.

```js
// main.js
import { Assets, Input, Audio } from './engine.js';

const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');

function resize() {
  const dpr = window.devicePixelRatio || 1;
  canvas.width  = Math.round(canvas.clientWidth  * dpr);
  canvas.height = Math.round(canvas.clientHeight * dpr);
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);   // draw in CSS pixels, render crisp
  ctx.imageSmoothingEnabled = false;        // crisp pixel art; set true for painterly art
}
addEventListener('resize', resize);
resize();

const STEP = 1 / 60;        // fixed sim step, seconds
let last = performance.now();
let acc = 0;
let paused = false;

function frame(now) {
  let dt = (now - last) / 1000;
  last = now;
  if (dt > 0.25) dt = 0.25;             // clamp: tab was backgrounded → don't spiral

  if (!paused) {
    acc += dt;
    while (acc >= STEP) {
      update(STEP);                     // fixed-step: deterministic physics
      acc -= STEP;
    }
  }
  render(acc / STEP);                    // alpha ∈ [0,1) for interpolation
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);

// Pause on blur AND on key — trauma-safe pacing.
addEventListener('blur', () => { paused = true; });
addEventListener('keydown', e => {
  if (e.code === 'Escape' || e.code === 'KeyP') paused = !paused;
});
```
Keep `update(dt)` and `render(alpha)` separate.

### 3. Drawing primitives

Canvas2D is an immediate-mode painter's-algorithm API: clear and redraw the whole frame every time.

```js
function render(alpha) {
  ctx.clearRect(0, 0, canvas.clientWidth, canvas.clientHeight);

  // rect
  ctx.fillStyle = '#4cc9f0';
  ctx.fillRect(20, 20, 64, 64);

  // stroked path
  ctx.strokeStyle = '#f72585';
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(120, 40);
  ctx.lineTo(180, 90);
  ctx.lineTo(120, 90);
  ctx.closePath();
  ctx.stroke();

  // circle
  ctx.beginPath();
  ctx.arc(240, 60, 30, 0, Math.PI * 2);
  ctx.fill();

  // text
  ctx.fillStyle = '#e8eef7';
  ctx.font = '16px system-ui, sans-serif';
  ctx.textBaseline = 'top';
  ctx.fillText('score: 0', 20, 100);

  // transforms: save/rotate/restore around each rotated sprite
  ctx.save();
  ctx.translate(300, 200);
  ctx.rotate(alpha * Math.PI);   // example use of interpolation alpha
  ctx.fillRect(-16, -16, 32, 32);
  ctx.restore();
}
```
Rules: batch state changes; always pair `save()`/`restore()`; `translate` then `rotate`/`scale` then draw at the origin. Gradients and `globalAlpha` are cheap; per-pixel `getImageData`/`putImageData` is **not** — avoid it in the hot loop.

### 4. Sprites from AI-art textures

Draw with the 9-argument `drawImage` to blit a sub-rectangle (a frame out of a sheet):

```js
// drawImage(img, sx, sy, sw, sh, dx, dy, dw, dh)
//           source rect on the sheet   →   dest rect on canvas
const sheet = Assets.img('hero');
const FW = 48, FH = 48;                 // frame size in the sheet
const frame = Math.floor(animTime * 10) % 6;   // 6-frame walk @ 10 fps
ctx.drawImage(sheet, frame * FW, 0, FW, FH,  x, y, FW, FH);
```
Guidelines:
- **Power-of-two-ish sheets, integer frame sizes.** Keep frames on a clean grid.
- **Snap dest to integers** for pixel art: `Math.round(x)`.
- **Pre-render static composites.** Draw a rarely-changing background once into an offscreen `document.createElement('canvas')` and blit that single image each frame.
- **SVG assets:** pre-rasterize SVGs to PNG at target resolution, or draw the SVG into an offscreen canvas at the size you need once.
- **Flip** by `ctx.scale(-1, 1)` inside a save/restore (translate to the sprite center first).

### 5. Input — pointer + keyboard

Keyboard as a held-state set (poll it in `update`), pointer as events. Track listeners to remove them on scene teardown.

```js
// engine.js
export const Input = (() => {
  const down = new Set();
  const pointer = { x: 0, y: 0, down: false };

  addEventListener('keydown', e => { down.add(e.code); });
  addEventListener('keyup',   e => { down.delete(e.code); });
  // guard against stuck keys when focus is lost:
  addEventListener('blur', () => down.clear());

  function bindPointer(canvas) {
    const to = e => {
      const r = canvas.getBoundingClientRect();
      pointer.x = e.clientX - r.left;    // CSS pixels — matches your setTransform space
      pointer.y = e.clientY - r.top;
    };
    canvas.addEventListener('pointermove', to);
    canvas.addEventListener('pointerdown', e => { to(e); pointer.down = true; });
    addEventListener('pointerup', () => { pointer.down = false; });
  }

  return {
    bindPointer,
    held: code => down.has(code),
    pointer,
  };
})();
```
Poll in `update`:
```js
function update(dt) {
  const speed = 200;                      // px per second
  if (Input.held('ArrowLeft')  || Input.held('KeyA')) player.x -= speed * dt;
  if (Input.held('ArrowRight') || Input.held('KeyD')) player.x += speed * dt;
}
```

### 6. Game state & scenes

A scene = `{ enter, update(dt), render(alpha), exit }`. A tiny manager swaps them and guarantees `exit` runs (remove listeners and free assets here).

```js
// engine.js
export class SceneManager {
  #current = null;
  set(scene) {
    if (this.#current?.exit) this.#current.exit();
    this.#current = scene;
    if (scene.enter) scene.enter();
  }
  update(dt)     { this.#current?.update?.(dt); }
  render(alpha)  { this.#current?.render?.(alpha); }
}
```
```js
const scenes = new SceneManager();

const Play = {
  enter() { Audio.play('music', { loop: true, volume: 0.4 }); },
  update(dt) { /* game logic */ if (dead) scenes.set(GameOver); },
  render(a) { /* draw world */ },
  exit() { Audio.stop('music'); },
};

scenes.set(Title);   // Title → Play → GameOver, each self-contained
```

### 7. Collision — AABB

An entity is `{x, y, w, h}`.

```js
export function aabb(a, b) {
  return a.x < b.x + b.w && a.x + a.w > b.x &&
         a.y < b.y + b.h && a.y + a.h > b.y;
}

// resolve overlap by pushing out on the smaller axis (player vs solid wall):
export function resolve(a, b) {
  const dx = (a.x + a.w / 2) - (b.x + b.w / 2);
  const dy = (a.y + a.h / 2) - (b.y + b.h / 2);
  const ox = (a.w + b.w) / 2 - Math.abs(dx);   // x overlap
  const oy = (a.h + b.h) / 2 - Math.abs(dy);   // y overlap
  if (ox <= 0 || oy <= 0) return;
  if (ox < oy) a.x += dx < 0 ? -ox : ox;       // push along least-penetration axis
  else         a.y += dy < 0 ? -oy : oy;
}
```
For many entities, spatial-hash into a grid before pairwise tests. Do collision inside the **fixed-step** `update`, never in `render`.

### 8. Audio — WebAudio, autoplay-safe

WebAudio is sample-accurate and mixable. **Browsers suspend the AudioContext until a user gesture** — resume it on the first click/keypress or nothing plays.

```js
// engine.js
export const Audio = (() => {
  const ctx = new (window.AudioContext || window.webkitAudioContext)();
  const buffers = new Map();
  const master = ctx.createGain();
  master.gain.value = 0.8;
  master.connect(ctx.destination);

  // unlock on first gesture — required by autoplay policy
  const unlock = () => {
    if (ctx.state === 'suspended') ctx.resume();
    removeEventListener('pointerdown', unlock);
    removeEventListener('keydown', unlock);
  };
  addEventListener('pointerdown', unlock);
  addEventListener('keydown', unlock);

  async function load(name, url) {
    const buf = await fetch(url).then(r => r.arrayBuffer());
    buffers.set(name, await ctx.decodeAudioData(buf));
  }

  const active = new Map();               // name → source (for stoppable loops)
  function play(name, { loop = false, volume = 1 } = {}) {
    const buf = buffers.get(name);
    if (!buf) return;
    const src = ctx.createBufferSource();
    src.buffer = buf; src.loop = loop;
    const g = ctx.createGain(); g.gain.value = volume;
    src.connect(g).connect(master);
    src.start();
    if (loop) active.set(name, src);
    return src;
  }
  function stop(name) { active.get(name)?.stop(); active.delete(name); }

  return { load, play, stop, ctx, master };
})();
```
Trauma-safe: start `master.gain` low, expose a volume slider, and **never** trigger a loud stinger without the player having interacted. Fade with `gain.linearRampToValueAtTime`.

### 9. Asset loading manager

Load everything up front behind a progress bar — **never** blit an `Image` that hasn't finished decoding.

```js
// engine.js
export const Assets = (() => {
  const images = new Map();

  async function loadAll(manifest, onProgress) {
    const img = manifest.images ?? {};
    const snd = manifest.sounds ?? {};
    const tasks = [
      ...Object.entries(img).map(([k, url]) => () => loadImage(k, url)),
      ...Object.entries(snd).map(([k, url]) => () => Audio.load(k, url)),
    ];
    let done = 0;
    await Promise.all(tasks.map(t => t().then(() => {
      onProgress?.(++done / tasks.length);
    })));
  }

  function loadImage(key, url) {
    return new Promise((res, rej) => {
      const im = new Image();
      im.onload  = () => { images.set(key, im); res(); };
      im.onerror = () => rej(new Error(`asset failed: ${url}`));
      im.decoding = 'async';
      im.src = url;
    });
  }

  return { loadAll, img: k => images.get(k) };
})();
```
```js
// boot
await Assets.loadAll({
  images: { hero: './assets/hero.png', tiles: './assets/tiles.png' },
  sounds: { hit: './assets/hit.wav',   music: './assets/music.ogg' },
}, p => drawLoadingBar(p));
scenes.set(Title);
requestAnimationFrame(frame);
```

### 10. When to drop to raw WebGL

Stay on Canvas2D until you hit a wall, then switch the **rendering** layer only. Escalate to WebGL when you need:
- **Thousands of moving sprites / particles.**
- **Fragment shaders** — CRT/scanline, bloom, chromatic aberration, water, etc.
- **Post-processing** — render the scene to a framebuffer, then a full-screen shader pass.
- **Additive/blend-heavy effects** at scale (fire, magic, glow).

Minimal WebGL bootstrap:
```js
const gl = canvas.getContext('webgl2', { antialias: false, alpha: false });
const vs = `#version 300 es
in vec2 a_pos; in vec2 a_uv; out vec2 v_uv;
uniform vec2 u_res;
void main(){ v_uv=a_uv; vec2 c=(a_pos/u_res)*2.0-1.0; gl_Position=vec4(c.x,-c.y,0,1);} `;
const fs = `#version 300 es
precision highp float; in vec2 v_uv; out vec4 o; uniform sampler2D u_tex;
void main(){ o = texture(u_tex, v_uv); }`;

function compile(type, src){ const s=gl.createShader(type); gl.shaderSource(s,src);
  gl.compileShader(s); if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))
  throw new Error(gl.getShaderInfoLog(s)); return s; }
const prog = gl.createProgram();
gl.attachShader(prog, compile(gl.VERTEX_SHADER, vs));
gl.attachShader(prog, compile(gl.FRAGMENT_SHADER, fs));
gl.linkProgram(prog); gl.useProgram(prog);
// … upload a quad VBO + texture, set u_res, gl.drawArrays. Then batch/instance sprites.
```
**Hybrid** is common: WebGL for the particle/effect layer, a second stacked Canvas2D for crisp UI/text.

## Pitfalls

1. **No dt scaling.** Moving by fixed px/frame makes the game run at different speeds on 60 vs 144 Hz displays. Always `pos += speed * dt`, and use a fixed-step accumulator for physics.
2. **Canvas DPI blur.** Setting only CSS size (not `canvas.width/height × devicePixelRatio` + `setTransform(dpr,…)`) gives a soft, upscaled image on HiDPI screens. Resize the backing store to DPR and redo it on `resize`.
3. **Blocking / racing asset load.** Blitting an `Image` before `onload` draws nothing (silent). Await all assets behind a loader + progress bar before starting the loop.
4. **Leaking listeners.** Adding `keydown`/`pointer`/`resize` handlers per scene without removing them stacks duplicates → ghost input and memory growth. Track and remove in `scene.exit()`; clear held-keys on `blur`.
5. **Ignoring the WebAudio autoplay policy.** The AudioContext starts `suspended`; sound is silent until you `ctx.resume()` inside a user gesture. Wire an unlock handler on first click/keypress.
6. **No pause / no interruptibility.** Beyond the bug of physics spiraling after a backgrounded tab (clamp `dt`), an unpausable game is trauma-unsafe. Ship `Escape`/`P` pause and pause-on-`blur` from the start.

## Verification

No build step. Serve the folder statically and open Chrome. In Windows (PowerShell):

```powershell
# from the game/ folder — pick one:
npx serve -l 5000 .
# or, no Node:
python -m http.server 5000
```

Open it:
```powershell
start chrome "http://localhost:5000"
```

**Verify a change actually rendered** — capture a screenshot with headless Chrome. `--virtual-time-budget` lets rAF frames advance before the shot:

```powershell
chrome --headless=new --disable-gpu `
  --window-size=1280,720 `
  --virtual-time-budget=2000 `
  --screenshot=shot.png `
  "http://localhost:5000"
```

Then `Read shot.png` to confirm the frame looks right (sprites placed, no blank canvas, no DPI blur). Also open Chrome DevTools → **Console** (catch asset 404s / shader compile errors) and **Performance** (confirm a steady 16.6 ms frame). For scripted interaction, use Playwright:
```powershell
npx playwright screenshot --wait-for-timeout=2000 http://localhost:5000 shot.png
```

Sanity loop: **serve → open → screenshot → Read → DevTools console** on every visual change.
