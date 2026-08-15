---
name: phaser-game-development
description: "Builds 2D HTML5 games with Phaser 3 + TypeScript + Vite (or a pinned CDN): scenes, Arcade/Matter physics, tilemaps, tweens, cameras, and a static dist/ bundle. Use when the user asks for Phaser, a 2D browser game with sprites/physics/scenes, or a web game engine. Not for raw Canvas2D (html5-canvas-game) or 3D scene graphs (three-js-web-game). Never inline binary game assets; keep Vite base './' so dist/ is portable."
version: 1.0.1
---

# Phaser 3 Game Development

Phaser 3 is the dominant 2D web game framework: WebGL/Canvas renderer, scene system, asset loader,
Arcade + Matter physics, tweens, cameras, input. It runs anywhere Chrome runs and builds to a plain
static `dist/` — ideal for the WEB delivery target. This skill is the structured 2D-web path; use
`three-js-web-game` for 3D and `html5-canvas-game` when you deliberately want no engine.

## When to Use

- The user asks for a **2D browser game** with sprites, physics, collisions, tilemaps, scenes, tweens, or a game loop.
- Trigger keywords: "Phaser", "make a browser game", "2D game", "sprite", "physics", "collision", "game scene", "web game with a game engine".
- You want a structured renderer, physics system, and scene management (vs. raw canvas in `html5-canvas-game`).
- The game is 2D. For 3D, use `three-js-web-game` instead.
- Art assets should be produced through `game-art-pipeline` (AI art / SVG → textures & atlases) and loaded into Phaser.

## Prerequisites

- **Runtime:** Chrome / Chromium with WebGL support.
- **Node 18+** for the Vite + TypeScript toolchain.
- **Windows host (primary):** PowerShell is the primary shell. Commands below use `npm run` scripts which are OS-agnostic. When using MSYS bash, use forward slashes in paths.
- **Phaser 3** installed via `npm install phaser` (Vite path) or pinned CDN URL (no-build path).
- Assets placed in `public/assets/` (Vite copies `public/` verbatim; reference as `assets/…` in code).

## Procedure

### 1. Scaffold — Vite + TypeScript (recommended)

```bash
# from your projects dir (PowerShell or MSYS bash)
npm create vite@latest my-game -- --template vanilla-ts
cd my-game
npm install phaser
npm pkg set scripts.dev="vite" scripts.build="vite build" scripts.preview="vite preview"
```

Create `vite.config.ts` — make the build path-relative so `dist/` works from any subfolder or `file://`:

```ts
import { defineConfig } from 'vite';

export default defineConfig({
  base: './',                 // relative asset URLs — portable static bundle
  server: { port: 5173, open: false },
  build: { target: 'es2020', assetsInlineLimit: 0 }, // don't inline binary game assets
});
```

Create `index.html`:

```html
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
    <title>My Game</title>
    <style>
      html, body { margin: 0; height: 100%; background: #0e0e1a; overflow: hidden; }
      #app { width: 100vw; height: 100vh; display: grid; place-items: center; }
      canvas { display: block; }
    </style>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
```

Put game assets in `public/assets/` (Vite copies `public/` verbatim; reference as `assets/…`).

#### CDN no-build alternative (prototype / single file)

```html
<script src="https://cdn.jsdelivr.net/npm/phaser@3.80.1/dist/phaser.min.js"></script>
```

**Pin the exact version** (`@3.80.1`), never `@3` or `@latest` — see pitfall #6.

### 2. Project structure

```
my-game/
├─ index.html
├─ vite.config.ts
├─ public/assets/           # png, svg, atlas json, audio  (served as /assets/…)
└─ src/
   ├─ main.ts               # Phaser.Game config + scene list
   └─ scenes/
      ├─ BootScene.ts       # preload the loader UI / global assets
      ├─ GameScene.ts       # gameplay
      └─ PauseScene.ts      # overlay
```

### 3. Game config + scene lifecycle

Every scene extends `Phaser.Scene` and uses three lifecycle hooks:

- **`preload()`** — queue asset loads. Nothing is available for use *yet*.
- **`create()`** — assets are loaded; build the world, sprites, physics, input, tweens.
- **`update(time, delta)`** — per-frame logic. `delta` is ms since last frame; scale movement by it.

`src/main.ts`:

