---
name: openmotion-aurora-gradient
description: >-
  OpenMotion — Make a SaaS hero film on a dark ground with slow, glowing aurora blobs, a short headline and a product dashboard that tilts into view. Use for app and dashboard launches that want a premium landing-page feel.
---

# OpenMotion · Aurora Gradient

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** SaaS launches, dashboard or analytics products, feature announcements and the first 10 s of a product page video.

## Look

| Element | Starting value |
| --- | --- |
| Background | Deep plum-black `#0B0610` |
| Aurora | 2–3 large blurred blobs (blur 80–140 px): magenta `#E8459A`, amber `#FFB547`, optional violet `#7A4DFF` |
| Type | Clean geometric sans, 600 weight, 80–110 px white headline, max 5 words, subtle soft shadow |
| UI | Real product dashboard on a white rounded card (radius 16–20 px), large soft shadow |
| Logo | Gradient app tile plus wordmark on a white rounded square or circle |

## Motion

- Blobs drift slowly and continuously (one loop per 6–10 s), never pausing; they are the only always-moving layer.
- Headline arrives word by word: fade up 24 px with blur clearing, 350 ms each, 120 ms apart.
- Logo tile grows from a dot into a rounded square or circle in 500 ms, then shrinks away.
- Dashboard enters as a 3D tilted card (rotateY 30–40°) that turns flat over 900 ms with a soft settle.
- One cursor click (150 ms press) closes the film.

## Inputs

Required: product name, logo, a headline of 2–5 words, one real dashboard screenshot. Optional: brand gradient colours, one metric shown in the UI (taken from the product, not invented).

## Avoid

Fast blob motion, more than three blob colours, invented metrics in the UI, text over the brightest blob without contrast, generic stock UI.

## Review

Headline contrast holds over every blob position; the dashboard is legible when flat; motion never stops completely before the last 1 s.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
