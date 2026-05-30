# Repo-Memory Hygiene Skill

## Purpose

Pre-write checklist and prune routine for ControlFlow's repo-persistent memory layer. Load before any `/memories/repo/` write or `NOTES.md` update. Prevents the two main pollution modes: near-duplicate repo-memory entries and task-history bloat in `NOTES.md`.

**Governance flag:** `governance/runtime-policy.json → memory_hygiene.repo_memory_dedup_required: true`. When true, this checklist is mandatory before any `/memories/repo/` `create`.

## When to Load

- Before `create` on `/memories/repo/`, or updating `NOTES.md` at a phase boundary / task completion.
- When `<repository_memories>` shows near-duplicate entries.

Applicable agents: Orchestrator (mandatory at phase boundaries), Planner (before repo-memory writes after plan completion).

---

## Checklist A — Pre-Write Deduplication (`/memories/repo/`)

Work through every step before `create`. Any "DO NOT WRITE" → stop.

1. **Normalize the subject.** Strip plan name/task slug/date; express as a repo-wide invariant (e.g., "ControlFlow eval harness" not "memory-plan eval harness notes"). If task-specific (one plan only) → belongs in task-episodic memory (`plans/artifacts/<task-slug>/`). **DO NOT WRITE.**
2. **Check near-duplicates by subject.** Scan `<repository_memories>` for semantically overlapping subjects (same system/command/invariant, any phrasing). Same-or-more-specific fact already present → **DO NOT WRITE** (old entries decay naturally). Outdated/wrong → write one corrected fact noting "supersedes prior entry about X".
3. **Check fact-text similarity.** If your `fact` adds no information to a reader who has the existing entry, it is a duplicate → **DO NOT WRITE.** (The current block already holds 6 near-identical `cd evals && npm test` entries; any new harness-command entry without a materially new fact is a duplicate.)
4. **Verify cross-plan.** Ask: actionable for a future task unrelated to this plan? If "only for this plan" → task-episodic; record in `plans/artifacts/<task-slug>/`. **DO NOT WRITE.**
5. **Fill all required fields.** Valid only with all five: `subject`, `fact`, `citations` (file + line), `reason` (cross-plan value), `category`. Missing any → **DO NOT WRITE** until complete.

### Dedup Heuristic (Pinned)

Deterministic similarity check for Step 3 (all steps mandatory):

1. Normalize each text: lowercase → strip punctuation → collapse whitespace.
2. Build input: concatenate `subject || fact` (separator: single literal pipe `|`), then normalize.
3. Tokenize on whitespace.
4. Token Jaccard: `|A ∩ B| / |A ∪ B|` over existing vs. candidate token sets.
5. Threshold: Jaccard ≥ 0.85 → **FLAG** (never auto-delete/auto-skip).

**On FLAG — operator action required:** pause the `/memories/repo/ create`; emit a readable diff (existing ↔ candidate); operator picks one of `skip` (existing sufficient) / `merge into existing` (update citation/reason on existing only) / `create as new with rationale` (only if materially new; document in `reason`).

- Positive (flag expected): two `cd evals npm test` harness facts differing only in wording → Jaccard ≈ 0.89 → **FLAG**.
- Negative (no flag): terse CI mention vs. detailed harness description adding material detail → Jaccard ≈ 0.33 → **no flag** (legitimate refinement).

---

## Checklist B — NOTES.md Prune Routine

Run at every phase boundary and task completion. Target ≤20 lines (enforced by `evals/validate.mjs` Pass 7).

1. Read the full current `NOTES.md`.
2. Keep only active-objective lines ("current task/phase + live blockers"): one "Active objective" bullet (plan/task + phase/wave), one "Blockers" bullet ("none" if empty), optional one "Pending" bullet (single most-important next action).
3. Delete everything else: completed phase notes, iteration counts, verdict references, artifact paths, historical decisions, completed-step lists, code blocks, cross-task references → belong in `plans/artifacts/<task-slug>/` or are obsolete.
4. Pass `validateNotesMdStyle` (from `evals/drift-checks.mjs`). CI fails on: lines with `iteration`/`verdict`; `phase-\d+-` artifact path fragments; >3 consecutive bullets under one heading; fenced code blocks.
5. Verify line count ≤20; trim further if over.

---

## When to Escalate (DO NOT WRITE)

Return `ABSTAIN` or skip the write when: the fact is task-specific; a near-duplicate exists in `<repository_memories>`; the five required fields cannot be completed with direct evidence; or the subject normalizes to a fact already captured more precisely.

---

## Checklist C — Phase-Boundary Promotion

Run after each completed phase, at task completion, and whenever the Orchestrator's Agentic Memory Policy requires it. Work through every step before promoting.

1. **Classify by taxonomy.** Assign each candidate one of `user` / `feedback` / `project` / `reference` (`docs/agent-engineering/MEMORY-ARCHITECTURE.md → Memory Content Taxonomy`). **Drop** derivable code state, git history, or ephemeral task state (e.g., "file X modified", "iteration 3 passed", "test run at 14:32").
2. **Scope question.** Applies across multiple plans? If task-specific (only the current plan/slug) → `plans/artifacts/<task-slug>/`. **DO NOT PROMOTE** task-specific facts.
3. **Near-duplicate check.** Overlapping subject + same/less specific fact → skip. Overlapping + outdated/wrong → write **one** corrected entry noting "supersedes prior entry about X" (not both forms).
4. **Verify all five fields** before `create`: `subject` (normalized, repo-wide), `fact` (concrete, falsifiable), `citations` (≥1 file path + line), `reason` (cross-plan value), `category` (taxonomy type from Step 1). Incomplete → **DO NOT WRITE**.
5. **Skill-proposal check.** Run Skill-Proposal Candidate Criteria from `skills/patterns/memory-promotion-candidates.md` on any pattern that passed Steps 1–2, has confidence ≥0.85, and is not already in `skills/index.md`. For each: create a proposal via `plans/templates/skill-proposal-template.md` at `plans/artifacts/<task-slug>/skill-proposals/<pattern-slug>.md`; do NOT write to `skills/patterns/` directly (awaits human review); log the proposal path in the phase summary.

---

## Checklist D — Periodic Memory Audit (Diagnostic)

Read-only operator routine; produces an Audit Report, modifies nothing. Run when `<repository_memories>` shows 5+ entries for the same system/command, or after major restructuring.

1. **Identify near-duplicate groups.** For each group of overlapping subjects, mark the most specific/recent entry as **"keeper"**; list the rest as **"candidates for natural decay"** (age out via retention; no manual delete needed or possible).
2. **Spot-check citations.** Verify each cited file still exists (`file_search`/`grep_search`). Flag moved/deleted as **"stale citation — candidate for supersede write"**. Skip well-known stable paths (e.g., `evals/package.json`) absent positive evidence of change.
3. **Produce the Audit Report** (plain text, two sections): (1) near-duplicate groups with keeper + decay candidates; (2) stale-citation entries with path + why suspect. Do NOT write new entries unless Step 2 found a stale entry needing a corrected supersede write. **No automatic delete is possible via the `/memories/repo/` API** — supersede or let decay.

---

## Related

- `docs/agent-engineering/MEMORY-ARCHITECTURE.md` — Cleanup & Enforcement section (authoritative spec).
- `governance/runtime-policy.json → memory_hygiene` — thresholds consumed by this skill.
- `evals/drift-checks.mjs` — exports `validateNotesMdStyle`.
- `evals/archive-completed-plans.mjs` — task-episodic auto-archive script.
