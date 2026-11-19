---
name: openmotion-liquid-glass-logo
description: >-
  OpenMotion — Make a 4 second logo reveal where a glossy glass app icon ripples into focus, then slides aside for the wordmark. Use for app openers, end cards and launch teasers.
---

# OpenMotion · Liquid Glass Logo

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** app openers, end cards and launch teasers that need a premium 3–5 s logo moment.

## Look

| Element | Starting value |
| --- | --- |
| Background | Pure black `#000000` or very dark grey |
| Glass tile | Rounded square (22% corner radius), translucent fill, white inner highlight, iridescent rim from cyan `#6FE3FF` through violet `#A98BFF` to warm `#FFD38A` |
| Mark | The user's logo inside the tile, white, slightly refracted while the glass moves |
| Wordmark | Rounded geometric sans (e.g. Unbounded 600) in white |
| Glow | Soft outer glow at 20–30% under the tile |

## Motion

- 0–1.2 s: the tile grows from 80% with a ripple distortion that settles to zero.
- 1.2–2 s: one specular streak sweeps across the glass in 600 ms.
- 2–3 s: the tile shrinks and slides left; the wordmark resolves from a brief colour-fringed blur (≤250 ms).
- 3–4 s: hold the lockup clean; a slow sheen may pass again on longer versions.

## Inputs

Required: logo (SVG or transparent PNG), wordmark text. Optional: brand colours for the rim, tagline.

## Avoid

Distorting the logo in the final hold, rainbow rims on the wordmark, glass tiles with no contrast against the background.

## Review

The final lockup matches the supplied logo exactly; distortion is zero by the hold; the lockup reads at small size.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
