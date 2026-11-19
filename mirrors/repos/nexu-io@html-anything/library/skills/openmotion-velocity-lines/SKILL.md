---
name: openmotion-velocity-lines
description: >-
  OpenMotion — Make a fast promo where blue speed streaks, motion-blurred words and pulsing rings sell performance. Use for fitness, sports, delivery and any product whose main claim is speed or power.
---

# OpenMotion · Velocity Lines

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** fitness apps, sports gear, fast delivery, performance software and launch teasers with one strong verb.

## Look

| Element | Starting value |
| --- | --- |
| Palette | Night navy `#0D1220`, electric blue `#3D7BFF`, pale blue `#8EB4FF`, off-white `#EEF1F7` |
| Streaks | Thin horizontal lines, 2–6 px, 120–600 px long, white to blue, fading at the tail |
| Type | Extra-wide or extended heavy sans, 140–200 px, one word per beat; italic only on the speed word |
| Rings | Concentric blue rings from the frame centre behind a key word |
| Icons | Thin 3 px line icons in blue or white inside circles |

## Motion

- Words arrive on the beat: slide in from the right with horizontal motion blur, 180–250 ms, then snap still.
- Streaks rush right to left at varying speeds behind every word change; density peaks for 300 ms, then thins.
- Rings pulse outward from the centre every 500 ms during the main claim.
- Icons draw their outline in 400 ms while a circle draws around them.
- Final card is calm: logo writes on letter by letter over 600 ms with no streaks.

## Inputs

Required: product name, logo, a claim of 3–6 words split into beats, one call to action. Optional: 2–3 icon subjects, a music track with a clear beat (timing follows its beats).

## Avoid

Streaks crossing text, blur left on a word that should be read, more than one word moving at once, rainbow colours.

## Review

Every word is sharp and still for at least 400 ms; cuts land on beats within 2 frames; the end card holds 1.5 s without motion.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
