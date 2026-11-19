---
name: openmotion-surreal-3d-poster
description: >-
  OpenMotion — Build a surreal 3D product poster: the product stands in a soft sculptural world of tubes, arches or floating forms in one muted palette, with oversized thin type behind it. Use for beauty, wellness and design-led product launches.
---

# OpenMotion · Surreal 3D Poster

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** beauty, wellness and design-led products that sell on mood rather than specs.

## Look

| Element | Starting value |
| --- | --- |
| World | Smooth clay-like forms — looping tubes, arches, spheres, steps — in one tone, e.g. stone `#D9D3C7` with shadows `#B8B0A2` |
| Light | Large soft key from the top left, gentle ambient occlusion, no hard specular spots |
| Product | Centre, 45–60% of the frame height, standing on or inside a form, crisp and true to the photo |
| Type | Oversized thin sans or serif word behind the product, `#FFFFFF` or a tone 10% lighter than the world; small script or caps tagline |
| Icons | Up to four thin line icons with two-word labels near the bottom |

## Motion

- Forms drift and rotate slowly (5–10° over the whole shot), each on its own sine timing; nothing snaps.
- The product rises from behind a form or a sphere rolls aside to reveal it, 900–1200 ms, ease in-out.
- The big word scales from 1.08 to 1.0 behind the product over 2 s, so depth reads.
- Icons fade up last, 120 ms apart.

## Inputs

Required: a cut-out photo of the real product, product name, a one-line tagline. Optional: up to four benefit labels, palette.

The sculptural world is generated through `openmotion_media_use` → `openmotion_assets_use`. Approve one test still first. Composite the user's product photo on top; never regenerate the product itself.

## Avoid

More than two hues, glossy plastic look, forms crossing the product label, physics-breaking speed.

## Review

The world reads as one material; the label is sharp; the big word sits behind the product; motion is slow enough to loop.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
