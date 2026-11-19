---
name: openmotion-electric-impact-type
description: >-
  OpenMotion — Add electric big-number graphics to a presenter video: deep navy backdrop, giant condensed figures that glow white then red, growth bars and one punchline card. Use for startup stories, growth recaps and strong opinions recorded by the creator.
---

# OpenMotion · Electric Impact Type

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

Use the creator's own recording and measured speech timing. Do not place graphics over someone else's speech, and keep the face and mouth clear.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** founder stories and growth recaps built around a few hard numbers.

## Look

| Element | Starting value |
| --- | --- |
| Backdrop | Deep navy gradient `#0F1C2E` → `#1E3350`, soft vignette |
| Figures | Heavy condensed sans in caps, 300–420 px tall beside the presenter; tabular digits |
| Accent | Signal red `#E8262F` with a soft outer glow; steel blue `#3D6FD8` for earlier, smaller values |
| Labels | Small spaced monospace caps, `#C9D3E0`, one hairline rule |
| Layout | Number beside the face, never over it; full-screen beats for bars and the punchline |

## Motion

- A figure punches in at 108% and settles to 100% in 250 ms, white first, then shifts to red over 300 ms when it is the headline.
- Growth bars extend left to right one row at a time (500–700 ms each); only the last, biggest row turns red and glows.
- Punchline card: kicker label appears, then the key word slams in, then the rest of the line in a lighter weight; the last word is red.
- One short glow flicker on impact, never a strobe.

## Inputs

Required: the presenter's recording, measured speech timing, every figure with its unit and source, the one-line takeaway. Optional: year or period labels for the bars.

## Avoid

More than one red element per screen, glow on body text, numbers rounded beyond what was said, unlabelled bars.

## Review

Each figure lands on its spoken word (±3 frames) and matches the source; red is used once per screen; text clears the face; the punchline reads in under two seconds.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
