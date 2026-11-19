---
name: openmotion-content-cover
description: >-
  OpenMotion — Read a video or article, pull its strongest line, and lay out a set of cover options in bold and safe styles, then pick and finish one. Use for video thumbnails, social covers and article headers.
---

# OpenMotion · Content Cover

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** Video thumbnails, vertical social covers, podcast episode art and article headers made from the content itself.

## Look

| Element | Starting value |
| --- | --- |
| Format | 3:4 vertical or 16:9 thumbnail, as the platform needs; show options side by side, the pick enlarged |
| Bold set | Yellow `#FFD43B` or red `#E8322B` ground, heavy condensed caps 3–5 words, a rotated sticker tag |
| Safe set | Off-white `#F4EFE6` or navy `#1C2340`, a serif or clean sans headline, one quiet accent |
| Person | A real frame of the creator, cut out, face large and unobstructed |
| Proof | Source panel showing the transcript line the title came from, highlighted in `#FFE24A` |

## Motion

- Highlight the chosen transcript line in 0.6 s and pop 2–3 keywords as chips.
- Generate four options, two bold and two safe, each popping in 350 ms apart.
- Mark the pick with a check, fade the rest in 0.5 s, then scale the pick to fill the frame in 0.9 s.
- Finish on the chosen cover held for 2 s with a label of its format.

## Inputs

Required: the video transcript or article text, at least one clear frame of the creator if they appear. Optional: channel style or past covers, platform and ratio, words that must or must not appear.

If no usable frame exists, a cover portrait may be generated through `openmotion_media_use` → `openmotion_assets_use` only with the user's consent, after one approved test image, and it is labelled as generated.

## Avoid

Titles the content does not deliver on, expressions the creator never made, more than six words, small text.

## Review

Every headline is traceable to a line in the source; the face and headline are readable at 160 px wide; bold and safe sets look clearly different; the final cover is exported at the platform's size.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
