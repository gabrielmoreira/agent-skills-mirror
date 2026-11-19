---
name: openmotion-liquid-blob
description: >-
  OpenMotion — Make a soft product promo where one rounded colour blob splits, stretches, floods the screen and melts into the next scene and finally the app icon. Use for calm consumer apps, planners, wellness and productivity tools.
---

# OpenMotion · Liquid Blob

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** friendly app promos where the transitions carry the mood: planners, wellness, finance.

## Look

| Element | Starting value |
| --- | --- |
| Background | Pale blue-white `#EEF3F9` |
| Blob | One saturated colour, e.g. `#2F6BFF`; shapes are circles and squircles merged with a goo filter (blur ≈ 22 px, alpha threshold) |
| End icon | The final squircle takes a two-stop gradient, blue to mint `#2BD4A4` |
| Type | Rounded geometric sans, extra bold, 84–110 px; white on the blob, deep navy `#0D1B33` on the background |
| Layout | Blob centred and large (300–480 px); short lines centred over or under it |

## Motion

- Every scene change is a shape change: the squircle shrinks to a circle, splits into three droplets that stretch apart (900 ms, power3 in-out), then rushes back and merges.
- The merged blob grows to flood the frame (≈ 700 ms) and becomes the background for the next line.
- A secondary white droplet can pull a smaller drop away to illustrate one idea, such as no clashes.
- Finish by draining the colour back into one gradient squircle that springs to size with the wordmark (600 ms, back-out), then a slow squash-and-stretch breath.

## Inputs

Required: app name, 2–4 short lines from the user's messaging, tagline. Optional: app icon to match in the final shape, brand colour, one product screenshot to show on the flooded background.

## Avoid

Several blob colours at once, text on top of a moving blob edge, hard cuts between scenes, sharp corners, sound-effect-heavy bounces.

## Review

Text never sits across a blob edge; merges read as liquid without flicker; the wordmark fits inside the final shape.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
