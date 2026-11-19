---
name: openmotion-runway-rebel
description: >-
  OpenMotion — Pair bold white uppercase words with thin yellow serif numerals over a presenter video, plus an occasional full-screen yellow card. Use for creator advice, fashion talk and hot takes recorded by the creator.
---

# OpenMotion · Runway Rebel

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

Use the creator's own recording and measured speech timing. Do not place graphics over someone else's speech, and keep the face and mouth clear.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** creator advice, fashion and lifestyle opinions, and short punchy talks with one or two numbers.

## Look

| Element | Starting value |
| --- | --- |
| Words | Extra-bold geometric sans, uppercase, white `#FFFFFF`, stacked in two lines with a staggered indent |
| Numerals | Hairline high-contrast serif in yellow `#F2F21B`, larger than the words and overlapping them |
| Card | Full-screen yellow `#F2F21B` with navy `#10204A` words filled by a slice of the presenter shot |
| Layout | Words in the lower third or beside the face; numerals behind or beside the words |

## Motion

- Words rise 20 px with a short fade (200–250 ms) one line at a time.
- Thin numerals draw or fade in slowly (500–700 ms) after the words, so the weight contrast reads.
- The yellow card cuts in on the strongest line, holds 1–1.5 s, then cuts back on the next sentence.
- Keep the presenter shot steady; a gentle 2% push-in at most.

## Inputs

Required: the presenter's recording, measured speech timing, the key phrases and numbers exactly as spoken. Optional: a darker or bluer grade of the shot for contrast.

## Avoid

Yellow on the bold words, more than one numeral on screen, cards on every line, words over the face, invented counts.

## Review

Words and numbers match the speech; the thin numeral is still readable on a phone; one yellow card per 20–30 s at most; face and mouth stay clear.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
