---
name: pptx
version: "1.0"
description: Extract text from Microsoft PowerPoint presentations
entry:
  script: scripts/main.py
  class: PptxSkill
triggers:
  extensions:
    - ".pptx"
  intents:
    - "powerpoint"
    - "presentation"
    - "pptx"
requires:
  - python-pptx
author: axoviq.com
license: AGPL-3.0-or-later
---

# PPTX Skill

Extracts text from `.pptx` files using `python-pptx`. Each slide is rendered as a titled section; speaker notes are appended when present.

## When this skill is used

- Source path ends with `.pptx`
- User intent contains: `powerpoint`, `presentation`, `pptx`
