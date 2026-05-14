---
name: plan-tree
description: Maintain a structured planning document tree made of roadmap/status files, topic notes, decision records, and open questions. Use when Codex needs to create, reorganize, audit, or update a multi-file plan, design-doc folder, roadmap tree, ADR/decision log, or linked planning knowledge base; reconcile Done/In Progress/Next state; move resolved questions into decisions; or keep plan documents internally consistent without making this project-specific.
---

# Plan Tree

Use this skill to manage a tree of Markdown planning documents. The goal is to keep plans navigable, current, and internally consistent while preserving the user's intent and existing document style.

## Document Model

Prefer this generic shape when creating a new tree, but adapt to existing names and conventions:

```text
<plan-root>/
  README.md
  roadmap.md
  open-questions.md
  topics/
    <topic>.md
  decisions/
    001-<decision>.md
```

- `README.md`: purpose, scope, file map, and how to read the tree.
- `roadmap.md`: current state grouped as `Done`, `In Progress`, `Next`, and `Deferred` unless the existing tree uses another state model.
- `topics/`: working context, options, constraints, implementation notes, and links to related decisions or questions.
- `decisions/`: stable decision records. Use numbered kebab-case files when no naming scheme exists.
- `open-questions.md`: unresolved questions only. Do not use it as a todo list.

## Workflow

1. Identify the plan root and objective. If the user did not give a path, infer the smallest existing planning folder from the request and nearby files; ask only when no safe inference exists.
2. Inventory existing files before editing. Read the root index, roadmap/status file, open questions, and only the topic/decision files relevant to the request.
3. Classify each change as one of: status update, topic addition, decision record, resolved question, link repair, tree restructure, or consistency audit.
4. Edit the minimum set of files needed to keep the tree coherent. Preserve headings, language, naming style, and chronological order unless they actively prevent clarity.
5. Run a consistency pass after edits. Check links, duplicated or conflicting decisions, status claims without support, orphan topics, resolved questions still listed as open, and roadmap items that should point to topics or decisions.
6. Report changed files, the state transition made, unresolved questions, and the next useful maintenance action.

## Decision Records

When a question has converged into a decision, create or update a decision record instead of leaving the conclusion scattered in topics or roadmap notes.

Use this minimal shape when no local template exists:

```md
# Short Decision Title

Date: YYYY-MM-DD

## Context

Why the decision was needed.

## Decision

The chosen direction.

## Consequences

What this enables, constrains, or defers.
```

Rules:

- Keep decisions descriptive, not promotional.
- Do not rewrite old decisions as if they were made today. Append a superseding decision when the direction changes.
- Link decisions back to the relevant topic and roadmap item when those files exist.
- Move resolved questions out of `open-questions.md`; retain any remaining uncertainty as a narrower follow-up question.

## Status Maintenance

Treat roadmap state as evidence-based bookkeeping:

- Mark work `Done` only when the supporting artifact exists or the user explicitly says it is complete.
- Mark work `In Progress` only when there is active implementation, review, or a concrete next action already underway.
- Put unscheduled but accepted work in `Next`.
- Put intentionally postponed work in `Deferred`.
- Keep each state item short and link to the source topic, decision, PR, issue, or file when available.

If a status item is contradicted by topic notes or decisions, fix the contradiction or surface it as an unresolved question.

## Consistency Checks

Before finishing, check for:

- Broken relative Markdown links introduced or touched by the edit.
- Topic files that mention a decision but do not link to it.
- Decision files that are not referenced from any topic, index, or roadmap when they should be discoverable.
- Duplicate decisions covering the same choice.
- Open questions that are already answered by a decision.
- Roadmap state that claims completion without an artifact or decision trail.
- Multiple names for the same workstream.

Do not create a large framework when a short roadmap update or one decision record is enough.

## Boundaries

- This skill manages planning documents; it does not perform code review, architecture scoring, implementation, or release gating.
- Do not generate a full plan from scratch unless the user asks for one. If the user only asks to maintain the tree, work from existing material.
- Do not force the default folder names into an established tree. Respect local conventions.
- Do not treat open questions as tasks. If an item is actionable and decided, move it to the roadmap or a topic instead.
- Do not hide tradeoffs to make the tree look cleaner. Planning trees are useful because they preserve the reasoning trail.
