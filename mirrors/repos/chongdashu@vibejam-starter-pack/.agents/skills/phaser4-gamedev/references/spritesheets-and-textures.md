# Phaser 4 Spritesheets and Textures

Most "rendering bugs" in 2D games are still asset metadata bugs.

Measure first.

## Before Loading

Confirm these values from the source asset:

- full image width and height
- frame width and height
- spacing
- margin
- atlas frame bounds
- whether the asset is pixel art or smooth art
- whether the texture is compressed

Do not infer any of these from appearance alone.

## Spritesheets

For spritesheets:

- compute the frame grid from exact dimensions
- verify spacing and margin numerically
- confirm whether frames are square or rectangular
- test the final frame index and row count, not just the first frame

One wrong measurement can look like a timing, animation, or rendering issue later.

## Atlases

For atlases:

- trust the atlas data, not visual intuition
- confirm the frame names the code expects actually exist
- inspect trimmed frames carefully when using tight collision or origin assumptions

## Texture Orientation

Phaser 4 uses GL-style texture orientation internally.

This matters most when:
- writing custom shaders
- using framebuffer outputs
- loading compressed textures

For ordinary PNG or JPG loading, Phaser handles the common cases for you.

For compressed textures, verify the Y-axis orientation during asset generation. If the old asset pipeline targeted Phaser 3 assumptions, it may need regeneration.

## `TileSprite`

Phaser 4 `TileSprite` is more capable, but it is not the old object internally.

Key implications:
- texture cropping support is gone
- repeating atlas or spritesheet frames is now viable
- `tileRotation` is available

If the old implementation relied on crop-based repetition tricks, redesign the approach instead of forcing the old behavior.

## Shader-Adjacent Texture Checks

If a shader effect looks upside down, mirrored, or vertically offset:

1. verify the shader's UV assumptions
2. verify the source texture orientation
3. verify whether the source came from a framebuffer or compressed texture path

Do not immediately blame the math if the asset pipeline may be wrong.

## Anti-Patterns

- Eyeballing frame dimensions
- Assuming all texture sources share the same orientation rules
- Debugging animation timing before verifying frame metadata
- Treating compressed textures like ordinary PNGs during migration
