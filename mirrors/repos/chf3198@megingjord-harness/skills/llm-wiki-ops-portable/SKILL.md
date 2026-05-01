---
name: llm-wiki-ops-portable
description: Operate an LLM Wiki knowledge system in any workspace using the Karpathy pattern
---

# llm-wiki-ops-portable — Portable Wiki Operations

## Purpose
Teach any agent consumer how to create, search, and grow an
LLM Wiki in their own workspace. Based on the Karpathy LLM
Wiki pattern: concepts, sources, entities, syntheses.

## Wiki Structure
```
wiki/
  index.md              # Master page index
  log.md                # Chronological change log
  concepts/             # Distilled ideas (agent-written)
  sources/              # Summarized external material
  entities/             # Named things (tools, services)
  syntheses/            # Cross-cutting analysis
```

## Getting Started
1. Create `wiki/` at your workspace root
2. Add `wiki/index.md` with a page registry
3. Add `wiki/log.md` for change tracking
4. Start with concepts — write what you know

## Page Format
Every wiki page uses this structure:
```markdown
# Page Title
## Summary (2-3 sentences)
## Details (body content)
## Related (wikilinks to other pages)
## Sources (external references)
```

## Adding Content

### Concepts
Distilled knowledge written by the agent after research.
One idea per page. Name: `wiki/concepts/<slug>.md`

### Sources
Summarized external material (articles, docs, papers).
One source per page. Name: `wiki/sources/<slug>.md`

### Entities
Named things: tools, services, platforms, people.
Name: `wiki/entities/<slug>.md`

### Syntheses
Cross-cutting analysis combining multiple concepts/sources.
Name: `wiki/syntheses/<slug>.md`

## Searching
Search the wiki with keyword matching across all pages:
```bash
grep -rli "search term" wiki/
```
For richer search, use a workspace search tool or semantic
search across the wiki directory.

## Growing the Wiki
1. After research tasks, create source pages
2. When patterns emerge, create concept pages
3. When concepts connect, create synthesis pages
4. Update `wiki/index.md` after adding pages
5. Log changes in `wiki/log.md`

## Seed Content
This plugin ships ~15 seed articles in `wiki/` covering
agent governance patterns. See `wiki/.seed-manifest.json`
for the universal seed article inventory.

## Constraints
- One topic per page
- Keep pages concise (aim for ≤100 lines)
- Use wikilinks `[[page-name]]` for cross-references
- Index and log are the source of truth for page inventory
