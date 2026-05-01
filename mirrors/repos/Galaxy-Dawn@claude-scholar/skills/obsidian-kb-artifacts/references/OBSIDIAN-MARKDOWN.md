# OBSIDIAN MARKDOWN

Use valid Obsidian-flavored Markdown for canonical project notes. Prefer readable notes first, then Obsidian-native structure.

## Core rules

- Keep a small frontmatter block at the top of canonical notes.
- Use `[[wikilinks]]` for vault-internal references and Markdown links only for external URLs.
- Use readable headings and short sections; avoid turning notes into raw dumps.
- Prefer Markdown tables only when the comparison is truly tabular.
- Keep system files and generated tables deterministic; keep human notes readable.

## Frontmatter and properties

Use frontmatter for stable metadata such as:

```yaml
---
type: knowledge
status: active
created: 2026-04-24
updated: 2026-04-24
tags:
  - research
  - active
aliases:
  - Alternative Note Name
---
```

Prefer simple scalar or list properties. Do not over-model note metadata unless the workflow needs it.

## Wikilinks

Common forms:

```md
[[Note Name]]
[[Folder/Note Name]]
[[Note Name|Display Text]]
[[Note Name#Heading]]
[[Note Name#^block-id]]
```

Use folder-qualified links when note names are ambiguous. Prefer links to canonical notes over duplicate notes.

## Embeds

Use embeds when the reader benefits from inline context, not just because the syntax exists.

```md
![[Note Name]]
![[Note Name#Heading]]
![[image.png|300]]
![[document.pdf#page=3]]
```

Avoid large embed chains that make notes hard to scan.

## Callouts

Use callouts to highlight information that benefits from visual separation:

```md
> [!note]
> Supporting detail.

> [!warning] Risk
> This assumption may break under domain shift.
```

Common types: `note`, `info`, `tip`, `warning`, `question`, `success`, `failure`, `quote`, `example`.

## Tables

Use tables for:
- comparison matrices
- experiment summaries
- compact registries meant for humans

Avoid tables for long prose or nested content.

## Tags and aliases

- Use tags sparingly and consistently.
- Use aliases when a note has a common alternate name or paper title variant.
- Do not rely on tags as the only navigation mechanism when wikilinks and index notes are clearer.
