---
name: openmotion-light-shadow-product
description: >-
  OpenMotion — Stage a product in warm directional light: window-blind and leaf shadows travel across a plinth, the cast shadow answers the light, and the camera slowly pushes in. Use for skincare, fragrance, home and design product ads.
---

# OpenMotion · Light Shadow Product

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** skincare, fragrance, candles, ceramics, homeware and any premium product that should feel calm and tactile.

## Look

| Element | Starting value |
| --- | --- |
| Set | Warm plaster wall `#E6D3B6`, a travertine plinth, a low floor plane `#C9AA80` |
| Light | One warm sun patch `#FFE2AA` from the side; blind stripes at 115° with 20% multiply and 9 px blur |
| Shadow | A soft leaf or branch silhouette in one corner; the product's own cast shadow on the plinth |
| Product | The real product cut-out, filling 60–70% of the frame height, with a narrow glass highlight |
| Type | A serif headline (60–70 px) and a small sans line on the empty side |

## Motion

- The light travels slowly across the whole shot: stripes move 200–260 px over 8 s, the sun patch follows.
- The cast shadow skews and shortens with the light so the scene stays physically believable.
- Leaves sway on two slow sine waves (about 2° and 0.6°).
- Camera pushes from 100% to 112% with a small lateral drift; nothing crops the product's top.
- Copy fades up in the first 2 s and stays; one word may warm in colour late in the shot.

## Inputs

Required: a clean cut-out photo of the product, product name and the exact copy. Optional: scent or ingredient notes, brand colours, a matching background plate.

The background plate or shadow layers can be generated through `openmotion_media_use` → `openmotion_assets_use`; approve one test still before generating more. Never regenerate the product itself; use the user's photo.

## Avoid

Harsh black shadows, coloured gels, several light directions, props that crowd the product, an altered label or bottle shape, claims about ingredients that were not given.

## Review

The product and its label match the supplied photo; shadows move in one consistent direction; the product top is never cropped; copy stays readable over the moving shadows.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
