---
name: plan-tree
description: Maintain a structured planning document tree made of roadmap/status files, implementation status or handoff TODO files, topic notes, decision records, open questions, ideas/inspiration pools, and repository/file-structure hygiene plans. Use when Codex needs to create, reorganize, audit, or update a multi-file plan, design-doc folder, roadmap tree, active implementation-status file, repo cleanup/filesystem plan, ADR/decision log, ideas inbox, or linked planning knowledge base; reconcile Done/In Progress/Next state; resume work from TODO/handoff state; move resolved questions into decisions; promote ideas into formal plan artifacts; or keep plan documents and file-structure planning internally consistent without making this project-specific.
---

# Plan Tree

Use this skill to manage a tree of Markdown planning documents. The goal is to keep plans navigable, current, and internally consistent while preserving the user's intent and existing document style.

## Execution Contract

For every plan-tree task:

1. Identify the plan root and user intent before editing.
2. Read the root index plus only the relevant status, topic, decision, question, idea, or history files.
3. Classify the request as an idea, promotion, status update, question, decision, archive, audit, resume, restructure, or consistency repair.
4. Preserve the existing planning entrypoint, registered plan roots, folder names, document style, and authority order unless the task is specifically to reorganize them.
5. Keep active roadmap and handoff files small; move historical evidence out of active state.
6. Update indexes, retrieval headers, and links when adding, moving, promoting, archiving, or splitting durable files.
7. Run the final checks before replying.
8. Report changed files, unresolved questions, and the next useful maintenance action.

## Intent Routing

When the request maps to one of these intents, follow the corresponding behavior. Explicit shortcuts such as `$plan-tree idea` or `$plan-tree resume` are intent hints, not a strict command language; natural-language requests with the same meaning should behave the same way.

- `idea`: add a low-commitment thought to `ideas/inbox.md` or the local equivalent.
- `promote`: move an idea into a roadmap item, topic, open question, or decision, and link the original idea to the promoted artifact.
- `status`: update active implementation or handoff state.
- `question`: add, narrow, or resolve an open question.
- `decision`: create or update a stable decision record.
- `archive`: move superseded evidence, old status detail, or reference-only material out of active files.
- `audit`: run consistency, retrieval, and drift checks without changing structure unless asked.
- `resume`: follow the resume workflow and summarize current phase, TODO, blockers, next target, and last verification before editing.

## Document Model

Prefer this generic shape when creating a new tree, but adapt to existing names and conventions:

```text
<plan-root>/
  README.md
  roadmap.md
  implementation-status.md
  open-questions.md
  indexes/
    <optional-index>.md
  topics/
    repository-cleanup-and-filesystem-plan.md
    <topic>.md
  decisions/
    README.md
    001-<decision>.md
  history/
    <optional-status-or-checkpoint-history>.md
  ideas/
    <optional-idea-or-inbox>.md
```

The tree above defines document roles, not a mandatory directory template. Rules for adapting it:

- The top-level files and the `decisions/` folder are generic roles that most multi-file plans need. Only create the ones the plan actually uses.
- `topics/` is a content container. Its internal organization, such as flat files or role-based subfolders like `contracts/`, `frontend/`, and `operations/`, should follow the project's domain structure, not a fixed template. Let the project's natural groupings emerge before creating subfolders.
- `indexes/`, `history/`, and folder-level README files are maintenance structure. Add them only when a specific navigation or lifecycle problem appears, not preemptively.
- When introducing subfolders inside `topics/`, keep depth to two levels maximum, such as `topics/frontend/interaction-contract.md`. Deeper nesting harms discoverability more than flat listing does.

