---
name: openmotion-orange-unfiltered
description: >-
  OpenMotion — Stamp grainy orange keywords straight onto a presenter video: heavy uppercase words typed in letter by letter around the face, with no boxes or panels. Use for fitness tips, hot takes and outdoor vlogs recorded by the creator.
---

# OpenMotion · Orange Unfiltered

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

Use the creator's own recording and measured speech timing. Do not place graphics over someone else's speech, and keep the face and mouth clear.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** fitness and sport tips, quick opinions and walk-and-talk vlogs where the keyword is the whole graphic.

## Look

| Element | Starting value |
| --- | --- |
| Words | Heavy geometric sans, uppercase, tight tracking; 90–160 px on a 1080 p frame |
| Colour | Orange `#FF6A13` with fine film grain inside the letters; no outline, a very soft shadow for contrast |
| Placement | Corners and the sky or ground around the presenter; never across eyes or mouth |
| Everything else | No boxes, bars, icons or panels. One or two words on screen at a time |

## Motion

- Type each word letter by letter, 35–50 ms per letter, each letter popping from 115% to 100%.
- Stack a second word under the first only when it finishes the phrase; it starts after the first word completes.
- Cut words off hard on the next beat; no fade-outs longer than 100 ms.
- Contrast pairs ("slow" / "fast") use opposite corners so the eye travels.

## Inputs

Required: the presenter's recording, measured speech timing, the keywords exactly as spoken. Optional: one number worth stamping (a pace, a percentage, a count).

## Avoid

Full sentences, words that were not said, more than two words at once, other colours, text crossing the face, slow fades.

## Review

Every word matches the speech and appears on its spoken syllable (±2 frames); grain is visible but letters stay sharp; words clear the face; nothing stays on screen after its beat.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
