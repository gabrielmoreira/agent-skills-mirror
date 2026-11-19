---
name: openmotion-echo-stack-type
description: >-
  OpenMotion — Stack one word many times in solid and outline rows that echo, offset and collapse to a beat, then resolve to a calm logo end card. Use for punchy product promos, manifestos and feature teasers.
---

# OpenMotion · Echo Stack Type

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** short product promos and teasers with one strong word per beat: the problem word, the verb that fixes it, the brand.

## Look

| Element | Starting value |
| --- | --- |
| Background | Ink navy `#14172A` for tension beats, warm paper `#EFE8DA` for resolution beats |
| Type | One ultra-condensed heavy sans in caps; the same word repeated 4–7 rows, alternating solid and 2 px outline |
| Accent | A single orange `#F2602B` mark per beat: a brush cross, a stamp or one solid row |
| Layout | Rows fill the full frame height; words may bleed past the edges on purpose, the hero row never does |

## Motion

- Rows stamp in top to bottom on the beat, 60–90 ms apart, each with a 4–8% scale settle.
- Echo rows trail the hero row with a 2–6 frame delay and a small x-offset, so the word visibly reverberates.
- On the next beat the stack collapses to one row (250 ms) and the new word bursts from it.
- Allow one rotation or skew moment per film (≤12°) for the turning point.
- End: everything clears to paper and the logo plus one-line tagline fade up over 400 ms and hold 1.5 s.

## Inputs

Required: 4–6 single words that tell the story, brand name, tagline, music tempo or a track. Optional: Brandkit colours and font.

## Avoid

Sentences in stacks, more than one accent colour, echoes on the logo card, easing that bounces, beats faster than 4 per second.

## Review

Each word readable on its first frame of hold; stacks land on beats (±2 frames); hero row never cropped; end card holds still and clean.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