- `README.md`: purpose, scope, file map, and how to read the tree.
- `roadmap.md`: current state grouped as `Done`, `In Progress`, `Next`, and `Deferred` unless the existing tree uses another state model.
- `implementation-status.md` or equivalent handoff file: optional active execution state for resuming work across sessions. Use it for current phase, active TODO, last completed step, blockers, next commit target, verification, and handoff notes; do not use roadmap as a volatile task board when a separate handoff file exists or would help.
- `indexes/`: optional navigation helpers for large trees. Use when the root README or a folder listing becomes too long to scan.
- `topics/`: working context, options, constraints, implementation notes, and links to related decisions or questions.
- `topics/repository-cleanup-and-filesystem-plan.md` or equivalent: optional repo hygiene and file-structure plan for implementation efforts. Use it when the plan affects project layout, legacy cleanup, generated files, assets, uploads, migrations, tests, or archive/delete rules.
- `decisions/`: stable decision records. Use numbered kebab-case files when no naming scheme exists.
- `decisions/README.md` or equivalent decision index: optional for large decision sets. Group decisions by theme, active/superseded state, and related topics.
- `history/`: optional append-only or low-churn history for accepted checkpoints, old review/job detail, retired status snapshots, or phase logs that no longer belong in active handoff files.
- `ideas/` or equivalent: optional low-commitment inspiration pool for thoughts that are not yet questions, decisions, or roadmap items. Use it for future possibilities, external inspiration, unvalidated improvement directions, or speculative features that may never be built. Keep the barrier to entry minimal; a single `ideas/inbox.md` list is enough until the pool grows large enough to need individual files.
- `open-questions.md`: unresolved questions only. Do not use it as a todo list.

Rules for the ideas area:

- Ideas carry no commitment. They are not requirements, roadmap items, or open questions.
- When an idea matures into real work, promote it by creating a roadmap item, topic, open question, or decision as appropriate, and mark the original idea as promoted with a link. Do not duplicate the content.
- Do not force status labels or metadata on ideas. A one-line description is a valid idea entry. Add source, context, or links only when they help future evaluation.
- Periodically scan the ideas pool during planning sessions. Remove duplicates, mark promoted ideas, and delete ideas the user explicitly rejects. Do not auto-reject ideas based on age alone.

## Root And Folder Governance

Planning entrypoints, plan roots, and folders are long-lived governance boundaries, not task labels.

- A project should have one planning entrypoint. It may point to one canonical plan root or to a registry of multiple stable plan roots.
- Add a second plan root only when the scope is independent enough that merging it into the current tree would blur ownership, authority, or retrieval. Register each stable root in the planning entrypoint with its scope, status, and authority relationship.
- Choose plan root paths that reflect project content, not the tool name, such as `docs/rebuild-plan/`, `docs/architecture/`, or `docs/design/`. If multiple independent plan trees are truly needed, use a registry such as `docs/plans/README.md` and stable child roots.
- Do not scatter unregistered plan folders across the repository or create a new plan root for each task, phase, worker package, review round, or discussion. Put task-specific state in roadmap, implementation status, history, or the relevant topic instead.
- Folder names should represent stable project domains or document roles, not transient work packages. Avoid folders named after dates, workers, review rounds, or one-off tasks unless they are under `history/` and intentionally archival.
- Before adding a folder, check the nearest index for an existing home. If the category has only one or two files, prefer the existing folder plus retrieval keywords until the grouping proves durable.
- When adding a durable folder, update the nearest folder index with its purpose, boundaries, and example contents.

## Scaling Large Trees

When a plan tree grows beyond easy manual scanning, preserve the same concepts but add navigation and lifecycle boundaries before adding more long files.

Use large-tree maintenance when any of these are true:

- The root README has become a dense table of contents instead of a quick entrypoint.
- `roadmap.md` or an equivalent status file is mostly completed history rather than current direction.
- `implementation-status.md` requires reading old reviews, job ids, or checkpoint logs to find the next action.
- `topics/` contains many files with mixed roles such as contracts, phase plans, evidence, review notes, and operational runbooks.
- Decisions are numerous enough that readers need a theme index or active/superseded view.

Large-tree rules:

