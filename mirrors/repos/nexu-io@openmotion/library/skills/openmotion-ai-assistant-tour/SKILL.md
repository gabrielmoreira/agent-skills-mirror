---
name: openmotion-ai-assistant-tour
description: >-
  OpenMotion — Make an AI assistant feature tour: orb intro, a prompt that types a real request, a tilted answer card that streams in, and quick result actions. Use for chatbot, copilot and AI feature launches.
---

# OpenMotion · AI Assistant Tour

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** launching an AI assistant, copilot or chat feature step by step.

## Look

| Element | Starting value |
| --- | --- |
| Background | Soft pastel gradient, blue `#EEF4FF` → lilac `#F6F0FF` → pink `#FDEFFA`, with faint concentric rings |
| Mark | A glossy orb with a conic gradient of blue `#3E8BFF`, violet `#7B5CFF` and pink `#F27AD4`; small rotated-square sparkles |
| Prompt box | Large white rounded field (radius 36 px) with a violet outline, mode chips and a dark send button |
| Answer card | White card, radius 28 px, a gradient user bubble at the top right, short structured lines with tinted labels |
| Type | Clean neo-grotesk; 80–90 px for the wordmark, 40–46 px typed prompt, 24–26 px answer text |

## Motion

- Orb spins in (700 ms, back-out) next to the wordmark; sparkles rotate slowly throughout.
- Prompt box rises, placeholder swaps to typed text at a natural pace (about 18 characters per second) with a blinking caret.
- Cursor clicks send; the answer card tilts up from 28° (600 ms) and lines appear one by one, 300 ms apart.
- Feature beats such as edit, save or voice get one screen each with a cursor hover that reveals the actions.

## Inputs

Required: assistant name, 2–4 features to show, one real example prompt and answer produced by the product, logo or orb colours. Optional: screenshots of the real interface, generated example images through `openmotion_media_use` → `openmotion_assets_use` (approve one test image before generating a set).

## Avoid

Answers the product cannot give, wall-of-text responses, unreadably fast typing, more than five feature beats in 30 s.

## Review

Prompt and answer come from the real product; typing finishes before the cut; the cursor never covers text being read.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
