---
name: openmotion-sticker-bounce
description: >-
  OpenMotion — Make a playful promo where benefits arrive as die-cut stickers with white borders and offset shadows that bounce, stack and wobble. Use for creator tools, social apps and consumer products with short, upbeat claims.
---

# OpenMotion · Sticker Bounce

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** creator and social apps, consumer launches, feature lists with 3–4 short benefits and upbeat ads for short-form feeds.

## Look

| Element | Starting value |
| --- | --- |
| Background | Flat sky blue `#93D0FF` (or one brand pastel) |
| Stickers | Shapes with a 6–10 px white border, 3 px navy `#121A3A` outline and a hard navy offset shadow (6–10 px down-right) |
| Colours | White, orange `#FF7A1A` and navy only on stickers |
| Type | Rounded heavy sans (800–900 weight), navy, short lowercase lines; the hero word in caps as its own sticker |
| Shapes | Star burst, arrow, blob hand, speech bubble, heart; 2–4 on screen |

## Motion

- Each sticker pops: scale 0 → 112% → 96% → 100% with a slight rotation (±6°), 350–450 ms.
- Stickers arrive in a 120–200 ms stagger, layered so later ones overlap earlier ones.
- Held stickers wobble gently (±2° over 1.2 s) so the frame never feels frozen.
- Benefit lines stack one per beat, each with a little drop-in of 20 px.
- Exit by peeling: a sticker scales to 0 with a quick tilt in 200 ms; end on the logo as one big sticker.

## Inputs

Required: product name, logo, 3–4 benefits of 2–3 words each, a one-line closing claim. Optional: brand pastel and accent, shapes that fit the product (hands, stars, arrows).

## Avoid

Soft blurred shadows, gradients, more than three sticker colours, stickers covering text, bounce on every element at once.

## Review

Every benefit line is readable for 1 s; stickers never cover each other's text; outline and shadow offsets are identical on every sticker; logo sticker holds 1.5 s.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
