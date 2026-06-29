# PixiJS v8 assets & display objects

Depth on the v8 asset pipeline and the display-object types beyond `Sprite`. The
`SKILL.md` covers the boot path and scene graph; this file fills in textures and
the other things you draw.

## The `Assets` system (v8)

`Assets` replaces the v7 `Loader`. It caches by URL/alias, so calling
`Assets.load` twice for the same source resolves immediately the second time.

```js
import { Assets } from 'pixi.js';

// Single asset.
const tex = await Assets.load('assets/hero.png');

// Register aliases up front, load later by name.
Assets.add({ alias: 'hero', src: 'assets/hero.png' });
const hero = await Assets.load('hero');

// Load several at once (object form keeps results keyed).
const sheet = await Assets.load([ 'a.png', 'b.png' ]);

// Background-load without blocking, then `load` resolves instantly when needed.
Assets.backgroundLoad(['level-2-bg.png']);

// Free GPU + CPU memory when a screen is done.
await Assets.unload('hero');
```

Supported source types include images, sprite-sheet JSON (atlases), bitmap fonts,
web fonts, and audio (with the right loader installed). Atlases load as a
`Spritesheet`; access frames by name:

```js
const sheet = await Assets.load('assets/characters.json'); // TexturePacker JSON
const idle = new Sprite(sheet.textures['hero_idle.png']);
const runFrames = sheet.animations['hero_run'];            // Texture[] for animation
```

## Texture settings

```js
import { Texture } from 'pixi.js';

texture.source.scaleMode = 'nearest';  // crisp pixel art ('linear' is the default)
const sub = new Texture({ source: texture.source, frame: new Rectangle(0, 0, 16, 16) });
```

`Texture` is a view into a `TextureSource` (the GPU resource). Many `Texture`s can
share one source — that's how atlases avoid extra uploads.

## Display object types

### AnimatedSprite

```js
import { AnimatedSprite } from 'pixi.js';
const anim = new AnimatedSprite(sheet.animations['hero_run']);
anim.animationSpeed = 0.2;   // fraction of a frame per ticker tick
anim.play();
app.stage.addChild(anim);
```

### Graphics (vector drawing)

v8 uses a fluent, retained API: define the shape, then call a fill/stroke.

```js
import { Graphics } from 'pixi.js';
const g = new Graphics()
  .roundRect(0, 0, 120, 60, 12)
  .fill(0x4488ff)
  .stroke({ width: 2, color: 0xffffff });
app.stage.addChild(g);
```

(In v7 the order was `beginFill` → draw → `endFill`; v8 draws the shape first, then
fills/strokes it.)

### Text & BitmapText

```js
import { Text, TextStyle } from 'pixi.js';
const score = new Text({
  text: 'Score: 0',
  style: new TextStyle({ fontFamily: 'Arial', fontSize: 24, fill: '#ffffff' }),
});
```

Use `BitmapText` for frequently changing strings (HUD counters): it re-uses glyph
textures instead of rasterising new ones each change.

### TilingSprite (scrolling backgrounds)

```js
import { TilingSprite } from 'pixi.js';
const bg = new TilingSprite({ texture: skyTexture, width: app.screen.width, height: app.screen.height });
app.ticker.add((t) => { bg.tilePosition.x -= 0.5 * t.deltaTime; });
```

### ParticleContainer (many simple sprites)

For thousands of cheap, same-texture sprites (bullets, particles), a
`ParticleContainer` trades per-child features for throughput. Keep dynamic
properties (position/rotation/etc.) explicit and avoid features it doesn't support.

## Filters

Filters are GPU post-process effects applied to a display object and its children:

```js
import { BlurFilter } from 'pixi.js';
container.filters = [new BlurFilter({ strength: 4 })];
```

Filters render the subtree to a temporary texture, so they cost memory and fill
rate — apply sparingly and remove (`obj.filters = null`) when not needed.

## Cleanup

- `removeChild(child)` detaches but does **not** free GPU memory.
- `child.destroy()` frees the display object; pass options to also destroy its
  texture: `sprite.destroy({ texture: true, textureSource: true })`.
- `Assets.unload(urlOrAlias)` frees a loaded asset's GPU/CPU memory.
- On WebGL/WebGPU context loss, textures are restored from their sources; keep the
  source (or be ready to reload) for anything generated at runtime.
