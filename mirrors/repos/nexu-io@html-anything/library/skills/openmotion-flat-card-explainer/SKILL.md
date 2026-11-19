---
name: openmotion-flat-card-explainer
description: >-
  OpenMotion — Make a SaaS explainer from flat UI cards: scattered windows show the problem, a cursor tidies them, a simple board shows the product working. Use for workflow, task and collaboration tools.
---

# OpenMotion · Flat Card Explainer

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** showing how a SaaS product works in 3–4 steps without screen recordings.

## Look

| Element | Starting value |
| --- | --- |
| Background | Very light grey `#F2F2F6` with a white centre glow |
| Cards | Flat white windows with an indigo `#5458E8` title bar, yellow `#F7C744` text bars and pink `#F0507A` blocks; radius 8 px, soft drop shadow |
| Type | Geometric sans in italics for captions (500, 54–60 px) with the key words in extra bold indigo or pink |
| UI | Simplified boards, lists and avatars rebuilt from the user's product; real labels, no lorem ipsum |
| Cursor | Dark arrow cursor with a white outline that performs every action |

## Motion

- Problem: 6–8 cards pop in across the frame (60 ms stagger) and drift slowly.
- Gather: the cursor arrives and the cards fly into one neat stack (600 ms each, power3 in-out, 50 ms stagger).
- Show: the stack opens into the product view; the cursor drags one item to its next state in ~700 ms and a check mark pops.
- Close: the view scales away and the call to action rises with a hand-drawn underline drawn in 500 ms.

## Inputs

Required: product name, the 3–4 workflow steps, real board or list labels, call to action. Optional: screenshots to copy the layout from, brand colours.

## Avoid

Pixel-perfect UI with tiny unreadable text, more than one cursor action per step, captions longer than six words, invented customer numbers.

## Review

Card labels are readable at 1×; the cursor reaches each target before acting; captions never overlap cards.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
