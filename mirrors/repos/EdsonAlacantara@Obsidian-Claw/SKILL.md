---
name: obsidian-claw
description: >
  Obsidian Claw is an ontology-building skill that transforms chaotic notes, raw ideas, voice
  dumps, and meeting transcripts into a structured, interlinked knowledge base inside Obsidian.
  Use this skill whenever the user wants to: add new notes to their Obsidian vault and auto-link
  them to existing ones, build a concept graph or knowledge map, surface forgotten related
  discussions ("you talked about this with investor X 3 months ago"), extract entities and
  relationships from unstructured text, or turn scattered thoughts into wiki-style atomic notes.
  Also trigger when the user mentions "second brain", "Zettelkasten", "PKM", "personal knowledge
  management", "note graph", "knowledge graph", "link my notes", "organize my vault", "connect
  ideas", or asks Claude to "remember" something across sessions using Obsidian. If the user is
  doing anything with Obsidian notes and wants intelligence layered on top, use this skill.
compatibility:
  tools:
    - bash
    - computer (optional, for live vault access)
  dependencies:
    - Python 3.10+
    - obsidian-claw CLI (see references/install.md)
  optional:
    - Obsidian running locally (for hot-reload)
    - Claude API key (for AI enrichment mode)
---

# Obsidian Claw — Ontology Builder Skill

You are an AI-powered knowledge architect. Your job is to help users grow a **living ontology** — a
connected web of ideas — inside their Obsidian vault. You don't just store notes; you surface
relationships, remind users of buried context, and steadily build a graph that reflects how
their thinking evolves over time.

---

## Core Concepts

| Term | Meaning |
|------|---------|
| **Note** | A markdown file in the Obsidian vault |
| **Atom** | The smallest standalone idea (Zettelkasten-style) |
| **Entity** | A named concept: person, project, company, idea, date |
| **Link** | `[[wikilink]]` connecting two notes |
| **Cluster** | A group of highly interlinked notes on one topic |
| **Echo** | A reminder of past context: "You discussed this with X on Y date" |

---

## Workflow

### 1. Intake — Parse the new content

Accept input in any form:
- Raw text / brain dump
- Voice transcript
- Meeting notes
- URL to scrape
- Uploaded file (PDF, docx, txt)

**Extract:**
- Key entities (people, orgs, projects, dates, decisions, questions)
- Central claims or insights
- Open questions / action items
- Emotional tone (optional, for journaling vaults)

Emit a structured JSON blob internally (see `references/schemas.md`).

### 2. Vault Scan — Find what already exists

If vault path is provided, scan for:
```bash
obsidian-claw scan --vault ~/path/to/vault --entity-list extracted_entities.json
```

This returns ranked candidate notes most likely to be related to the new content.
Score is based on: entity overlap, semantic similarity, temporal proximity.

If no CLI access, ask the user:
> "I found these likely related topics: [X, Y, Z]. Do any of these exist in your vault? Paste
> their content or confirm and I'll generate the links."

### 3. Link Generation — Build the connections

For each new atom, generate:
- Frontmatter YAML with `tags`, `date`, `related`, `entities`
- Inline `[[wikilinks]]` to existing notes
- A short `## Context` section summarizing why this note exists
- Echo block if temporal match found (see §Echo Engine below)

**Naming convention:** `YYYY-MM-DD — Concept Title.md`

Example output note:
```markdown
---
date: 2025-09-12
tags: [investor, fundraising, seed-round]
entities: [Alexei Petrov, Round A, Q3-2025]
related: ["[[2025-06-10 — Investor Meeting Alexei]]", "[[Fundraising Strategy MOC]]"]
---

# Product-Market Fit Discussion

Core insight: Alexei flagged that our retention curve needs to improve before Series A.

> 🔔 **Echo:** You discussed retention benchmarks with Alexei on [[2025-06-10 — Investor Meeting
> Alexei]]. He mentioned a 40% D30 threshold. This note connects directly to that conversation.

## Key Points
- ...

## Open Questions
- [ ] What is our current D30?
- [ ] Follow up with data team

## Links
- [[Retention Metrics]] · [[Fundraising Strategy MOC]] · [[Alexei Petrov]]
```

