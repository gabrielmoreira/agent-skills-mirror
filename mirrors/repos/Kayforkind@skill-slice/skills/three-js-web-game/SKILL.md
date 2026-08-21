---
name: three-js-web-game
description: "Scaffolds a Vite+TypeScript Three.js browser game: PBR plus IBL and EffectComposer, state-machine loops, SVG or AI-art ingest, and Chrome 60 fps budgets. Use when the deliverable is an install-free WebGL game or itch.io HTML5 build. Not a scene-camera-renderer primer (threejs-fundamentals) and not a general Three.js VFX cookbook (threejs-skills)."
version: 1.0.1
alwaysApply: false
---

# Three.js Web Game — high-fidelity browser games, zero install

Build games that run by opening a URL. The stack is **Vite + TypeScript + three** (npm). The output of `npm run build` is a static folder you can host anywhere — GitHub Pages, Netlify, Cloudflare Pages, itch.io HTML5, or a local `npx serve`. No engine editor, no export templates, no installer. The browser talks to the GPU through WebGL, so the RTX 3090 Ti is used automatically — no CUDA/driver work needed; Chrome is both the dev runtime and the verification target.

**Priority order for this skill: visuals first, then feel, then features.** A flat-lit, un-graded Three.js scene looks like a tech demo from 2012. The difference between that and "best of the best" is almost entirely: PBR materials + environment lighting + tone mapping + postprocessing + art direction. That path is the Procedure below — do not skip it.

Related skills: `creative/comfyui` (generate the art this game consumes), `svg-quality-audit` / `svg-asset-qa` (gate SVG assets before ingest), `godot-2d-game-development` (the native-engine alternative — use that when the target is desktop builds, not web).

---

## When to Use

- Building a browser-delivered game with Three.js (no install, no engine editor).
- Converting AI-generated art or SVG vault assets into a playable WebGL scene.
- Standing up a Vite + TypeScript + three project from scratch.
- Achieving high visual fidelity: PBR materials, IBL, tone mapping, postprocessing.
- Designing game architecture: state machines, systems, input-as-intent.
- Performance tuning a Three.js game for 60 fps in Chrome.
- Verifying a Three.js game visually via browser CDP and screenshot analysis.

**Do NOT use this skill when:** the target is a native desktop/mobile binary (use `godot-2d-game-development`), or when you need a full-featured game engine editor with scene graphs and visual scripting.

---

## Prerequisites

- **Node.js** installed (for `npm create vite`).
- **Chrome** installed — it is both the dev runtime and the verification target.
- **GPU:** The browser uses WebGL automatically; an RTX 3090 Ti or similar is utilized without driver/CUDA work.
- **Windows host (primary):** Commands below assume PowerShell. Use `npm` directly; no WSL required.
- **Related skill outputs (upstream):**
  - `creative/comfyui` — generates AI art (albedo, reference images) this game consumes.
  - `svg-quality-audit` / `svg-asset-qa` — run on vault SVGs **before** ingest. Broken viewBoxes and invisible-fill bugs waste a render cycle to discover in-engine.
- **Reference files:** If this skill ships a `references/` directory, load those files when the Procedure calls for deep dives into specific subsystems (e.g., postprocessing pass configs, KTX2 compression details). If a `scripts/` directory exists, use those helper scripts for asset conversion tasks as noted in the steps below.

---

## Procedure

### Step 1 — Scaffold the project (Vite + TypeScript + three)

**Why Vite:** instant HMR (edit a material parameter, see it without reload), TypeScript out of the box, an asset pipeline that hashes/bundles textures and audio, and a production build that is plain static files. Hand-rolling `<script src="three.min.js">` costs you all of that and breaks the moment you need addons (loaders, postprocessing live in `three/addons/`, which needs a bundler or import maps).

```powershell
npm create vite@latest ink-and-spirit -- --template vanilla-ts
cd ink-and-spirit
npm i three howler
npm i -D @types/three @types/howler
npm run dev        # -> http://localhost:5173, HMR on
npm run build      # -> dist/ (static, deploy anywhere)
npm run preview    # serve dist/ locally to sanity-check the production build
```

**Project layout — systems, not one giant file:**

```
index.html                  # one <canvas> host, nothing else
public/
  assets/
    textures/               # AI-art albedo/normal/roughness maps (PNG/WebP/KTX2)
    hdri/                   # .hdr environment maps
    sprites/                # rasterized SVGs, UI atlases
    audio/                  # ogg/mp3
src/
  main.ts                   # bootstrap only: create Game, start loop
  game/
    Game.ts                 # owns renderer/scene/camera/composer, ticks systems
    states/
      StateMachine.ts       # generic FSM
      FreezeState.ts  FlightState.ts  FightState.ts  FawnState.ts
  systems/
    render.ts               # renderer + composer setup (Step 3 lives here)
    input.ts                # pointer/keyboard -> intent events
    loader.ts               # LoadingManager, texture/audio helpers
    audio.ts                # Howler wrapper, ducking, mute
  scenes/                   # per-chapter scene builders
```

