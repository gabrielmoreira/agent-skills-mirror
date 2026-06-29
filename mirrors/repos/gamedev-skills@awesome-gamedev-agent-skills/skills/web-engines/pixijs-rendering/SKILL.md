---
name: pixijs-rendering
description: >
  Build a PixiJS v8 render layer: create the async Application, load textures with
  Assets, compose the scene graph with Container and Sprite, drive the ticker loop,
  wire pointer events, and group draws with render groups. Use when building or
  debugging PixiJS v8 — when the user mentions PixiJS, Pixi, Application, app.stage,
  Container, Sprite, Assets.load, app.ticker, or eventMode. Pins the v8 async
  init() API.
license: Apache-2.0
compatibility: PixiJS v8 (npm pixi.js@8; Node 20+; WebGL/WebGPU)
metadata:
  engine: pixijs
  category: web-engines
  difficulty: intermediate
---

# PixiJS v8 Rendering

Set up and structure a PixiJS **v8** application: the async `Application`, asset
loading via `Assets`, the `Container`/`Sprite` scene graph, the ticker loop,
pointer events, and render groups. Pins the v8 API (async `init`, unified
`Assets`, `eventMode`).

## When to use

- Use when starting a PixiJS v8 project, fixing a blank canvas, structuring the
  display list, loading textures, animating via the ticker, or handling pointer
  input.
- Use when `package.json` depends on `pixi.js` (v8) and code does
  `import { Application } from 'pixi.js'`.

**When *not* to use:** Phaser's scene/loader model → `phaser-core`. 3D scenes →
`threejs-scene-setup`. PixiJS v7-and-earlier code (synchronous `new
Application({...})`, `Loader`, `interactive = true`) needs the v8 migration first;
this skill targets v8 only.

## Core workflow

1. **Create and `await` the Application.** In v8, `new Application()` is empty;
   configuration happens in `await app.init({...})`. Append `app.canvas` (not
   `app.view`) to the DOM. Wrap top-level `await` in an async function for bundlers.
2. **Load assets with `Assets`.** `await Assets.load(url)` returns a `Texture`. For
   many assets, register a manifest/bundle and load by name. There is no v7 `Loader`.
3. **Build the scene graph.** Everything descends from `app.stage` (a `Container`).
   Group related objects in `Container`s; child transforms are relative to the
   parent. Draw order = insertion order (later = on top).
4. **Animate with the ticker.** `app.ticker.add((ticker) => {...})`. Scale motion by
   `ticker.deltaTime` (frames, ~1 at 60fps) or `ticker.deltaMS` (milliseconds) so
   speed is frame-rate independent.
5. **Enable events per object** by setting `eventMode = 'static'` (or `'dynamic'`),
   then `obj.on('pointerdown', ...)`. Federated pointer events cover mouse/touch/pen.
6. **Promote big static subtrees to render groups** (`isRenderGroup: true`) so the
   GPU caches their transforms. Profile before and after; confirm pixels on screen.

## Patterns

### 1. Async Application boot (the v8 entry point)

```js
import { Application, Assets, Sprite } from 'pixi.js';

(async () => {
  // v8: construct empty, then await init(). Config does NOT go in the constructor.
  const app = new Application();
  await app.init({
    background: '#1099bb',
    resizeTo: window,        // track the window size
    antialias: true,
    // preference: 'webgpu',  // opt into WebGPU; default 'webgl'
  });

  document.body.appendChild(app.canvas); // v8 uses app.canvas, not app.view

  const texture = await Assets.load('https://pixijs.com/assets/bunny.png');
  const bunny = new Sprite(texture);
  bunny.anchor.set(0.5);
  bunny.position.set(app.screen.width / 2, app.screen.height / 2);
  app.stage.addChild(bunny);
})();
```

### 2. Containers for a relative-transform scene graph

```js
import { Container, Sprite } from 'pixi.js';

const world = new Container();
app.stage.addChild(world);

// Children are positioned relative to `world`; move/scale/rotate the whole group
// by transforming the parent.
for (let i = 0; i < 10; i++) {
  const coin = new Sprite(coinTexture);
  coin.x = i * 40;
  world.addChild(coin);
}
world.position.set(100, 100);
world.scale.set(2);            // every coin scales with the container
```

### 3. The ticker loop (frame-rate independent)

```js
let elapsed = 0;
app.ticker.add((ticker) => {
  // deltaTime ≈ 1 at 60fps; deltaMS is milliseconds since last frame.
  elapsed += ticker.deltaMS;
  bunny.rotation += 0.05 * ticker.deltaTime;          // smooth at any frame rate
  bunny.y = app.screen.height / 2 + Math.sin(elapsed / 500) * 50;
});
```

### 4. Pointer events (federated)

```js
bunny.eventMode = 'static';   // 'static' = interactive, doesn't move on its own
bunny.cursor = 'pointer';
bunny.on('pointerdown', (event) => {
  bunny.tint = 0xff0000;
  // event.global is the pointer position in stage space.
});
bunny.on('pointerover', () => bunny.scale.set(1.1));
bunny.on('pointerout',  () => bunny.scale.set(1.0));
```

### 5. Loading many assets by name (bundles)

```js
import { Assets } from 'pixi.js';

await Assets.init({
  manifest: {
    bundles: [{
      name: 'level-1',
      assets: [
        { alias: 'hero',  src: 'assets/hero.png' },
        { alias: 'tiles', src: 'assets/tiles.png' },
      ],
    }],
  },
});

const bundle = await Assets.loadBundle('level-1'); // { hero: Texture, tiles: Texture }
const hero = new Sprite(bundle.hero);
```

### 6. Render groups for large static layers

```js
// A big, rarely-changing background subtree: let the GPU cache its transforms.
const background = new Container({ isRenderGroup: true });
app.stage.addChild(background);
// Add hundreds of static tiles to `background`. Moving `background` itself stays
// cheap; constantly re-adding/removing children negates the benefit.
```

## Pitfalls

- **Blank canvas / "app.stage is undefined"** → you didn't `await app.init()`, or you
  configured the constructor. In v8 the constructor is empty; all options go to
  `init()`.
- **`app.view` is undefined** → v8 renamed it to `app.canvas`.
- **v7 code throwing** → `interactive = true` → `eventMode = 'static'`; `Loader`/
  `loader.add` → `Assets.load`; synchronous `new Application({...})` → async `init`.
- **Top-level await build error (Vite ≤6.0.6)** → wrap boot in `(async () => { ... })()`.
- **Speed varies with frame rate** → multiply movement by `ticker.deltaTime` (or use
  `deltaMS`); never assume 60fps.
- **Clicks do nothing** → the object's `eventMode` is still `'none'` (the default);
  set it to `'static'` or `'dynamic'`.
- **Textures look blurry on pixel art** → set
  `texture.source.scaleMode = 'nearest'` (or pass it when loading).
- **Memory grows** → `removeChild` does not free GPU memory; call
  `sprite.destroy()` and `Assets.unload(url)` for assets you're done with.

## References

- For the texture/asset pipeline (sprite sheets/atlases, `Assets.add`, background
  loading, unloading) and Graphics/Text/`TilingSprite`/`ParticleContainer` plus
  filters, read `references/assets-and-display.md`.

## Related skills

- `phaser-core` — a batteries-included 2D framework (scenes, physics, input).
- `threejs-scene-setup` — 3D in the browser with three.js.
- `prototype-fast` — greybox a playable slice quickly (often cites PixiJS).
