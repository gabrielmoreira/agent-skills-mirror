---
name: openmotion-paper-map-journey
description: >-
  OpenMotion — Make a paper-cut map video: a red route drawn between stops with pop-up landmarks and one fact per stop. Use for travel itineraries, destination introductions and expansion stories.
---

# OpenMotion · Paper Map Journey

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** travel explainers, itineraries, destination introductions and expansion stories (offices, stores, launches).

## Look

| Element | Starting value |
| --- | --- |
| Map | Cream paper base `#F3EEDF`, mint paper terrain `#BFE3D0`, water in pale blue; layered cut-paper edges with soft shadows |
| Route | One red line `#D7263D`, dashed while travelling, solid once completed |
| Stops | Paper-cut landmark or photo cutout per stop, with a small label tag |
| Type | Clean sans for place names; a bigger number for day or stop order |

## Motion

- Open on the whole country or region, then zoom to the first stop (1–1.5 s ease-in-out).
- Draw the route between stops along an SVG path; the camera follows the line head.
- At each stop, pop the landmark up from the map like a pop-up book (300 ms), hold 2–4 s with one fact.
- Close by pulling back to show the full completed route.

## Inputs

Required: place list in order, one fact per stop, aspect ratio. Optional: photos, narration. Map outlines must come from an open dataset with its licence recorded; do not trace copyrighted maps.

## Avoid

Wrong geography or invented borders, more than five stops in 30 seconds, labels that overlap the route.

## Review

Stop order and positions are geographically correct; each label is readable; the route never jumps; the map data source and licence are recorded.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
