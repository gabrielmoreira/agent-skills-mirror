# Repo-Memory Hygiene Skill

## Purpose

Pre-write checklist and prune routine for ControlFlow's repo-persistent memory layer. Load this skill before any `/memories/repo/` write or `NOTES.md` update. Prevents the two most common memory pollution failure modes: near-duplicate repo-memory entries and task-history bloat in `NOTES.md`.

**Governance flag:** `governance/runtime-policy.json → memory_hygiene.repo_memory_dedup_required: true`. If this flag is present and true, following this checklist is mandatory before any `/memories/repo/` `create` call.

## When to Load

- Before calling `create` on `/memories/repo/`.
- Before updating `NOTES.md` at a phase boundary or task completion.
- When the `<repository_memories>` block in context shows near-duplicate entries.

Applicable agents: Orchestrator (mandatory at phase boundaries), Planner (before any repo-memory write after plan completion).

---

## Checklist A — Pre-Write Deduplication (`/memories/repo/`)

Work through every step before calling `create`. If any step returns "DO NOT WRITE", stop and do not create the entry.

### Step 1: Normalize the subject

Rewrite your intended `subject` field in canonical form:

- Strip the plan name, task slug, or date from the subject.
- Express it as a repo-wide invariant (e.g., "ControlFlow eval harness" not "memory-plan eval harness notes").
- If the subject is task-specific (only applies to one plan), it belongs in **task-episodic memory** (`plans/artifacts/<task-slug>/`), not `/memories/repo/`. **DO NOT WRITE.**

### Step 2: Check for near-duplicates by subject

Scan the `<repository_memories>` context block for entries whose `subject` overlaps semantically with your normalized subject. Two subjects overlap if they describe the same system, command, or invariant — even with different phrasing.

- If an existing entry covers the same subject with the same or more specific fact: **DO NOT WRITE.** The retention mechanism will naturally decay older entries.
- If an existing entry is outdated or wrong: write a corrected fact with an explicit note ("supersedes prior entry about X"). One correction write per outdated fact.

### Step 3: Check for fact-text similarity

Compare your `fact` text against existing entries with the same subject. Similarity threshold: if your fact would convey no additional information to a reader who already has the existing entry, it is a duplicate. **DO NOT WRITE.**

Key signal: the current `<repository_memories>` block for this repo already shows 6 near-identical entries about `cd evals && npm test`. Any new entry describing the eval harness command without a materially new fact is a duplicate.

### Step 4: Verify the fact is cross-plan

Ask: "Will this fact be actionable for a future task unrelated to the current plan?" If the answer is "only for this plan", it is task-episodic. **DO NOT WRITE** to `/memories/repo/`; record in `plans/artifacts/<task-slug>/` instead.

### Step 5: Fill all required fields

A `/memories/repo/` entry is only valid with all five fields: `subject`, `fact`, `citations` (concrete file + line references), `reason` (why this is worth storing cross-plan), `category`. An entry missing any field may cause downstream readers to misinterpret it. **DO NOT WRITE** until all five fields are complete.

### Dedup Heuristic (Pinned)

A deterministic similarity check to run at Step 3 above. All steps are mandatory.

**Algorithm:**

1. **Normalize** each text: lowercase → strip punctuation → collapse whitespace.
2. **Build comparison input**: concatenate `subject || fact` (separator: a single literal pipe `|`), then normalize the combined string.
3. **Tokenize** on whitespace.
4. **Compute token Jaccard similarity**: `|A ∩ B| / |A ∪ B|` where A and B are the token sets of the existing and candidate entries.
5. **Threshold**: Jaccard ≥ 0.85 → **FLAG** (do not auto-delete or auto-skip).

**On FLAG — operator action required:**

- Pause the `/memories/repo/ create` call.
- Emit a readable diff of (existing fact ↔ candidate fact).
- Operator chooses one of:
  - `skip` — discard candidate; existing entry is sufficient.
  - `merge into existing` — update citation/reason fields on the existing entry only.
  - `create as new with rationale` — proceed only if candidate adds material new information; document the rationale in the `reason` field.

**Worked example (positive — flag expected):**

- Existing: `"ControlFlow eval harness|Canonical repository validation runs offline via cd evals npm test which executes validatemjs plus promptbehavior and orchestrationhandoff regression tests without invoking live agents"`
- Candidate: `"ControlFlow eval harness|Repository validation runs offline via cd evals npm test which executes validatemjs plus the promptbehavior and orchestrationhandoff regression tests without live agents"`
- Normalized Jaccard ≈ 0.89 → **FLAG**.

**Worked example (negative — no flag):**

- Existing: `"ControlFlow eval harness|Repositorys canonical verification is cd evals npm test offline eval harness and ci runs this command"`
- Candidate: `"ControlFlow eval harness|Canonical repository validation runs offline via cd evals npm test which executes validatemjs plus promptbehavior and orchestrationhandoff regression tests without invoking live agents"`
- Normalized Jaccard ≈ 0.33 → **no flag** (legitimate refinement — candidate adds material detail not present in the existing entry).

---

## Checklist B — NOTES.md Prune Routine

Run at every phase boundary and at task completion. Target: ≤20 lines (enforced by `evals/validate.mjs` Pass 7).

### Step 1: Open NOTES.md

Read the full current content.

### Step 2: Identify active-objective lines

