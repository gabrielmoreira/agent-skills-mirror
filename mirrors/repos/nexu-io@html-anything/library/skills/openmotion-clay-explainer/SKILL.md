---
name: openmotion-clay-explainer
description: >-
  OpenMotion — Tell a simple science or story idea with plasticine characters, soft studio light and stop-motion timing. Use for kids' lessons, science basics and friendly brand stories.
---

# OpenMotion · Clay Explainer

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** children's lessons, everyday science and gentle brand stories with one or two characters.

## Look

| Element | Starting value |
| --- | --- |
| Material | Rounded plasticine shapes with lumpy edges, a top-left highlight and a grounded shadow |
| Palette | Mint sky `#A6D8CB`, grass `#7DB86A`, soil `#A9784F`, water `#3C8FD1`, sun `#F2A93B`, warm brown text `#5A2E1A` |
| Characters | Simple faces: two dot eyes, a curved mouth, pink cheeks; expressions change by swapping the mouth shape |
| Type | A rounded sans (Fredoka or similar) on clay plaques and a step chip |

## Motion

- Animate on twos: hold each pose for 1/12 s and let the clay surface shift slightly between poses.
- Grow and squash with overshoot: a character fills up over 2–3 s, then settles with a 5–8% bounce.
- Show a process as repeating small actions: drops rise or fall in loops of 0.9–1.6 s, staggered 300–400 ms.
- Change the step chip at each new idea with a quick 250 ms bump.

## Inputs

Required: the script or question, 2–4 steps to show, the main character idea. Optional: voice-over, music, a reference image of a character the user owns. Generated pieces go through `openmotion_media_use` then `openmotion_assets_use`; one test image or clip is approved before batch generation. Label generated people as generated. Simple scenes can be built from code shapes instead.

## Avoid

Glossy plastic or 3D-render looks, realistic people, more than two characters talking at once, science claims the brief does not support.

## Review

Movement reads as stepped, not smooth; each step chip matches the narration; characters stay inside the frame at their largest size; faces stay readable on a phone.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
