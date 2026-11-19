---
name: openmotion-splash-float-product
description: >-
  OpenMotion — Burst a product into a splash with its ingredients — fruit slices, ice, leaves, droplets — that fly out and then hang weightless in layered depth around it. Use for drinks, snacks, beauty and fresh food ads.
---

# OpenMotion · Splash Float Product

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** drinks, snacks, sauces, skincare and fresh food where the ingredients are the story.

## Look

| Element | Starting value |
| --- | --- |
| Background | A soft radial gradient in one fresh hue, such as mint `#E4F7EC` to `#6FBFA6` |
| Product | The real pack, tilted 6–10°, centred or on the right half, 65% of frame height |
| Splash | Liquid tongues in the product's own colour radiating behind the pack, semi-opaque with white highlights |
| Floaters | Three depth layers: far small and blurred, mid behind the pack, near large and sharp in front |
| Type | A heavy sans headline (80–100 px) on the empty side and one short pill tag |

## Motion

- The pack rises in 0.7 s with a light overshoot; the splash erupts behind it 0.5 s later (0.7 s, strong ease out).
- Ingredients burst out from the pack's top with exponential slowdown: most travel in 0.6 s, then hover.
- While hovering, everything bobs on slow sines (8–10 px) and turns gently; the pack sways ±6°.
- The camera pushes in 8% across the shot; copy builds line by line after the burst.

## Inputs

Required: a cut-out image of the product, the ingredient list to show, the exact headline. Optional: flavour colour, size or volume line, brand colours.

Splash and ingredient layers are generated through `openmotion_media_use` → `openmotion_assets_use` as separate transparent stills; approve one test image first, then generate the rest with the same light. Use the user's photo for the product itself.

## Avoid

Ingredients the product does not contain, splash colours that contradict the flavour, floaters covering the logo, chaotic motion with no hover phase, more than about 25 floating pieces.

## Review

Every ingredient shown is in the product; the pack and logo are never covered; the hover phase is calm and readable; no floater is cut awkwardly at the frame edge in the final second.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
