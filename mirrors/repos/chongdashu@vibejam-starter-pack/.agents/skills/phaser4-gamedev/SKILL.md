---
name: phaser4-gamedev
description: "Build 2D browser games with Phaser 4: WebGL-first rendering, scenes, filters, lighting, shaders, DynamicTexture and RenderTexture, tilemaps, SpriteGPULayer, TilemapGPULayer, and Phaser 3 to 4 migration work."
metadata:
  short-description: "Phaser 4 game dev and migration."
---

# Phaser 4 Game Development

Build 2D browser games using Phaser 4's WebGL-first renderer, scene model, and updated rendering APIs.

## Philosophy: Renderer-Aware, Asset-Exact

Phaser 4 is not Phaser 3 with a few renamed methods. The renderer, filter model, shader assumptions, texture orientation, and batching behavior changed. Good Phaser 4 work starts by choosing the right rendering path and measuring assets before code is written.

**Before coding, ask:**
- Is this a new Phaser 4 feature or a Phaser 3 migration?
- Does this feature stay on standard game object APIs, or does it depend on filters, shaders, lighting, or custom rendering?
- What is the asset source of truth: exact frame size, spacing, margin, atlas bounds, and texture orientation?
- Is the bottleneck CPU object churn, GPU fill rate, or batch breaking?
- Would `SpriteGPULayer`, `TilemapGPULayer`, `RenderTexture`, or a plain `Sprite` solve this more cleanly?

**Core principles**:
1. **WebGL-first, not Canvas-first**: Phaser 4 is designed around WebGL. Treat Canvas as legacy compatibility, not the default target.
2. **Measure assets before loader config**: Sprite and tile bugs often start as incorrect frame metadata, not rendering bugs.
3. **Prefer the simplest rendering path**: Use standard game objects until scale or effect requirements justify filters, GPU layers, or shader work.
4. **Treat rendering features as architectural choices**: Filters, lighting, shaders, and render textures affect coordinate systems, batching, and debugging.
5. **Migration is selective redesign**: Basic scene code may port cleanly, but masks, FX, custom pipelines, shaders, and texture workflows usually need real updates.

## STOP: Before Loading Any Spritesheet or Atlas

Read `references/spritesheets-and-textures.md` first.

Spritesheet loading is still fragile. A few pixels off in frame size, spacing, or margin can create silent corruption that looks like animation or rendering bugs later.

**NEVER** guess frame dimensions.  
**DO NOT** assume texture orientation details are irrelevant if compressed textures or custom shaders are involved.

## STOP: Before Porting Phaser 3 Code

Read `references/migration-hotspots.md` first.

Search for the Phaser 3 APIs that changed meaning or disappeared. These are where most migration time goes:

- `setTintFill`
- `BitmapMask`
- `preFX` / `postFX`
- `Phaser.Geom.Point`
- `Math.TAU` / `Math.PI2`
- `setPipeline('Light2D')`
- `DynamicTexture` / `RenderTexture`
- custom pipelines
- custom shader code
- `TileSprite` cropping

## Reference Files

Read these before working on the relevant feature:

| When working on... | Read first |
|--------------------|------------|
| Migrating Phaser 3 code | `references/migration-hotspots.md` |
| Loading spritesheets, atlases, compressed textures, or TileSprite | `references/spritesheets-and-textures.md` |
| Performance issues, GPU layers, filters, lighting, or batching | `references/rendering-and-performance.md` |

## Architecture Decisions (Make Early)

### Rendering Path Choice

| Path | Use when |
|------|----------|
| Standard game objects | Most gameplay, UI, and ordinary animation |
| `SpriteGPULayer` | Very large numbers of mostly simple quads or particle-like members |
| `TilemapGPULayer` | Very large orthographic tile layers using one tileset |
| `RenderTexture` / `DynamicTexture` | You need capture, compositing, stamping, or texture reuse |
| Filters / Shader | The effect is genuinely image-space or shader-driven |

### Physics System Choice

| System | Use when |
|--------|----------|
| Arcade | Platformers, shooters, most 2D action games |
| Matter | Physics puzzles, compound bodies, more realistic collisions |
| None | Menu scenes, card games, visual novels, strategy UIs |

### Scene Structure

```text
scenes/
├── BootScene.ts      # Asset loading, progress bar, shader/texture setup
├── MenuScene.ts      # Title screen and options
├── GameScene.ts      # Main gameplay
├── UIScene.ts        # HUD overlay (launched in parallel)
└── GameOverScene.ts  # End screen and restart flow
```

### Scene Transitions

```ts
this.scene.start('GameScene', { level: 1 }); // Stop current, start new
this.scene.launch('UIScene');                // Run in parallel
this.scene.pause('GameScene');               // Pause
this.scene.stop('UIScene');                  // Stop
```

## Core Patterns

### Game Configuration

Prefer explicit WebGL unless there is a concrete reason not to.

