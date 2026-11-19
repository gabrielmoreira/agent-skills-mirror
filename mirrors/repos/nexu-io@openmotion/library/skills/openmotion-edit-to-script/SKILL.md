---
name: openmotion-edit-to-script
description: >-
  OpenMotion — Assemble a rough cut from the creator's takes by following their target script line by line, then play it back for review. Use when someone has a script and a folder of recorded takes.
---

# OpenMotion · Edit To Script

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

Use the creator's own recording and measured speech timing. Do not place graphics over someone else's speech, and keep the face and mouth clear.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** talking-head, tutorial and explainer recordings where the creator already has the script they want.

## Look

| Element | Starting value |
| --- | --- |
| Review layout | Script card on the left, preview monitor top right, takes and rough-cut track below |
| Script card | Off-white `#FFFDF8`, a serif such as Lora at 26–30 px; the active line gets a `#FFE58A` marker |
| Takes | Small chips with take number and duration; unused takes dim to 35% with a strikethrough reason |
| Rough cut | Dark track `#26252A`; clip widths follow real durations; a yellow playhead |
| Captions | Plain sentence-case captions on a dark pill under the speaker |

## Motion

- Mark a script line (300–400 ms), then move the matching take from the bin into its slot (500–600 ms).
- Tick each script line once its take is placed.
- After assembly, sweep a playhead across the cut and sync the preview caption to the clip under it.
- Keep pacing natural: trim fillers and long gaps but never cut inside a word.

## Inputs

Required: the creator's recordings, the target script, transcripts with word timing (from the host or a provider). Optional: pace preference (tight, natural, relaxed), notes on which takes the creator prefers.

## Avoid

Writing words the creator never said, reordering inside a sentence, using a take that only partly matches without flagging it, mixing two speakers' takes into one line.

## Review

Every script line maps to a recorded take or is reported missing; the cut plays in script order; transcript and caption match the audio; unused takes are listed with a reason.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