- Keep `README.md` as the entrypoint, not the full catalog. Prefer purpose, authority order, role-based reading paths, and links to indexes.
- Split long catalogs into local indexes such as `topics/README.md`, `decisions/README.md`, `indexes/phase-map.md`, or `indexes/authority-map.md` when those names fit the tree.
- Keep `roadmap.md` focused on current phase state and upcoming direction. Move accepted checkpoint logs, detailed completion history, and repeated verification summaries to `history/` or a dedicated checkpoint log.
- Keep `implementation-status.md` short enough for session resume. It should answer: what phase is active, what changed most recently, what is blocked, what is next, what was last verified, and where older evidence lives.
- Classify topic files by role when the folder is large: contracts, implementation plans, evidence/readiness, operations/runbooks, reviews, and legacy/context. Use either lightweight section labels in an index or subfolders if the existing tree already tolerates subfolders.
- When physically reorganizing topics into subfolders, start with the most cohesive group, update all relative links in the same commit, and verify the root README or topic index remains discoverable. Do not reorganize more than one group per pass.
- Prefer indexes over mass renames. Do not restructure a mature tree just to match the generic model unless navigation is already failing and links can be repaired safely.

## Workflow Detail

The execution contract above is the authoritative sequence. This section expands steps that benefit from additional guidance.

- Step 1: If the user did not give a path, infer the smallest existing planning folder from the request and nearby files; ask only when no safe inference exists.
- Step 2: Inventory existing files before editing. Read the root index, roadmap/status file, implementation status/handoff file if present, open questions, existing indexes/history files if present, and only the topic/decision files relevant to the request.
- Step 3: Classify each change as one of: status update, active implementation TODO update, repository/file-structure hygiene update, topic addition, decision record, resolved question, link repair, tree restructure, or consistency audit.
- Step 4: Edit the minimum set of files needed to keep the tree coherent. Preserve headings, language, naming style, and chronological order unless they actively prevent clarity.
- Step 7: Run final checks after edits. Check links, duplicated or conflicting decisions, status claims without support, orphan topics, resolved questions still listed as open, and roadmap items that should point to topics or decisions.

## Retrieval Units And Keywords

Treat each durable Markdown file as a retrieval unit. A maintainer or agent should be able to locate and read the relevant context without loading unrelated history.

Apply these rules when the tree has grown large enough that folder listing alone does not help a reader find the right file, typically when `topics/` exceeds 15-20 files or when multiple files share similar names.

- Prefer one responsibility per file. Add content to an existing file only when it shares the same role, lifecycle, authority level, and retrieval keywords.
- Use line counts as split signals, not strict law: keep active entrypoints/status files roughly under 150 lines, ordinary topics roughly under 300 lines, and large contracts/history files over roughly 500 lines indexed or split.
- When a file grows beyond easy scanning, split by topic, lifecycle, authority, or reader task. Do not split into arbitrary part numbers.
- Keep active roadmap and implementation-status files especially small. Move completed history and repeated evidence to `history/`.
- Use short retrieval headers on durable topic, decision, history, and expanded idea files when the tree is large. Typical fields are `Role`, `Status`, `Authority`, `Domain`, `Phase`, `Lifecycle`, `Read when`, and `Related`.
- Keep the controlled vocabulary small. Use generic keywords for role, status, authority, and lifecycle; define project-local domain or phase keywords in the nearest folder index.
- Search metadata and folder indexes before body text when the tree is large. If a search usually returns many unrelated files, split the overloaded file or add clearer metadata.

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
- When there are many decision records, maintain a decision index grouped by theme or phase. Mark superseded decisions explicitly and link to the superseding record instead of deleting or silently rewriting the old record.
- Keep decision records stable; put implementation progress, review outcomes, and operational evidence in status/history files rather than decision files.

## Status Maintenance

Treat roadmap state as evidence-based bookkeeping:

- Mark work `Done` only when the supporting artifact exists or the user explicitly says it is complete.
- Mark work `In Progress` only when there is active implementation, review, or a concrete next action already underway.
- Put unscheduled but accepted work in `Next`.
- Put intentionally postponed work in `Deferred`.
- Keep each state item short and link to the source topic, decision, PR, issue, or file when available.
- Do not let `Done` become a full changelog. Keep only durable milestones and move detailed package history, review ids, repeated test counts, and old checkpoint narratives to a history/checkpoint file.
- When a roadmap item accumulates many sub-bullets, promote the details to a phase/topic file and keep the roadmap item as a one-line link.

