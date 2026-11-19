---
name: openmotion-adaptive-layout
description: >-
  OpenMotion — Make a product promo where one set of selling points re-flows between desktop, tablet and phone layouts on a dark grid, after a stretched-type opener. Use for design systems, responsive tools, multi-platform apps and any product that promises to fit every screen.
---

# OpenMotion · Adaptive Layout

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** responsive tools, design systems and multi-platform apps.

## Look

| Element | Starting value |
| --- | --- |
| Background | Deep navy `#0D1330` with a faint 40 px blueprint grid in sky blue at 6% opacity |
| Accent | Sky `#5CC8FF` for the lead card and highlights, amber `#FFB547` for icon tiles; everything else white or `#1B2556` |
| Type | One heavy grotesk (800 weight), 120–140 px for the opener, 34–54 px card titles, 19–22 px card lines |
| Frame | A thin rounded outline (2 px sky at 55%) that stands for the device; radius grows as the frame narrows (28 → 44 px) |
| Cards | Three cards with the same title, line and small visual in every layout; the first card is the filled lead card |

## Motion

- Opener: the headline snaps out of a light streak (scaleX 2.4 → 1, scaleY 0.08 → 1, 550 ms, expo-out).
- Layout changes are a single 700 ms power3-in-out move of the frame and all cards together, cards staggered by 50 ms. Never cut between layouts.
- Each layout holds 1.2–1.6 s with a short side label (Desktop / Tablet / Phone) fading in after the move settles.
- Close by collapsing the cards into the logo mark (500 ms), logo and tagline pop in with a small overshoot.

## Inputs

Required: product name, three selling points with one line each, a tagline. Optional: logo, brand colours, real UI crops for the card visuals, supported breakpoints.

## Avoid

Changing the wording between layouts, more than three cards, text that reflows mid-move into overlap, decorative device mockups that hide the cards, invented platform support.

## Review

Same three points, same order, in every layout; no text clips during a move; each layout readable for 1 s+; labels name only supported platforms.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
