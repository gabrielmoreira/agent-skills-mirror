---
name: openmotion-editorial-webinar
description: >-
  OpenMotion — Build calm paper-textured course slides with typewriter type, staged timelines, comparisons and checklists, plus a round presenter bubble. Use for lessons, webinars and framework explainers.
---

# OpenMotion · Editorial Webinar

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

Use the creator's own recording and measured speech timing. Do not place graphics over someone else's speech, and keep the face and mouth clear.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** online courses, webinars and teaching outlines where one idea is explained per slide.

## Look

| Element | Starting value |
| --- | --- |
| Paper | Warm off-white `#EFEBE3` with faint grain; no gradients, cards or shadows |
| Type | One typewriter face (Courier Prime or similar): titles 76–92 px bold, body 25–34 px, small spaced kickers in `#8A8378` |
| Accent | Brick red `#C2492F` only for the current item, the active node and ticks; ink `#24221F` for lines and text |
| Diagrams | Hairline rules (2 px), hollow circle nodes, outlined boxes; one diagram per slide |
| Presenter | The creator's recording cropped into a 210 px circle, lower right, with a thin ink ring |

## Motion

- Type the title in 1–1.2 s with a red block caret; draw the rule under it in 500 ms.
- Reveal diagram parts in reading order, 300–420 ms apart: line draws, then nodes pop, then labels fade up 14 px.
- Switch slides with a 300 ms fade-up; never overlap two slides.
- Draw checkmarks in 350 ms on the spoken word; the chosen option gets a soft 4 px red halo.

## Inputs

Required: the lesson outline or script, the creator's recording, measured speech timing. Optional: module number and lesson code, a logo for the end slide.

## Avoid

Icons, stock photos, a second accent colour, prices or results the lesson does not state.

## Review

Each reveal lands on its phrase (±3 frames); the presenter circle never overlaps a diagram or covers the face; numbers match the script.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