If a status item is contradicted by topic notes or decisions, fix the contradiction or surface it as an unresolved question.

## Implementation Status / Handoff

When the planning tree is being used to drive ongoing implementation, maintain a small active-status file if one exists, or create one when the user asks for durable TODO/handoff state across sessions.

Suggested filename:

- `implementation-status.md`

Use the local naming convention if the tree already has another equivalent status file.

Suggested sections:

```md
# Implementation Status

Date: YYYY-MM-DD

## Current Phase

## Active TODO

## Done This Phase

## Blockers

## Next Commit Target

## Last Verified Commands

## Handoff Notes
```

Rules:

- Keep this file short and operational. It is for session resume and immediate execution, not for architecture reasoning.
- Link active tasks back to roadmap items, phase details, topics, decisions, or issues.
- Move completed items into `Done This Phase` with evidence such as commit hash, test command, or created artifact.
- Keep `Blockers` limited to issues that currently stop progress. Move broader unresolved decisions to `open-questions.md`.
- Keep `Next Commit Target` concrete enough that a new session can resume without rereading the entire tree.
- Update this file at the end of implementation turns and whenever the active phase changes.
- Keep `roadmap.md` higher-level. Do not churn it for every small task when `implementation-status.md` is carrying active execution state.
- Keep old automation/CI/review job identifiers and routing details out of active handoff unless they are still blocking the next action. Preserve them in `history/`, a review log, or the relevant evidence topic.
- If the active-status file becomes difficult to skim, reduce it to current phase, active TODO, blockers, next target, latest verification, and links to older evidence.
- Treat `Active TODO` as the next few actionable items, not a full accepted-work inventory.

## History And Archival

Use history files to retain evidence without making every active document harder to read.

Good candidates for history:

- Accepted checkpoint logs and older commit/test summaries.
- Review/job ids after the package is accepted and no longer blocking work.
- Retired phase status snapshots.
- Old verification outputs that are superseded by newer gate evidence.
- Resolved review findings when the final decision or fix is already linked elsewhere.

Rules:

- Archive by moving stable, superseded detail behind a link; do not delete evidence just because it is noisy.
- Keep the active document with a short current summary and a pointer to the history file.
- Do not archive unresolved blockers, current owner decisions, active TODOs, or unsatisfied gates.
- Prefer chronological history files for execution logs and thematic history files for evidence that readers will search by subject.
- When a topic file is no longer referenced by any active roadmap item, open question, or implementation TODO, consider marking it as reference-only in the nearest index or moving it to `history/` if the tree uses that convention. Do not delete topics that preserve reasoning trails.

## Index And Link Hygiene

Indexes are maintenance tools, not another place to restate every detail.

- Create only the indexes that solve a real navigation problem in the current tree; most trees need at most one.
- Root README: keep purpose, scope, authority/order, how-to-read paths, and links to indexes.
- Topic index: group files by role or theme and include one-line descriptions.
- Decision index: group by theme/phase and show active/superseded relationships.
- Phase map: link each phase to its roadmap item, implementation detail, gate/checklist, evidence, and accepted checkpoint if those exist.
- Authority map: identify which file wins when roadmap, topic, decision, and implementation status disagree.
- When adding a new topic or decision, update the nearest useful index if one exists. If no index exists and the root README is already overloaded, create or recommend one.

## Repository And File-Structure Hygiene

When a planning tree will drive code implementation, preserve project file-structure cleanliness as part of the plan. Create or update a repo hygiene topic when cleanup, restructuring, generated artifacts, legacy files, media/assets, migrations, tests, or archive/delete decisions matter.

Suggested filename:

- `topics/repository-cleanup-and-filesystem-plan.md`

Use the local naming convention if an equivalent file already exists.

Suggested sections:

