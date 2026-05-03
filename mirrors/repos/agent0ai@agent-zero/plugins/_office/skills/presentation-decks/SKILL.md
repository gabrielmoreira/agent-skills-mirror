---
name: presentation-decks
description: Use when creating, opening, or editing PowerPoint-compatible PPTX presentations, slide decks, talks, briefing decks, or LibreOffice Impress files.
version: "1.0.0"
author: "Agent Zero Core Team"
tags: ["presentation", "pptx", "powerpoint", "slides", "deck", "impress"]
triggers:
  - "PowerPoint"
  - "PPTX"
  - "pptx"
  - "presentation"
  - "slide deck"
  - "slides"
  - "deck"
  - "Impress"
allowed_tools:
  - document_artifact
---

# Presentation Decks

Use PPTX when the user asks for PowerPoint, a presentation, slides, a deck, or an Impress-compatible artifact.

The canvas is user-owned UI. Creating or editing a PPTX must save the deck and return action buttons, but must not open the canvas automatically. Use Desktop/Impress only for explicit GUI requests, visual layout polish, or final visual confirmation.

## Workflow

Create:

```json
{
  "tool_name": "document_artifact:create",
  "tool_args": {
    "kind": "presentation",
    "title": "Roadmap",
    "format": "pptx",
    "content": "Title Slide\n\n---\n\nNext Steps"
  }
}
```

Edit slides:

```json
{
  "tool_name": "document_artifact:edit",
  "tool_args": {
    "file_id": "abc123",
    "operation": "set_slides",
    "slides": [
      {"title": "Now", "bullets": ["Stabilize"]},
      {"title": "Next", "bullets": ["Polish"]}
    ]
  }
}
```

Practical rules:

- Use `slides` arrays for structured decks and `---` separators for simple text-to-slide creation.
- Keep slide text concise and scannable.
- Do not create ODP in this workflow.
- Do not open Impress/canvas automatically. The user can choose Open in canvas when they want to inspect or polish the deck visually.
