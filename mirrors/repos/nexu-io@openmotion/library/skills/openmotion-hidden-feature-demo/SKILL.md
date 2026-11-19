---
name: openmotion-hidden-feature-demo
description: >-
  OpenMotion — Make a hidden-feature product demo: a hook asks if viewers knew this trick, a close-up shows the exact press or move, and a callout names the result. Use for appliances, gadgets and apps with a useful feature people miss.
---

# OpenMotion · Hidden Feature Demo

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** appliances, gadgets, tools and apps where one lesser-known button, gesture or setting saves time.

## Look

| Element | Starting value |
| --- | --- |
| Shots | Wide shot of the product in its real setting, then tight close-ups on the control and the result |
| Hook | Bold white sans with a dark rounded backing, `#111317` at 80%, top third, 4–8 words |
| Focus | A soft circle or ring, accent `#FFD23F`, around the exact button or part |
| Steps | Numbered chips `1 2 3` with two-word actions |
| Result | One line naming what the feature gives, with a tick |

## Motion

- Open on the hook within the first 0.5 s, over the wide shot.
- Push in on the control over 600–900 ms; the focus ring draws on in 300 ms as the finger arrives.
- Hold the press long enough to see it (≥600 ms) and pulse the ring once.
- Cut to the result close-up; step chips and the result line land 300 ms apart.

## Inputs

Required: the real product, the exact feature and how to trigger it, what it produces. Optional: presenter, setting, call to action.

Shots the user cannot film are generated through `openmotion_media_use` → `openmotion_assets_use` from the product photo. Approve one test clip first; keep buttons and display text true to the real product. Generated people are labelled as generated.

## Avoid

Features the product does not have, button labels that change between shots, more than three steps, hiding the finger action behind text.

## Review

A viewer could repeat the trick after one watch; the ring sits on the correct control; on-screen text matches the real labels; generated content is labelled.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
