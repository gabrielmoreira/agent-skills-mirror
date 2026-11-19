---
name: openmotion-multi-clips-to-reels
description: >-
  OpenMotion — Turn a folder of short clips into one vertical reel: review every clip, skip the weak ones, order the keepers and cut them on the beat with a short title. Use for trips, events, product footage and recaps.
---

# OpenMotion · Multi Clips To Reels

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** trips, events, product shoots and weekly recaps made from many short clips.

## Look

| Element | Starting value |
| --- | --- |
| Format | 9:16 vertical, 15–30 s; a short title in a heavy display font with one accent such as `#C8F03C` |
| Framing | Reframe each landscape clip around its subject; never squash or letterbox by default |
| Cut rhythm | Cuts land on beats, usually every 2 beats; faster in the middle, a longer last shot |
| Overlays | Thin progress bar and the title only; no stickers over faces |
| Review board | Grid of source clips with a pick number or skip reason on each |

## Motion

- Review the source clips first and mark picks and skips with a reason (shaky, duplicate, dark, no subject).
- Order the picks for a small arc: opener, detail, wide, people, closer.
- Cut on the beat with a 6–8% punch-in that eases out over the shot; an optional 1–2 frame flash on hard cuts.
- Bring the title in on the first beat and keep it at most 3 s unless the user wants it throughout.

## Inputs

Required: the source clips (user footage). Optional: a music track or BPM, the title, preferred length, logos or a closing card.

## Avoid

Using every clip, cutting off the beat, cropping away the subject, repeating the same shot twice, music louder than any speech kept in the reel.

## Review

Each skip has a reason; every cut is on a beat; subjects stay centred after reframing; length matches the brief.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
