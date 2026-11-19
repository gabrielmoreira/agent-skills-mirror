---
name: openmotion-caption-styling
description: >-
  OpenMotion — Restyle the word-timed captions on a talking video and let the user compare a few looks, such as clean sentence captions, bold pop words or a marker box on key words. Use when a talking video needs captions or a new caption look.
---

# OpenMotion · Caption Styling

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

Use the creator's own recording and measured speech timing. Do not place graphics over someone else's speech, and keep the face and mouth clear.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** talking-head clips, podcasts and tutorials that need readable or more energetic captions.

## Look

| Element | Starting value |
| --- | --- |
| Clean | Sentence case, Inter 600 at about 40 px, white with a soft shadow; spoken words full, upcoming ones at 30% |
| Pop | Uppercase condensed (e.g. Anton) at 70–80 px, black outline, two or three words at a time, active word `#FFE14D` |
| Marker | Poppins 800 at about 56 px, two words at a time, key word on a `#FF6B4A` box |
| Position | Lower third over the chest, clear of face, mouth and platform UI |
| Picker | A small panel with one live sample per style so the user can choose |

## Motion

- Time every word from the transcript; a word appears on its first frame of speech.
- Pop: the active word scales from 70% to 100% with a short overshoot (about 180 ms).
- Marker: the box wipes left to right behind the key word in about 200 ms.
- Change chunks on phrase boundaries, never mid-phrase.

## Inputs

Required: the creator's recording and a word-timed transcript. Optional: brand fonts and colours, a list of key words to emphasise, the target platform.

## Avoid

Captions that paraphrase the speech, more than one emphasis colour, captions over the face, chunks longer than the line width.

## Review

Captions match the audio word for word; timing is within ±2 frames; nothing covers the face; the chosen style stays consistent across the video.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
