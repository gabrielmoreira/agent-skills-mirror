---
description: 'Research the codebase for a Issue — find existing patterns, affected files, risks, and context before planning begins. Requires Phase 1 (Discuss) to be complete.'
agent: 'Research'
---
# Phase 2 — Codebase Research

**Issue doc**: ${input:issue-doc:Path to Issue doc (e.g., docs/issues/ISSUE-042-name.md)}

## Step 1 — Read the Issue doc

Open `${input:issue-doc}` and read Phase 1 requirements.

> If Phase 1 is NOT marked `[x] complete` → **STOP**.
> Say: *"Phase 1 (Discuss) must be complete before research. Run `/discuss` first and agree on requirements."*

## Step 2 — Explore the codebase

Based on what's being built, investigate:

- **Files that will likely change** — trace from the entry point inward
- **Existing patterns to reuse** — how is similar functionality already built?
- **Related services and middleware** — what dependencies exist?
- **Database schemas involved** — what tables, columns, indices?
- **Existing tests that may need updating** — which test files cover affected code?
- **Relevant flow docs** in `docs/flows/` — what user journey does this touch?
- **Relevant API docs** in `docs/apis/` — what endpoints are involved?

## Step 3 — Write research findings into Issue doc Phase 2

Format your findings as:

```
## Research Findings (Phase 2)

**Files to modify:**
- `src/[path]` — [reason]

**Existing patterns to follow:**
- [Pattern name]: `src/[path]` (use same style)

**Related schemas:**
- [table]: `src/db/schema/[file]`

**Risks identified:**
- [specific risk or edge case]

**No-go zones:**
- [files/patterns to avoid]
```

## Step 4 — Hand off to Planner

After writing findings, present a guided next step to Planner.
The Planner needs these research notes to create a grounded implementation plan.

Use this exact transition guidance:
- Primary: click **Open Planner →** handoff button
- Fallback: run `/plan` manually with the same issue/work context

Do not force automatic send. The developer remains in control of when planning starts.
