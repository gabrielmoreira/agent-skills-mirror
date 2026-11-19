---
name: openmotion-dark-premium-poster
description: >-
  OpenMotion — Animate a dark premium product poster: near-black stage, one spotlight, slow reveal of the product with a light sweep and refined condensed type. Use for perfume, drinks, audio gear and launch teasers that should feel expensive.
---

# OpenMotion · Dark Premium Poster

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** premium launches, limited editions and teasers for perfume, spirits, sparkling drinks, headphones and watches.

## Look

| Element | Starting value |
| --- | --- |
| Stage | Near-black `#0B0B0F` with a soft spotlight pool, `#2A2A33` at the centre; faint film grain at 4% |
| Product | Centre or slightly right, 55–70% of the frame height, rim light on one edge, reflection on a dark floor |
| Accent | One metal or brand tone only, e.g. warm gold `#C9A45C` or violet `#7B4DFF` |
| Type | Large condensed caps for the name, wide-tracked small caps (letter-spacing 0.25–0.35 em) for details |
| Details | Two or three thin spec lines in the corners, hairline rules at 30% white |

## Motion

- Open in darkness; the spotlight fades up over 800–1200 ms to reveal the product.
- A diagonal light sweep crosses the product once in 700–900 ms.
- The product rises 10–20 px or rotates ≤8°, slow and eased (power2), never bouncy.
- Name letters fade in with tracking tightening from 0.5 em to 0.3 em over 1 s; spec lines follow.

## Inputs

Required: a clean photo or cut-out of the real product, product name, the exact detail lines. Optional: accent colour, release date, edition number.

Backgrounds, smoke or reflections that the photo lacks are generated through `openmotion_media_use` → `openmotion_assets_use`. Approve one test still first; keep the user's product pixels for the product itself.

## Avoid

Glows on every element, more than one accent colour, fast cuts, busy backgrounds, crushed blacks that hide the product edge.

## Review

The product silhouette stays readable against black; one light sweep only; type is aligned to one grid; small caps are at least 18 px at 720p.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
