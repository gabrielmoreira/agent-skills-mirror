---
name: openmotion-shot-breakdown
description: >-
  OpenMotion — Break a reference video into a shot-by-shot board: one card per shot with a frame grab, timecode, shot size, lens, movement, why it cuts there and what it adds to the story. Use before recreating a reference or briefing a shoot.
---

# OpenMotion · Shot Breakdown

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** studying a reference film, ad or trailer before recreating its rhythm, or briefing a shoot from it.

## Look

| Element | Starting value |
| --- | --- |
| Board | Charcoal `#131518`, cards `#1C1F24`, cream text `#EDE6D6` |
| Accent | Amber `#F2A541` only on the turning-point shots and the playhead |
| Type | Plain sans for notes, monospace for timecodes and shot numbers |
| Layout | Three-column grid, one card per shot: grab on top, then Frame, Lens, Cut and Why rows; a strip of all shots above |

## Motion

- When the board is rendered as video, a playhead crosses the shot strip and each card fills as it passes that cut.
- Grab wipes in over 0.4 s; note rows follow with a 100 ms stagger.
- Six shots build in about 3 s; then the turning points get the amber outline and the rest dim to 55%.
- Finish on the one-line visual rule for the whole sequence.

## Inputs

Required: a reference video the user may analyse, and measured shot boundaries (detect cuts, then confirm against frames). Optional: transcript or audio notes, the user's goal, a shot limit. With more than 20 shots, report the count and ask which range to cover.

## Avoid

Describing only what is visible without saying why; stating lens or focal length as fact when it is an estimate (mark it); notes about frames nobody inspected; copying the reference's text or footage into the user's own video.

## Review

Each card's grab matches its timecode; shot count equals cut count; every card answers why the cut lands there; the closing rule is one or two sentences the user can shoot or edit to.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
