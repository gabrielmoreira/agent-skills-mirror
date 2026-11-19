---
name: openmotion-pixel-art-explainer
description: >-
  OpenMotion — Explain a topic as a retro pixel-art game scene with a character, a dialogue box and a facts counter. Use for gaming, retro and science topics aimed at a young or playful audience.
---

# OpenMotion · Pixel Art Explainer

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** game, retro-tech and simple science topics told as a tiny side-scrolling level.

## Look

| Element | Starting value |
| --- | --- |
| Canvas | Draw at 160×90 logical pixels and scale ×8 with nearest-neighbour; no anti-aliased edges |
| Palette | 16 colours or fewer: night sky `#1B1F3B` → `#7C63A6`, sea `#2E6FB0` / `#4FA3D9`, sand `#E8C27A`, hero red `#D64545`, coin gold `#FFD447` |
| Type | A pixel font (Press Start 2P or similar) for HUD and dialogue, cream `#FFF6D8` on `#14162B` boxes with a 6 px cream border |
| Layout | HUD chips in the top corners, the scene in the middle, a dialogue box with a speaker tag along the bottom |

## Motion

- Step all motion at 12 frames per second; sprites use 2-frame walk cycles.
- Type dialogue at about 25 characters per second with a blinking caret; hold the full line 1 s.
- Show the idea as an event in the level (water rises, a door opens) over 3–4 s, not as a text slide.
- Reward each fact with a 600 ms pickup: sprite hop, star in the HUD, `+1 FACT` pop that fades in 400 ms.

## Inputs

Required: the script or topic, 2–4 facts to explain, a name for the hero. Optional: a character sheet if the user already has one, sound effects, chiptune music. Draw sprites and tiles in code by default; generated backgrounds are optional and go through `openmotion_media_use` then `openmotion_assets_use` with one approved test frame first.

## Avoid

Smooth tweens or blur on sprites, real game characters or logos, facts the brief does not supply.

## Review

No blurred edges at full size; each line is readable before it changes; the hero never floats; the counter matches the facts told.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
