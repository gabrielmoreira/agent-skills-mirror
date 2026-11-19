---
name: openmotion-ring-mask-reveal
description: >-
  OpenMotion — Make a flat geometric promo where circles, pills and bars act as masks that open, overlap and carry words between scenes. Use for modular or design-led SaaS products that want a clean, playful brand film.
---

# OpenMotion · Ring Mask Reveal

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** design tools, builders, modular products and brand intros with a three-word idea (for example "plan, build, ship").

## Look

| Element | Starting value |
| --- | --- |
| Palette | Ink `#24183F`, orange `#FF8A3D`, sky `#7CC4FF`, paper `#EEF0F6`; flat fills only |
| Shapes | Circles, rounded pills and full-height bars; overlaps change colour where two shapes cross |
| Type | One tight sans, 600–700 weight; words sit inside a shape and are clipped by it |
| Layout | Shapes fill most of the frame; a small logo stays top right on every scene |

## Motion

- Circles expand from points to full size in 500–700 ms with a soft overshoot, revealing the word inside.
- Three circles slide together and morph into three vertical bars (700 ms), each carrying one word.
- A bar widens to fill the frame and becomes the next background; that is the scene cut, no fades.
- Text is masked, never faded: it slides through the shape edge and is clipped by it (300–400 ms).
- End on one circle closing onto the logo, held 1.5 s.

## Inputs

Required: product name, logo, one headline and three short words or phrases that describe what it does. Optional: brand colours (keep to four), a one-line closing claim.

## Avoid

Gradients, drop shadows, more than four colours, words split across two shapes for longer than a transition, linear easing.

## Review

Each word is fully inside its shape when it holds; every scene cut comes from a shape growing, not a crossfade; text never touches the frame edge; logo is legible at the end.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
