---
name: openmotion-mystery-box-reveal
description: >-
  OpenMotion — Build a playful product reveal around a choice of mystery boxes: pick one, shake, pop the lid and lift the product out with its name and price. Use for launches, drops, giveaways and gift ideas.
---

# OpenMotion · Mystery Box Reveal

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** launches, limited drops, giveaways and gift guides.

## Look

| Element | Starting value |
| --- | --- |
| Set | Soft studio colour, e.g. `#F3C9CF` to `#E7AFB8`, with a floor line and one warm spotlight |
| Boxes | Two to four plain kraft boxes `#C99A66` with a cream `?` sticker; no logos until the reveal |
| Product | Clean, centred, at least half the frame height after the reveal |
| Type | One heavy display font for the headline and name, one plain sans for details; ink `#2B1A2E` |
| Accent | A single accent such as `#E0507A` for the label, price tag and confetti |

## Motion

- Open on the choice: a headline such as "Pick a box" and a highlight that hops between boxes every 350–400 ms before landing.
- Clear the other boxes (400–500 ms) and bring the chosen one forward; shake it for about 1 s with growing amplitude.
- Pop the lid off in 600–800 ms with a light burst and a short confetti fall (2–3 s, gravity, no loops).
- Lift the product out with a soft overshoot, then slide in the name and swing in the price tag.

## Inputs

Required: the product, its real name and price, one or two true selling points. Optional: brand colours, a host recording.

Product stills or a host scene can be generated through `openmotion_media_use` → `openmotion_assets_use`. Approve one test image with the user before generating the rest, and label any generated person as generated.

## Avoid

Fake prizes or prices, more than four boxes, a reveal that comes after 6 s in an 8–15 s clip.

## Review

The suspense phase is under half the runtime; the product is sharp and fully visible after the pop; name and price match the brief exactly.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
