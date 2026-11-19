---
name: openmotion-paper-stop-motion
description: >-
  OpenMotion — Explain how something works with flat cut-paper pieces, sticky notes and red marker notes, moved frame by frame. Use for science, engineering and how-it-works explainers.
---

# OpenMotion · Paper Stop Motion

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** how-it-works topics (flight, weather, machines) explained in one or two scenes.

## Look

| Element | Starting value |
| --- | --- |
| Cut-outs | Flat paper shapes with a 6 px white border and a hard offset shadow `5px 7px` at 25% navy |
| Palette | Sky paper `#7EC3E6`, cream clouds `#F4EBD8`, red `#E8503A`, teal `#2E8FA3`, grass `#7DB65B` |
| Notes | Yellow `#FFE77A` and mint `#9FE0C8` sticky notes with tape, handwritten font (Caveat); red marker text `#D7322B` (Permanent Marker) |
| Labels | A torn cream title strip top left; a dark readout tag top right for one measured value |

## Motion

- Move every piece on twos (12 poses per second) with a 1–2 px jitter so it feels shot by hand.
- Show the mechanism with marker strokes drawn in 600–900 ms (arrows, squiggles), then let the object act.
- Move the world, not the camera: background pieces slide past at different speeds while the hero stays near centre.
- Slap notes on with a 400 ms overshoot; write marker text left to right in about 900 ms.

## Inputs

Required: the topic and the 2–3 steps of the explanation, any measured values to show. Optional: narration, music, reference photos. Generated pieces go through `openmotion_media_use` then `openmotion_assets_use`; one test paper still or clip is approved before batch generation. Label generated people as generated. Most pieces can be drawn in code instead.

## Avoid

Smooth tweens, gradients inside pieces, values not in the brief, marker text that crosses an arrow or a note.

## Review

Readout values come from the brief; notes and marker text never overlap; the hero stays fully in frame while the world moves; each step is on screen while it is narrated.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
