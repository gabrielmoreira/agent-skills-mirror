---
name: openmotion-whiteboard-marker
description: >-
  OpenMotion — Add hand-written whiteboard graphics to a presenter video: marker keywords in blue and coral, arrows that link ideas as they are said. Use for concept breakdowns and lessons recorded by the creator.
---

# OpenMotion · Whiteboard Marker

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

Use the creator's own recording and measured speech timing. Do not place graphics over someone else's speech, and keep the face and mouth clear.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** concept breakdowns and whiteboard-style lessons over a presenter recording.

## Look

| Element | Starting value |
| --- | --- |
| Board | White `#FAFAF7` with a very light grid or none |
| Ink | Handwritten-style font for keywords; marker blue `#2F6BFF` for ideas, coral `#FF6F59` for the contrast or warning |
| Connectors | Hand-drawn arrows, circles and underlines as SVG paths with slightly irregular strokes |
| Layout | Ideas accumulate on one board; earlier items dim to 40% instead of disappearing |

## Motion

- Animate keywords as if written: SVG stroke-dashoffset or a left-to-right mask, 400–700 ms per word.
- Draw an arrow only when the presenter links two ideas; the arrow finishes before the second idea appears.
- Use coral once per board for the "but" or the mistake.
- End each section on the completed board for 1.5–2 s, then return to the presenter.

## Inputs

Required: presenter recording, transcript with timings, the idea list and how ideas connect. Optional: Brandkit colours to replace blue and coral.

## Avoid

Clip-art icons, typed computer fonts for keywords, boards with more than six ideas, arrows that do not match a spoken link.

## Review

Every written word matches the speech; arrows connect the ideas the presenter linked; the final board is legible on a phone screen.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
