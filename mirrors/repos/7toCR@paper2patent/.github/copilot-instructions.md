# GitHub Copilot Instructions

This repository maintains Paper2Patent prompt templates and AI agent skills for converting academic papers into Chinese invention patent application drafts.

## Working Rules

- Use `skills/paper2patent/SKILL.md` as the main workflow for paper-to-patent tasks.
- Keep detailed drafting rules in `skills/paper2patent/references/`.
- Preserve source-paper fidelity: do not invent technical features, embodiments, datasets, effects, or application scenarios.
- Do not commit unpublished papers, generated patent drafts, personal data, API keys, tokens, local usernames, or local absolute paths.
- Keep Markdown UTF-8 and follow the existing Chinese patent terminology.

## Validation

After changing skill content, run the skill validator for `skills/paper2patent` and check whitespace with `git diff --check`. On Windows, set `PYTHONUTF8=1` before validating UTF-8 Chinese Markdown.