```ts
import Phaser from 'phaser';
import { BootScene } from './scenes/BootScene';
import { GameScene } from './scenes/GameScene';
import { PauseScene } from './scenes/PauseScene';

const config: Phaser.Types.Core.GameConfig = {
  type: Phaser.AUTO,                 // WebGL if available, else Canvas
  parent: 'app',
  backgroundColor: '#0e0e1a',
  scale: {
    mode: Phaser.Scale.FIT,          // letterbox-fit a fixed design resolution
    autoCenter: Phaser.Scale.CENTER_BOTH,
    width: 960,
    height: 540,
  },
  render: { antialias: true, roundPixels: true },   // pixelArt:true + antialias:false for pixel games
  physics: { default: 'arcade', arcade: { gravity: { y: 0 }, debug: false } },
  scene: [BootScene, GameScene, PauseScene],
};

new Phaser.Game(config);
```

Design at a fixed base resolution (960×540 here) and let `Scale.FIT` upscale. See pitfall #4 for
crisp text/HiDPI.

### 4. Concrete minimal scene (copy-paste, runs as-is)

`src/scenes/GameScene.ts` — player + Arcade physics + input + overlap + tween feedback + camera follow:

```ts
import Phaser from 'phaser';

export class GameScene extends Phaser.Scene {
  private player!: Phaser.Types.Physics.Arcade.SpriteWithDynamicBody;
  private cursors!: Phaser.Types.Input.Keyboard.CursorKeys;
  private coins!: Phaser.Physics.Arcade.Group;
  private score = 0;
  private scoreText!: Phaser.GameObjects.Text;

  constructor() {
    super('game');                    // scene key used by scene.start('game')
  }

  preload() {
    // Load EVERYTHING you reference in create() here first (pitfall #1).
    this.load.image('player', 'assets/player.png');
    this.load.svg('coin', 'assets/coin.svg', { width: 32, height: 32 }); // SVG → rasterized texture
    this.load.image('tiles-bg', 'assets/bg.png');
  }

  create() {
    this.add.image(480, 270, 'tiles-bg').setScrollFactor(0.3); // parallax backdrop

    // Player: physics sprite (body auto-sized to the texture frame).
    this.player = this.physics.add.sprite(480, 270, 'player');
    this.player.setCollideWorldBounds(true);
    this.player.body.setSize(40, 40).setOffset(4, 8); // tighten body vs sprite (pitfall #2)

    // Collectibles as a physics group.
    this.coins = this.physics.add.group();
    for (let i = 0; i < 8; i++) {
      this.coins.create(120 + i * 90, 120 + (i % 2) * 260, 'coin');
    }

    // Overlap → collect. collide() would block; overlap() just detects.
    this.physics.add.overlap(
      this.player,
      this.coins,
      (_p, coin) => this.collectCoin(coin as Phaser.Physics.Arcade.Sprite),
      undefined,
      this,
    );

    // Input.
    this.cursors = this.input.keyboard!.createCursorKeys(); // `!` — keyboard may be null in TS
    this.input.keyboard!.on('keydown-P', () => this.togglePause());

    // World + camera.
    this.physics.world.setBounds(0, 0, 1920, 1080);
    this.cameras.main.setBounds(0, 0, 1920, 1080);
    this.cameras.main.startFollow(this.player, true, 0.08, 0.08); // gentle lerp — no lurching

    this.scoreText = this.add.text(16, 16, 'Score: 0', { fontSize: '24px', color: '#fff' })
      .setScrollFactor(0)          // pin to camera (HUD)
      .setResolution(window.devicePixelRatio); // crisp on HiDPI (pitfall #4)

    // Clean up on restart/shutdown (pitfall #3).
    this.events.once(Phaser.Scenes.Events.SHUTDOWN, this.cleanup, this);
    document.addEventListener('visibilitychange', this.onVisibility);
  }

  update() {
    const speed = 220;
    const body = this.player.body;
    body.setVelocity(0);
    if (this.cursors.left.isDown)  body.setVelocityX(-speed);
    if (this.cursors.right.isDown) body.setVelocityX(speed);
    if (this.cursors.up.isDown)    body.setVelocityY(-speed);
    if (this.cursors.down.isDown)  body.setVelocityY(speed);
    body.velocity.normalize().scale(speed); // no faster diagonals
  }

  private collectCoin(coin: Phaser.Physics.Arcade.Sprite) {
    coin.disableBody(true, false);           // stop physics, keep visible for the tween
    this.score += 10;
    this.scoreText.setText(`Score: ${this.score}`);
    // Juicy feedback — a short pop, then remove.
    this.tweens.add({
      targets: coin,
      scale: { from: 1, to: 1.6 },
      alpha: { from: 1, to: 0 },
      duration: 180,
      ease: 'Cubic.easeOut',
      onComplete: () => coin.destroy(),
    });
  }

  private togglePause() {
    this.scene.pause();
    this.scene.launch('pause'); // overlay scene on top
  }

  private onVisibility = () => {
    if (document.hidden && !this.scene.isPaused()) this.togglePause();
  };

  private cleanup() {
    this.tweens.killAll();
    this.time.removeAllEvents();
    this.input.keyboard?.removeAllKeys(true);
    document.removeEventListener('visibilitychange', this.onVisibility); // undo the global listener
  }
}
```