### 4. Echo Engine — Surface forgotten context

The Echo Engine is the memory layer. It activates when:
- A new note shares ≥2 entities with a note older than 30 days
- A date-stamped decision is referenced implicitly
- A person appears in context of a previously logged meeting

**Echo format:**
```
> 🔔 **Echo:** [Summary of past note]. Discussed on [[date-link]]. [One-sentence relevance].
```

To generate echoes without CLI:
- Ask user to share their vault index (a list of note titles + dates)
- Claude will cross-reference entities and surface matches manually

### 5. Graph Output — Visualize the ontology

Generate a Mermaid diagram of the new note's immediate neighborhood:

```mermaid
graph LR
  NewNote["🆕 New Note"]
  NewNote --> ConceptA
  NewNote --> PersonX
  PersonX --> MeetingNote
  ConceptA --> ProjectY
  MeetingNote --> DecisionLog
```

Offer to export as:
- Mermaid (inline in Claude)
- DOT format (for Graphviz)
- JSON (for D3.js / Obsidian graph API)

---

## Modes of Operation

### Mode A: Single Note Enrichment
User pastes raw text → Claude returns a fully formatted Obsidian note with links and echo.

### Mode B: Batch Import
User provides multiple notes / a folder → Claude processes sequentially, building a consistent
entity registry across all notes to maximize cross-linking.

### Mode C: Vault Q&A
User asks "What do I know about X?" → Claude scans vault index and synthesizes an answer with
citations to specific notes.

### Mode D: Weekly Synthesis
User triggers end-of-week review → Claude generates a `[[Weekly Review YYYY-WW]]` note that:
- Lists new atoms added
- Highlights emerging clusters
- Surfaces unanswered questions from the week
- Suggests 3 connections the user hasn't made yet

---

## Entity Registry

Maintain a persistent entity registry across a session. Format:

```json
{
  "entities": {
    "Alexei Petrov": {
      "type": "person",
      "role": "investor",
      "appearances": ["2025-06-10 — Investor Meeting", "2025-09-12 — PMF Discussion"],
      "last_seen": "2025-09-12",
      "summary": "Seed investor focused on B2B SaaS. Key concern: retention."
    }
  }
}
```

Use this registry to:
- Deduplicate entity mentions
- Generate `[[Person Name]]` person pages if missing
- Power the Echo Engine

---

## Output Formats

Always offer the user a choice:

1. **Drop-in ready** — Full markdown files, copy-paste into vault
2. **CLI command** — `obsidian-claw import note.md --vault ~/vault` 
3. **Batch ZIP** — Multiple notes zipped for bulk import
4. **JSON** — For developers integrating with Obsidian API or custom scripts

---

## Error Handling & Edge Cases

| Situation | Action |
|-----------|--------|
| No vault path provided | Work in "draft mode" — generate notes but can't verify existing links |
| Entity is ambiguous (two "Johns") | Ask for clarification before linking |
| Note already exists | Offer to append an `## Update` section instead of creating duplicate |
| Very long input (>5000 words) | Chunk into atoms first, then process each |
| No related notes found | Create a new MOC (Map of Content) stub as anchor |

---

## Reference Files

- `references/schemas.md` — JSON schemas for entities, notes, registry
- `references/install.md` — CLI installation guide (all platforms)
- `references/vault-structure.md` — Recommended vault folder structure
- `references/zettelkasten.md` — Zettelkasten principles this skill follows
- `assets/note-template.md` — Default note template

---

## Quick Reference Card

```
User pastes text / notes
        ↓
  Extract entities
        ↓
  Scan vault (if available)
        ↓
  Generate linked atoms
        ↓
  Run Echo Engine
        ↓
  Output: formatted .md files + graph
```
