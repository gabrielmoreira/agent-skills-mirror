---
name: openmotion-split-slot-type
description: >-
  OpenMotion — Cut words into slices that slide apart and reassemble, and spin a slot-machine column to swap one benefit word at a time. Use for product promos that rotate through features, audiences or use cases.
---

# OpenMotion · Split Slot Type

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** promos that keep one fixed phrase and swap the last word ("Back up your photos / notes / code"), or a headline that breaks to reveal the next.

## Look

| Element | Starting value |
| --- | --- |
| Background | Deep night `#0A1018`, flat, no texture |
| Type | Rounded geometric heavy sans; white `#F2F5F8` for the fixed phrase, mint `#2FD6A3` for the word that lands |
| Slot window | Fixed word baseline; neighbours above and below dimmed to 35% and clipped by a soft mask |
| Layout | One line centred, or left-aligned phrase plus slot column; end card logo with a one-line tagline |

## Motion

- Split: the word is cut into 3–5 horizontal slices that shoot apart sideways with motion blur (300–400 ms) and lock back into the next word.
- Slot: the column spins with accelerating then decelerating easing (600–900 ms), overshoots 4–6 px and settles; the landed word turns mint.
- Hold each landed word 700–1000 ms before the next spin.
- Optional scatter: letters fly out as loose glyphs and regroup into the logo (≤1 s).

## Inputs

Required: the fixed phrase, 3–6 swap words of similar length, brand name and tagline. Optional: Brandkit colours, music tempo for spin timing.

## Avoid

Swap words that differ wildly in length, spins with no hold, more than one accent colour, slicing the logo.

## Review

Landed word sits exactly on the baseline; every swap word readable for at least 0.7 s; slices never leave gaps in the final word; mask hides neighbours cleanly.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