```ts
const config: Phaser.Types.Core.GameConfig = {
  type: Phaser.WEBGL,
  width: 800,
  height: 600,
  roundPixels: false,
  scale: {
    mode: Phaser.Scale.FIT,
    autoCenter: Phaser.Scale.CENTER_BOTH
  },
  physics: {
    default: 'arcade',
    arcade: { gravity: { y: 300 }, debug: false }
  },
  scene: [BootScene, MenuScene, GameScene]
};
```

### Scene Lifecycle

```ts
class GameScene extends Phaser.Scene {
  init(data: unknown) {} // Receive data from previous scene
  preload() {}           // Load assets before create
  create() {}            // Set up game objects, physics, input
  update(time: number, delta: number) {} // Use delta for frame-rate independence
}
```

### Frame-Rate Independent Movement

```ts
// Correct: scales with frame rate
this.player.x += this.speed * (delta / 1000);

// Wrong: varies with frame rate
this.player.x += this.speed;
```

### Phaser 4 Migration Replacements

```ts
// Phaser 3
sprite.setTintFill(0xff0000);

// Phaser 4
sprite.setTint(0xff0000).setTintMode(Phaser.TintModes.FILL);
```

```ts
// Phaser 3
sprite.setPipeline('Light2D');

// Phaser 4
sprite.setLighting(true);
```

```ts
// Phaser 3
const mask = new Phaser.Display.Masks.BitmapMask(scene, maskObject);
sprite.setMask(mask);

// Phaser 4
sprite.filters.internal.addMask(maskObject);
```

### RenderTexture and DynamicTexture

Phaser 4 buffers drawing commands. If you queue drawing work into a `DynamicTexture` or `RenderTexture`, execute it deliberately.

```ts
const rt = this.add.renderTexture(0, 0, 256, 256);

rt.draw(sprite, 0, 0);
rt.render();
```

Use `preserve()` or render modes only when they solve a concrete problem. Extra indirection complicates debugging quickly.

### Pixel Rounding

Do not assume old `roundPixels` behavior. Phaser 4 defaults it to `false`, and per-object control is more explicit.

```ts
sprite.vertexRoundMode = 'safe';
```

Use rounding intentionally for pixel art. Leave it off for rotated, scaled, or camera-heavy scenes unless you want the visual tradeoff.

## Anti-Patterns to Avoid

| Anti-pattern | Why it hurts | Better |
|--------------|--------------|--------|
| Treating Phaser 4 as a drop-in Phaser 3 upgrade | You miss renderer, filter, shader, and texture changes | Audit migration hotspots first, then port intentionally |
| Starting new work on Canvas-first assumptions | Many Phaser 4 features are WebGL-centric or unavailable in Canvas | Design for WebGL and treat Canvas as fallback only if required |
| Guessing spritesheet or atlas metadata | Visual corruption appears far away from the actual mistake | Measure frames, spacing, margin, and bounds before loading |
| Using filters or shaders for every visual effect | More complexity, more batch breaks, harder debugging | Use plain sprites, textures, and tint where possible |
| Applying lighting or filters everywhere | Shader changes break batches and can tank performance | Reserve them for objects that benefit visually |
| Forgetting `render()` on `DynamicTexture` or `RenderTexture` | Queued work never lands on the texture | Make render execution explicit in the workflow |
| Using `SpriteGPULayer` for frequently mutated gameplay entities | Its strength is scale, not arbitrary object behavior | Keep complex interactive entities on normal game objects |
| Assuming `TilemapGPULayer` is a universal tilemap replacement | It is orthographic-only and more constrained | Use it when the layer size and rendering profile justify it |
| Making raw `gl` calls outside supported integration points | You can desync Phaser's renderer state | Use `Extern` or higher-level Phaser APIs |

Common pitfall: "the port compiles, so the migration is done." Rendering, shader, and texture bugs often survive the first compile.

## Variation Guidance

Avoid converging on a single Phaser 4 setup. Choose based on context:

- Rendering path: standard objects vs GPU layers vs textures vs shader/filter pipelines
- Physics: Arcade vs Matter vs none
- Content: tilemaps vs pure sprites vs hybrid
- Pixel art handling: `roundPixels` off, safe per-object rounding, or deliberate full rounding
- Assets: spritesheets vs atlases vs single textures
- Scene layout: separate `UIScene` vs in-scene HUD

What should vary is the architecture, not the rigor. Measure assets, check batching costs, and adapt the solution to the game's real constraints.

## Remember

Phaser 4 gives you a more capable renderer and more explicit rendering tools, but it expects better architectural choices in return.

Before coding: what rendering path are you choosing, what assets define the truth, and what batch-breaking features are actually worth their cost?

Codex can do strong Phaser 4 work when the problem is framed precisely: scene boundaries, asset dimensions, rendering constraints, performance targets, and migration scope. These guidelines illuminate the path; they do not replace engineering judgment.
