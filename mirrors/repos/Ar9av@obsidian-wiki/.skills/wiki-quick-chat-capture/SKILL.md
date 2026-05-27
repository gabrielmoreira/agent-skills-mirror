---
name: wiki-quick-chat-capture
description: >
  Fast, zero-friction capture of technical findings from the current conversation to the wiki's
  _raw/ staging area. Use this skill when the user says "/wiki-quick-chat-capture", "quick capture",
  "capture this finding", "save this bug fix", "capture this gotcha", "drop this to raw",
  "quick save to wiki", or wants to capture a non-obvious discovery mid-session without a full
  wiki-ingest run. Writes one _raw/ file per topic cluster in under 60 seconds — no subagents,
  no QMD updates, no manifest writes. Run /wiki-ingest or /data-ingest later to promote raw
  files to proper wiki pages.
compatibility: Requires ~/.obsidian-wiki/config or OBSIDIAN_VAULT_PATH env var. qmd CLI optional.
metadata:
  version: "1.0"
allowed-tools: Bash Read Write
---

# Wiki Quick Chat Capture

Extract reusable technical findings from the current conversation and stage them in `_raw/` for
later promotion. The goal is zero-friction capture of discoveries that would otherwise be lost
when the session ends.

**Speed contract:** Inline only. No subagents. No QMD. No manifest writes. Target: <60 seconds.

## When to Use This Skill

Right tool when:
- The user just hit a non-obvious bug or confirmed a framework gotcha mid-session
- There's a concrete finding worth keeping but a full `/wiki-ingest` run would be too disruptive
- The user wants to offload the knowledge now and defer promotion to end-of-day

NOT a replacement for `wiki-capture` (promotes directly to a final wiki page) or
`wiki-ingest` (full document ingestion with cross-links and manifest tracking).

## Before You Start

1. **Resolve config** — follow the Config Resolution Protocol in `llm-wiki/SKILL.md` (walk up
   CWD for `.env` → `~/.obsidian-wiki/config` → prompt setup). Extract:
   - `OBSIDIAN_VAULT_PATH`
   - `OBSIDIAN_RAW_DIR` (default: `$OBSIDIAN_VAULT_PATH/_raw`)
2. Ensure `$OBSIDIAN_RAW_DIR` exists. If not, create it.

## Step 1: Scan the Conversation for Findings

Extract **reusable technical knowledge** — things worth having in 3 months with no memory of
this session.

**Capture:**
- Non-obvious bugs and their root causes
- Framework or library gotchas (undocumented behavior, edge cases)
- API behavior that surprised the user
- Workarounds or fixes that required investigation
- Environment/toolchain quirks
- Patterns that emerged from debugging or testing

**Skip:**
- Project management updates, roadmap changes, config already in CLAUDE.md
- Exploratory back-and-forth where no conclusion was reached
- Things obvious from the docs or boilerplate any developer finds on first read
- Pleasantries, meta-conversation, status updates

If nothing material emerged, tell the user and stop.

## Step 2: Cluster by Topic

Group related findings — one raw file per topic cluster, not per individual finding.

Examples: "Swift 6 concurrency gotchas", "Next.js hydration edge cases", "Postgres advisory locks".

Name each cluster as a kebab-case slug: `swift-actor-reentrancy`, `nextjs-hydration-mismatch`.

## Step 3: Infer Project Context

Check the conversation for clues — repo names, file paths, framework mentions, error messages.
Use the most specific project name you can reliably infer. If unclear, use `null`.

## Step 4: Write Raw Files

For each cluster, write `$OBSIDIAN_RAW_DIR/<ISO-date>-<slug>.md`.

Read `references/RAW-FORMAT.md` for the full frontmatter spec, body structure (finding block
format), and the provenance/confidence calibration table.

Quick reference for frontmatter fields that vary per cluster:
- `title` — descriptive cluster title
- `tags` — 2–4 domain tags matching the vault taxonomy
- `summary` — 1–2 sentences, ≤200 chars
- `project` — inferred project name or `null`
- `base_confidence` — 0.6 (discussed, unconfirmed) → 0.75 (fix applied) → 0.9 (test confirmed)
- `provenance.extracted` / `provenance.inferred` — must sum to 1.0
- `lifecycle_changed` — today's ISO date
- `sources` — `"<project> session (<YYYY-MM-DD>)"`

## Step 5: Confirm to User

```
Staged to _raw/:
  _raw/2026-05-27-swift-actor-reentrancy.md   — "Actor reentrancy causes deadlock in async forEach"
  _raw/2026-05-27-xcode-derived-data-cache.md — "Stale derived data silently breaks incremental builds"

Run /wiki-ingest (or /data-ingest) to promote these to full wiki pages.
```

If nothing was captured: "Nothing worth capturing found in this session."

## What This Skill Does NOT Do

- No manifest writes — `_raw/` files are not tracked in `.manifest.json`
- No `index.md`, `log.md`, or `hot.md` updates — those happen during promotion
- No QMD refresh — raw files are drafts, not indexed content
- No subagents — everything runs inline in this context window

These constraints are intentional. Speed is the point. Promotion via `/wiki-ingest` handles
all of the above when the user is ready.