`public/` files are served at `/` verbatim (use for HDRIs, audio, large textures); anything `import`ed from `src/` gets hashed and bundled. Both work — `public/` is simpler for game assets.

### Step 2 — Minimal render loop (`src/main.ts`)

```ts
import * as THREE from 'three';

const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));   // cap DPR — 4K + DPR 2 melts fill rate
renderer.setSize(innerWidth, innerHeight);
renderer.toneMapping = THREE.ACESFilmicToneMapping;      // filmic response — see Step 3
renderer.toneMappingExposure = 1.0;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(50, innerWidth / innerHeight, 0.1, 100);
camera.position.set(0, 1.5, 4);

const clock = new THREE.Clock();
function tick() {
  requestAnimationFrame(tick);
  const dt = Math.min(clock.getDelta(), 0.05);  // clamp: tab-switch returns a huge delta
  update(dt);                                   // game logic — dt-scaled, never frame-counted
  renderer.render(scene, camera);               // becomes composer.render() in Step 3
}
tick();

addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
```

### Step 3 — The visual fidelity path (do this BEFORE adding gameplay)

This is the checklist that takes a scene from "gray boxes" to matching AI-generated reference art. Apply in order; each step is visible on its own.

#### 3.1 Tone mapping + color space (the foundation)

`ACESFilmicToneMapping` (set in Step 2) gives filmic highlight rolloff instead of clipped whites. Since three r152 the renderer outputs sRGB by default — **your job is tagging inputs correctly** (Step 3.3). Get this wrong and everything is washed-out or crushed and no amount of light tweaking fixes it.

#### 3.2 Environment lighting (IBL) — the single biggest visual win

PBR materials look dead under point lights alone. Give the scene an environment map and every `MeshStandardMaterial`/`MeshPhysicalMaterial` picks up believable ambient light and reflections:

```ts
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';

new RGBELoader().load('/assets/hdri/moody_forest_2k.hdr', (tex) => {
  tex.mapping = THREE.EquirectangularReflectionMapping;
  scene.environment = tex;                    // lights ALL PBR materials
  scene.environmentIntensity = 0.9;           // grade to taste
  // scene.background = tex;                  // optional: also show it
});
```

