---
name: openmotion-corner-frames
description: >-
  OpenMotion — Make a clean tech promo where four corner brackets glide from target to target: headline, product card, key number, logo. Use for developer tools, analytics and other technical SaaS.
---

# OpenMotion · Corner Frames

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** technical promos that point at one thing at a time: a dashboard, a metric, the logo.

## Look

| Element | Starting value |
| --- | --- |
| Background | Deep navy `#0A1220` with a faint 40 px grid at 6% opacity |
| Brackets | Four L-shaped corners, 46 px arms, 4 px stroke, cyan `#5BE0E6`; a small mono label (`TARGET 01`, metric name) rides above the top-left corner |
| Type | Grotesk sans for headlines (700, 90–110 px); mono for labels and small data, tracked +12% |
| Accent | One signal colour, lime `#B8F25C`, used only for live states and the key change |
| Product | Dark UI card `#101C2E` with a 1 px border, chart line in the bracket colour |

## Motion

- Brackets start at the screen corners and slide in to frame the first headline (700 ms, expo in-out), each corner 30 ms after the last.
- Every new beat moves the same four brackets to the next target instead of cutting; the label text swaps halfway through the move.
- Zoom the product card 1.2× toward the key metric while the brackets tighten around it; count the number to its value over ~1 s.
- A soft scan line crosses the frame every few seconds; on the end card the corners flash the accent colour twice.

## Inputs

Required: product name, logo, 1–2 headline lines, one real metric with unit and source, a UI screenshot to rebuild. Optional: brand colours, call to action.

## Avoid

Framing more than one thing at once, metrics without a source, brackets drifting off the target, glow effects everywhere, more than one accent colour.

## Review

Brackets enclose each target with even padding; no text sits under a corner; the key number is legible for at least one second.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
