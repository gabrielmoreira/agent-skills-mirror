---
name: litbase
description: "Academic paper reading and research development system for biomedical researchers. Finds papers via Semantic Scholar, reads with structured notes, tracks discussion insights, and synthesizes literature into a Research Foundation Document (RFD) for downstream protocol design skills. 8 commands: /setup /feed /read /discuss /recap /update /sync /propose"
license: MIT
author: AIPOCH
metadata:
  openclaw:
    optional_bins:
      - python      # optional: accelerates paper search if available; falls back to inline WebFetch calls
      - pdftotext   # optional: accelerates PDF text extraction if available; falls back to Claude native PDF reading
  capability_tiers:
    tier_a: "Conversation mode — Web Claude or any LLM chat interface; no file system; notes output as Artifacts; state maintained via session card"
    tier_b: "File mode — Manus or any file-capable agent; file read/write available; no Python/bash required"
    tier_c: "Full mode — OpenClaw / Claude Code; full file system, bash, and optional Python acceleration"
  downstream_skills:
    - clinical-cohort-protocol-designer
    - translational-study-blueprint
    - statistical-analysis-plan-writer
    - protocol-writer
---

# LitBase

An academic paper reading and research development system running inside Claude Code (or any compatible agent environment). Built for **biomedical researchers** who want to find papers, build structured reading notes, track discussion insights, and ultimately synthesize their literature base into a research proposal.

Paper source: [Semantic Scholar](https://www.semanticscholar.org) — free, no login required, 200M+ papers across all disciplines.

---

## Quick Start

**Step 1** — Edit `config.json` with your research folder path:

```json
{
  "data_dir": "/path/to/your/research/folder",
  "s2_api_key": "optional — leave empty to use free tier",
  "mode": "auto"
}
```

**Step 2** — Open this folder in Claude Code, then type `/setup`.

The setup command configures everything automatically — no terminal commands needed.

---

## Commands

| Command | When to use | What it does |
|---------|------------|--------------|
| `/setup` | First use | Guided research profile setup; auto-configures environment |
| `/feed` | Daily | Updates search terms → searches Semantic Scholar → recommends papers |
| `/read` | Per paper | Submit a PDF path, DOI, or abstract → generates 4-section structured note |
| `/discuss [keyword]` | Deep dive | Locate a paper note by author/title/keyword and discuss; auto-records insights |
| `/recap` | Weekly review | Reading overview, framework completeness map, next-step recommendations |
| `/update` | Direction shift | Sync research direction changes to memory and search terms |
| `/sync` | Maintenance | Cross-document consistency check; literature integrity audit |
| `/propose` | Proposal stage | Synthesizes reading notes into a Research Foundation Document (RFD) for downstream protocol design |

---

## Note Structure

Each paper analysis is structured in four sections:

| Section | Content |
|---------|---------|
| **I. Paper Weight** | Journal/conference rank, IF, database indexing (SSCI/Scopus/etc.), Q-rank; each author's institution, position, h-index; citation count and yearly average; overall assessment |
| **II. Paper Highlights** | Methodological innovation / critique of systemic problems / significance of the research object |
| **III. Transferable Elements** | Theory framework, method details, conceptual tools — each tagged to which part of the user's own paper it can support |
| **IV. How to Use in Your Paper** | Literature review positioning, suggested citation phrases (English), methodological precedent, research motivation |

---

## Research Foundation Document (RFD)

The `/propose` command generates an RFD — a structured synthesis of the user's accumulated literature base. It serves as a standardized upstream input to any downstream protocol design skill.

RFD sections: Study Population & Clinical Context → Focused Research Question (P/E/C/O/D/T) → Theoretical Framework & Mechanistic Basis → Methodological Precedents → Identified Research Gaps → Literature Source Index.

All citations in the RFD are sourced exclusively from the user's confirmed reading list. No fabricated references.

---

## Capability Tiers

LitBase adapts to its runtime environment automatically:

| Tier | Environment | PDF reading | Paper search | Notes storage | State persistence |
|------|------------|-------------|--------------|--------------|-------------------|
| A | Web Claude, any LLM chat | Native upload | WebSearch / WebFetch | Artifact output | Session card (paste at session start) |
| B | Manus, file-capable agents | Claude Read tool | WebFetch → S2 API | File system | MEMORY.md |
| C | OpenClaw / Claude Code | Claude Read tool (+ optional pdftotext) | WebFetch → S2 API (+ optional Python) | File system | Claude persistent memory |

---

## Dependencies

| Dependency | Purpose | Required? |
|-----------|---------|-----------|
| Python (stdlib) | Runs paper search and metadata scripts | Optional — WebFetch fallback available |
| pdftotext (poppler) | PDF text extraction | Optional — Claude native PDF reading available |
| Claude Code | Executes skill commands | Required for Tier C |

No API key required for Semantic Scholar. An optional free key raises rate limits.

---

## Literature Integrity

All commands follow the rules in `LITERATURE_HARD_RULES.md`:
- No fabricated PMIDs, DOIs, titles, authors, citation counts, or study data.
- All citations in notes and proposals must be traceable to user-provided papers.
- Unverifiable claims are labeled explicitly rather than omitted silently.

---

## File Structure

```
litbase/
├── SKILL.md                        ← skill manifest (this file)
└── core/                           ← open this folder in Claude Code
    ├── CLAUDE.md                   ← project rules (auto-loaded)
    ├── README.md
    ├── config.json                 ← user config (data_dir, API key, mode)
    ├── search_config.json          ← search terms (maintained by Claude)
    ├── settings.local.json         ← Claude Code permissions template
    ├── install.sh                  ← optional manual setup script
    ├── commands/
    │   ├── setup.md
    │   ├── feed.md
    │   ├── read.md
    │   ├── discuss.md
    │   ├── recap.md
    │   ├── update.md
    │   ├── sync.md
    │   └── propose.md
    ├── references/
    │   ├── LITERATURE_HARD_RULES.md
    │   └── SESSION_CARD_TEMPLATE.md
    ├── scripts/
    │   ├── recommend.py            ← optional: Semantic Scholar search
    │   ├── lookup_paper.py         ← optional: paper metadata query
    │   └── rename_pdfs.py          ← optional: PDF batch rename
    ├── memory/
    │   └── MEMORY.md
    └── notes/
        └── WORKFLOW.md

data_dir/                           ← path set in config.json
  notes/
    reading_list.md
    YYYY-MM-DD/
      recommendations.md
      Author_Year_Keywords/
        Author_Year_Keywords.pdf
        Author_Year_Keywords.md
    recaps/
      YYYY-MM-DD_recap.md
    proposal/
      YYYY-MM-DD_RFD.md
```
