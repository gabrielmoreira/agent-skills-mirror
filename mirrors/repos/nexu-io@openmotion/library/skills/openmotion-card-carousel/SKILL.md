---
name: openmotion-card-carousel
description: >-
  OpenMotion — Slide a row of bright benefit cards sideways like a carousel, each card one colour, one icon or object and two or three words. Use for product promos that list features, plans or use cases.
---

# OpenMotion · Card Carousel

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** feature round-ups, plan comparisons and "what you can do" promos with 4–8 short points.

## Look

| Element | Starting value |
| --- | --- |
| Background | Near-black `#0B0D14` stage |
| Cards | Portrait cards 3:4, radius 20 px, solid colours that rotate: tangerine `#F2643A`, violet `#5B4BF0`, mint `#1FA67A`, magenta `#E0459B` |
| Type | White bold sans, 2–4 words per card, set large; a small brand mark in one corner |
| Object | One glossy illustrated object or icon per card, centred, with soft highlight |

## Motion

- The row glides left continuously at a steady speed (one card width per 0.8–1.2 s) with gentle ease at start and end.
- The card crossing centre scales to 1.08 and lifts its shadow; others stay at 0.94.
- Each card's object turns or bobs slightly (≤8°) while centred.
- Words on the centre card stagger in by word, 80 ms apart.
- End: the row slows, the centre card expands to the end card with logo and tagline in 500 ms.

## Inputs

Required: 4–8 benefit phrases, brand name, tagline. Optional: icons or object images; glossy objects are generated through `openmotion_media_use` → `openmotion_assets_use` after one test image is approved. Brandkit colours replace the defaults.

## Avoid

Paragraphs on cards, jittery speed changes, more than four card colours, cards that repeat within one screen width.

## Review

Centre card always fully inside the frame; each card readable while centred; colours alternate without neighbours matching; motion speed steady.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