Free HDRIs: polyhaven.com (2k is plenty for lighting; use 4k+ only if it's the visible skybox).

No HDRI that fits the mood? Neutral studio IBL with zero assets:

```ts
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment()).texture;
```

Then add **one** key light (`DirectionalLight`, with shadows) for direction and drama. Resist adding five lights — one key + IBL + postprocessing beats a light-salad every time.

#### 3.3 PBR materials from AI art

Generate/derive three maps per surface (ComfyUI can produce albedo directly; normal/roughness can be derived with tools like Materialize or a normal-from-height node):

```ts
const tl = new THREE.TextureLoader(manager);

const albedo = tl.load('/assets/textures/ink_paper_albedo.png');
albedo.colorSpace = THREE.SRGBColorSpace;               // COLOR data -> sRGB. Mandatory.

const normal = tl.load('/assets/textures/ink_paper_normal.png');   // DATA -> leave linear
const rough  = tl.load('/assets/textures/ink_paper_rough.png');    // DATA -> leave linear

const mat = new THREE.MeshPhysicalMaterial({
  map: albedo, normalMap: normal, roughnessMap: rough,
  roughness: 1.0,        // multiplies the map
  sheen: 0.3,            // nice for cloth/paper — fits an ink & paper aesthetic
});
```

**HARD RULE: albedo/emissive = sRGB; normal/roughness/metalness/AO = linear (default).** The #1 Three.js visual bug is a missing or extra `colorSpace = SRGBColorSpace`.

#### 3.4 Postprocessing (bloom, AO, grade) — where "game" becomes "art"

```ts
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
composer.addPass(new UnrealBloomPass(
  new THREE.Vector2(innerWidth, innerHeight),
  0.35,   // strength — subtle; > 0.6 looks like 2008
  0.8,    // radius
  0.85,   // threshold — only bright things bloom
));
composer.addPass(new OutputPass());   // applies tone mapping + sRGB — MUST be the last pass

// in tick(): composer.render() instead of renderer.render()
// in resize: composer.setSize(innerWidth, innerHeight)
```

- **Bloom:** emissive ink glow, spirit effects. Threshold high, strength low.
- **AO:** `SSAOPass` from addons works; the `n8ao` npm package (N8AOPass, drop-in) looks better and runs faster — worth it for a visuals-first game.
- **Color grade:** cheapest big win is a LUT — grade a screenshot in any photo editor, export a LUT, apply with `LUTPass` + `LUTCubeLoader`. This is how you lock the game to the reference art's palette without touching materials.
- Also consider `ShaderPass` with a vignette, and film grain for the ink aesthetic.

#### 3.5 Match the reference art — the actual workflow

1. Pick 2–3 AI-generated reference images (the target look).
2. Build the scene with the steps above, screenshot it (see Verification).
3. Put screenshot and reference side by side (or `vision_analyze` both) and diff: palette, contrast, light direction, texture density, edge quality.
4. Adjust in this order: environment/exposure → key light → material maps → grade/LUT → bloom.
5. Repeat. HMR makes each iteration seconds, not minutes.

For 2.5D — a strong option given a large 2D asset library — put AI art on lit planes (`MeshStandardMaterial` + alpha), add parallax layers, fog (`scene.fog`), and particles. Full-3D fidelity is not required to look stunning; *Hollow Knight* is planes.

### Step 4 — Ingest assets from the SVG vault and AI art

**Gate first:** run `svg-quality-audit` on any vault SVGs before ingest — broken viewBoxes and invisible-fill bugs waste a render cycle to discover in-engine.

**SVGs as sprites/UI — rasterize, don't parse (default path).** Browsers rasterize SVG natively:

```ts
async function svgToTexture(url: string, size = 512): Promise<THREE.Texture> {
  const img = new Image();
  img.src = url;
  await img.decode();
  const c = Object.assign(document.createElement('canvas'), { width: size, height: size });
  c.getContext('2d')!.drawImage(img, 0, 0, size, size);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 8;
  return tex;
}
// use on THREE.Sprite (billboard) or a PlaneGeometry + MeshBasicMaterial({ transparent: true })
```

Caveat: the SVG root needs `width`/`height` or a `viewBox` for `Image` to size it — the vault audit checks this. Rasterize at the largest on-screen size you'll need (power of two).

**SVGs as geometry (special cases):** `SVGLoader` from `three/addons` parses paths into `ShapeGeometry`/`ExtrudeGeometry` — real 3D extruded icons/glyphs. Use sparingly; complex SVGs triangulate badly.

**Pure HUD/menus:** plain HTML/CSS overlaid on the canvas beats in-scene UI — SVGs drop in as `<img>`, and it's accessible and crisp for free.

**AI art (PNG/WebP):** load via `TextureLoader`, tag sRGB. For big scenes, compress to **KTX2**:

```powershell
toktx --genmipmap --t2 --encode uastc out.ktx2 in.png
```

Load with `KTX2Loader` — stays compressed in VRAM, 4–8× memory saving. If a `scripts/` helper exists for batch KTX2 conversion, use it here.

**3D models:** glTF only (`GLTFLoader` + `DRACOLoader`) — never OBJ/FBX on the web.

### Step 5 — Game architecture

- **One `Game` class** owns renderer, scene, camera, composer, and an array of systems with `update(dt)`. `main.ts` constructs it and starts the loop. Nothing else touches the renderer.
- **Input as intent:** `input.ts` translates pointer/keyboard into semantic events (`approach`, `withdraw`, `hold`, `soothe`) — states consume intents, never raw keycodes. This also makes remapping and touch support trivial later.
- **State machine — the 4 Fs are literally states:**

```ts
interface GameState {
  enter(from: string | null): void;
  update(dt: number): void;
  exit(): void;
}

class StateMachine {
  private states = new Map<string, GameState>();
  private current: GameState | null = null;
  private name: string | null = null;

  add(name: string, s: GameState) { this.states.set(name, s); }
  transition(to: string) {
    this.current?.exit();
    const prev = this.name;
    this.name = to;
    this.current = this.states.get(to)!;
    this.current.enter(prev);
  }
  update(dt: number) { this.current?.update(dt); }
}
```

Each F-state owns its camera behavior, palette/grade, audio bed, and available intents — `FreezeState.enter()` might desaturate via the LUT pass, slow the camera, and muffle audio (Howler low-pass). Transitioning states *is* the emotional storytelling.

- **Camera:** fixed/authored cameras (lerped between anchor points) fit a narrative game far better than free orbit. Keep `OrbitControls` behind a `?debug` URL flag for development only.
- **Loading:** one `THREE.LoadingManager` for everything; `onProgress` drives a styled loading screen (in the game's aesthetic — first impression matters); start the loop only `onLoad`.
- **Audio:** Howler for music/SFX (handles autoplay-policy unlock on first gesture); `THREE.PositionalAudio` only if you need true 3D positioning.

### Step 6 — Trauma-informed design → mechanics

- **Recognition over reliving:** abstract/symbolic representation (ink, weather, spirit forms), never literal reenactment. The visuals-first approach serves this directly.
- **The 4 Fs are protective, not failures:** every state has valid moves and forward paths. No fail states, no game-overs, no forced repetition of distressing beats. "Losing" redirects, never punishes.
- **Player choice as the growth arc:** state *transitions* are chosen by the player (intent events), never forced by timers or scripted takeovers. Agency is the mechanic.
- **Pacing and exits:** pause always available, instant and judgment-free; autosave at every transition; a persistent "breathe"/grounding interaction that is always valid input.
- **Soft feedback:** grade shifts, audio warmth, light — not klaxons, screen shake, or red flash.

### Step 7 — Performance (target: 60 fps in Chrome)

The 3090 Ti is not the bound — the browser's single JS thread and fill rate are. Budget: **< 300 draw calls, < 500k triangles, DPR capped at 2.**

- Read `renderer.info.render.calls` / `.triangles` every frame in a debug overlay from day one.
- **InstancedMesh** for anything repeated (particles, foliage, ink drops): 1000 objects → 1 draw call.
- **Texture atlases** for sprites/UI (many small textures → many draw calls); share materials so Three.js can batch state changes.
- **LOD** (`THREE.LOD`) only if you build large 3D environments; irrelevant for 2.5D.
- KTX2 textures (Step 4) for VRAM; `frustumCulled` stays on (default).
- Profile with Chrome DevTools Performance tab (long frames → is it JS or GPU?) and **Spector.js** extension (per-draw-call GPU capture).
- Postprocessing costs one full-screen pass each — bloom + AO + grade + output is fine; ten passes is not.

---

## Pitfalls

| # | Pitfall | Consequence / fix |
|---|---------|-------------------|
| 1 | Hand-rolling script tags instead of Vite | No HMR, no addons, no TS; every visual iteration costs a manual reload. Scaffold from Step 1. |
| 2 | Texture color space wrong | Washed-out or crushed everything. Albedo → `SRGBColorSpace`; normal/roughness/AO → leave linear. |
| 3 | No IBL, no postprocessing | The "flat tech demo" look. Steps 3.2/3.4 are not optional for a visuals-first game. |
| 4 | One-file monolith | main.ts hits 2000 lines and every change risks everything. Systems + states from day one (Step 5). |
| 5 | Never calling `dispose()` | Removing a mesh from the scene does NOT free GPU memory. On scene teardown: `geometry.dispose()`, `material.dispose()`, `texture.dispose()`. Long sessions leak VRAM until context loss. |
| 6 | Blocking on load / no loading UX | White screen for 10s = closed tab. One `LoadingManager`, styled progress screen, then start. |
| 7 | WebGL context loss unhandled | Tab suspended or GPU reset → permanent black canvas. `canvas.addEventListener('webglcontextlost', e => e.preventDefault())` + restore handler (re-upload or reload prompt). |
| 8 | Web delivery tested last | `import` paths that work in dev break in `dist/` (base URL, `public/` vs bundled). Run `npm run build && npm run preview` from week one, not release day. |

---

## Verification

1. `npm run dev` (background), confirm the terminal reports the localhost URL.
2. Open in Chrome via `browser_cdp` → navigate to `http://localhost:5173`.
3. **Check the console first** (`browser_cdp` console logs): Three.js warns loudly — texture size, shader errors, missing assets all land here before they're visible.
4. Screenshot via `browser_cdp`.
5. `vision_analyze` the screenshot against the acceptance bar: correct palette vs reference art, no black/magenta surfaces (missing texture), no washed-out haze (color space bug), UI legible.
6. Before shipping: `npm run build && npm run preview` and repeat steps 2–5 against the preview URL — dev and prod builds can differ (asset paths, base URL).

Asset-level QA belongs upstream: `svg-quality-audit` before SVGs enter `public/assets`.

---

## Quick reference

```powershell
# scaffold
npm create vite@latest <game> -- --template vanilla-ts
cd <game> && npm i three howler && npm i -D @types/three @types/howler

# develop / verify / ship
npm run dev                      # localhost:5173, HMR
npm run build && npm run preview # production sanity check
npx serve dist                   # or deploy dist/ to any static host / itch.io HTML5
```

**Visual pipeline order:** ACES tone mapping → HDRI environment → one key light → PBR maps (sRGB albedo, linear data) → EffectComposer (Render → Bloom → AO → LUT → OutputPass last) — then iterate against reference art with screenshot + vision diff until they match.
