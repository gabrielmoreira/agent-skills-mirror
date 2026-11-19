---
name: openmotion-in-hand-product
description: >-
  OpenMotion — Make a close-up in-hand product clip: one hand presents the item against a clean colour backdrop, it turns gently and short benefit tags pop beside it. Use for skincare, gadgets and small products in social posts.
---

# OpenMotion · In-Hand Product

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** small products that fit in one hand, in recommendation and launch posts.

## Look

| Element | Starting value |
| --- | --- |
| Backdrop | One saturated colour with a soft radial light, e.g. electric blue `#2F6BFF` to `#1C45C9`; or a colour taken from the packaging |
| Hand | Relaxed open palm or light pinch from the lower edge; neutral nails |
| Product | Centre of frame, filling 45–60% of the height, crisp edges, one soft highlight |
| Tags | White rounded pills, `#FFFFFF` with `#14213D` text, plain sans 600, 2–4 words each |
| Name | Bottom or top line, bold sans, high contrast to the backdrop |

## Motion

- The hand rises into frame from below in 500–700 ms and settles with a tiny overshoot.
- The product tilts ±6° over 3–4 s, as if the hand is showing it off; no full spins.
- Tags pop in one by one beside the product, 250 ms each, 400–600 ms apart.
- End on the name and one call to action held 1.5 s.

## Inputs

Required: a clear photo of the real product, product name, 2–4 true benefit lines. Optional: brand colour, price, call to action.

The hand shot is generated through `openmotion_media_use` → `openmotion_assets_use` with the user's product photo as reference. Approve one test image or clip before generating more. Generated hands and people are labelled as generated in the caption.

## Avoid

Warped fingers, the product changing shape or text between frames, more than four tags, claims the user did not supply.

## Review

Packaging text matches the real product; finger count and grip look natural in every frame; tags never cover the label; the hold on the name is readable.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
