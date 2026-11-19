---
name: openmotion-paper-diorama
description: >-
  OpenMotion — Turn a history or process story into layered cut-paper diorama scenes with a slow camera push between paper planes. Use for history lessons, how-it-was-made stories and cultural explainers.
---

# OpenMotion · Paper Diorama

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** history lessons, craft and process stories, short cultural explainers narrated by a voice.

## Look

| Element | Starting value |
| --- | --- |
| Planes | 4–6 flat paper layers per scene (sky, far hills, mid buildings, near water, foreground prop), each with a soft drop shadow, `0 10px 8px` at 35% black |
| Palette | Warm dusk set: sky `#E58E5A` to `#F6DDB2`, sea `#2C5466`, hills `#7C918F`, buildings `#C9A27E` / `#B9805F`; night shifts the sky to `#1E2F4C` |
| Texture | Fine paper grain over everything (fractal noise, multiply, about 30%) |
| Type | One display serif for chapter titles on a torn paper label, a small spaced sans kicker for era or chapter |

## Motion

- Open each scene as a pop-up: layers rise into place back to front, 280 ms apart, with a slight overshoot (700–1000 ms each).
- Move the camera slowly (6–8% push over the whole scene); nearer layers move more than far ones.
- Show change through light, not cuts: sky darkens over 2–3 s, windows switch on one by one at random 100–250 ms gaps.
- Hold each finished scene at least 1.5 s before the next pop-up.

## Inputs

Required: the narration script or topic, 3–6 key moments to stage, and the facts or dates to show. Optional: reference photos of the place or object, voice-over, music. Generated pieces go through `openmotion_media_use` then `openmotion_assets_use`; one test scene is approved before batch generation. Label generated people as generated.

## Avoid

Photo textures inside layers, more than one moving prop at a time, dates or numbers the brief does not supply.

## Review

No empty layer edges during the push; the label reads at 1× speed; one focal point per scene; light changes land on their narration line.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
