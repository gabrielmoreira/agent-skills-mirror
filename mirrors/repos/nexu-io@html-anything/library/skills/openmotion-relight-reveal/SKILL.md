---
name: openmotion-relight-reveal
description: >-
  OpenMotion — Reveal a product in a dark scene with sweeping light beams and a final full relight, with short lines of type between passes. Use for premium hardware, security and night-mode product promos.
---

# OpenMotion · Relight Reveal

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** premium hardware, audio, security and "see what was hidden" product promos of 6–15 s.

## Look

| Element | Starting value |
| --- | --- |
| Background | Near black `#05080D` with a faint cool vignette |
| Light | One soft beam in warm amber `#FFB547` or the brand colour, 120–220 px wide with a heavy blur; a hot white core at 60% |
| Product | Product still or cutout, mostly in shadow; only the area under the beam is lit, plus a thin rim light |
| Type | Condensed bold sans (e.g. Barlow Condensed 700) in off-white `#EEF4F8`, 2–6 words per line |
| Relight | One moment where the whole frame floods with the beam colour and the product is fully lit |

## Motion

- Open on darkness with the beam already moving; it crosses the product in 1.2–1.8 s and lights only what it touches.
- A second pass comes from the opposite side, 0.3 s after a line of type fades up.
- Build to the relight: two beams cross, then the frame floods in 250–400 ms and holds 1–1.5 s.
- Drop back to dark for the logo lockup with a slow 3 s shimmer across the mark.

## Inputs

Required: product image (cutout preferred) or a brief, logo, 2–3 copy lines in the user's words. Optional: brand colour for the beam. When there is no product image, generate one still through `openmotion_media_use` → `openmotion_assets_use` on a plain dark background, get the test image approved before any batch generation, and keep the product shape exact.

## Avoid

Lighting the whole product before the relight, more than one beam colour, strobing faster than three flashes per second, text sitting on the beam's hot core.

## Review

Product shape and logo are unaltered; every line of type is readable against both dark and flooded frames; flashes stay within photosensitivity limits.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
