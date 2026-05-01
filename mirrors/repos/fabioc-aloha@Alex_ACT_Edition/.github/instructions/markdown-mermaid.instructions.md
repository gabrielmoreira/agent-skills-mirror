---
type: instruction
lifecycle: stable
inheritance: inheritable
description: "Markdown and Mermaid — author markdown, render diagrams, prevent silent failures, lint clean, sanitize user content"
application: "When creating or editing markdown or Mermaid diagrams"
applyTo: "**/*.md,**/*mermaid*"
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Markdown & Mermaid — Routing

Multiple skills cover this domain. Pick the one that matches the work — they don't overlap.

| When working on | Use skill |
|---|---|
| Authoring markdown, choosing a diagram type, GitHub Pastel palette, ATACCU workflow | [markdown-mermaid](../skills/markdown-mermaid/SKILL.md) |
| Mermaid renders blank or garbled (timeline / gitGraph / gantt with colons) | [markdown-mermaid § Mode Fragility](../skills/markdown-mermaid/SKILL.md) |
| Writing markdown that has to pass `markdownlint` on first attempt | [lint-clean-markdown](../skills/lint-clean-markdown/SKILL.md) |
| Rendering user-supplied markdown in an app (XSS prevention) | [markdown-sanitization-chain](../skills/markdown-sanitization-chain/SKILL.md) |

`markdown-mermaid` is the primary reference (including the Mode Fragility section). The other two are gotcha-and-pattern specialists — load when their trigger fires.
