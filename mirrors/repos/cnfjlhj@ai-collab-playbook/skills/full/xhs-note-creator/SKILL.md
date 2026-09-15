---
name: xhs-note-creator
description: Use when the user wants Xiaohongshu note materials such as the note text, cover card, body cards, or publishing-ready assets. Do not use this for generic social copywriting or image generation when the deliverable is not a Xiaohongshu post package.
---

# XHS Note Creator

## Overview

Create Xiaohongshu note packages: note copy, renderable card Markdown, cover and body images, and optional publishing steps. This skill is for post-ready assets, not just short-form caption writing.

Use it when the platform and deliverable are clearly Xiaohongshu-specific. Reuse the bundled render and publish tooling instead of re-explaining the entire production process in chat.

## Rules

- Keep the task Xiaohongshu-specific: title, body style, cards, and publish flow should all fit the platform.
- Separate note copy from card-render Markdown; they are related but not identical artifacts.
- Reuse bundled scripts and assets for rendering or publishing when the user wants execution.
- Keep titles, subtitles, and card content short enough for mobile reading.
- If the user only wants copy ideas, do not force card rendering or publishing.
- Treat publishing as an account-affecting action: confirm the intended visibility and scope before execution.
- Default to private visibility and use `--public` only after explicit confirmation.
- Never commit or expose `.env`, cookies, generated debug responses, or browser profiles.

## When to Use

Use when:

- the user wants to create a Xiaohongshu note
- source material should become Xiaohongshu-style copy plus card assets
- the deliverable includes cover cards, body cards, or renderable Markdown for Xiaohongshu
- the user wants help publishing a finished Xiaohongshu note package

Do not use when:

- the task is generic marketing copy or another platform's post
- the user only wants a single image or a plain article
- the deliverable is not Xiaohongshu-specific
- the user is still brainstorming the topic and does not need note assets yet

## Bundled Resources

- primary renderer: `scripts/render_xhs.py`
- alternate renderers: `scripts/render_xhs_v2.py`, `scripts/render_xhs.js`, `scripts/render_xhs_v2.js`
- publisher: `scripts/publish_xhs.py`
- templates and styles: `assets/`, `STYLES.md`
- setup and usage: `README.md`
- full parameter reference: `references/params.md`

## Output Modes

- note text only
- note text plus renderable card Markdown
- full asset package with rendered images
- publish-ready package when execution is explicitly requested
