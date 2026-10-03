---
name: site-ux-patterns
description: >-
  Small UX patterns that owners of community websites ask for after launch, ready to apply up front:
  a light/dark mode switch people can find, a social (Facebook group) button in the header, header that
  never wraps, no unwanted banners, plain-language copy an average high-school student understands,
  well-known labels like "Frequently Asked Questions", progressive enhancement without layout shift.
  Use when changing the header, footer, navigation, theme, wording, labels or page copy.
---

# Site UX patterns

## Light / dark mode that people can find

Following the device setting is not enough — the first owner could not find how to switch.

- **Header button** (tablet and desktop): round sun/moon icon button next to the social button. Label
  reflects the action: "Switch to light mode" / "Switch to dark mode" (`aria-label` + `title`). Hidden
  on very small phones to save room.
- **Phone Menu** and **every footer**: a labeled group "Light or dark mode" with three chips:
  Light · Dark · Auto, plus the hint "Auto matches your phone or computer."
- Remember the choice in `localStorage` (`<site>-theme`), apply it in the **inline head script** before
  first paint (`document.documentElement.dataset.theme = …`), so there is no flash. Auto removes the key.
- CSS: keep one set of dark tokens used by both
  `@media (prefers-color-scheme: dark) { :root:not([data-theme='light']) { … } }` and
  `:root[data-theme='dark'] { … }`; set `color-scheme` per choice. A unit test asserts both blocks are
  identical and that there are no other `prefers-color-scheme` rules (they would ignore the choice).
  Use tokens for things like map tile filters and icon visibility (`--when-light`/`--when-dark`).
- Track `theme_change` (method, location). Mention the stored choice on the privacy page.
- The inline script's CSP hash changes when you edit it; the postbuild step recomputes it.
- Starter files: `src/components/ThemeSwitch.astro`, `src/scripts/theme.ts`, `tests/unit/theme-css.test.ts`.

## Header that never wraps

- Contents: logo + name, nav links, theme button, social button. Measure the total at the widest
  breakpoint; switch to the Menu button *before* links wrap (first project: Menu below 78rem/1248 px, header
  allowed up to 80rem while the page stays 72rem).
- `visual-check.mjs` in `site-quality-gates` measures header height from 320 to 1600 px.
- Very narrow phones: let the brand text shrink and hyphenate (`min-width: 0`, `hyphens: auto`), and
  shrink the logo and Menu button below 360 px, so any organization name fits with any system font.

## Social link in the header

The organization's main community (usually a Facebook group) gets a round brand-colored button in the
header on every page, plus a card on Contact and a footer link. Track `outbound_click` (method facebook,
location header). Don't rely on the footer alone.

## Banners

Announcements default to **unpublished**. Keep one hidden example in the CMS so the collection isn't
empty. Only show a banner when an editor publishes one (weather closures, special notices).

## Progressive enhancement without layout shift

- An inline head script adds `js` to `<html>`. CSS hides JS-only controls when `html:not(.js)` and hides
  "collapsed" content only when `.js` is present. Everything still works without JavaScript.
- `[hidden]` always wins: `[hidden]:not([hidden='until-found']) { display: none !important; }` in the reset layer.
- Placeholders for client-filled text (relative dates) are hidden until filled.

## Plain language and labels

Read [references/plain-language.md](references/plain-language.md). Apply it to every page, button, form,
chart, table, error and email. Use the names people already know: "Frequently Asked Questions" (not
"Questions and answers"), "Add to calendar", "Get directions", "Share", "Contact", "Membership".

## Other small things owners notice

- Teacher, band and DJ names link to their sites everywhere they appear (cards, event pages, profiles).
- "Beginners welcome · No partner needed" on every home event.
- Captions on people photos ("Teacher: Jane Doe") rather than unlabeled faces.
- Copy feedback is a toast, not an alert. Buttons are ≥ 44 px tall.