`src/scenes/PauseScene.ts`:

```ts
import Phaser from 'phaser';

export class PauseScene extends Phaser.Scene {
  constructor() { super('pause'); }
  create() {
    this.add.rectangle(480, 270, 960, 540, 0x000000, 0.55);
    this.add.text(480, 250, 'Paused', { fontSize: '48px', color: '#fff' }).setOrigin(0.5);
    this.add.text(480, 310, 'Press P or Esc to resume', { fontSize: '20px', color: '#ccc' })
      .setOrigin(0.5);
    const resume = () => { this.scene.stop(); this.scene.resume('game'); };
    this.input.keyboard!.on('keydown-P', resume);
    this.input.keyboard!.on('keydown-ESC', resume);
  }
}
```

`src/scenes/BootScene.ts` (minimal — jump straight to game, or add a loader bar here):

```ts
import Phaser from 'phaser';
export class BootScene extends Phaser.Scene {
  constructor() { super('boot'); }
  create() { this.scene.start('game'); }
}
```

### 5. Art from AI/SVG (`game-art-pipeline`) + texture atlases

Produce art through `game-art-pipeline`, drop it in `public/assets/`, then load:

```ts
// Single images
this.load.image('hero', 'assets/hero.png');

// SVG (crisp vector art rasterized at a chosen size — load at 2× if you zoom in)
this.load.svg('shield', 'assets/shield.svg', { width: 128, height: 128 });

// Spritesheet (uniform grid, e.g. from a walk-cycle export)
this.load.spritesheet('run', 'assets/run.png', { frameWidth: 48, frameHeight: 48 });

// Texture ATLAS (TexturePacker / free-packed frames + JSON) — one draw call, many frames
this.load.atlas('ui', 'assets/ui.png', 'assets/ui.json');
```

Use atlas frames and build animations from them:

```ts
this.add.image(100, 100, 'ui', 'button_play');       // frame name from the atlas JSON
this.anims.create({
  key: 'run',
  frames: this.anims.generateFrameNumbers('run', { start: 0, end: 7 }),
  frameRate: 12,
  repeat: -1,
});
this.player.play('run');
```

**Prefer one atlas over many loose PNGs** — fewer HTTP requests and fewer WebGL texture binds (each
texture swap is a draw-call break). Pack related sprites together via `game-art-pipeline`.

### 6. Arcade physics essentials

- **Body vs sprite:** an Arcade body is an axis-aligned rectangle sized to the texture frame. It does
  **not** rotate and does **not** follow non-uniform scale. Fit it explicitly:
  ```ts
  sprite.body.setSize(w, h).setOffset(x, y); // rectangle
  sprite.body.setCircle(r, offX, offY);      // circle (better for round actors)
  ```
- **`collider` vs `overlap`:** `this.physics.add.collider(a, b)` resolves & blocks; `overlap(a, b, cb)`
  only fires a callback (pickups, triggers, damage zones).
- **Static geometry:** `this.physics.add.staticGroup()` for walls/platforms that never move.
- **Debug:** flip `arcade.debug: true` in config to draw body outlines & velocity vectors — the fastest
  way to diagnose a body/sprite mismatch. Turn it off for the shipped build.
- Need rotation, joints, stacking, or slopes? Switch `default: 'matter'` and use `this.matter.*`.

### 7. Tweens — juicy feedback

Tweens are the cheapest way to make a game feel alive: hit-pops, screen-independent easing, pulses.

```ts
this.tweens.add({ targets: sprite, scale: 1.15, yoyo: true, duration: 120, ease: 'Sine.easeInOut' });
this.tweens.chain({ targets: door, tweens: [
  { x: '+=200', duration: 400, ease: 'Cubic.easeInOut' },
  { alpha: 0, duration: 200 },
]});
```

Always `killAll()`/kill the relevant tweens on scene shutdown so callbacks don't fire on destroyed
objects.

