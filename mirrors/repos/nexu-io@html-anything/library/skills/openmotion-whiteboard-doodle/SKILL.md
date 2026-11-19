---
name: openmotion-whiteboard-doodle
description: >-
  OpenMotion — Make a narrated whiteboard-doodle explainer: simple line drawings drawn in sync with the voice and a camera that pans along one long board. Use for lessons and step-by-step processes.
---

# OpenMotion · Whiteboard Doodle Explainer

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** lessons, step-by-step processes and concept explainers narrated without a presenter.

## Look

| Element | Starting value |
| --- | --- |
| Board | Clean white, no frame |
| Drawings | Simple black line doodles (SVG paths, 3–4 px stroke), one flat accent colour for the focus object |
| Text | Handwritten-style labels, five words or fewer |
| Layout | One idea per board; boards connect left to right like a long whiteboard |

## Motion

- Draw each doodle along its path in sync with narration (0.6–1.5 s per object), labels written after the object.
- Pan the camera to the next empty area of the board instead of cutting; the board history stays visible.
- Use the accent fill only when the narration names the key object.
- Finish with a pull-back showing the whole board as the summary.

## Inputs

Required: topic or script, target duration. Optional: voice, brand accent colour. Approve the first board and a voice sample before producing the rest.

## Avoid

Detailed illustrations, more than one accent colour, drawing that starts before the narration mentions it, a hand prop that covers the drawing.

## Review

Each drawing matches its sentence; pans never lose the reader; the final pull-back is legible; total text per board stays at or under five words.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
