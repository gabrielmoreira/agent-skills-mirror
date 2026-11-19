---
name: openmotion-storybook-myth
description: >-
  OpenMotion — Tell a fable, myth or legend as painted picture-book scenes with a parchment text page and drifting light. Use for folk tales, bedtime stories and mythology explainers.
---

# OpenMotion · Storybook Myth

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** fables, myths, legends and bedtime stories narrated over a few painted scenes.

## Look

| Element | Starting value |
| --- | --- |
| Painting | Watercolour-style night or dusk scenes: soft washes, wobbly hill edges, gentle paper grain (soft-light, about 55%) |
| Palette | Night sky `#0D1838` → `#6E5E8C`, hills `#283862` / `#131E3A`, moon `#F6E7B0`, lantern gold `#FFD27A`, hero orange `#E07A35` |
| Type | An old-style serif (Cormorant Garamond or similar): italic gold title `#F2D58A`, story lines in dark brown on a parchment page `#F1E4C6` with a red drop cap `#A33A2A` |
| Layout | Title top left, one painted scene full frame, the story page low on the left |

## Motion

- Push the camera in slowly, 5–6% over a scene.
- Move the hero along a path with a walk cycle; small props (tail, lantern) swing on their own sine.
- Let light carry the magic: stars join into a shape line by line (300 ms apart), glows grow over 1.5–2 s, motes drift along an arc.
- Write each story line onto the page in about 1.5 s; crossfade the page between lines in 300 ms.

## Inputs

Required: the story text or the tale's name, the 3–5 beats to show, the main character. Optional: narration, music, a style reference the user owns. Generated pieces go through `openmotion_media_use` then `openmotion_assets_use`; one test painted scene is approved before batch generation. Label generated people as generated.

## Avoid

Retelling a protected modern book or film, scary imagery for young audiences, more than one story line on the page, claiming a myth's origin or date without a source.

## Review

Page text matches the narration word for word; the hero is never cut by the frame; glows never wash out the title; each scene holds 1 s after its last line.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
