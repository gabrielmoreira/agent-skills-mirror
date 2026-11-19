---
name: openmotion-chalk-blueprint
description: >-
  OpenMotion — Sketch the product in thin chalk-white lines on a dark blue grid, then light the key parts in cyan and resolve to the logo. Use for developer tools, APIs and technical product promos.
---

# OpenMotion · Chalk Blueprint

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** developer tools, APIs, infrastructure and planning apps where structure and precision are the story.

## Look

| Element | Starting value |
| --- | --- |
| Background | Deep blueprint `#13202E` with a faint chalk-dust texture and a 40 px grid at 8% white |
| Lines | 1.5–2 px chalk white `#DCE6EF`, construction circles and diagonals, small node dots |
| Accent | Cyan `#3AA0F0` for the active path, node and the second half of the wordmark |
| Type | Thin geometric sans, light weight, wide tracking; short lines typed on beside the drawing |

## Motion

- Lines draw on with stroke-dash animation, 400–900 ms per shape, construction lines first and the final shape last.
- Nodes pop in (120 ms) where lines meet; one path at a time turns cyan to show flow.
- The camera drifts slowly across a tiled pattern of the drawing (≤20 px/s) between beats.
- Captions type on at 25–35 characters per second next to the shape they describe.
- End: the drawing clears, the wordmark draws on, an underline extends, tagline types; hold 1.5 s.

## Inputs

Required: product name, 2–4 short lines on what it does, the UI or architecture to sketch (screenshots or a diagram). Optional: Brandkit accent colour.

## Avoid

Filled shapes or gradients, more than one accent colour, drawing every UI detail, fast camera moves.

## Review

Every line reads on a phone screen; cyan marks only the active part; captions sit clear of lines; drawing matches the real product structure.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
