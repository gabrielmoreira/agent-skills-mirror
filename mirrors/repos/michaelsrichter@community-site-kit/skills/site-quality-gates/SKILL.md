---
name: site-quality-gates
description: >-
  Verify a community website before publishing: type check, unit/API/e2e tests, accessibility (axe),
  320 px layout, header fit, link check, Lighthouse, live smoke test, and screenshots in light and dark
  mode on phone and desktop that are actually reviewed. Use before every commit that changes UI or
  content, before deploys, when the owner reports something "looks weird", or when asked to QA a site.
---
> `<kit>` = the folder where the community-site-kit plugin is installed (usually `~/.copilot/installed-plugins/community-site-kit/community-site-kit`; check with `copilot plugin list --json`) or a clone of github.com/michaelsrichter/community-site-kit. Run Node scripts from the site repo folder so they can use its `sharp`, `playwright` and `yaml` packages.


# Quality gates (run before every publish)

The owner's rule: **verify visually before publishing**, in light and dark mode, on phone and desktop.
Tests passing is not enough; look at the screenshots.

## 1. Automated checks (starter commands)

```powershell
node <kit>/skills/site-quality-gates/scripts/normalize-lockfile.mjs --check   # lockfiles use registry.npmjs.org
npx astro check                                   # 0 errors
npx vitest run                                    # unit
cd api; npm test; cd ..                           # API
$env:BUILD_NOW='2026-10-01T22:00:00-04:00'; npm run build   # pinned date for repeatable output
npm run test:links                                # no broken internal links
npx playwright test                               # e2e incl. axe, 320 px, keyboard, CMS loads
```

Stop any preview server on port 4321 before Playwright (its webServer needs the port). If a test is
flaky, rerun it alone; if it fails twice, it's a real bug.

If the lockfile check fails, the machine installed through a private npm mirror (company proxy, Azure
Artifacts, Artifactory) and wrote the mirror's URLs into `package-lock.json`. Run the same script without
`--check` to rewrite them to `registry.npmjs.org` before committing — otherwise a public repo leaks an
internal host and Dependabot fails with `private_source_authentication_failure`.

CI runs on Linux, whose fallback fonts are wider than Windows' (Segoe UI). A layout that fits at 320 px
locally can overflow in CI; long organization names in the header are the usual cause. Test with a wide
font (inject `body,button{font-family:Verdana!important}`) when a 320 px check fails only in CI.

Lighthouse's SEO score drops to ~0.7 when pages are `noindex`; build CI with indexing allowed and keep
deploys `noindex` until launch.

## 2. Visual check (always)

```powershell
npx astro preview --port 4400   # in another terminal, or async
node <kit>/skills/site-quality-gates/scripts/visual-check.mjs --base http://localhost:4400 --paths "/,/events/,/events/map/,/contact/" --out shots --clock 2026-10-01T22:00:00-04:00
```

It saves `shots/<page>-<phone|desktop>-<light|dark>.png` and prints, per page and mode: horizontal
overflow at 320 px (with the offending elements), header height at widths 320–1600 (a jump means the
nav wrapped), console errors, broken images, and images displayed larger than their source (upscaled).
Then **open the screenshots with the view tool** and check:

- Nothing cut off (heads in photos, text in buttons), no overlapping, no empty sections.
- Dark mode: text contrast, badges, maps, photos, focus rings, form controls, the footer.
- Phone: the next event and its buttons are above the fold; buttons are big enough; the Menu works.
- Words: would an average U.S. high-school student understand every label and sentence?

For a specific feature, screenshot it in its states (e.g. collapsed/expanded, menu open, popup open).
Scroll maps and lazy content into view first.

## 3. Accessibility

- axe via `@axe-core/playwright` on key pages in both color schemes: no serious/critical violations.
- Keyboard: tab through header, menu, filters, cards, share dialog, slideshow; visible focus; Escape closes.
- Reduced motion: slideshow doesn't autoplay; no smooth scroll.
- Screen reader names: buttons say what they do ("Show 7 more dances", "Switch to light mode").

## 4. Performance and SEO

`npx lhci autorun` (or Lighthouse in Chrome) on home, events, an event page: ≥ 90 performance, ≥ 95 the
rest. Check titles/descriptions are unique, canonical URLs use the live domain, JSON-LD validates.

## 5. After deploy

- `node scripts/smoke.mjs https://<live site>` — all pass.
- Open the live site in a browser (Playwright) on phone + desktop, both color schemes; check the changed
  feature works there and the console has no errors.
- Then send the owner the update email (see `modernize-community-site/references/owner-handoff.md`).

## Writing new tests

Every owner request gets at least one e2e test that would fail without the change (e.g. "only 3 home
events visible, toggle reveals the rest", "theme choice remembered on the next page", "Facebook button in
the header on every page", "no announcement banner"). Pin the clock (`page.clock.setFixedTime`) for anything
date-related.
