---
name: openmotion-liquid-logo
description: >-
  OpenMotion — Make a logo reveal where glossy liquid drops flow in, merge and settle into the logo mark. Use for drinks, beauty, wellness and any brand with a fluid, friendly feel.
---

# OpenMotion · Liquid Logo

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** logo openers and end cards for drinks, beauty, wellness and friendly consumer brands.

## Look

| Element | Starting value |
| --- | --- |
| Background | Deep blue `#06224A` to `#0A3C7A` gradient with soft light rays from the top |
| Liquid | Merging blobs built with an SVG goo filter (blur then alpha threshold); aqua `#3BD2FF` to blue `#1E6BFF` gradient fill; specular highlight on top |
| Mark | The logo as a solid shape that the liquid settles into; must be simple and closed |
| Wordmark | Rounded sans (e.g. Nunito 800) in white |
| Extras | A few floating bubbles at 30–50% opacity |

## Motion

- Drops enter from the frame edges and orbit the centre for 1.5–2.5 s, merging and splitting.
- They pull into the logo shape over 1–1.5 s; the goo filter makes the joins look wet.
- Swap the liquid for the crisp logo with a 300 ms crossfade so the final mark is exact.
- The wordmark rises 20 px and fades in; hold 2 s with a slow shine.

## Inputs

Required: logo (simple SVG shape works best), brand name. Optional: brand colours, tagline. Liquid is drawn in SVG; when the user wants photoreal liquid, generate one test clip through `openmotion_media_use` → `openmotion_assets_use`, get it approved before any further generation, and still finish on the exact logo.

## Avoid

Thin or detailed logos that the goo destroys, more than two liquid colours, the liquid still wobbling in the final hold.

## Review

The final logo is the exact supplied shape; blobs never cover the wordmark; motion stays smooth at 30 fps.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
