---
name: openmotion-highlighter-notes
description: >-
  OpenMotion — Add calm highlighter-note graphics to a presenter video: off-white paper cards, charcoal text and one yellow highlighter stroke on the key line. Use for study tips, book notes and knowledge talks recorded by the creator.
---

# OpenMotion · Highlighter Notes

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

Use the creator's own recording and measured speech timing. Do not place graphics over someone else's speech, and keep the face and mouth clear.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** study tips, book notes and calm knowledge talks with one presenter.

## Look

| Element | Starting value |
| --- | --- |
| Paper | Off-white card, `#F4F1EA`, faint paper grain; full-frame insert or a side card beside the presenter |
| Text | Charcoal `#2B2B2B`; one serif for quotes, one plain sans for labels |
| Accent | A single yellow highlighter stroke, `#FFE14D` at 85% opacity, behind the key words only |
| Everything else | No icons, gradients or badges. One accent per screen |

## Motion

- Write the line onto the card with a short fade-up (300–400 ms), then hold it still.
- Draw the highlighter left to right behind the key phrase in 400–600 ms, starting on the spoken word. Slightly uneven stroke ends read as hand-made.
- Cut back to the presenter between notes. A note stays at least as long as it takes to read twice.
- Lower-third captions stay small and separate from the note card.

## Inputs

Required: the presenter's recording, measured speech timing, the 3–6 lines worth noting. Optional: book cover or source title.

## Avoid

Highlighting more than one phrase per card, bouncy easing, music louder than the voice, notes that paraphrase what was not said.

## Review

Each highlight lands on its spoken word (±3 frames); each note is readable at 1× speed; face and mouth are never covered; at most one accent colour on screen.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
