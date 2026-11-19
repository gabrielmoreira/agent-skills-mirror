---
name: openmotion-paper-collage-explainer
description: >-
  OpenMotion — Make a narrated explainer or story ad from large paper-cutout collage scenes assembled on the narration beats. Use for video essays and explainers with no presenter on camera.
---

# OpenMotion · Paper Collage Explainer

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** narrated explainers, video essays and story-led ads without a presenter on camera.

## Look

| Element | Starting value |
| --- | --- |
| Scene | 6–8 large, separate cutout pieces per scene: one hero subject, two or three context pieces, texture and a headline strip |
| Material | Torn paper edges, halftone photo cutouts, newsprint and kraft textures, a visible drop shadow under each piece |
| Palette | Muted base (cream, newsprint grey) plus one saturated accent per film |
| Type | Bold condensed headline on a paper strip; short phrases, not sentences |

## Motion

- Assemble each scene piece by piece on the narration beats: pieces slide or drop in 250–400 ms with a small overshoot, never fly from off-screen corners.
- Keep a slow camera drift (2–3% over the scene) so a still collage feels alive.
- Move between scenes by reusing one piece as the bridge, or with a paper-tear wipe.
- Keep generated pieces as separate layers so each one stays editable in Studio.

## Inputs

Required: topic or script (write the narration first), aspect ratio. Optional: voice choice, music, user images. Discover providers with `openmotion_media_use` and generate missing pieces with `openmotion_assets_use`; one style test image is approved before the full set is generated.

## Avoid

Collages with more than eight pieces, small pieces that read as clutter, flattened single-image scenes, archival-looking images presented as real history.

## Review

Each scene has one clear subject; pieces arrive on the words they illustrate; text strips are readable on a phone; all pieces remain separate editable layers.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
