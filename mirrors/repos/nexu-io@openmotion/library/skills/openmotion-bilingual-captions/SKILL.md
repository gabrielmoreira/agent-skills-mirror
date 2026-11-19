---
name: openmotion-bilingual-captions
description: >-
  OpenMotion — Add two-line bilingual captions to a talking video: the spoken line on top, its translation underneath, timed and styled as one readable pair. Use for interviews, tutorials and talks published to two language audiences.
---

# OpenMotion · Bilingual Captions

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

Use the creator's own recording and measured speech timing. Do not place graphics over someone else's speech, and keep the face and mouth clear.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** interviews, tutorials, lessons and creator talks that need the original words and a translation on screen together.

## Look

| Element | Starting value |
| --- | --- |
| Caption box | Dark panel `rgba(14,18,16,.66)`, 16 px radius, centred in the bottom 15% safe area |
| Original line | Bold sans, white `#FFFFFF`, the word being spoken in `#FFD45C` |
| Translation | Same width, about 70% of the original size, light italic serif or the same sans in `#D9E6DC` |
| Layout | One line per language, about 42 characters each; use a font that covers both scripts |

## Motion

- The pair cuts in on the first word of the phrase; no fade longer than 150 ms.
- Word highlight on the original line follows the measured word timing, not an even spread.
- The translation fades up 120–250 ms after the original, so the eye reads top line first.
- Swap pairs on phrase boundaries with a 2–3 frame gap; clear the caption during silences over 1 s.

## Inputs

Required: the creator's recording, a word-timed transcript in the spoken language, and the target language (ask; do not guess it from the chat language). Optional: an approved translation or glossary, whether both languages share one style or get separate styles, Brandkit fonts.

## Avoid

Translating names or terms the glossary keeps; three-line captions; a translation that outlives its phrase; captions over the mouth.

## Review

Every pair is readable twice at 1× speed; the translation says what was said, not more; no missing glyphs; highlight lands on each spoken word (±3 frames).

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
