---
name: presentation-decks
description: Use when creating, opening, or editing LibreOffice Impress ODP presentations, or PPTX decks only when PowerPoint compatibility is explicitly required.
version: "1.1.0"
author: "Agent Zero Core Team"
tags: ["presentation", "odp", "opendocument", "pptx", "powerpoint", "slides", "deck", "impress"]
triggers:
  - "Impress"
  - "ODP"
  - "odp"
  - "OpenDocument Presentation"
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

# Impress Presentations

Use ODP when the user asks for a presentation, slides, a deck, or an Impress artifact. Use PPTX only when the user asks for PowerPoint/PPTX compatibility or provides an existing `.pptx`.

The canvas is user-owned UI. Creating or editing an ODP or PPTX must save the deck and return action buttons, but must not open the canvas automatically. Use Desktop/Impress only for explicit GUI requests, visual layout polish, or final visual confirmation.

## Workflow

Create:

```json
{
  "tool_name": "document_artifact:create",
  "tool_args": {
    "kind": "presentation",
    "title": "Roadmap",
    "format": "odp",
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
- Treat PPTX as a compatibility export/request, not the default presentation format.
- Do not open Impress/canvas automatically. The user can choose Open in canvas when they want to inspect or polish the deck visually.
