# Claude Code Instructions

This repository publishes Paper2Patent prompt templates and AI agent skills for converting academic papers into Chinese invention patent application drafts.

## Project Skill

Use `.claude/skills/paper2patent/SKILL.md` when the task involves paper-to-patent conversion, claim drafting, patent specification drafting, patent drawing descriptions, or fidelity checks against a source paper.

## Repository Rules

- Keep generated patent drafts, unpublished papers, invention disclosures, and private user materials out of git.
- Do not add local machine paths, usernames, API keys, tokens, cookies, phone numbers, emails, addresses, or identity numbers to `skills/` or `.claude/skills/`.
- Keep skill instructions concise; move long drafting rules into `references/`.
- Preserve UTF-8 Markdown and the existing Chinese patent terminology.

## Validation

Run skill validation after changes:

```powershell
$env:PYTHONUTF8='1'; python <skill-creator>/scripts/quick_validate.py skills/paper2patent
$env:PYTHONUTF8='1'; python <skill-creator>/scripts/quick_validate.py .claude/skills/paper2patent
git diff --check
```
