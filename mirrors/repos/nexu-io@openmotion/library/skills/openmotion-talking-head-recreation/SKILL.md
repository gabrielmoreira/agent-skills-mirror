---
name: openmotion-talking-head-recreation
description: >-
  OpenMotion — Re-edit the creator's own talking-head footage with the cutting rhythm and packaging of a reference video they like: punch-ins, caption style, text cards, name tags and pacing, mapped beat by beat to their own words. Use when a creator asks to edit theirs like that one.
---

# OpenMotion · Talking Head Recreation

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

Use the creator's own recording and measured speech timing. Do not place graphics over someone else's speech, and keep the face and mouth clear.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** creators who have their own talking-head recording and a reference edit whose style they want.

## Look

| Element | Starting value |
| --- | --- |
| Captions | Measured from the reference; sample: condensed caps, white, lime `#C6FF3D` keyword |
| Punch-ins | Reference zoom amount, usually 110–120%, centred above the eyes |
| Text cards | Reference card colour and two-word rhythm; sample: black with one lime word |
| Name tag | Reference position and length; sample: lower left, accent bar, 1.5 s |

## Motion

- First build a beat map of the reference: every cut, zoom, card, tag and B-roll with its timecode and job.
- Map each beat to the creator's line that does the same job (key line, number, list, call to action); match function, not timestamp.
- Keep the average shot length within ±20% of the reference.
- Punch-ins snap in about 120 ms on the key word; cards hold 1–1.5 s.

## Inputs

Required: the creator's recording(s), the reference video (file or link), measured speech timing for both. Optional: logo or product images for B-roll, notes on length. Swapping people or products inside the reference, or having no own footage, needs a different Skill.

## Avoid

Copying the reference's words, music, logos or footage into the output; forcing a beat where the creator says nothing that fits; punch-ins that crop the chin or forehead; captions that cover the mouth.

## Review

Deliver the beat map as matched, adapted or skipped with a reason for each; check every punch-in frame; the result is an editable composition, not a flattened file.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
