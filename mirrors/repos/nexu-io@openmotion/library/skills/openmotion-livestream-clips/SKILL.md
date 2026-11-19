---
name: openmotion-livestream-clips
description: >-
  OpenMotion — Cut a recorded livestream sale into short product clips: one product per clip, a real hook first, then proof, the offer and one call to action. Use for live shopping replays that must become posts or ads.
---

# OpenMotion · Livestream Clips

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

Use the creator's own recording and measured speech timing. Do not place graphics over someone else's speech, and keep the face and mouth clear.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** live shopping replays with several products that need one standalone vertical clip each.

## Look

| Element | Starting value |
| --- | --- |
| Format | 9:16, host centred, product beside the face, never over it |
| Hook | Top 12%, heavy sans, white with one yellow `#FFE14D` keyword |
| Product tag | White card lower left: name and one plain fact |
| Offer and CTA | Red bar `#FF3D5A` for the deal mechanic; white pill button for the call to action |

## Motion

- Open on the strongest spoken line about this product, verbatim, inside the first 2 s.
- Hook text pops in (scale 1.4 → 1, about 350 ms).
- Product tag slides in when the host names the product; offer bar at the move from proof to deal.
- Call to action in the last 2–3 s; pulse at most three times.

## Inputs

Required: the replay, its transcript, the product list. Optional: product photos, publishing window, price policy, target platform. Map product segments from transcript and frames, skip products whose pitch was cut off, and cut out room chatter: greetings, giveaways, stock counts, queue numbers.

## Avoid

Prices or discounts nobody said; two products in one clip; countdowns or 'today only' lines in clips posted later; banned claims for the market (miracle, cure, best ever); captions covering the product.

## Review

Each clip makes sense with no context; the hook is a real quote; every price matches the stream and the chosen price policy; product name and visuals agree.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
