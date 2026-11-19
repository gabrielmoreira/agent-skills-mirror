---
name: openmotion-push-in-type
description: >-
  OpenMotion — Make a product promo where the camera keeps pushing forward through layers of big words until it lands on the logo. Use for app and SaaS launch teasers, feature one-liners and short brand openers.
---

# OpenMotion · Push-In Type

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** app and SaaS launch teasers, 6–15 s feature one-liners and brand openers built from a few short words.

## Look

| Element | Starting value |
| --- | --- |
| Background | Warm paper `#F2EEE6`, flat; thin crop-mark corners and faint guide lines in `#16161A` at 25% |
| Type | One heavy grotesk (e.g. Inter Tight 800), all caps, 2–3 words per layer, ink `#16161A` |
| Accents | One signal colour `#F0532B` for the key word, short yellow `#F7C534` slashes that fly past |
| Layout | Every layer centred on the same axis so the push reads as one camera move |
| End card | Logo, product name and a one-line promise at normal scale on the paper |

## Motion

- The camera never stops: each layer grows from about 60% to 100% over 0.8–1.2 s, then rushes past to 600–900% in 0.4–0.6 s with 6–12 px blur and fades out.
- The next layer is already emerging behind the one leaving; overlap the two by 150–250 ms so there is no empty frame.
- Push through a letter's counter (the hole in an O or A) when the copy allows it; it sells the depth.
- Accent slashes cross the frame on each pass in 300 ms.
- Ease into the end card over 0.8 s and hold it at least 2 s.

## Inputs

Required: product name, 3–5 short copy beats in the user's words, logo. Optional: brand font and colours, website for copy.

## Avoid

More than three words per layer, rotating or tilting the camera, cutting instead of pushing, small body copy in the push.

## Review

Every layer is readable for at least 0.5 s at rest; no frame is empty; the final logo is sharp and unscaled; the push direction never reverses.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