### 8. Camera

```ts
this.cameras.main.setBounds(0, 0, worldW, worldH);
this.cameras.main.startFollow(target, true, 0.08, 0.08); // roundPixels, gentle lerp
this.cameras.main.setZoom(1.5);
this.cameras.main.fadeIn(400);
this.cameras.main.flash(150, 255, 255, 255); // brief hit flash
```

Trauma-informed pacing (this is a trauma-support game — keep the player safe and in control):

- **Never trap the player.** Pause is always one key away (`P`/`Esc`) and the game auto-pauses on tab
  blur (shown above). Provide a visible exit.
- **No sudden violent motion.** Skip `camera.shake()` or gate it behind a "reduced motion" toggle and
  honor the OS setting:
  ```ts
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!reduce) this.cameras.main.shake(120, 0.004); // tiny, opt-out-able
  ```
- **Predictable pacing:** no jump-scares, no forced loud audio; ease transitions with fades, keep
  camera lerp gentle, telegraph events.

### 9. Build → static web

```bash
npm run build       # → dist/  (index.html + hashed JS + copied public/assets)
npm run preview     # serve dist/ locally to sanity-check the production build
```

`dist/` is a self-contained static bundle (thanks to `base: './'`). Drop it on any static host or open
via the preview server. Do a production build before shipping — dev-only issues (missing `public/`
asset, absolute path) surface only in `build`.

## Pitfalls

1. **Using an asset before it's loaded.** Anything referenced in `create()`/`update()` must be queued
   in `preload()` (or a prior scene's loader). Symptom: missing/green textures, `Texture not found`.
   Fix: load in `preload`, or gate on `this.load.once('complete', …)`.
2. **Physics body ≠ sprite.** The default AABB body matches the texture frame, ignores rotation, and
   doesn't track non-uniform scale — so collisions feel "off." Fix with `body.setSize/setOffset/setCircle`
   and confirm visually via `arcade.debug: true`.
3. **Memory leaks on scene restart.** `scene.restart()` / `scene.start()` recreates scene objects but
   **not** listeners you attached to global targets (`document`, `window`, `this.game.events`) or
   long-lived tweens/timers. Each restart stacks another listener → runaway callbacks, growing memory,
   ghost input. Fix: register everything you add on `Phaser.Scenes.Events.SHUTDOWN` cleanup — remove DOM
   listeners, `tweens.killAll()`, `time.removeAllEvents()`, `keyboard.removeAllKeys()`.
4. **HiDPI blur.** Phaser 3 has no working `resolution` game-config prop; on Retina/HiDPI the FIT
   upscale can soften text and thin art. Fix: design at a fixed base resolution and upscale with FIT;
   for text call `.setResolution(window.devicePixelRatio)`; for pixel-art games set
   `render: { pixelArt: true, antialias: false, roundPixels: true }`.
5. **No pause / no blur handling.** By default the loop keeps running when the tab loses focus — bad
   for a calm, trauma-safe experience and it burns cycles. Add a Pause scene, a `P`/`Esc` toggle, and a
   `visibilitychange` auto-pause (shown above).
6. **CDN version drift.** `phaser@3` or `@latest` in a `<script>` tag silently upgrades and can break
   the game between sessions. **Pin the exact version** (`phaser@3.80.1`), or better, use the Vite path
   with Phaser in `package.json` so the version is locked and bundled.

## Verification

1. `npm run dev` and open `http://localhost:5173` in Chrome.
2. Open DevTools → **Console must be clean.** Common red flags:
   - `Texture "x" not found` / green-and-black boxes → asset not loaded in `preload` (pitfall #1).
   - `Failed to load resource 404` → wrong path; assets live in `public/assets/` → referenced as
     `assets/…`.
   - WebGL context lost / warnings → too many textures or a leak on restart (pitfall #3).
3. **Screenshot the canvas** and confirm: sprites render, player moves, collisions/overlaps fire,
   tweens play, HUD is crisp, pause works, tab-away pauses.
4. Run through `npm run preview` too — verify the built bundle, not just dev.

Verify checklist: console clean · assets render · movement + collision/overlap fire · tweens play ·
HUD crisp on HiDPI · pause works · tab-blur auto-pauses · production `preview` matches dev.

## Related skills

- **`game-art-pipeline`** — produce AI art / SVG → textures & atlases for loading into Phaser.
- **`html5-canvas-game`** — raw canvas games with no engine, when you want zero dependencies.
- **`three-js-web-game`** — 3D web games with Three.js.
