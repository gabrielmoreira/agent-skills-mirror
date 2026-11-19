---
name: openmotion-before-after
description: >-
  OpenMotion — Make a before-and-after product video: show the problem, the product being used, then the visible result with a split wipe and clear labels. Use for cleaning, beauty, haircare, tools and fix-it products.
---

# OpenMotion · Before and After

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** products whose value is a visible change — stains removed, frizz calmed, scratches filled, rooms tidied.

## Look

| Element | Starting value |
| --- | --- |
| Frames | Same subject, same angle, same light for before and after; vertical or horizontal split |
| Labels | Small caps pills: `BEFORE` in slate `#5B6573`, `AFTER` in fresh green `#18B26B`, white text |
| Divider | 4 px white line with a round handle, soft shadow |
| Product | A clean product shot between the two halves or in the corner, 20–30% of the frame |
| Type | One plain bold sans for a 3–6 word result line |

## Motion

- Hold the before for 1–1.5 s so the problem is clear.
- Show the product in use for 1.5–2.5 s (pour, spray, brush, wipe).
- The divider wipes across in 900–1200 ms, revealing the after; a short sparkle or tick marks the end.
- End on the after with the product and the result line, held 1.5 s.

## Inputs

Required: the real product, a true description of the result. Optional: the user's own before and after footage, presenter, timing claim.

When the user has no footage, the before, use and after shots are generated through `openmotion_media_use` → `openmotion_assets_use` from the product photo. Approve one test clip first, then generate the rest with the same subject and lighting. Generated people and results are labelled as generated; never present them as a real customer.

## Avoid

Changing angle, light or subject between before and after, exaggerated results, invented time claims, beauty filters on the after only.

## Review

Before and after match framing within 5%; the change shown is the one the product claims; labels never cover the change; generated content is labelled.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
