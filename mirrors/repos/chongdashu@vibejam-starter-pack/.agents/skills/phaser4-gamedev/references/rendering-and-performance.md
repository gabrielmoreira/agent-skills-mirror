# Phaser 4 Rendering and Performance

Phaser 4 performance work starts with one question: what is actually expensive here?

The answer is usually one of these:

- too many independent objects and CPU-side updates
- too many shader or filter changes breaking batches
- too much fill-rate from large filtered or lit surfaces
- incorrect asset choices causing unnecessary work

## Choose the Right Rendering Path

### Standard Game Objects

Use standard sprites, images, text, and tilemaps by default.

They are the right choice when:
- entities are interactive
- state changes frequently
- gameplay logic is per-object
- debugging clarity matters more than raw maximum counts

Do not move to a more specialized path just because it sounds faster.

### `SpriteGPULayer`

Use `SpriteGPULayer` when you need huge numbers of mostly simple quads with predictable animation behavior.

Good fit:
- starfields
- animated backgrounds
- particle-like swarms
- dense decorative motion

Bad fit:
- ordinary enemies with unique gameplay logic
- objects that need constant structural edits
- scenes where per-member mutation is more important than raw count

The layer is fast because it avoids ordinary per-object CPU work. The tradeoff is flexibility.

### `TilemapGPULayer`

Use `TilemapGPULayer` when:
- the map is orthographic
- one tileset is sufficient
- very large visible tile counts matter
- smooth filtering without seams matters

Do not use it as a reflex upgrade over `TilemapLayer`. Its constraints are real.

After editing layer data, regenerate the layer data texture so the GPU representation stays correct.

### `RenderTexture` and `DynamicTexture`

Use these when you need:
- texture capture
- compositing
- reuse of generated visuals
- staged multi-pass effects

Remember that queued work is not the same as executed work. Call `render()` when the texture must update.

## Batch Breakers

These features are valuable, but they are not free:

- filters
- lighting
- shader changes
- unusual blend behavior
- render target switches

Use them where the effect is visible and justified. A subtle glow on one hero object may be worth it; the same glow on every prop usually is not.

## Pixel Art Guidance

Phaser 4 no longer defaults to old `roundPixels` behavior.

For pixel art:
- start with `roundPixels: false`
- enable per-object rounding only where needed
- test camera movement, scaling, and rotation before committing

If the scene has transforms everywhere, forcing full rounding can trade shimmer for wobble. That is a stylistic choice, not a default.

## Debugging Order

When performance is poor:

1. Count object types and churn.
2. Check whether filters or lighting are everywhere.
3. Identify whether a GPU layer would simplify the scene.
4. Verify textures and tile data are not causing avoidable redraws.
5. Profile before rewriting architecture.

## Anti-Patterns

- Using shader/filter solutions for problems that tint, texture, or art direction could solve
- Moving gameplay entities into `SpriteGPULayer` too early
- Assuming the most GPU-heavy path is the fastest path
- Optimizing before validating correctness
