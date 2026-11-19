---
name: openmotion-spec-sheet
description: >-
  OpenMotion — Add a spec-table overlay to a presenter review: black dot-matrix table, condensed type and a red row for the spec being discussed, with values appearing as they are spoken. Use for gadget, software and pricing reviews.
---

# OpenMotion · Spec Sheet

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

Use the creator's own recording and measured speech timing. Do not place graphics over someone else's speech, and keep the face and mouth clear.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** gadget, camera, software and pricing reviews where numbers matter.

## Look

| Element | Starting value |
| --- | --- |
| Table | Black panel `#0B0B0B`, dot-matrix or monospace figures, hairline row rules `#333` |
| Type | Condensed sans in caps for labels, tabular numbers for values |
| Accent | One red highlight row, `#E5322D`, for the spec currently being discussed |
| Placement | Side panel (16:9) or lower half (9:16); the presenter stays visible |

## Motion

- Add a row the moment the spec is said: label slides in 6–8 px, value counts or flips to its final number in 300–500 ms.
- Move the red highlight to the active row; previous rows stay visible in grey.
- Comparisons use two aligned columns, never two separate tables.
- Collapse the panel when the talk moves away from specs.

## Inputs

Required: presenter recording with timings, a spec list with sources (manufacturer page, measured result or the user's own test). Optional: product image for the panel header.

## Avoid

Numbers that were not spoken or sourced, more than eight rows, animated counters on values that are not quantities, red used for anything except the active row.

## Review

Every value matches its source and the speech; units are correct; the active row changes in sync with the voice; the table never covers the face.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
