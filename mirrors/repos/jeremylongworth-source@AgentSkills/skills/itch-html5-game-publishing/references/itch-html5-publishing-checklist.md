# itch.io HTML5 Publishing Checklist

Use this checklist before uploading, updating, or monetizing a browser-playable itch.io game.

## Build Package

- Multi-file projects are uploaded as a ZIP, not loose files or unsupported archive formats.
- `index.html` is at the ZIP root.
- All required assets are inside the ZIP or loaded from HTTPS URLs.
- Paths are relative and filename casing matches exactly.
- File count, extracted size, single-file size, and path length fit current itch.io limits.
- Release build excludes unnecessary source maps, raw source assets, caches, and unused files.

## Embed Settings

- The project kind is set to HTML Game.
- Embed-in-page or click-to-launch-fullscreen is chosen based on game layout.
- Viewport dimensions are set for embedded games.
- Fullscreen button, click-to-play, and scrollbars are configured deliberately.
- Mobile Friendly is enabled only after real mobile browser testing.
- Cover/background image and page theme make the pre-launch state look intentional.

## Browser Testing

- Uploaded preview loads without console asset errors.
- Audio starts correctly after click/touch.
- Fullscreen, keyboard focus, pointer/touch, gamepad, pause, and restart work inside the iframe.
- Save data works if local storage or IndexedDB is used.
- The game handles dynamic viewport sizes, especially fullscreen and mobile.

## Pricing And Support

- Pricing mode matches the intent: donation/free support, paid downloadable access, no payments, or optional extras.
- Suggested donation and project copy explain what support funds.
- Optional paid files are stable enough that future price changes will not surprise existing buyers.
- Creator payment settings, tax/payment expectations, and revenue share settings are reviewed in itch.io account settings.

## Page Readiness

- Page has title, short pitch, controls, screenshots/GIFs, cover image, tags, platform notes, accessibility notes, and known issues.
- Changelog/update notes explain what changed.
- Support/contact link exists.
- Analytics or feedback plan is ready if the launch is a prototype or jam build.
