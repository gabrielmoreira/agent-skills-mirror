---
name: openmotion-motion-graphic-placement
description: >-
  OpenMotion — Plan where motion graphics go in a talking video: tie each graphic to a line that earns it, such as a number, a list or a quote, match the graphic type to that line and keep face and captions clear. Use for talking-head, lecture, tutorial and podcast edits.
---

# OpenMotion · Motion Graphic Placement

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

Use the creator's own recording and measured speech timing. Do not place graphics over someone else's speech, and keep the face and mouth clear.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** talking-head, lecture, tutorial, interview and podcast videos that need graphics placed with intent.

## Look

| Element | Starting value |
| --- | --- |
| Number card | Saturated blue `#1F3BFF`, white figures, before → after |
| Steps card | White card, numbered blue dots, one short line per step |
| Quote card | Charcoal `#15171C`, serif quote, amber `#FFC53D` on the key words |
| Position | Opposite the face; above the caption zone; one card family for the whole video |

## Motion

- Each graphic lands on its trigger word (±3 frames) and enters in 300–400 ms.
- Hold at least twice the reading time; exit before the next trigger.
- Density: one meaningful graphic every 5–8 s in landscape, every 3–5 s in vertical; tighter in the first 15 s.
- Match type to the line: number → counter, steps → list, choice → split card, opinion → quote, name → lower third, call to action → button card.
- After a full-screen graphic, leave at least 1.5 s before the next one.

## Inputs

Required: the creator's recording, a word-timed transcript, the aspect ratio. Optional: brand style, existing graphics to reuse. Write the plan (trigger word, timecode, type, position) before building.

## Avoid

Graphics on a timer; the same form twice in a row unless it is a deliberate series; covering face, hands, product or captions; full-screen takeovers where a card is enough; illustrating filler words.

## Review

Every graphic in the plan has a trigger word and timecode; check the frame at each one for overlap; nothing appears before its line is spoken.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
