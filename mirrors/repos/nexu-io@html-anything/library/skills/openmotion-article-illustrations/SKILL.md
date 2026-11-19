---
name: openmotion-article-illustrations
description: >-
  OpenMotion — Turn the key ideas of an article into hand-drawn line-illustration cards with a small mascot and handwritten captions. Use for blog posts, newsletters and method write-ups that need a short visual summary.
---

# OpenMotion · Article Illustrations

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** blog posts, newsletters and method articles where 2–5 ideas need one picture each.

## Look

| Element | Starting value |
| --- | --- |
| Card | White 16:9 card on a warm grey desk `#E9E6DF`, 14 px radius, soft shadow; one idea per card |
| Line | Black `#1E1E1E` 5 px round strokes with a slight hand-drawn wobble; few fills |
| Accent | At most two accents per card: orange-red `#E4572E`, blue `#2F6DB5`, light blue fill `#CFE3F7` |
| Mascot | A round outlined character with dot eyes and an orange scarf, doing the idea, not watching it |
| Type | Handwritten captions (Caveat) 42–54 px; a small spaced sans header with the article title and figure count |

## Motion

- Draw the main line in 0.8–1.3 s, then let the mascot act it out (climb, push, carry) over 2–3 s.
- Write captions left to right in 0.8–0.9 s; the second caption arrives once the action makes the point.
- Slide cards like a carousel: out left and in from the right over 500 ms, slightly rotated.
- Small payoffs (a flag, a growing shape) pop with a 400 ms overshoot.

## Inputs

Required: the article text, the 2–5 ideas to illustrate, the article title. Optional: brand colours, a mascot the user owns. Everything is drawn in code; no generated media is required.

## Avoid

Infographic clutter, stock icons, more than one sentence of caption, numbers not in the article (or computed and stated plainly, like 1.01^365 ≈ 38), copying another illustrator's character.

## Review

Each card states one idea from the article; captions match its wording or meaning; the mascot is part of the action; nothing touches the card edge during the slide.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
