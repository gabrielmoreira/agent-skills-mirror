---
type: instruction
lifecycle: stable
inheritance: inheritable
description: "Markdown to email (.eml) conversion with preview support"
application: "When converting Markdown files to email format"
applyTo: "**/*eml*,**/*email*convert*"
currency: 2026-04-22
lastReviewed: 2026-01-01
---

# Markdown to Email Conversion

Auto-loaded for email conversion requests.

Full protocol in `.github/skills/md-to-eml/SKILL.md`.

## Quick Reference

| Option | Usage |
|--------|-------|
| `--test` | Override recipients for safe preview |
| `--test-to EMAIL` | Custom test recipient |
| `--inline-images` | Embed images as CID attachments |
| `--debug` | Save intermediate HTML |
