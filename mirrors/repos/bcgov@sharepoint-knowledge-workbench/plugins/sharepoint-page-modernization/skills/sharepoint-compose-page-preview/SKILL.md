---
name: sharepoint-compose-page-preview
plugin: sharepoint-page-modernization
description: Merges a site's structural chrome (navigation, header, logo, ancestors) with an already-extracted page's content (modern-preview.html + metadata.json) into a single self-contained offline preview HTML file. Disk-only; performs no tenant writes.
allowed-tools: Bash, Read
examples:
  - "python3 scripts/preview_composition.py --page-folder ./destination/My-Page --chrome-folder ./site-chrome/Example --output ./destination/My-Page/full-preview.html"
---

# Compose Page Preview

## Trigger and Purpose

A reviewer confirming a page conversion needs to see the result in context --
not a bare content fragment, but the page as it would look with the site's
own navigation, header, logo, and breadcrumb trail in place. This skill
merges a page folder's extracted content with a chrome folder's structural
data into one complete, self-contained offline HTML file.

## Inputs

- **Page folder**: must contain `metadata.json` (page title, source URL,
  extraction timestamp) and `modern-preview.html` (the extracted page
  content, wrapped in a `<main class="page-content">` or `<div
  class="page-content">` element -- falls back to `<body>` if that wrapper is
  absent).
- **Chrome folder**: must contain `site-chrome.json` with `Web` (title, and
  optionally `SiteLogoUrl` or `SiteLogoLocalFile`), `TopNav` (a list of
  `{Title, Url, Children}` entries), and `Ancestors` (a list of `{Title,
  Url}` breadcrumb entries).

## Honest outcomes

| Condition | Outcome | Output written? |
|---|---|---|
| Page or chrome folder missing a required file | `Unavailable` | No |
| Page content is empty | `Empty` | No |
| Chrome present but missing logo, ancestors, and/or navigation | `Partial` (missing parts named) | Yes |
| Full chrome and content present | `Observed` | Yes |

A missing logo is never replaced with a placeholder image, and missing
ancestors/navigation never fabricate breadcrumb or menu entries -- the
preview is built from exactly what is on disk, and every gap is named in the
outcome detail so a reviewer can see what is missing.

## No tenant writes

This skill only reads the two folders it is given and writes the one output
file it is given (or `full-preview.html` inside the page folder, by
default). It performs no network calls and no SharePoint/tenant I/O of any
kind.

## Usage

```bash
python3 scripts/preview_composition.py \
  --page-folder ./destination/My-Page \
  --chrome-folder ./site-chrome/Example \
  --output ./destination/My-Page/full-preview.html
```

If `--output` is omitted, the preview is written to `full-preview.html`
inside the page folder.

## Scripts

- `scripts/preview_composition.py` -- CLI entry point
- `scripts/outcomes.py` -- shared status vocabulary

## Provenance

Adapted from a component of `sp-running-sharegate-jobs` in the originating
SharePoint migration repository. That skill otherwise depends on a
commercial migration tool; this component was independently verified to
have zero calls into it and zero live-tenant I/O, and was extracted here on
that basis. See
`docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md`.

