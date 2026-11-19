---
name: openmotion-shutter-bands
description: >-
  OpenMotion — Make a bold typographic promo where horizontal colour bands slide across like a shutter to switch between scenes of big condensed words. Use for brand launches, service promos and short social teasers.
---

# OpenMotion · Shutter Bands

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** punchy promos built from a few strong words, a promise and a logo.

## Look

| Element | Starting value |
| --- | --- |
| Palette | Three flat colours: navy `#0E1A2B`, ivory `#F2EEE6`, one loud accent such as orange `#FF5A1F` |
| Type | A tall condensed display face in caps for single words (180–220 px); a heavy grotesk for sentences (130–150 px) |
| Bands | Six equal horizontal strips covering the frame, each a single flat colour |
| Rows | Scenes are built from three full-width rows, alternating dark and light, each holding one word or one short phrase |
| End card | Logo and one plain tagline on navy |

## Motion

- Opening rows carry marquee words that drift sideways at a steady pace, alternate rows moving in opposite directions.
- Shutter transition: bands slide in from alternating sides in 300–350 ms with 30–40 ms stagger, the scene swaps underneath, then the bands exit to the opposite side.
- Inside a scene, each row slides in on its own (450 ms, expo out) so the sentence builds row by row.
- Hold every scene 1.2–1.8 s; use a slow 3–4% scale push on held text so it never freezes.

## Inputs

Required: brand name, 3–6 short words or phrases from the user's own messaging, logo, tagline. Optional: one real proof point (e.g. an on-time rate) with its source, brand colours.

## Avoid

More than three colours, words over eight letters in condensed rows, invented stats, more than four shutters in 15 s.

## Review

Every held word is fully on screen; bands cover the frame completely before each swap; one accent element per scene.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
