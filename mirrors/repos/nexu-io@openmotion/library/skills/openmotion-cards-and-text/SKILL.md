---
name: openmotion-cards-and-text
description: >-
  OpenMotion — Make a two-colour product promo that alternates bold short lines with stacks of duotone photo cards: cards fan in, gather, frame a big number, then line up under the closing line. Use for app launches, offers and feature lists that have a few strong images.
---

# OpenMotion · Cards And Text

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** launches, offers and feature lists backed by 3–5 strong images.

## Look

| Element | Starting value |
| --- | --- |
| Palette | Two tones only: deep maroon `#4B1430` and blush `#F4E4E1`, plus mid tone `#B07A89`; one orange accent `#FF8A3D` for numbers and check badges |
| Cards | Portrait cards 3:4, 24 px radius, deep soft shadow; every image converted to the two-tone duotone; light halftone or stripe texture allowed |
| Type | One tight grotesk, 800 weight, 78–110 px, letter spacing -0.04 em; numbers 200 px in the accent colour |
| Layout | Text on one side, cards on the other; never text on top of a card |
| Background | Maroon to start, blush after a circular wipe; text colour flips with it |

## Motion

- Cards slide in tilted ±10–16° (600 ms, 150 ms stagger); words rise in 120–140 ms apart.
- Change scene with a circular wipe (700 ms) while the cards regroup in the same move.
- For a number, push cards to the corners and count up over ~1 s, ending with one pulse.
- Close with the cards in a single row under the final line, slight alternating tilt; hold at least 1.5 s.

## Inputs

Required: product name, three or four short lines, any real number to feature, and 3–5 images: the user's own photos or product screenshots, or images generated through `openmotion_media_use` → `openmotion_assets_use` after one test image is approved. Label any generated people as generated. Optional: logo, brand colours to replace the two tones.

## Avoid

Full-colour photos next to duotone ones, more than four cards on screen, lines longer than five words, numbers the brief does not supply, text placed over card images.

## Review

Cards read as one two-tone set; lines hold long enough to read twice; the number matches the source; no card clips text.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
