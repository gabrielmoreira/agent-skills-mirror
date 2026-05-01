---
name: itch-html5-game-publishing
description: Package, test, publish, price, and update browser-playable HTML5 games on itch.io. Use when Codex is asked about itch.io HTML5 uploads, ZIP requirements, index.html, iframe embeds, fullscreen mode, mobile-friendly settings, case-sensitive paths, HTTPS assets, compression, game page setup, donations, pay-what-you-want pricing, creator payments, bonus files, or itch.io launch readiness.
license: MIT
---

# itch.io HTML5 Game Publishing

## Core Workflow

1. Identify the build type, engine/framework, expected viewport, desktop/mobile support, file size, payment intent, and whether the game should run embedded or fullscreen.
2. Produce a clean browser build with `index.html` at the ZIP root unless the project is a single self-contained HTML file.
3. Use relative paths and exact filename casing. Treat itch.io hosting as case-sensitive even if the local OS is forgiving.
4. Test the build from a local static server, then test the uploaded itch.io preview because iframe, fullscreen, HTTPS, audio, and path behavior can differ from local files.
5. Configure embed options: viewport size or fullscreen launch, click-to-play, fullscreen button, scrollbars, mobile-friendly flag, and pre-launch cover art.
6. Configure pricing deliberately. HTML5 games currently accept payments as donations; use project pricing, suggested donation, bonus downloadable files, or downloadable kind depending on the business model.
7. Prepare the game page for conversion: title, capsule/cover art, screenshots/GIFs, description, controls, accessibility notes, update notes, tags, engine tag, and support/contact details.

## Packaging Requirements

- Use ZIP for multi-file games; single HTML upload only works for truly self-contained files.
- Include every runtime asset needed by the game inside the ZIP.
- Keep `index.html` at the ZIP root.
- Avoid unsupported archive formats.
- Keep file count, path length, extracted size, and single-file size under itch.io's current limits.
- Do not reference non-HTTPS external resources.
- Optimize loading like a website: compress assets, reduce large files, avoid unnecessary source maps in release builds, and show loading progress.

## Donation And Pay-What-You-Want Guidance

- For HTML5 game pages, treat money as donation/support unless itch.io's current docs say otherwise.
- Use `$0 or Donate` when players should play for free but be asked to support.
- Use a suggested donation amount and page copy that explains what support funds.
- Use individually priced files for optional extras such as soundtrack, art pack, source files, bonus levels, wallpapers, or downloadable builds.
- Avoid relying on optional donations as the only monetization plan for a large commercial project without a realistic conversion expectation.
- If the game must require payment before access, review current itch.io docs and consider using a downloadable project kind or separate downloadable files.

## Freshness Rule

Verify current itch.io creator docs before giving tactical advice about file size limits, ZIP requirements, mobile-friendly flags, embed/fullscreen settings, payment behavior, creator payments, revenue share, or pay-what-you-want/donation mechanics.

## Browser QA

- Test Chrome, Firefox, and Edge at minimum when practical.
- Test mobile only if the page will be marked mobile friendly.
- Test audio unlock after click/touch.
- Test fullscreen and iframe sizing.
- Test save data behavior with local storage/IndexedDB where used.
- Test keyboard focus, pointer lock, gamepad, touch, and pause/focus loss.
- Test all asset loads after upload to catch case mismatches and path errors.

## Deliverable Shape

For itch.io publishing work, provide:

- Build/package requirements
- Upload ZIP structure
- Embed/fullscreen/mobile settings
- Pricing, donation, or pay-what-you-want setup
- Page copy and asset checklist
- Browser/upload QA steps
- Launch risks and update plan

## References

- Read `references/itch-html5-publishing-checklist.md` before shipping, updating, or monetizing an itch.io HTML5 game.
