# Sprite Production Checklist

## Design

- Sprite reads clearly at final in-game size.
- Silhouette, value, and color separate the sprite from likely backgrounds.
- Perspective, lighting, line weight, and proportions match the asset set.
- Character, enemy, item, tile, UI, or VFX role is obvious.
- Variants preserve identity while communicating state or type.

## Animation

- Animation states are named and scoped.
- Key poses communicate action clearly.
- Frame count and timing match gameplay responsiveness.
- Loops do not pop unless intentional.
- Feet, weapon tips, shadows, and VFX anchors do not jitter between frames.
- Attack, hit, interaction, and damage frames align with gameplay timing.

## Sheet And Atlas

- Frame dimensions, tile size, and grid layout are documented.
- Transparent background is preserved.
- Padding and border padding prevent bleeding.
- Edge extrusion is used when scaling/filtering requires it.
- Trimmed frames include metadata and do not shift pivots unexpectedly.
- File names and animation tags are stable and engine-friendly.

## Engine Readiness

- Pivot/origin is defined.
- Hitbox, hurtbox, collision, and interaction bounds are gameplay-appropriate.
- Texture filtering, pixel snapping, scaling, and camera zoom preserve the intended style.
- Sprite imports cleanly into Phaser, engine atlas tools, or the target pipeline.
- Tile sets define terrain transitions, collision, animated tiles, and autotile rules where relevant.

## Generation QA

- Generated variants keep the same character identity, pose logic, and proportions.
- No stray artifacts, halos, inconsistent shadows, broken transparency, or mismatched frame sizes.
- Source prompts/settings and provenance are retained when AI-generated assets are used.