```md
# Repository Cleanup And Filesystem Plan

Date: YYYY-MM-DD

## Purpose

## Current Inventory

## Target Structure

## Keep / Move / Archive / Delete Rules

## Generated And Runtime Files

## Legacy Freeze Rules

## Cleanup Sequence

## Safety Checks
```

Rules:

- Inventory before deleting or moving files.
- Prefer archive/quarantine before irreversible deletion unless the user explicitly asks for deletion and the files are clearly generated/disposable.
- Preserve user-created source, docs, scripts, reusable assets, seeds, migrations, and production data unless a written rule says otherwise.
- Keep generated/runtime artifacts out of the source plan where possible: caches, coverage output, local databases, temporary uploads, logs, and build output should have clear ignore/cleanup rules.
- Keep old and new structures side by side during strangler/rebuild work until the old path is proven unused.
- Define target directories before moving files. Avoid ad hoc folders with unclear ownership.
- Record safety checks before cleanup: git status, backup/archive path, link/import search, tests or startup smoke, and rollback path.
- Update README or tree index when a new canonical directory or cleanup plan becomes part of the workflow.

## Final Checks

Run before replying after edits or an audit.

Governance and structure:

- Planning entrypoint, registered plan roots, and folder choices still follow root and folder governance rules.
- Any new stable plan root is registered in the planning entrypoint with scope, status, and authority relationship.
- Any added, moved, split, promoted, or archived durable file is discoverable from the nearest useful index or root README.
- Active roadmap and implementation-status files did not absorb completed history, repeated evidence, or old automation/review details.
- Ideas promoted into formal artifacts are marked promoted with a link.
- Open questions contain unresolved questions only, not tasks or already-decided items.
- Large or drifting files were split, indexed, archived, or explicitly left as-is with a reason.

Content and consistency:

- Relative Markdown links introduced or touched by the edit still resolve.
- Topic files that mention a decision but do not link to it.
- Decision files that are not referenced from any topic, index, or roadmap when they should be discoverable.
- Duplicate decisions covering the same choice.
- Open questions that are already answered by a decision.
- Active implementation TODOs that are contradicted by roadmap, phase gates, or decisions.
- Completed implementation-status items that have no evidence such as artifact, commit, or verification note.
- Repository cleanup tasks that delete/move files without inventory, archive/backup rule, owner decision, or rollback note.
- Newly introduced top-level directories or generated artifacts that are not documented, ignored, or assigned an owner.
- Roadmap state that claims completion without an artifact or decision trail.
- Multiple names for the same workstream.
- Markdown files that have grown into multiple unrelated retrieval units and should be split, indexed, or archived.
- Durable leaf files whose retrieval headers, folder index entries, or project-local keywords are missing or contradict their folder, role, authority, or lifecycle.
- Ideas that have been fully promoted to roadmap, topic, open question, or decision but are not marked as promoted in the ideas area.
- When a plan tree drives active implementation, periodically verify that key claims such as module boundaries, API shapes, and state machines still match the implemented code. Flag drift as an open question rather than silently updating the plan to match code that may itself be wrong.

Do not create a large framework when a short roadmap update or one decision record is enough.

## Resume Workflow

When the user asks to resume a planning/implementation effort after a new session:

1. Read `README.md` or the root index first.
2. Read the core/authority file if the tree has one.
3. Read `implementation-status.md` or equivalent handoff file if present.
4. Read `roadmap.md` for phase context.
5. Read only the phase/topic/decision files linked from the active TODO.
6. Summarize current phase, active TODO, blockers, next commit target, and last verification before editing or implementing.

## Boundaries

- This skill manages planning documents; it does not perform code review, architecture scoring, implementation, or release gating.
- Do not generate a full plan from scratch unless the user asks for one. If the user only asks to maintain the tree, work from existing material.
- Do not force the default folder names into an established tree. Respect local conventions.
- Do not treat open questions as tasks. If an item is actionable and decided, move it to the roadmap or a topic instead.
- Do not turn implementation status into a second roadmap. Keep it current-phase and handoff oriented.
- Do not hide tradeoffs to make the tree look cleaner. Planning trees are useful because they preserve the reasoning trail.