Keep only lines that answer: "What is the current task and phase, and what are the live blockers?" Maximum structure:

- One "Active objective" bullet (what plan/task is running and which phase/wave).
- One "Blockers" bullet (empty "none" if no blockers).
- One "Pending" bullet for a single most-important next action (optional).

### Step 3: Delete everything else

Remove: completed phase notes, iteration counts, verdict references, artifact paths, historical decisions, list of completed steps, embedded code blocks, cross-references to other tasks. These belong in `plans/artifacts/<task-slug>/` or are no longer needed.

### Step 4: Verify the updated content passes the style check

The content must pass `validateNotesMdStyle` (exported from `evals/drift-checks.mjs`). Violations that will fail CI:

- Lines containing `iteration` or `verdict`.
- Lines containing `phase-\d+-` artifact path fragments.
- More than 3 consecutive bullet items under a single heading.
- Fenced code blocks.

### Step 5: Verify line count ≤ 20

Count lines. If > 20, trim further. The 20-line budget is enforced by CI.

---

## When to Escalate (DO NOT WRITE)

Return `ABSTAIN` or skip the write entirely when:

- The fact is task-specific (only applies to the current plan).
- A near-duplicate already exists in `<repository_memories>`.
- All five required fields cannot be completed with direct evidence.
- The subject normalizes to a fact that is already captured more precisely by an existing entry.

---

## Checklist C — Phase-Boundary Promotion

Decision routine run after each completed plan phase, before any `/memories/repo/` write. Work through every step before promoting any fact.

**When to run:** Run this checklist after every completed phase, at task completion, and whenever the Orchestrator's Agentic Memory Policy step requires it.

### Step 1: Classify each candidate fact by content taxonomy

For each candidate fact captured during the phase (in session notes or phase deliverable), assign one of the four taxonomy types from `docs/agent-engineering/MEMORY-ARCHITECTURE.md → Memory Content Taxonomy`: `user`, `feedback`, `project`, or `reference`.

Facts that are derivable code state, git history, or ephemeral task state (e.g., "file X was modified", "iteration 3 passed", "test run at 14:32") must be **dropped** — do not promote them.

### Step 2: Apply the scope question

Ask: does this fact apply across multiple plans (not just the current one)? If the fact is task-specific — meaning it is only relevant to the current plan or task slug — record it in `plans/artifacts/<task-slug>/` (task-episodic memory), not in `/memories/repo/`. **DO NOT PROMOTE** task-specific facts to repo-persistent memory.

### Step 3: Check for near-duplicates

Scan the `<repository_memories>` context block for entries with semantically overlapping `subject` fields:

- Same subject + same or less specific fact → **skip the write**; the existing entry is sufficient.
- Same subject + existing entry is outdated or wrong → write **one** corrected entry with an explicit note (e.g., "supersedes prior entry about X"). Do not write both the old and corrected form.

### Step 4: Verify all required fields before writing

Confirm all five required fields are present and complete before calling `create` on `/memories/repo/`:

- `subject` — normalized, repo-wide (not task-specific).
- `fact` — concrete, falsifiable statement.
- `citations` — at least one concrete file path + line reference.
- `reason` — explains why this is worth storing cross-plan.
- `category` — one of the taxonomy types from Step 1.

Incomplete entries must not be created. If any field cannot be completed with direct evidence, **DO NOT WRITE**.

---

## Checklist D — Periodic Memory Audit (Diagnostic)

Read-only manual routine for an operator to run periodically. Does not modify memory; produces an Audit Report only.

**When to run:** Run this routine when the `<repository_memories>` block shows 5+ entries for the same system or command, or after any major codebase restructuring.

### Step 1: Identify near-duplicate groups

Scan the `<repository_memories>` context block for entries with semantically overlapping `subject` fields. For each group of overlapping entries:

- Note the most specific or most recently written entry as the **"keeper"**.
- List the remaining entries as **"candidates for natural decay"** (they will age out via the retention mechanism; no manual deletion is needed or possible).

### Step 2: Spot-check citations for staleness

For each entry with file/line citations, verify that the cited file still exists at the expected path using a search tool (e.g., `file_search` or `grep_search`). Flag any entry whose cited file has moved or been deleted as:

> **stale citation — candidate for supersede write**

Do not flag entries whose cited file path is a well-known stable path (e.g., `evals/package.json`) unless you have positive evidence it has changed.

### Step 3: Produce the Audit Report

Output a plain-text **"Audit Report"** in the session with two sections:

1. **Near-duplicate groups** — list each group with its keeper and candidates for natural decay.
2. **Stale-citation entries** — list each flagged entry with the citation path and why it is suspect.

Do NOT write new `/memories/repo/` entries during this routine unless a stale entry clearly requires a corrected supersede write (identified in Step 2). Note explicitly: **no automatic delete is possible via the `/memories/repo/` API**; stale entries can only be superseded by a corrected write or allowed to decay naturally.

---

## Related

- `docs/agent-engineering/MEMORY-ARCHITECTURE.md` — Cleanup & Enforcement section (authoritative spec).
- `governance/runtime-policy.json → memory_hygiene` — thresholds consumed by this skill.
- `evals/drift-checks.mjs` — exports `validateNotesMdStyle`.
- `evals/archive-completed-plans.mjs` — task-episodic auto-archive script.
