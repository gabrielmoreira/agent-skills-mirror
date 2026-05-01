---
name: zotero-obsidian-bridge
description: Use this skill when Zotero is the literature source of truth and the project KB should receive source notes under Sources/Papers plus project-linked synthesis in Knowledge and Writing.
version: 0.3.0
---

# Zotero Obsidian Bridge

Use this skill when papers live in Zotero and the project KB should receive project-local notes.

Default flow:

```text
Zotero -> Sources/Papers -> Knowledge -> Writing -> Maps/literature.canvas
```

Rules:
- one canonical paper note per paper under `Sources/Papers/`
- literature synthesis goes to `Knowledge/`
- writing-oriented outputs go to `Writing/`
- `Maps/literature.canvas` is the default derived graph artifact
- update `_system/registry.md`, `02-Index.md`, and today's `Daily/` after substantial ingestion
