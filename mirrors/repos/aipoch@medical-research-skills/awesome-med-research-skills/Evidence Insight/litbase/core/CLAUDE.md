# LitBase

Academic paper reading and research development system for biomedical researchers. Runs inside Claude Code. Three core functions: **find papers, analyze papers, build a research foundation**.

---

## Available Commands

| Command | Function |
|---------|----------|
| `/setup` | First-time setup: guided research profile, auto-environment configuration, generates MEMORY.md / search_config.json / reading_list.md |
| `/feed` | Paper recommendations: update search terms → search Semantic Scholar → filter and rank → list open-access PDFs |
| `/read` | Deep paper analysis: 4-section structured note (Paper Weight / Highlights / Transferable Elements / How to Use), saved to data directory |
| `/discuss [keyword]` | Paper discussion: locate a note by author surname, year, or title keyword; auto-records valuable insights to the note file |
| `/recap` | Reading progress: overview by theory layer, framework completeness map, next-step recommendations, saves snapshot to recaps/ |
| `/update` | Research direction changed: sync updates to MEMORY.md and search_config.json |
| `/sync` | Consistency and integrity check: audit all command and document files, fix format issues, flag logic conflicts, run literature integrity scan |
| `/propose` | Research Foundation Document: synthesizes all reading notes into a structured RFD (P/E/C/O/D/T) for downstream protocol design skills |

---

## Literature Integrity

@references/LITERATURE_HARD_RULES.md

All commands must follow the rules in `LITERATURE_HARD_RULES.md`. Key points:
- Never fabricate PMIDs, DOIs, author names, citation counts, impact factors, or study findings.
- All citations in notes and RFDs must be traceable to a paper in `reading_list.md` marked `[x]`.
- Unverifiable claims must be labeled explicitly. Do not omit silently.

---

## File Structure

```
core/                      ← open this folder in Claude Code
  config.json              ← the only file users need to manually edit (set data_dir)
  search_config.json       ← Semantic Scholar search terms, maintained by Claude during /feed
  settings.local.json      ← Claude Code permissions template
  install.sh               ← optional manual setup script
  commands/                ← skill command files (symlinked to .claude/commands/ by /setup)
  references/
    LITERATURE_HARD_RULES.md  ← citation integrity rules (auto-loaded)
    SESSION_CARD_TEMPLATE.md  ← state template for Web Claude (Tier A) users
  scripts/
    recommend.py           ← optional: paper search script (accelerates /feed on Tier C)
    lookup_paper.py        ← optional: paper metadata query (accelerates /read on Tier C)
    rename_pdfs.py         ← optional: PDF batch rename to Author_Year_Keywords.pdf
  memory/MEMORY.md         ← Claude's persistent memory

data_dir/                  ← path set in config.json (store PDFs here)
  notes/
    reading_list.md        ← reading tracker with categories
    recaps/
      YYYY-MM-DD_recap.md
    proposal/
      YYYY-MM-DD_RFD.md
    YYYY-MM-DD/
      recommendations.md
      Author_Year_Keywords/
        Author_Year_Keywords.pdf
        Author_Year_Keywords.md
```

---

## Core Rules

**File writes**: All file operations during command execution (writing notes, updating reading_list.md, writing recommendations.md, updating search_config.json, updating MEMORY.md) are executed **directly without asking the user for confirmation**. Steps marked "auto-execute" or "no user prompt" in command files follow this rule.

**Paths**: All paths are derived from `data_dir` in `config.json`. Scripts use `os.path.dirname(__file__)` to locate themselves. No hardcoded absolute paths anywhere.

**After analyzing any paper — auto-sync silently:**
1. `reading_list.md` — add `[x]` entry with relative link (`YYYY-MM-DD/Name/Name.md`, relative to `notes/`)
2. `search_config.json` `based_on_notes` — add note filename; sliding window max 25
3. `MEMORY.md` `Reading Progress` — append one line; sliding window max 20
4. Create dated folder, copy PDF, save MD — all in one step

**First use**: Open this folder in Claude Code and type `/setup`. No terminal commands required. The setup command configures everything automatically.

---

## Capability Tiers

Commands detect the runtime environment and adapt:
- **Tier C** (OpenClaw / Claude Code): full file system + bash + optional Python
- **Tier B** (Manus, file-capable agents): file read/write, no bash required
- **Tier A** (Web Claude): no file system; notes as Artifacts; state via Session Card

---

## Document Sync Rule (auto-execute, no reminder needed)

After adding or modifying any file in `commands/`, immediately update:
1. **README.md** — command table
2. **CLAUDE.md** (this file) — command table
3. **SKILL.md** — command list in description and body table
4. **notes/WORKFLOW.md** — quick-reference command table

Also verify:
- Path conventions are consistent across all commands (`data_dir`, `notes_dir`)
- Auto-sync rules (reading_list / search_config / MEMORY.md) are described identically across all commands that trigger them
- No logic conflicts between commands
