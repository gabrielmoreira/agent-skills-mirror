---
name: openmotion-premium-halo
description: >-
  OpenMotion — Make a high-end product promo on deep blue: a comet draws a glowing halo around the headline, the halo tilts into a light floor, the product rises into it and frosted glass spec chips orbit in. Use for premium hardware, wearables, audio and flagship app launches.
---

# OpenMotion · Premium Halo

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** premium hardware, wearables and flagship launches.

## Look

| Element | Starting value |
| --- | --- |
| Background | Radial deep blue: `#12306E` centre to `#040A20` edges |
| Halo | Cyan `#5CE1FF` ring, 8–10 px stroke with a strong glow, comet head in white-to-cyan, faint full-circle guide at 12% |
| Product | Centred, 70–75% of frame height, soft cyan rim glow, slow light sweep |
| Type | One clean geometric sans; 60–70 px headline with one cyan phrase; wordmark 40–46 px with 0.4 em letter spacing |
| Chips | Frosted glass cards (white 5–16% fill, 12 px blur, 1 px cyan edge), 30 px title and 18 px detail |

## Motion

- The comet starts drawing the halo at frame 0 and closes the ring in about 1.7 s, then keeps orbiting.
- Headline lines de-blur and rise inside the ring (600 ms, 300 ms stagger); the ring pulses once when it closes.
- The ring tilts into a flattened floor ellipse below the product (1 s power3) while the product rises 260 px into place (1.1 s), then floats a few pixels.
- Spec chips arrive from their corners (550 ms, 220 ms stagger) and drift ±8 px; the wordmark tightens in from wide spacing.

## Inputs

Required: product name, a two-part headline, three or four real specs with short details, a product shot or clean render from the user. If no product image exists, generate one through `openmotion_media_use` → `openmotion_assets_use` after one test image is approved. Optional: brand accent to replace cyan, launch date the user confirms.

## Avoid

More than four chips, chips covering the product, warm or neon accents next to the cyan, spec numbers not on the official spec sheet, fast spins of the product.

## Review

Specs match the source; chips never overlap the product; the halo is visible in every frame.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
