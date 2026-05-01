---
name: obsidian-literature-workflow
description: Use this skill for project-scoped literature review built on Sources/Papers, with synthesis landing in Knowledge, writing handoff in Writing, and the default literature canvas under Maps/literature.canvas.
version: 1.0.0
---

# Obsidian Literature Workflow

This skill owns the **project literature workflow**.

## Main flow

```text
Sources/Papers/ -> Knowledge/ -> Writing/ -> Maps/literature.canvas
```

## Default outputs

- `Sources/Papers/{paper-slug}.md`
- `Knowledge/Literature Overview.md`
- `Knowledge/Method Taxonomy.md`
- `Knowledge/Research Gaps.md`
- `Knowledge/Claim Map.md`
- `Writing/related-work-draft.md`
- `Writing/comparison-matrix.md`
- `Maps/literature.canvas`

## Rules

- paper notes stay under `Sources/Papers/`
- literature synthesis does not live inside source notes
- every synthesis note must link its supporting source notes
- every research gap must carry evidence
- default graph output is `Maps/literature.canvas`
- do not generate extra canvases unless explicitly requested

## Read next

- `references/PAPER-NOTE-SCHEMA.md`
- `references/LITERATURE-OVERVIEW.md`
- `references/CLAIM-EXTRACTION.md`
- `references/METHOD-TAXONOMY.md`
- `references/RESEARCH-GAPS.md`
- `references/LITERATURE-CANVAS.md`
