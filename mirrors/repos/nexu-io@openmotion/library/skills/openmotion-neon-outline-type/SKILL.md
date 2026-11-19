---
name: openmotion-neon-outline-type
description: >-
  OpenMotion — Make a dark kinetic-type promo where outlined words glow, fill letter by letter and sit inside nested light frames. Use for hardware, gaming, audio and performance claims that need a bold short tagline.
---

# OpenMotion · Neon Outline Type

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** hardware teasers, gaming gear, audio products and any promo built on two or three punchy words per beat.

## Look

| Element | Starting value |
| --- | --- |
| Background | Near-black `#0C0A10`, a faint vignette, no texture |
| Outline | 2 px stroke in amber `#FF8A3D` with a soft glow (blur 8–14 px, 60% opacity) |
| Fill | Warm white `#FFF6EC` for filled letters; one optional hot accent `#FF3D7F` for a closing rule |
| Type | Heavy condensed or grotesk caps, 120–180 px, 1–3 words per line, max 3 lines |
| Frames | 2–4 nested rectangles or chevrons in the outline colour, 1.5 px, around the word block |

## Motion

- Each word enters as outline only, drawn with a stroke-dash sweep in 400–600 ms.
- Letters fill left to right with a 40–60 ms stagger, as if switched on; add one flicker (2 frames off) on the first fill.
- Frames scale out from the text block in a 120 ms stagger and settle with a slight overshoot.
- Change beats every 1.5–2 s: frames rotate into chevrons or collapse to a single line that carries the next word in.
- Close on a thin accent line that hands off to the logo.

## Inputs

Required: product name, a tagline split into 2–4 short beats, logo. Optional: one spec number, brand accent colour.

## Avoid

Glow on body copy, more than one accent colour per beat, lines longer than three words, outlines thinner than 1.5 px at 1080p, flicker loops.

## Review

Every beat is readable when fully filled for at least 600 ms; glow never merges letters; frames never cross the text; the logo holds for 1.5 s at the end.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
