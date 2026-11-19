---
name: openmotion-red-pen-archive
description: >-
  OpenMotion — Add archive-paper graphics to a presenter video where one red pen circles, strikes and corrects claims with cited sources. Use for history, investigations and fact-checks.
---

# OpenMotion · Red-Pen Archive

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

Use the creator's own recording and measured speech timing. Do not place graphics over someone else's speech, and keep the face and mouth clear.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** history, investigations and fact-checks where a claim is examined and corrected.

## Look

| Element | Starting value |
| --- | --- |
| Paper | Aged archive paper `#EFE6D2`, light fold lines and edge wear |
| Type | Typewriter face for documents and quotes; dates in larger type |
| Accent | One red pen `#C8102E`: circles, strike-throughs, margin notes and corrected numbers |
| Evidence | Documents, photos and screenshots the user supplied or cited, shown as paper inserts |

## Motion

- Slide documents in like they are placed on a desk (slight rotation, 200–300 ms), then hold.
- The red pen acts only on the spoken claim: circle it, strike it, write the correction beside it, each stroke 300–600 ms.
- Push in slowly (2–4% scale over the shot) on the evidence being read.
- Cut back to the presenter for the conclusion.

## Inputs

Required: presenter recording with timings, the claims and their corrections, the source for every correction. Optional: archive images with usage rights.

## Avoid

Fabricated documents or quotes presented as real, correcting a claim without a source, more than one red mark per beat.

## Review

Every correction cites a real source; struck text is the claim actually spoken; generated or reconstructed documents are labelled as illustrations.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
