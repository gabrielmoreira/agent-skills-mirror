---
name: controlflow-memory-hygiene
description: "Use when work spans many turns or phases and you need durable notes, active-objective tracking, or context compaction without letting stale memory override the current codebase."
---

# ControlFlow Memory Hygiene

## Overview

Keep useful memory without letting it rot into hallucinated certainty. This skill ports ControlFlow's layered memory model into a lightweight Codex workflow for long-running tasks.

## Workflow

1. Separate memory into three layers:
   - session scratch for temporary reasoning
   - task artifact for plan and implementation history
   - repo-persistent note for stable cross-task facts
2. Put ephemeral reasoning in session notes or the active plan artifact. Only stable cross-task facts belong in persistent memory.
3. Re-verify any file, function, or test claim taken from memory before acting on it or reporting it.
4. Update the active objective only at phase boundaries or major state changes.
5. Keep the repo-persistent note terse: current objective, current phase, blockers, and decisions that are still active.
6. Prune stale entries aggressively using [references/prune-checklist.md](references/prune-checklist.md). If a note is superseded, delete or rewrite it instead of stacking contradictions.
7. If the user asks for fresh context or says to ignore memory, do not consult or update persistent notes on that turn.
8. Prefer additive artifacts in repo paths over bloated chat summaries.

## Common Mistakes

- Treating memory as stronger evidence than the current repository state.
- Storing task-specific churn in repo-persistent notes.
- Letting NOTES-like files become a second plan document.
- Updating durable notes before a phase outcome is actually verified.

## References

- `references/memory-layers.md`
- `references/notes-template.md`
- `references/prune-checklist.md`
